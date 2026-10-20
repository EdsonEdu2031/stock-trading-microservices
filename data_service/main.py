
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

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


class Ativo(BaseModel):
    ticker: str
    nome: str
    preco_atual: float = Field(ge=0)


# Clientes
@app.post("/clientes")
def criar_cliente(cliente: Cliente):
    with get_connection() as conn:
        cursor = conn.execute(
            "INSERT INTO clientes (nome, senha, saldo) VALUES (?, ?, ?)",
            (cliente.nome, cliente.senha, cliente.saldo)
        )
        id_cliente = cursor.lastrowid

        cursor = conn.execute(
            "INSERT INTO carteiras (id_cliente) VALUES (?)",
            (id_cliente,)
        )

        return {
            "id_cliente": id_cliente,
            "id_carteira": cursor.lastrowid,
            "nome": cliente.nome
        }


@app.get("/clientes")
def listar_clientes():
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT id_cliente, nome, saldo FROM clientes"
        ).fetchall()
        return [dict(row) for row in rows]


