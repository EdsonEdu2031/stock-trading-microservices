from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field
import sqlite3
from database import init_db, get_connection


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="Stock Trading Data Service", lifespan=lifespan)


# Modelos
class Cliente(BaseModel):
    nome: str
    senha: str
    saldo: float = Field(default=0, ge=0)


class Carteira(BaseModel):
    id_carteira: int
    ticker: str
    quantidade: int = Field(ge=0)
    valor: float = Field(ge=0)

class Login(BaseModel):
    nome: str
    senha: str


# Autenticação 
@app.post("/login")
def logar(login: Login):
    with get_connection() as conn:
        try:
            cursor = conn.execute(
                "SELECT id_cliente, nome, saldo FROM clientes WHERE nome = ? AND senha = ?",
                (login.nome, login.senha)
            ).fetchone()

            if not cursor:
                return {"status": 401}

            if cursor:
                return {"id_cliente": cursor["id_cliente"], "nome": cursor["nome"],"saldo": cursor["saldo"], "status": 200}
        except:
            return 

@app.post("/cadastro")
def cadastro_cliente(cliente: Cliente):
    with get_connection() as conn:
        try:
            cursor = conn.execute(
                "INSERT INTO clientes (nome, senha, saldo) VALUES (?, ?, ?)",
                (cliente.nome, cliente.senha, cliente.saldo)
            )
            id_cliente = cursor.lastrowid

            cursor = conn.execute(
                "INSERT INTO carteiras (id_cliente) VALUES (?)",
                (id_cliente,)
            )
            id_carteira = cursor.lastrowid

            conn.commit()

            return {"id_cliente": id_cliente, "id_carteira": id_carteira, "nome": cliente.nome, "saldo": cliente.saldo, "status": 201}

        except sqlite3.IntegrityError:
            conn.rollback()
            return {"status": 409}

#para relatório
@app.get("/cliente/{id_cliente}")
def buscar_cliente(id_cliente: int):
    with get_connection() as conn:
        cursor = conn.execute(
            "SELECT id_cliente, nome, saldo FROM clientes WHERE id_cliente = ?",
            (id_cliente,)
        ).fetchone()
        
        if not cursor:
            raise HTTPException(status_code=404, detail="Cliente não encontrado")
            
        return {
            "id_cliente": cursor["id_cliente"],
            "nome": cursor["nome"],
            "saldo": cursor["saldo"]
        }

@app.get("/carteira/{id_cliente}")
def buscar_carteira(id_cliente: int):
    with get_connection() as conn:
        cursor = conn.execute("""
            SELECT ac.ticker, ac.quantidade 
            FROM ativos_carteira ac
            JOIN carteiras c ON c.id_carteira = ac.id_carteira
            WHERE c.id_cliente = ?
        """, (id_cliente,)).fetchall()
        
        return [{"ticker": row["ticker"], "quantidade": row["quantidade"]} for row in cursor]

# Operações
@app.post("/comprar")
def comprar_ativo(compra: Carteira):
    with get_connection() as conn:
        try:
            cursor = conn.execute(
                """INSERT INTO ativos_carteira (id_carteira, ticker, quantidade) VALUES (?, ?, ?) 
                ON CONFLICT(id_carteira, ticker) DO UPDATE SET quantidade = quantidade + excluded.quantidade""",
                (compra.id_carteira, compra.ticker.strip().upper(), compra.quantidade)
            )

            cursor = conn.execute(
                "UPDATE clientes SET saldo = saldo - ? WHERE id_cliente = ?",
                (compra.valor, compra.id_carteira)
            )

            conn.commit()

            cursor = conn.execute(
                "SELECT saldo FROM clientes WHERE id_cliente = ?",
                (compra.id_carteira,)
            ).fetchone()

            return {"saldo": cursor["saldo"], "status": 200}
        except:
            return {"status": 401}
        

@app.post("/vender")
def vender_ativo(operacao: Carteira):
    with get_connection() as conn:
        try:
            cursor = conn.execute(
                "UPDATE ativos_carteira SET quantidade = quantidade - ? WHERE id_carteira = ? AND ticker = ?",
                (operacao.quantidade, operacao.id_carteira, operacao.ticker.strip().upper())
            )

            cursor = conn.execute(
                "DELETE FROM ativos_carteira WHERE id_carteira = ? AND ticker = ? AND quantidade <= 0",
                (operacao.id_carteira, operacao.ticker.strip().upper())
            )

            cursor = conn.execute(
                "UPDATE clientes SET saldo = saldo + ? WHERE id_cliente = ?",
                (operacao.valor, operacao.id_carteira)
            )
            
            conn.commit()

            cursor = conn.execute(
                "SELECT saldo FROM clientes WHERE id_cliente = ?",
                (operacao.id_carteira,)
            ).fetchone()

            return {"saldo": cursor["saldo"], "status": 200}
        except:
            return {"status": 401}

@app.get("/carteiras/{id_carteira}")
def buscar_ativos_carteira(id_carteira: int):
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT ticker, quantidade FROM ativos_carteira WHERE id_carteira = ?",
            (id_carteira,)
        ).fetchall()
        return [dict(row) for row in rows]