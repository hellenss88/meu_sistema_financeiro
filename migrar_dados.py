import pandas as pd
from sqlalchemy import create_engine

print("🚀 Iniciando o teletransporte de dados...")

# 1. Suas duas chaves de conexão
# Substitua pela URL que você usava antes (ex: sqlite:///./banco.db ou a do seu Postgres local)
URL_ANTIGA = "postgresql://postgres:146946@localhost:5432/financas_familia" 

# Substitua pela sua URL completa do Neon
URL_NOVA = "postgresql://neondb_owner:npg_KN6FkUGXI2yf@ep-floral-mud-amfdg395.c-5.us-east-1.aws.neon.tech/neondb?sslmode=require"

engine_antigo = create_engine(URL_ANTIGA)
engine_novo = create_engine(URL_NOVA)

# 2. Ordem das tabelas (Atualizada para incluir Investimentos e Dólar)
tabelas = ["transacoes", "contas_fixas", "investimentos", "conta_dolar"]

# 3. A mágica do Pandas
for tabela in tabelas:
    print(f"\nLendo dados da tabela '{tabela}'...")
    try:
        # Puxa tudo do banco antigo e transforma em um DataFrame
        df = pd.read_sql(f"SELECT * FROM {tabela}", engine_antigo)
        
        if not df.empty:
            print(f"Encontradas {len(df)} linhas. Copiando para as nuvens...")
            # Joga o DataFrame inteiro no banco novo de uma vez só!
            # if_exists='append' garante que ele só adicione os dados, sem apagar a tabela.
            df.to_sql(tabela, engine_novo, if_exists='append', index=False)
            print(f"✅ Tabela '{tabela}' copiada com sucesso!")
        else:
            print("⚠️ Tabela vazia. Pulando...")
            
    except Exception as e:
        print(f"❌ Ops, deu erro na tabela {tabela}: {e}")

print("\n🎉 Migração concluída com sucesso! Seu banco na nuvem já tem histórico.")