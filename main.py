from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Usuario, Transacao, Investimento, ContaDolar, ContaFixa
from pydantic import BaseModel
from typing import Optional
from sqlalchemy import func
from enum import Enum
from datetime import date
from apscheduler.schedulers.background import BackgroundScheduler
import smtplib
from email.mime.text import MIMEText


app = FastAPI()

# --- ENUMS (Listas Restritas para o TOC não sofrer! Haha) ---
class CategoriaFinalidade(str, Enum):
    alimentacao = "Alimentação"
    assinaturas = "Assinaturas"
    carro = "Carro"
    casa = "Casa"
    dividas = "Dívidas"
    emprestimo = "Empréstimo"
    estudos = "Estudos"
    investimentos = "Investimentos"
    lazer = "Lazer"
    pensao = "Pensão"
    pet = "Pet"
    presente = "Presente"
    salario = "Salário"
    saude = "Saúde"
    seguro = "Seguro"
    unitv = "UniTV"
    vale_alimentacao = "Vale-Alimentação"
    vendas = "Vendas"
    vestuario = "Vestuário"
    viagem = "Viagem"
    outros = "Outros"

class MetodoPagamento(str, Enum):
    pix = "PIX"
    boleto = "Boleto"
    dinheiro = "Dinheiro"
    debito = "Débito"
    cc_inter = "CC - Inter Hellen"
    cc_xp = "CC - XP Tiago"
    cc_ml = "CC - ML Hellen"
    cc_nu = "CC - Nu Tiago"
    cc_c6 = "CC - C6 Tiago"

# --- SCHEMAS ---
class TransacaoCreate(BaseModel):
    descricao: str
    valor: float
    finalidade: CategoriaFinalidade
    tipo: str 
    metodo_pagamento: MetodoPagamento
    data_transacao: date
    cartao_id: Optional[int] = None

class PagamentoFatura(BaseModel):
    metodo_pagamento: MetodoPagamento
    data_corte: date

class InvestimentoUpdate(BaseModel):
    valor: float
    data_verificacao: date

class DolarUpdate(BaseModel):
    valor: float
    data_verificacao: date

class TransacaoUpdate(BaseModel):
    descricao: str
    valor: float
    finalidade: str
    tipo: str
    metodo_pagamento: str
    data_transacao: date

class ContaFixaSchema(BaseModel):
    descricao: str
    valor: float
    dia_vencimento: int
    metodo_pagamento: str


# --- ROTAS ---
@app.get("/")
def home():
    return {"mensagem": "Sistema Financeiro Hellen & Tiago - Ativo"}

@app.post("/login")
def login(email: str, senha: str, db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter(Usuario.email == email).first()
    if not usuario or usuario.senha_hash != senha:
        raise HTTPException(status_code=401, detail="Dados incorretos")
    return {"status": "sucesso", "usuario_id": usuario.id, "nome": usuario.nome}

@app.post("/transacoes/{usuario_id}")
def criar_transacao(usuario_id: int, transacao: TransacaoCreate, db: Session = Depends(get_db)):
    nova_transacao = Transacao(
        usuario_id=usuario_id,
        descricao=transacao.descricao,
        valor=transacao.valor,
        finalidade=transacao.finalidade,
        tipo=transacao.tipo,
        metodo_pagamento=transacao.metodo_pagamento,
        data_transacao=transacao.data_transacao,
        # Se for Cartão de Crédito (CC), começa como NÃO PAGO
        pago=False if "CC -" in transacao.metodo_pagamento else True
    )
    db.add(nova_transacao)
    db.commit()
    db.refresh(nova_transacao)
    return {"status": "sucesso", "item": nova_transacao}

@app.get("/resumo/{usuario_id}")
def obter_resumo(usuario_id: int, db: Session = Depends(get_db)):
    # Agora somamos TUDO de todos os usuários para a conta conjunta
    entradas = db.query(func.sum(Transacao.valor)).filter(Transacao.tipo == 'entrada').scalar() or 0
    saidas_reais = db.query(func.sum(Transacao.valor)).filter(Transacao.tipo == 'saida', Transacao.pago == True).scalar() or 0
    divida_cartao = db.query(func.sum(Transacao.valor)).filter(Transacao.tipo == 'saida', Transacao.pago == False).scalar() or 0
    
    # Snapshot Investimento (Pega o último lançamento global)
    ultimo_inv = db.query(Investimento).order_by(Investimento.data_verificacao.desc()).first()
    inv_total = ultimo_inv.valor if ultimo_inv else 0
    data_inv = ultimo_inv.data_verificacao if ultimo_inv else None

    # NOVO: Snapshot Dólar (Pega o último lançamento global)
    ultimo_dolar = db.query(ContaDolar).order_by(ContaDolar.data_verificacao.desc()).first()
    
    dolar_total = ultimo_dolar.valor if ultimo_dolar else 0.0
    data_dolar = ultimo_dolar.data_verificacao if ultimo_dolar else None

    return {
        "entradas": entradas,
        "saidas_reais": saidas_reais,
        "saldo_em_conta": entradas - saidas_reais,
        "divida_cartao": divida_cartao,
        "investimento_total": inv_total,
        "data_investimento": data_inv,
        "dolar_total": dolar_total,
        "data_dolar": data_dolar
    }

# Rota para salvar novo valor de Dólar (No final do arquivo)
@app.post("/dolar/{usuario_id}")
def atualizar_dolar(usuario_id: int, d: DolarUpdate, db: Session = Depends(get_db)):
    novo_dolar = ContaDolar(usuario_id=usuario_id, valor=d.valor, data_verificacao=d.data_verificacao)
    db.add(novo_dolar)
    db.commit()
    return {"status": "sucesso"}

@app.post("/pagar_fatura/{usuario_id}")
def pagar_fatura(usuario_id: int, pagamento: PagamentoFatura, db: Session = Depends(get_db)):
    # Pega os gastos do cartão X até a data de corte que você informar
    transacoes = db.query(Transacao).filter(
        Transacao.usuario_id == usuario_id,
        Transacao.metodo_pagamento == pagamento.metodo_pagamento.value,
        Transacao.data_transacao <= pagamento.data_corte,
        Transacao.pago == False
    ).all()
    
    total = sum([t.valor for t in transacoes])
    for t in transacoes:
        t.pago = True
        
    db.commit()
    return {"status": "sucesso", "valor_pago": total, "itens_pagos": len(transacoes)}

@app.post("/investimentos/{usuario_id}")
def atualizar_investimento(usuario_id: int, inv: InvestimentoUpdate, db: Session = Depends(get_db)):
    novo_inv = Investimento(
        usuario_id=usuario_id,
        valor=inv.valor,
        data_verificacao=inv.data_verificacao
    )
    db.add(novo_inv)
    db.commit()
    return {"status": "sucesso"}

@app.get("/transacoes/{usuario_id}")
def listar_transacoes(usuario_id: int, db: Session = Depends(get_db)):
    # Agora buscamos TODAS as transações do banco, independente de quem as criou
    # A variável usuario_id continua no nome da função para não quebrar o Streamlit,
    # mas o banco de dados vai ignorar ela e trazer tudo.
    return db.query(Transacao).order_by(Transacao.data_transacao.desc()).all()

# --- ROTA PARA ATUALIZAR (EDITAR) ---
@app.put("/transacoes/{transacao_id}")
def editar_transacao(transacao_id: int, t: TransacaoUpdate, db: Session = Depends(get_db)):
    # Procura a transação pelo ID
    transacao = db.query(Transacao).filter(Transacao.id == transacao_id).first()
    if transacao:
        transacao.descricao = t.descricao
        transacao.valor = t.valor
        transacao.finalidade = t.finalidade
        transacao.tipo = t.tipo
        transacao.metodo_pagamento = t.metodo_pagamento
        transacao.data_transacao = t.data_transacao
        db.commit()
        return {"status": "sucesso"}
    return {"status": "erro"}

# --- ROTA PARA DELETAR ---
@app.delete("/transacoes/{transacao_id}")
def deletar_transacao(transacao_id: int, db: Session = Depends(get_db)):
    transacao = db.query(Transacao).filter(Transacao.id == transacao_id).first()
    if transacao:
        db.delete(transacao)
        db.commit()
        return {"status": "sucesso"}
    return {"status": "erro"}

# --- ROTAS DE CONTAS FIXAS ---
@app.get("/contas_fixas/{usuario_id}")
def listar_contas_fixas(usuario_id: int, db: Session = Depends(get_db)):
    return db.query(ContaFixa).filter(ContaFixa.usuario_id == usuario_id).order_by(ContaFixa.dia_vencimento.asc()).all()

@app.post("/contas_fixas/{usuario_id}")
def criar_conta_fixa(usuario_id: int, c: ContaFixaSchema, db: Session = Depends(get_db)):
    nova_conta = ContaFixa(usuario_id=usuario_id, descricao=c.descricao, valor=c.valor, dia_vencimento=c.dia_vencimento, metodo_pagamento=c.metodo_pagamento)
    db.add(nova_conta)
    db.commit()
    return {"status": "sucesso"}

@app.put("/contas_fixas/{conta_id}")
def editar_conta_fixa(conta_id: int, c: ContaFixaSchema, db: Session = Depends(get_db)):
    conta = db.query(ContaFixa).filter(ContaFixa.id == conta_id).first()
    if conta:
        conta.descricao = c.descricao
        conta.valor = c.valor
        conta.dia_vencimento = c.dia_vencimento
        conta.metodo_pagamento = c.metodo_pagamento
        db.commit()
        return {"status": "sucesso"}
    return {"status": "erro"}

@app.delete("/contas_fixas/{conta_id}")
def deletar_conta_fixa(conta_id: int, db: Session = Depends(get_db)):
    conta = db.query(ContaFixa).filter(ContaFixa.id == conta_id).first()
    if conta:
        db.delete(conta)
        db.commit()
        return {"status": "sucesso"}
    return {"status": "erro"}
