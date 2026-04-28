### 🚀 GUIA RÁPIDO - SISTEMA FINANCEIRO

#### 1. Como rodar o sistema (Abrir 2 terminais no VS Code)

* **Terminal 1 (Backend - API):**
    ```bash
    source .venv/bin/activate
    uvicorn main:app --reload
    ```
* **Terminal 2 (Frontend - Site):**
    ```bash
    source .venv/bin/activate
    streamlit run frontend.py
    ```

---

#### 2. Links Importantes

* **Banco de Dados (Neon):** [https://neon.tech](https://neon.tech)
* **Documentação da API (Local):** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
* **Dashboard (Local):** [http://localhost:8501](http://localhost:8501)

---

#### 3. Comandos do Banco de Dados (Neon)

* **Inicializar via NPX:** `npx neonctl@latest init`
* **Instalar e Inicializar (Linux/Mac):** `brew install neonctl && neonctl init`

---

#### 4. Instalação (Caso precise refazer o ambiente)

* **Criar Ambiente Virtual:** `python3 -m venv .venv`
* **Ativar Ambiente:** `source .venv/bin/activate`
* **Instalar tudo:**
    ```bash
    pip install fastapi uvicorn sqlalchemy streamlit pandas plotly requests apscheduler psycopg2-binary
    ```

---

#### 5. Lembretes de Configuração

* **Arquivo `main.py`:** Contém o "Cérebro" e as rotas da API.
* **Arquivo `frontend.py`:** Contém a interface e os gráficos.
* **Conexão Banco:** A linha `SQLALCHEMY_DATABASE_URL` no `main.py` (ou `database.py`) deve ter o link do Neon que começa com `postgresql://...`.

---

**Dica:** No VS Code, você pode deixar os dois terminais abertos lado a lado clicando no ícone de "Split Terminal" (o quadradinho cortado ao meio no canto superior do terminal). Assim você monitora o "motor" e o "painel" ao mesmo tempo!
