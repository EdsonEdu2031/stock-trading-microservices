from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
import requests
import os

app = FastAPI(title="Report Service")

DATA_SERVICE_URL = os.getenv("DATA_SERVICE_URL", "http://data_service:8000")

def get_user_data(id_cliente: int):
    response = requests.get(f"{DATA_SERVICE_URL}/cliente/{id_cliente}", timeout=5)
    if response.status_code != 200:
        raise HTTPException(status_code=404, detail="User not found")
    return response.json()

def get_user_portfolio(id_cliente: int):
    response = requests.get(f"{DATA_SERVICE_URL}/carteira/{id_cliente}", timeout=5)
    if response.status_code != 200:
        return []
    return response.json()

@app.get("/reports/html/{user_id}", response_class=HTMLResponse)
def generate_html_report(user_id: int):
    user = get_user_data(user_id)
    portfolio = get_user_portfolio(user_id)

    nome = user.get('nome', 'Cliente')
    saldo = user.get('saldo', 0.0)

    table_rows = ""
    for item in portfolio:
        table_rows += f"""
        <tr>
            <td style="padding: 12px; border-bottom: 1px solid #30363d;">{item.get('ticker')}</td>
            <td style="padding: 12px; border-bottom: 1px solid #30363d;">{item.get('quantidade')}</td>
        </tr>
        """

    if not table_rows:
        table_rows = "<tr><td colspan='2' style='text-align:center; padding: 12px; color: #8b949e;'>Nenhum ativo na carteira.</td></tr>"

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; margin: 20px; background-color: #0d1117; color: #c9d1d9; }}
            .card {{ background: #161b22; padding: 25px; border-radius: 8px; border: 1px solid #30363d; max-width: 600px; margin: auto; }}
            h1 {{ color: #58a6ff; margin-bottom: 15px; font-size: 22px; }}
            p {{ font-size: 15px; margin: 6px 0; color: #8b949e; }}
            strong {{ color: #c9d1d9; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 20px; background: #0d1117; border-radius: 6px; overflow: hidden; }}
            th {{ background-color: #21262d; color: #58a6ff; padding: 12px; text-align: left; border-bottom: 2px solid #30363d; }}
        </style>
    </head>
    <body>
        <div class="card">
            <h1>📊 Relatório da Carteira de Ações</h1>
            <p><strong>Investidor(a):</strong> {nome}</p>
            <p><strong>Saldo Disponível:</strong> R$ {float(saldo):.2f}</p>
            
            <table>
                <thead>
                    <tr>
                        <th>Ativo (Ticker)</th>
                        <th>Quantidade</th>
                    </tr>
                </thead>
                <tbody>
                    {table_rows}
                </tbody>
            </table>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)