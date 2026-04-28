from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# Carrega as variáveis do arquivo .env
load_dotenv()

# Puxa a URL do cofre em vez de deixar escrita aqui
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

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