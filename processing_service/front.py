import streamlit as st
import requests
import pandas as pd

API_URL = "http://localhost:8001"

st.set_page_config(page_title = "Sistema de Venda de ações", layout="wide")

# Função para exibir o título com tamanho customizado utilizando css
def titulo(texto, tamanho=14):
    st.markdown(f'<p style="font-size: {tamanho}px; margin: 0;"><b>{texto}</b></p>', unsafe_allow_html=True)

def incrementar(i):
    st.session_state[f"contador_{i}"] += 1

def decrementar(i):
    if st.session_state[f"contador_{i}"] > 0:
        st.session_state[f"contador_{i}"] -= 1

def comprar_acoes(id_carteira, saldo):
    total_compra = 0
    for ac in acoes:
        total_compra+= st.session_state[f"contador_{i}"]*acoes[i]

    if saldo < total_compra:
        st.error(f"Saldo insuficiente são necessários R${total_compra}")
    # Terminar de implementar
    return 0
dados = {
    'Ticker': ['Abba', 'Baab'],
    'Quantidade': [5, 2]
}
acoes = {
    'Abba': 5.82,
    'Baab': 58.2,
    'Caac': 582.0
}
dados = pd.DataFrame(dados)


dados['Valor da Ação (R$)'] = dados['Ticker'].map(acoes)
dados['Valor total (R$)'] = dados['Valor da Ação (R$)'] * dados['Quantidade']


for i in acoes:
    if f"contador_{i}" not in st.session_state:
        st.session_state[f"contador_{i}"] = 0

if "token" not in st.session_state:
    st.session_state["token"] = None

if "nome" not in st.session_state:
    st.session_state["nome"] = None

col1, col2, col3 = st.columns(3)
if st.session_state["token"] is None:
    with col2:
        opcao = st.radio("Acesso", ["Login", "Cadastro"], horizontal=True)

        if opcao == "Login":
            st.title("Login")

            with st.form("form_login"):
                nome = st.text_input("Digite o seu nome:", placeholder="Fulano de tal")
                senha = st.text_input("Digite sua senha:", type="password", placeholder="Senha")
                enviar = st.form_submit_button("Login")

            if enviar:
                st.session_state["token"] = 'askask'
                st.session_state["nome"] = 'Tayana'
                st.rerun()
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
            st.title("Cadastro")

            with st.form("form_cadastro"):
                nome = st.text_input("Digite seu nome:", placeholder="Fulano de tal")
                senha = st.text_input("Crie uma senha:", type="password", placeholder="Senha")
                confirmar_senha = st.text_input("Confirme sua senha:", type="password", placeholder="Senha")
                cadastrar = st.form_submit_button("Criar conta")

            if cadastrar:
                if not nome.strip() or not senha:
                    st.warning("Preencha todos os campos.")

                elif senha != confirmar_senha:
                    st.error("As senhas não coincidem.")

                else:
                    try:
                        resposta = requests.post(
                            f"{API_URL}/clientes",
                            json={
                                "nome": nome.strip(),
                                "senha": senha
                            },
                            timeout=10
                        )

                        if resposta.status_code == 201:
                            st.success("Cadastro realizado! Agora você pode fazer login.")
                        elif resposta.status_code == 409:
                            st.error("Já existe um cliente com esse nome.")
                        elif resposta.status_code == 422:
                            st.error(resposta.json()["detail"])
                        else:
                            st.error("Não foi possível realizar o cadastro.")

                    except requests.RequestException:
                        st.error("Não foi possível conectar ao Serviço de Dados.")
else:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.title(f"Bem-vindo(a) {st.session_state['nome']}")
        saldo = 59.99
        titulo(f'Saldo disponível: {saldo}', 24)
    col1, col2 = st.columns(2)
    with col1:
        st.subheader('Carteira')
        st.table(dados)
    with col2:
        #st.subheader('Ações disponíveis')
        #st.table(acoes)

        col11, col22, col33, col44 = st.columns([2,1,1,1])


        for i in acoes:
            with col11:
                titulo(f'{i} {acoes[i]}', 33)

            with col22:
                st.button("➖", key=f"menos_{i}", on_click=decrementar, args=(i,))

            with col33:
                titulo(f'{st.session_state[f"contador_{i}"]}', 33)

            with col44:
                st.button("➕", key=f"mais_{i}", on_click=incrementar, args=(i,))
        st.button("Comprar", on_click=comprar_acoes, args=(i,))
        


