---

## 📂 Meu Sistema Financeiro - Guia de Arquitetura

### 🌍 1. Onde tudo está hospedado
* **Banco de Dados (DB):** [Neon.tech](https://neon.tech) (PostgreSQL nas nuvens).
* **Backend (API):** [Render.com](https://render.com) (Hospeda o código Python/FastAPI).
* **Frontend (Interface):** [Streamlit Cloud](https://share.streamlit.io) (A tela que eu e o Tiago acessamos).

---

### ⚙️ 2. Tecnologias Utilizadas
* **Linguagem:** Python.
* **Framework API:** FastAPI (Rápido e moderno).
* **ORM:** SQLAlchemy (Para o Python conversar com o SQL).
* **Manipulação de Dados:** Pandas (Usado no script de migração).

---

### 🔑 3. Credenciais e URLs Importantes
* **GitHub:** Repositório `meu_sistema_financeiro` (Onde o código "mora").
* **DATABASE_URL (Render):** Deve sempre começar com `postgresql://` e terminar com `?sslmode=require` para o Neon aceitar a conexão.
* **Login do Sistema:**
    * **Usuário:** Seu e-mail cadastrado.
    * **Senha Padrão:** `146946`.

---

### 🛠️ 4. Scripts Úteis (Rodar no VS Code)
* **`main.py`:** O coração da API (rotas de resumo, transações, etc.).
* **`migrar_dados.py`:** Teletransporte de dados do SQLite/Postgres local para o Neon.
* **`frontend.py`:** Onde eu mudo o visual e as cores do site no Streamlit.

---

### ⚠️ 5. Lembretes de Manutenção
* **Sequências do Banco:** Se eu migrar dados novos via Pandas e o ID parar de funcionar, devo rodar o `SELECT setval(...)` no SQL Editor do Neon para sincronizar os contadores.
* **Deploy:** Toda vez que eu der **Sync Changes** no VS Code, o Render faz o deploy automático em ± 1 minuto.
* **Variáveis de Ambiente:** Credenciais sensíveis ficam escondidas no `.env` (local) e na aba "Environment" (no Render), nunca abertas no código.

---
