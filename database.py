from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Configuração da URL de conexão: usuario:senha@local:porta/banco
SQLALCHEMY_DATABASE_URL = "postgresql://neondb_owner:npg_KN6FkUGXI2yf@ep-floral-mud-amfdg395.c-5.us-east-1.aws.neon.tech/neondb?sslmode=require"

# O Engine é o motor que gerencia a conexão
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# A SessionLocal é o que usaremos para fazer as consultas (Queries)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para criarmos os modelos das tabelas depois
Base = declarative_base()

# Função auxiliar para abrir e fechar a conexão automaticamente
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

print("Conexão com o banco configurada com sucesso!")