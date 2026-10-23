from datetime import datetime
from zoneinfo import ZoneInfo
import yfinance as yf

def obter_cotacao(ticker: str) -> dict:
    ticker = ticker.strip().upper()

    if not ticker:
        raise ValueError("O ticker não pode estar vazio.")

    # Adiciona o sufixo da Bolsa brasileira quando necessário.
    ticker_yahoo = ticker if "." in ticker else f"{ticker}.SA"

    acao = yf.Ticker(ticker_yahoo)

    # Tenta obter os dados intradiários mais recentes.
    historico = acao.history(
        period="1d",
        interval="1m",
        auto_adjust=False
    )

    # Se não houver dados intradiários, usa o histórico diário.
    if historico.empty:
        historico = acao.history(
            period="5d",
            interval="1d",
            auto_adjust=False
        )

    if historico.empty or "Close" not in historico.columns:
        raise ValueError(
            f"Não foi possível obter a cotação de {ticker_yahoo}."
        )

    historico = historico.dropna(subset=["Close"])

    if historico.empty:
        raise ValueError(
            f"Não há preços válidos para {ticker_yahoo}."
        )

    ultima_linha = historico.iloc[-1]
    preco = float(ultima_linha["Close"])
    data_cotacao = historico.index[-1]

    if data_cotacao.tzinfo is None:
        data_cotacao = data_cotacao.tz_localize("UTC")

    data_cotacao = data_cotacao.tz_convert(
        ZoneInfo("America/Sao_Paulo")
    )

    return {
        "ticker": ticker,
        "ticker_provedor": ticker_yahoo,
        "preco": round(preco, 2),
        "moeda": "BRL",
        "fonte": "Yahoo Finance",
        "atualizado_em": data_cotacao.isoformat()
    }
