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

def incrementar(acao, var, qtd = None):
    if var == 'venda':
        if st.session_state[f"contador_{var}_{acao}"] <  qtd:
            st.session_state[f"contador_{var}_{acao}"] += 1
    else: 
        #if st.session_state[f"contador_venda_{acao}"] > qtd:
        #    aviso(f"Você está tantando vender mais ações do que possui da ação {acao}.")
        #else:
        st.session_state[f"contador_{var}_{acao}"] += 1

def decrementar(acao, var):
    if st.session_state[f"contador_{var}_{acao}"] > 0:
        st.session_state[f"contador_{var}_{acao}"] -= 1

def calcular_total(var):
    total_compra = 0
    for acao in acoes:
        total_compra += st.session_state[f"contador_{var}_{acao}"] * acoes[acao]
    return round(total_compra, 2)

def comprar_acoes():
    total_compra = calcular_total('compra')

    if st.session_state["saldo"] < total_compra:
        aviso(f"Saldo insuficiente para comprar todas!")
    else:
        for acao in acoes:
            if st.session_state[f"contador_compra_{acao}"] == 0:
                continue
            resposta = requests.post(
                f"{API_URL}/comprar",
                json={"id_carteira": st.session_state["id_cliente"], "ticker": acao, "quantidade": st.session_state[f"contador_compra_{acao}"], "valor": acoes[acao] * st.session_state[f"contador_compra_{acao}"]},
                timeout=10
            )
            dados_resposta = resposta.json()
            if dados_resposta['status'] == 200:
                st.session_state["saldo"] = dados_resposta['saldo']
                st.session_state[f"contador_compra_{acao}"] = 0
                st.success(f'Compra de R${acoes[acao]} para ação {acao} realizado com sucesso!')
            else:
                aviso("Não foi possível realizar a compra.")
    return
def vender_acoes():
    for acao in acoes:
        if st.session_state[f"contador_venda_{acao}"] == 0:
            continue
        resposta = requests.post(
            f"{API_URL}/vender",
            json={"id_carteira": st.session_state["id_cliente"], "ticker": acao, "quantidade": st.session_state[f"contador_venda_{acao}"], "valor": acoes[acao] * st.session_state[f"contador_venda_{acao}"]},
            timeout=10
        )
        dados_resposta = resposta.json()
        if dados_resposta['status'] == 200:
            st.session_state["saldo"] = dados_resposta['saldo']
            st.session_state[f"contador_venda_{acao}"] = 0
            st.success(f'Venda de R${acoes[acao]} para ação {acao} realizada com sucesso!')
        else:
            aviso(f"Não foi possível realizar a venda de R${acoes[acao]} para ação {acao}.")
    st.session_state["dados_resposta"] = None
    return



acoes = {
    'ABBA': 5.82,
    'BAAB': 58.2,
    'CAAC': 582.0
}

for acao in acoes:
    for var in ['compra', 'venda']:
        if f"contador_{var}_{acao}" not in st.session_state:
            st.session_state[f"contador_{var}_{acao}"] = 0

if "logado" not in st.session_state:
    st.session_state["logado"] = None

if "nome" not in st.session_state:
    st.session_state["nome"] = None

col1, col2, col3 = st.columns(3)
if st.session_state["logado"] is None:
    with col2:
        col11, col22, col33 = st.columns([1, 2, 1])
        with col22:
            opcao = st.segmented_control('', options=['Login', 'Cadastro'])
        if opcao == "Login":
            st.title("Login")

            with st.form("form_login"):
                nome = st.text_input("Digite o seu nome:", placeholder="Fulano de tal")
                senha = st.text_input("Digite sua senha:", type="password", placeholder="Senha")
                enviar = st.form_submit_button("Login")

            if enviar:
                try:
                    resposta = requests.post(
                        f"{API_URL}/login",
                        json={"nome": nome.strip(), "senha": senha},
                        timeout=10
                    )
                    dados_resposta = resposta.json()
                    if dados_resposta['status'] == 200:
                        st.session_state["logado"] = True
                        st.session_state["nome"] = dados_resposta['nome']
                        st.session_state["id_cliente"] = dados_resposta['id_cliente']
                        st.session_state["saldo"] = dados_resposta['saldo']
                        st.rerun()

                    elif dados_resposta['status'] == 401:
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
                        dados_resposta = resposta.json()
                        if dados_resposta['status'] == 201:
                            st.success("Cadastro realizado!")
                            st.session_state["logado"] = True
                            st.session_state["nome"] = dados_resposta['nome']
                            st.session_state["id_cliente"] = dados_resposta['id_cliente']
                            st.session_state["saldo"] = dados_resposta['saldo']
                            st.rerun()

                        elif dados_resposta['status'] == 409:
                            st.error("Já existe um cliente com esse nome.")
                        else:
                            st.error("Não foi possível realizar o cadastro.")

                    except requests.RequestException:
                        st.error("Não foi possível conectar ao Serviço de Dados.")
else:
    col11, col22, col33 = st.columns(3)
    with col22:
        titulo(f"Bem-vindo(a) {st.session_state['nome']}", 35)
        option = st.segmented_control('', options=['Carteira', 'Comprar', 'Vender'])
    
    col1, col2, col3 = st.columns([1, 3, 1])

    if option == 'Carteira':
        st.session_state["dados_resposta"] = None
        # Mostrando Carteira
        resposta = requests.get(f"{API_URL}/carteiras/{st.session_state['id_cliente']}", timeout=10)
        dados_resposta = resposta.json()

        # Trabalhar com a resposta
        col11, col22, col33, col44 = st.columns(4)
        with col11: 
            titulo_centralizado('Ação', 35)
        with col22:
            titulo_centralizado('Quantidade', 35)
        with col33:
            titulo_centralizado('Valor unitário', 35)
        with col44:
            titulo_centralizado('Valor total', 35)
        for linha in dados_resposta:
            col11, col22, col33, col44 = st.columns(4)
            if linha['quantidade'] == 0:
                continue
            with col11:
                titulo_centralizado(f"{linha['ticker']}", 33)
            with col22:
                titulo_centralizado(f"{linha['quantidade']}", 33)
            with col33:
                titulo_centralizado(f"{acoes[linha['ticker']]}", 33)
            with col44:
                titulo_centralizado(f"{acoes[linha['ticker']]*linha['quantidade']}", 33)

        with col2:
            titulo_centralizado('Carteira', 40)
            titulo_centralizado(f'Saldo disponível: R${round(st.session_state["saldo"], 2)}', 24)

    elif option == 'Comprar':
        st.session_state["dados_resposta"] = None
        # Mostrando ações para comprar
        with col2:
            titulo_centralizado(f'Saldo disponível: R${round(st.session_state["saldo"], 2)}', 24)
            titulo_centralizado(f'Compra de ações:', 40)

            col11, col22, col33, col44, col55 = st.columns([2,2,1,1,1])
            with col11: 
                titulo('Código Ação', 35)
            with col22:
                titulo('Valor ação', 35)
            #col11, col22, col33, col44, col55 = st.columns([2,1,1,1,1])  
            for acao in acoes:
                col11, col22, col33, col44, col55 = st.columns([2,2,1,1,1])
                with col11:
                    titulo_centralizado(f'{acao}', 33)
                with col22:
                    titulo_centralizado(f'R${acoes[acao]}', 33)
                with col33:
                    titulo('', 24)
                    st.button("➖", key=f"menos_{acao}", on_click=decrementar, args=(acao,'compra',))
                with col44:
                    #titulo('⠀', 3)
                    titulo_centralizado(f'{st.session_state[f"contador_compra_{acao}"]}', 33)
                with col55:
                    titulo(' ', 24)
                    st.button("➕", key=f"mais_{acao}", on_click=incrementar, args=(acao,'compra',))
            st.divider()
            col11, col22, col33 = st.columns(3)
            with col22:
                titulo(f'Total:', 33)
            with col33:
                titulo(f"R${calcular_total('compra'):.2f}", 33)
                col111, col222, col333 = st.columns([0.5,2,1])
                with col222:
                    st.button("Comprar", on_click=comprar_acoes)

    # Mostrando ações para vender
    elif option == 'Vender':
        if st.session_state["dados_resposta"] is None:
            resposta = requests.get(
                f"{API_URL}/carteiras/{st.session_state['id_cliente']}",
                timeout=10
            )
            resposta.raise_for_status()
            st.session_state["dados_resposta"] = resposta.json()

        dados_resposta = st.session_state["dados_resposta"]
        with col2:
            titulo_centralizado(f'Saldo disponível: R${round(st.session_state["saldo"],2)}', 24)
            titulo_centralizado(f'Venda de ações:', 40)

        col11, col22, col33, col44, col55, col66 = st.columns([2,2,2,1,1,1])
        with col11: 
            titulo_centralizado('Ação', 35)
        with col22:
            titulo_centralizado('Quantidade', 35)
        with col33:
            titulo_centralizado('Valor unitário', 35)
        for linha in dados_resposta:
            acao = linha['ticker']
            qtd = linha['quantidade']
            col11, col22, col33, col44, col55, col66 = st.columns([2,2,2,1,1,1])
            if qtd == 0:
                continue
            with col11:
                titulo_centralizado(f"{acao}", 33)
            with col22:
                titulo_centralizado(f"{qtd}", 33)
            with col33:
                titulo_centralizado(f"{acoes[acao]}", 33)
            with col44:
                titulo('', 24)
                st.button("➖", key=f"menos_venda_{acao}", on_click=decrementar, args=(acao, 'venda',))
            with col55:
                #titulo('⠀', 3)
                titulo_centralizado(f'{st.session_state[f"contador_venda_{acao}"]}', 33)
            with col66:
                titulo(' ', 24)
                st.button("➕", key=f"mais_venda_{acao}", on_click=incrementar, args=(acao, 'venda', qtd,))
        st.divider()
        col11, col22, col33 = st.columns(3)
        with col22:
            titulo(f'Total:', 33)
        with col33:
            titulo(f"R${calcular_total('venda'):.2f}", 33)
            col111, col222, col333 = st.columns([0.5,2,1])
            with col222:
                st.button("Vender", on_click=vender_acoes)
