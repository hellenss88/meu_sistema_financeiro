import streamlit as st
import requests

if "logado" not in st.session_state:
    st.session_state.logado = False
    st.session_state.usuario_id = None
    st.session_state.nome_usuario = ""

# Configurações da página
st.set_page_config(page_title="Finanças Familiares", page_icon="💰")
st.title("💰 Sistema Financeiro Familiar")

# Endereço do seu FastAPI (o motor que está rodando no fundo)
API_URL = "https://meu-sistema-financeiro.onrender.com"

# Cria uma "memória" para o site saber se você está logada
if "usuario_id" not in st.session_state:
    st.session_state["usuario_id"] = None

# --- TELA DE LOGIN ---
if st.session_state["usuario_id"] is None:
    st.subheader("Acesso Restrito")
    
    # Criamos um formulário para o Streamlit entender que o "Enter" envia tudo
    with st.form("form_login"):
        email = st.text_input("E-mail")
        senha = st.text_input("Senha", type="password") # Esconde o que é digitado
        
        # O st.button vira st.form_submit_button
        botao_entrar = st.form_submit_button("Entrar")
        
# O "if" agora fica fora do form e olha para a variável do botão
    if botao_entrar:
        if email and senha:
            # Pede para o FastAPI conferir a senha
            resposta = requests.post(f"{API_URL}/login?email={email}&senha={senha}")
            
            if resposta.status_code == 200:
                dados = resposta.json()
                
                # --- AQUI ESTÁ A MUDANÇA: SALVANDO O ESTADO ---
                st.session_state["logado"] = True
                st.session_state["usuario_id"] = dados["usuario_id"]
                st.session_state["nome_usuario"] = dados["nome"]
                
                st.success(f"Bem-vinda, {dados['nome']}!")
                st.balloons() # Solta balõezinhos na tela!
                
                # O rerun agora vai ver que "logado" é True e mudar a tela
                st.rerun() 
            else:
                st.error("❌ E-mail ou senha incorretos.")
        else:
            st.warning("Preencha os dois campos.")

# --- TELA PRINCIPAL ---
else:
    import datetime
    import pandas as pd # <-- Agora o Pandas entra em ação!

    # 1. Busca os dados atualizados
    try:
        # Tenta buscar o resumo do banco de dados
        resposta_resumo = requests.get(f"{API_URL}/resumo/{st.session_state['usuario_id']}")
        resumo = resposta_resumo.json()
    except Exception as e:
        # Plano B: Se o servidor falhar, define valores zerados para a tela não quebrar
        st.warning("⚠️ O servidor está acordando. Os valores abaixo serão atualizados em instantes...")
        resumo = {
            "entradas": 0, "saidas_reais": 0, "saldo_em_conta": 0, 
            "divida_cartao": 0, "investimento_total": 0, "dolar_total": 0,
            "data_investimento": None, "data_dolar": None
        }

    # Busca a lista de todas as transações para os gráficos
    try:
        resposta_transacoes = requests.get(f"{API_URL}/transacoes/{st.session_state['usuario_id']}")
        todas_transacoes = resposta_transacoes.json()
    except:
        todas_transacoes = []
    
    st.sidebar.button("Sair", on_click=lambda: st.session_state.update({"usuario_id": None}))

    # Função de Formatação BR
    def formata_br(valor):
        return f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    # --- TOP CARDS (Layout 2x2 que você preferiu) ---
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Saldo em Conta", f"R$ {formata_br(resumo['saldo_em_conta'])}")
        data_i = resumo['data_investimento'] if resumo['data_investimento'] else "Nunca"
        st.metric("Investimentos", f"R$ {formata_br(resumo['investimento_total'])}", help=f"Última atualização: {data_i}")

    with col2:
        data_d = resumo['data_dolar'] if resumo['data_dolar'] else "Nunca"
        st.metric("Dólar (USD)", f"$ {formata_br(resumo['dolar_total'])}", help=f"Última atualização: {data_d}")
        st.metric("Dívida de Cartões", f"R$ {formata_br(resumo['divida_cartao'])}", delta_color="inverse")

    st.divider()

    # --- SISTEMA DE ABAS ---
    aba_lancamento, aba_relatorio, aba_previsao = st.tabs(["➕ Novos Lançamentos", "📊 Relatórios e Filtros", "🗓️ Previsão do Mês"])

    with aba_lancamento:
        col_esq, col_dir = st.columns(2)

        with col_esq:
            with st.expander("➕ Novo Gasto/Entrada", expanded=True):
                with st.form("form_transacao", clear_on_submit=True):
                    data = st.date_input("Data", datetime.date.today(), format="DD/MM/YYYY")
                    desc = st.text_input("Descrição")
                    val = st.number_input("Valor", min_value=0.01)
                    fin = st.selectbox("Finalidade", ["Alimentação", "Assinaturas", "Carro", "Casa", "Dívidas", "Empréstimo", "Estudos", "Investimentos", "Lazer", "Pensão", "Presente", "Salário", "Saúde", "Seguro", "UniTV", "Vale-Alimentação", "Vendas", "Vestuário", "Viagem", "Outros"])
                    tipo = st.selectbox("Tipo", ["saida", "entrada"])
                    met = st.selectbox("Método", ["PIX", "Boleto", "Dinheiro", "Débito", "CC - Inter Hellen", "CC - XP Tiago", "CC - ML Hellen", "CC - Nu Tiago"])
                    
                    if st.form_submit_button("Salvar"):
                        payload = {"descricao": desc, "valor": val, "finalidade": fin, "tipo": tipo, "metodo_pagamento": met, "data_transacao": data.isoformat()}
                        requests.post(f"{API_URL}/transacoes/{st.session_state['usuario_id']}", json=payload)
                        st.rerun()

        with col_dir:
            with st.expander("💳 Pagar Fatura", expanded=True):
                st.write("Selecione o cartão e a data de fechamento.")
                cartao_alvo = st.selectbox("Cartão", ["CC - Inter Hellen", "CC - XP Tiago", "CC - ML Hellen", "CC - Nu Tiago"])
                data_fechamento = st.date_input("Até qual data pagar?", format="DD/MM/YYYY")
                
                if st.button("Confirmar Pagamento da Fatura"):
                    payload_f = {"metodo_pagamento": cartao_alvo, "data_corte": data_fechamento.isoformat()}
                    res = requests.post(f"{API_URL}/pagar_fatura/{st.session_state['usuario_id']}", json=payload_f).json()
                    st.success(f"Pago! R$ {res['valor_pago']:.2f} processados.")
                    st.rerun()

    with aba_relatorio:
        # Aqui entra o seu conhecimento de Data Science!
        df = pd.DataFrame(todas_transacoes)
        
        if df.empty:
            st.info("Lance alguns gastos para ver os gráficos!")
        else:
            st.subheader("🔍 Filtros e Análise")
            df['data_transacao'] = pd.to_datetime(df['data_transacao'])
            
            # --- Filtro de data inteligente (Padrão: Últimos 30 dias) ---
            # O Python calcula que dia foi 30 dias atrás
            trinta_dias_atras = datetime.date.today() - datetime.timedelta(days=30)
            
            col_f1, col_f2 = st.columns(2)
            with col_f1:
                # O padrão agora é trinta_dias_atras, mas você pode editar na tela quando quiser!
                dt_inicio = st.date_input("De:", trinta_dias_atras, format="DD/MM/YYYY")
            with col_f2:
                dt_fim = st.date_input("Até:", datetime.date.today(), format="DD/MM/YYYY")

            # Aplicando filtros no DataFrame
            mask = (df['data_transacao'].dt.date >= dt_inicio) & (df['data_transacao'].dt.date <= dt_fim)
            df_filtrado = df.loc[mask]

            # Gráficos Dinâmicos
            g1, g2 = st.columns(2)
            
            with g1:
                st.write("### Gastos por Categoria")
                saidas = df_filtrado[df_filtrado['tipo'] == 'saida']
                if not saidas.empty:
                    import plotly.express as px
                    
                    # Prepara os dados do jeito que o Plotly gosta
                    pizza = saidas.groupby('finalidade', as_index=False)['valor'].sum()
                    
                    # Cria um gráfico de rosca (hole=0.4) interativo
                    fig = px.pie(pizza, values='valor', names='finalidade', hole=0.4)
                    
                    # Plota na tela do Streamlit
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.write("Sem saídas no período.")

            with g2:
                # 1. Preparar os dados com Pandas
                if todas_transacoes:
                    df = pd.DataFrame(todas_transacoes)
                    df['data_transacao'] = pd.to_datetime(df['data_transacao'])
                    
                    # Criar uma coluna de Mês/Ano para agrupar
                    df['Mes'] = df['data_transacao'].dt.strftime('%b/%Y')
                    
                    # Agrupar por Mês e Tipo, somando os valores
                    df_mensal = df.groupby(['Mes', 'tipo'])['valor'].sum().reset_index()
                    
                    # Pivotar os dados para o gráfico de barras
                    df_pivot = df_mensal.pivot(index='Mes', columns='tipo', values='valor').fillna(0)
                    
                    st.subheader("Balanço Mensal: Entradas vs Saídas")
                    st.bar_chart(df_pivot)
                else:
                    st.info("Ainda não há transações para gerar o balanço mensal.")

            st.write("### Extrato Detalhado")
            
            # Cria uma cópia só para a tela (assim não quebra os filtros)
            df_tela = df_filtrado[['id', 'data_transacao', 'descricao', 'valor', 'finalidade', 'metodo_pagamento', 'pago']].copy()
            
            # Formata a coluna para o padrão BR (DD/MM/AAAA) e arranca as horas
            df_tela['data_transacao'] = df_tela['data_transacao'].dt.strftime('%d/%m/%Y')
            
            # --- NOVIDADE: Renomeando as colunas para o visual ---
            df_tela = df_tela.rename(columns={
                'id': 'ID',
                'data_transacao': 'Data',
                'descricao': 'Descrição',
                'valor': 'Valor (R$)',
                'finalidade': 'Categoria',
                'metodo_pagamento': 'Método',
                'pago': 'Pago?'
            })
            
            # Exibe a tabela escondendo o índice numérico (0,1,2,3...) para ficar mais limpo
            st.dataframe(df_tela, use_container_width=True, hide_index=True)
            st.divider()
            st.write("### ✏️ Gerenciar Lançamentos")
            
            # Cria uma lista pro seletor no formato: "12 | Mercado (R$ 150.0)"
            opcoes_lista = df_filtrado.apply(lambda x: f"{x['id']} | {x['descricao']} (R$ {x['valor']})", axis=1).tolist()
            escolha = st.selectbox("Selecione um lançamento para Editar ou Excluir:", ["Selecione..."] + opcoes_lista)
            
            if escolha != "Selecione...":
                # Pega só o número do ID (tudo antes da barra reta)
                id_selecionado = int(escolha.split(" |")[0])
                
                # Resgata todos os dados daquela linha do Pandas
                linha = df_filtrado[df_filtrado['id'] == id_selecionado].iloc[0]
                
                st.write(f"**Alterando o lançamento:** {linha['descricao']}")
                
                # Formulário visual de edição
                c1, c2 = st.columns(2)
                with c1:
                    novo_desc = st.text_input("Nova Descrição", value=linha['descricao'])
                    nova_data = st.date_input("Nova Data", linha['data_transacao'].date(), format="DD/MM/YYYY")
                    novo_val = st.number_input("Novo Valor", value=float(linha['valor']), min_value=0.01)
                
                with c2:
                    novo_tipo = st.selectbox("Novo Tipo", ["saida", "entrada"], index=0 if linha['tipo']=='saida' else 1)
                    
                    lista_fin = ["Alimentação", "Assinaturas", "Carro", "Casa", "Dívidas", "Empréstimo", "Estudos", "Investimentos", "Lazer", "Pensão", "Presente", "Salário", "Saúde", "Seguro", "UniTV", "Vale-Alimentação", "Vendas", "Vestuário", "Viagem", "Outros"]
                    idx_fin = lista_fin.index(linha['finalidade']) if linha['finalidade'] in lista_fin else 0
                    nova_fin = st.selectbox("Nova Finalidade", lista_fin, index=idx_fin)
                    
                    lista_met = ["PIX", "Boleto", "Dinheiro", "Débito", "CC - Inter Hellen", "CC - XP Tiago", "CC - ML Hellen", "CC - Nu Tiago"]
                    idx_met = lista_met.index(linha['metodo_pagamento']) if linha['metodo_pagamento'] in lista_met else 0
                    novo_met = st.selectbox("Novo Método", lista_met, index=idx_met)
                
                # Botões de Ação
                col_btn1, col_btn2 = st.columns(2)
                with col_btn1:
                    if st.button("💾 Atualizar Lançamento", use_container_width=True):
                        payload = {"descricao": novo_desc, "valor": novo_val, "finalidade": nova_fin, "tipo": novo_tipo, "metodo_pagamento": novo_met, "data_transacao": nova_data.isoformat()}
                        requests.put(f"{API_URL}/transacoes/{id_selecionado}", json=payload)
                        st.success("Atualizado com sucesso!")
                        st.rerun()
                
                with col_btn2:
                    # type="primary" deixa o botão de excluir destacado (geralmente vermelho)
                    if st.button("🗑️ Excluir Lançamento", type="primary", use_container_width=True):
                        requests.delete(f"{API_URL}/transacoes/{id_selecionado}")
                        st.error("Lançamento excluído permanentemente!")
                        st.rerun()

    with aba_previsao:
        st.subheader("🗓️ Suas Contas Fixas Mensais")
        
        # Puxa os dados do banco
        contas_fixas = requests.get(f"{API_URL}/contas_fixas/{st.session_state['usuario_id']}").json()
        
        col_form, col_lista = st.columns([1, 2])
        
        # LADO ESQUERDO: Adicionar Nova Conta
        with col_form:
            with st.form("form_conta_fixa", clear_on_submit=True):
                st.write("➕ **Nova Conta Fixa**")
                desc_cf = st.text_input("Descrição (Ex: Aluguel)")
                val_cf = st.number_input("Valor Estimado", min_value=0.01)
                dia_cf = st.number_input("Dia do Vencimento", min_value=1, max_value=31, value=10)
                met_cf = st.selectbox("Método Previsto", ["PIX", "Boleto", "Débito Automático", "CC - Inter Hellen", "CC - XP Tiago", "CC - ML Hellen", "CC - Nu Tiago"])
                
                if st.form_submit_button("Salvar Conta Fixa", use_container_width=True):
                    payload_cf = {"descricao": desc_cf, "valor": val_cf, "dia_vencimento": dia_cf, "metodo_pagamento": met_cf}
                    requests.post(f"{API_URL}/contas_fixas/{st.session_state['usuario_id']}", json=payload_cf)
                    st.rerun()

        # LADO DIREITO: Tabela e Gerenciamento
        with col_lista:
            df_cf = pd.DataFrame(contas_fixas)
            if not df_cf.empty:
                # Soma total prevista
                total_previsto = df_cf['valor'].sum()
                st.info(f"💰 **Total Fixo Previsto para o Mês: R$ {formata_br(total_previsto)}**")
                
                # Tabela de visualização limpa
                df_tela_cf = df_cf[['id', 'dia_vencimento', 'descricao', 'valor', 'metodo_pagamento']].copy()
                df_tela_cf = df_tela_cf.rename(columns={'id': 'ID', 'dia_vencimento': 'Dia', 'descricao': 'Descrição', 'valor': 'Valor (R$)', 'metodo_pagamento': 'Método'})
                st.dataframe(df_tela_cf, use_container_width=True, hide_index=True)
                
                # Edição e Exclusão (Igual ao extrato)
                st.write("✏️ **Editar ou Excluir**")
                opcoes_cf = df_cf.apply(lambda x: f"{x['id']} | {x['descricao']} (Dia {x['dia_vencimento']})", axis=1).tolist()
                escolha_cf = st.selectbox("Selecione uma conta para modificar:", ["Selecione..."] + opcoes_cf)
                
                if escolha_cf != "Selecione...":
                    id_cf = int(escolha_cf.split(" |")[0])
                    linha_cf = df_cf[df_cf['id'] == id_cf].iloc[0]
                    
                    with st.expander("Modificar Conta", expanded=True):
                        c1, c2 = st.columns(2)
                        with c1:
                            e_desc = st.text_input("Descrição", value=linha_cf['descricao'], key="e_desc")
                            e_val = st.number_input("Valor", value=float(linha_cf['valor']), key="e_val")
                        with c2:
                            e_dia = st.number_input("Dia", value=int(linha_cf['dia_vencimento']), min_value=1, max_value=31, key="e_dia")
                            lista_met = ["PIX", "Boleto", "Débito Automático", "CC - Inter Hellen", "CC - XP Tiago", "CC - ML Hellen", "CC - Nu Tiago"]
                            idx_met = lista_met.index(linha_cf['metodo_pagamento']) if linha_cf['metodo_pagamento'] in lista_met else 0
                            e_met = st.selectbox("Método", lista_met, index=idx_met, key="e_met")
                        
                        btn1, btn2 = st.columns(2)
                        if btn1.button("💾 Atualizar", use_container_width=True):
                            requests.put(f"{API_URL}/contas_fixas/{id_cf}", json={"descricao": e_desc, "valor": e_val, "dia_vencimento": e_dia, "metodo_pagamento": e_met})
                            st.rerun()
                        if btn2.button("🗑️ Excluir", type="primary", use_container_width=True):
                            requests.delete(f"{API_URL}/contas_fixas/{id_cf}")
                            st.rerun()
            else:
                st.write("Nenhuma conta fixa cadastrada ainda.")

    # Sidebar: Seus formulários de atualização manual (Snapshots)
    with st.sidebar:
        st.divider()
        st.subheader("📈 Snapshots de Patrimônio")
        novo_v = st.number_input("Investimento Total (BRL)", min_value=0.0, value=float(resumo['investimento_total']))
        if st.button("Salvar Patrimônio"):
            p_inv = {"valor": novo_v, "data_verificacao": datetime.date.today().isoformat()}
            requests.post(f"{API_URL}/investimentos/{st.session_state['usuario_id']}", json=p_inv)
            st.rerun()
            
        st.divider()
        novo_usd = st.number_input("Total Dólar (USD)", min_value=0.0, value=float(resumo['dolar_total']))
        if st.button("Salvar Saldo Dólar"):
            p_usd = {"valor": novo_usd, "data_verificacao": datetime.date.today().isoformat()}
            requests.post(f"{API_URL}/dolar/{st.session_state['usuario_id']}", json=p_usd)
            st.rerun()