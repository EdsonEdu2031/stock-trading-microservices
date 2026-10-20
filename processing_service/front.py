import streamlit as st
import requests

API_URL = "http://localhost:8001"

st.set_page_config(page_title = "Sistema de Venda de ações", layout="wide")

# Função para exibir o título com tamanho customizado utilizando css
def titulo(texto, tamanho=14):
    st.markdown(f'<p style="font-size: {tamanho}px; margin: 0;"><b>{texto}</b></p>', unsafe_allow_html=True)

if "token" not in st.session_state:
    st.session_state["token"] = None

if "nome" not in st.session_state:
    st.session_state["nome"] = None

col1, col2, col3 = st.columns(3)
if st.session_state["token"] is None:
    with col2:
        st.title("Login")
        nome = st.text_input("Digite o seu nome:", placeholder="Ex: Maria Silva")
        senha = st.text_input("Digite sua senha:", placeholder="Senha")

        if st.button("Login"):
            try:
                resposta = requests.post(
                    f"{API_URL}/login",
                    json={"nome": nome, "senha": senha},
                    timeout=10
                )

                if resposta.status_code == 200:
                    dados = resposta.json()

                    st.session_state["token"] = dados["access_token"]
                    st.session_state["nome"] = dados["nome"]

                    st.rerun()

                elif resposta.status_code == 401:
                    st.error("Nome ou senha inválidos.")

                else:
                    st.error("Não foi possível realizar o login.")
            except requests.RequestException:
                st.error("Não foi possível conectar ao Serviço de Dados.")
else:
    with col2:
        st.title(f"Bem-vindo {st.session_state["nome"]}")
        # Mostrar carteira


