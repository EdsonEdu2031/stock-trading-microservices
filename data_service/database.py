
import os
import sqlite3
from pathlib import Path

DB_PATH = os.getenv("DB_PATH", "stock.db")

Path(DB_PATH).parent.mkdir(parents=True, exist_ok=True)

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
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
        
        """)
