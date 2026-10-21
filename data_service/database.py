
import os
import sqlite3
from pathlib import Path

DATABASE_PATH = os.getenv(
    "DATABASE_PATH",
    "data/stocks.db"
)


def get_connection():
    # Cria o diretório do banco, se necessário.
    Path(DATABASE_PATH).parent.mkdir(
        parents=True,
        exist_ok=True
    )

    conn = sqlite3.connect(
        DATABASE_PATH,
        timeout=30
    )

    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA busy_timeout = 30000")

    return conn


def init_db():
    with get_connection() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS clientes (
                id_cliente INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL UNIQUE,
                senha TEXT NOT NULL,
                saldo REAL NOT NULL DEFAULT 0
                    CHECK (saldo >= 0)
            );

            CREATE TABLE IF NOT EXISTS carteiras (
                id_carteira INTEGER PRIMARY KEY AUTOINCREMENT,
                id_cliente INTEGER NOT NULL UNIQUE,
                FOREIGN KEY (id_cliente)
                    REFERENCES clientes(id_cliente)
                    ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS ativos_carteira (
                id_carteira INTEGER NOT NULL,
                ticker TEXT NOT NULL,
                quantidade INTEGER NOT NULL DEFAULT 0
                    CHECK (quantidade >= 0),
                PRIMARY KEY (id_carteira, ticker),
                FOREIGN KEY (id_carteira)
                    REFERENCES carteiras(id_carteira)
                    ON DELETE CASCADE
            );
            
            CREATE TABLE IF NOT EXISTS operacoes (
                id_operacao INTEGER PRIMARY KEY AUTOINCREMENT,
                id_carteira INTEGER NOT NULL,
                ticker TEXT NOT NULL,
                tipo TEXT NOT NULL
                    CHECK (tipo IN ('COMPRA', 'VENDA')),
                quantidade INTEGER NOT NULL
                    CHECK (quantidade > 0),
                preco_unitario REAL NOT NULL
                    CHECK (preco_unitario >= 0),
                data_hora TEXT NOT NULL
                    DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (id_carteira)
                    REFERENCES carteiras(id_carteira)
            );
        """)
