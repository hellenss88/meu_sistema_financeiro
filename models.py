from sqlalchemy import Column, Integer, String, Numeric, ForeignKey, Boolean, Date
from sqlalchemy.orm import relationship
from database import Base
import datetime

class Usuario(Base):
    __tablename__ = "usuarios"
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    senha_hash = Column(String, nullable=False)
    
    # Relacionamentos
    transacoes = relationship("Transacao", back_populates="dono")
    cartoes = relationship("Cartao", back_populates="dono")

class Cartao(Base):
    __tablename__ = "cartoes"
    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"))
    nome_cartao = Column(String, nullable=False)
    dia_vencimento = Column(Integer, nullable=False)
    dia_fechamento = Column(Integer, nullable=False)
    
    dono = relationship("Usuario", back_populates="cartoes")
    transacoes = relationship("Transacao", back_populates="cartao")

class Transacao(Base):
    __tablename__ = "transacoes"
    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"))
    cartao_id = Column(Integer, ForeignKey("cartoes.id"), nullable=True)
    descricao = Column(String, nullable=False)
    valor = Column(Numeric(10, 2), nullable=False)
    finalidade = Column(String)
    tipo = Column(String) # entrada ou saida
    metodo_pagamento = Column(String)
    pago = Column(Boolean, default=False)
    data_transacao = Column(Date, default=datetime.date.today)
    data_pagamento_real = Column(Date, nullable=True)
    finalidade = Column(String)

    dono = relationship("Usuario", back_populates="transacoes")
    cartao = relationship("Cartao", back_populates="transacoes")

class Investimento(Base):
    __tablename__ = "investimentos"
    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"))
    valor = Column(Numeric(10, 2), nullable=False)
    data_verificacao = Column(Date, nullable=False)

class ContaDolar(Base):
    __tablename__ = "conta_dolar"
    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"))
    valor = Column(Numeric(10, 2), nullable=False)
    data_verificacao = Column(Date, nullable=False)

class ContaFixa(Base):
    __tablename__ = "contas_fixas"
    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"))
    descricao = Column(String, nullable=False)
    valor = Column(Numeric(10, 2), nullable=False)
    dia_vencimento = Column(Integer, nullable=False)
    metodo_pagamento = Column(String, nullable=False)