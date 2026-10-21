import streamlit as st
import requests
import pandas as pd

API_URL = "http://localhost:8001"

st.set_page_config(page_title = "Sistema de Venda de ações", layout="wide")

# Função para exibir o título com tamanho customizado utilizando css
def titulo(texto, tamanho=14):
    st.markdown(f'<p style="font-size: {tamanho}px; margin: 0;"><b>{texto}</b></p>', unsafe_allow_html=True)

def titulo_centralizado(texto, tamanho):
    st.markdown(f'<h1 style="text-align: center; font-size: {tamanho}px; margin: 0;">{texto}</h1>', unsafe_allow_html=True,)

@st.dialog("Aviso")
def aviso(mensagem):
    st.warning(mensagem)
    if st.button("Fechar"):
        st.rerun()

def incrementar(i):
    st.session_state[f"contador_{i}"] += 1

def decrementar(i):
    if st.session_state[f"contador_{i}"] > 0:
        st.session_state[f"contador_{i}"] -= 1

def calcular_total():
    total_compra = 0
    for acao in acoes:
        total_compra += st.session_state[f"contador_{acao}"] * acoes[acao]
    return round(total_compra, 2)

def comprar_acoes():
    total_compra = calcular_total()   

    if st.session_state["saldo"] < total_compra:
        aviso(f"Saldo insuficiente!")
    else:
        for acao in acoes:
            resposta = requests.post(
                f"{API_URL}/comprar",
                json={"id_carteira": st.session_state["id_cliente"], "ticker": acao, "quantidade": acoes[acao]},
                timeout=10
            )
            if resposta.status == 200:
                st.success(f'Compra de {acoes[acao]} para ação {acao} realizado com sucesso!')
            else:
                aviso("Não foi possível realizar a compra.")
    return

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

if "logado" not in st.session_state:
    st.session_state["logado"] = None

if "nome" not in st.session_state:
    st.session_state["nome"] = None
st.session_state["saldo"] = 1000.00
col1, col2, col3 = st.columns(3)
if st.session_state["logado"] is None:
    with col2:
        opcao = st.radio("Acesso", ["Login", "Cadastro"], horizontal=True)

        if opcao == "Login":
            st.title("Login")

            with st.form("form_login"):
                nome = st.text_input("Digite o seu nome:", placeholder="Fulano de tal")
                senha = st.text_input("Digite sua senha:", type="password", placeholder="Senha")
                enviar = st.form_submit_button("Login")

            if enviar:
                st.session_state["logado"] = True
                st.session_state["nome"] = 'Edson'
                st.rerun()
                try:
                    resposta = requests.post(
                        f"{API_URL}/login",
                        json={"nome": nome.strip(), "senha": senha},
                        timeout=10
                    )

                    if resposta.status == 200:
                        st.session_state["logado"] = True
                        st.session_state["nome"] = resposta.nome
                        st.session_state["id_cliente"] = resposta.id_cliente
                        st.session_state["saldo"] = resposta.saldo
                        st.rerun()

                    elif resposta.status == 401:
                        st.error("Nome ou senha inválidos. Tente novamente!")

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
                    aviso("Preencha todos os campos.")

                elif senha != confirmar_senha:
                    st.error("As senhas não coincidem.")

                else:
                    try:
                        resposta = requests.post(
                            f"{API_URL}/cadastro",
                            json={
                                "nome": nome.strip(),
                                "senha": senha,
                                "saldo":1000
                            },
                            timeout=10
                        )

                        if resposta.status == 201:
                            st.success("Cadastro realizado!")
                            st.session_state["logado"] = True
                            st.session_state["nome"] = resposta.nome
                            st.session_state["id_cliente"] = resposta.id_cliente
                            st.session_state["saldo"] = resposta.saldo
                            st.rerun()

                        elif resposta.status == 409:
                            st.error("Já existe um cliente com esse nome.")
                        else:
                            st.error("Não foi possível realizar o cadastro.")

                    except requests.RequestException:
                        st.error("Não foi possível conectar ao Serviço de Dados.")
else:
    titulo_centralizado(f"Bem-vindo(a) {st.session_state['nome']}", 35)
    option = st.segmented_control('Ferramente para acessar', options=['Carteira', 'Comprar', 'Vender'])
    
    col1, col2, col3 = st.columns([1, 3, 1])

    if option == 'Carteira':
        # Mostrando Carteira
        resposta = requests.get(f"{API_URL}/carteira/{st.session_state['id_cliente']}", timeout=10)

        # Trabalhar com a resposta
        for linha in resposta:
            with col11: 
                titulo_centralizado('Ação', 35)
            with col22:
                titulo_centralizado('Quantidade', 35)
            col11, col22, col33 = st.columns(3)
            with col11:
                titulo_centralizado(f"{linha['ticker']}", 33)
            with col22:
                titulo_centralizado(f"{linha['quantidade']}", 33)

        with col2:
            titulo_centralizado('Carteira', 40)

            st.table(dados)
            
            titulo_centralizado(f'Saldo disponível: R${round(st.session_state["saldo"],2)}', 24)







    elif option == 'Comprar':
        # Mostrando ações para comprar
        with col2:
            titulo_centralizado(f'Compra de ações:', 40)
            #st.table(acoes)

            col11, col22, col33, col44, col55 = st.columns([2,2,1,1,1])
            with col11: 
                titulo('Código Ação', 35)
            with col22:
                titulo('Valor ação', 35)
            #col11, col22, col33, col44, col55 = st.columns([2,1,1,1,1])  
            for i in acoes:
                col11, col22, col33, col44, col55 = st.columns([2,2,1,1,1])
                with col11:
                    titulo_centralizado(f'{i}', 33)
                with col22:
                    titulo_centralizado(f'R${acoes[i]}', 33)
                with col33:
                    titulo('', 24)
                    st.button("➖", key=f"menos_{i}", on_click=decrementar, args=(i,))
                with col44:
                    #titulo('⠀', 3)
                    titulo_centralizado(f'{st.session_state[f"contador_{i}"]}', 33)
                with col55:
                    titulo(' ', 24)
                    st.button("➕", key=f"mais_{i}", on_click=incrementar, args=(i,))
            st.divider()
            col11, col22, col33 = st.columns(3)
            with col22:
                titulo(f'Total:', 33)
            with col33:
                titulo(f'R${calcular_total():.2f}', 33)
                col111, col222, col333 = st.columns([0.5,2,1])
                with col222:
                    st.button("Comprar", on_click=comprar_acoes)

    # Mostrando ações para vender
    elif option == 'Vender':
        with col2:
            titulo_centralizado(f'Venda de ações:', 40)
        


