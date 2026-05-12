from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import sqlite3
import os

# Inicializa o aplicativo FastAPI
app = FastAPI(title="Portal Tiro Esportivo Dinâmico")

# Configuração de CORS (Permite requisições do frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Cria e conecta ao Banco de Dados SQLite local
def init_db():
    conn = sqlite3.connect('acervo.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS processos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            processo TEXT,
            gru TEXT,
            estado TEXT,
            delegacia TEXT,
            tipo TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db() # Executa a criação do banco ao ligar o servidor

# Estrutura de dados esperada do Frontend
class ProcessoNovo(BaseModel):
    processo: str
    gru: str
    estado: str
    delegacia: str
    tipo: str

# ROTA DA API 1: Buscar todos os processos
@app.get("/api/processos")
def listar_processos():
    conn = sqlite3.connect('acervo.db')
    conn.row_factory = sqlite3.Row # Retorna como dicionário
    cursor = conn.cursor()
    cursor.execute("SELECT processo, gru, estado, delegacia, tipo FROM processos")
    linhas = cursor.fetchall()
    conn.close()
    return [dict(linha) for linha in linhas]

# ROTA DA API 2: Gravar um novo processo
@app.post("/api/processos")
def cadastrar_processo(p: ProcessoNovo):
    conn = sqlite3.connect('acervo.db')
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO processos (processo, gru, estado, delegacia, tipo) VALUES (?, ?, ?, ?, ?)",
        (p.processo, p.gru, p.estado, p.delegacia, p.tipo)
    )
    conn.commit()
    conn.close()
    return {"mensagem": "Processo salvo com sucesso no banco de dados!"}


# ==========================================
# ROTAS FRONTEND (Servindo o HTML, CSS e JS)
# ==========================================

# Garante que a pasta static existe antes de tentar montá-la
if not os.path.exists("static"):
    os.makedirs("static")

# Monta a pasta 'static' para servir arquivos estáticos (como imagens, se tiver no futuro)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Rota principal para abrir o site
@app.get("/")
def read_index():
    # Retorna o arquivo index.html que está dentro da pasta static
    return FileResponse('static/index.html')
