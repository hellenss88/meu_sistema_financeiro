from database import SessionLocal
from models import Usuario

def testar_login():
    db = SessionLocal()
    try:
        # Tenta buscar o usuário que você inseriu no DBeaver
        email_procurado = "hellenss88@gmail.com"
        usuario = db.query(Usuario).filter(Usuario.email == email_procurado).first()

        if usuario:
            print(f"\n✅ CONEXÃO OK! Usuário encontrado: {usuario.nome}")
            print(f"🔑 Senha no banco: {usuario.senha_hash}")
        else:
            print("\n❌ Banco conectado, mas usuário não encontrado. Verifique o email no DBeaver.")
    except Exception as e:
        print(f"\n❌ ERRO DE CONEXÃO: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    testar_login()