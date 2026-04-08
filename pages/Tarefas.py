import streamlit as st
import pandas as pd
import plotly.express as px
import os
from datetime import date, datetime

# Configuração da página
st.set_page_config(page_title="Gestor de Tarefas", layout="wide")

# Definição do arquivo de persistência de dados
DATA_FILE = "tarefas_db.csv"

# Configuração de usuário e senha
USUARIO_CORRETO = "gabriel.silva"
SENHA_CORRETA = "89187"

# Inicialização de estado para o formulário
if "input_tarefa" not in st.session_state:
    st.session_state["input_tarefa"] = ""
if "input_data" not in st.session_state:
    st.session_state["input_data"] = date.today()

def carregar_dados():
    """Carrega os dados do arquivo CSV e força a tipagem como 'object' para evitar erros de tipo float64."""
    if os.path.exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE)
        
        # Estrutura de atualização para bases legadas
        if "Criada_em" not in df.columns:
            df["Criada_em"] = ""
        if "Concluida_em" not in df.columns:
            df["Concluida_em"] = ""
            
        # Força o tipo 'object' (que aceita qualquer conteúdo, inclusive strings e nulos)
        df["Criada_em"] = df["Criada_em"].fillna("").astype(object)
        df["Concluida_em"] = df["Concluida_em"].fillna("").astype(object)
            
        return df
    else:
        return pd.DataFrame(columns=["ID", "Tarefa", "Data", "Status", "Criada_em", "Concluida_em"])

def salvar_dados(df):
    """Salva o DataFrame atualizado no arquivo CSV de persistência."""
    df_salvar = df.copy()
    df_salvar['Data'] = df_salvar['Data'].apply(str)
    df_salvar.to_csv(DATA_FILE, index=False)

def verificar_login():
    """Verifica as credenciais inseridas pelo usuário."""
    if st.session_state["usuario"] == USUARIO_CORRETO and st.session_state["senha"] == SENHA_CORRETA:
        st.session_state["autenticado"] = True
    else:
        st.session_state["autenticado"] = False
        st.error("Usuário ou senha incorretos. Acesso negado.")

def limpar_form():
    """Limpa os campos do formulário no estado da sessão."""
    st.session_state["input_tarefa"] = ""
    st.session_state["input_data"] = date.today()

def registrar_tarefa():
    """Registra uma nova tarefa na base de dados com data e hora da criação."""
    global df_tarefas
    nova_tarefa = st.session_state["input_tarefa"]
    data_tarefa = st.session_state["input_data"]
    data_criacao = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    if nova_tarefa:
        novo_id = df_tarefas["ID"].max() + 1 if not df_tarefas.empty else 1
        novo_registro = pd.DataFrame([{
            "ID": novo_id,
            "Tarefa": nova_tarefa,
            "Data": data_tarefa,
            "Status": "Pendente",
            "Criada_em": data_criacao,
            "Concluida_em": ""
        }])
        df_tarefas = pd.concat([df_tarefas, novo_registro], ignore_index=True)
        salvar_dados(df_tarefas)
        st.success("Tarefa registrada com sucesso.")
        limpar_form() 
    else:
        st.error("Por favor, preencha a descrição da tarefa.")

def concluir_tarefas_selecionadas(ids_selecionados):
    """Atualiza o status para 'Concluída' e registra a data e hora da conclusão."""
    global df_tarefas
    data_conclusao = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    
    # Garantia de tipagem object antes da atribuição pelo .loc
    df_tarefas["Concluida_em"] = df_tarefas["Concluida_em"].astype(object)
    
    df_tarefas.loc[df_tarefas["ID"].isin(ids_selecionados), "Status"] = "Concluída"
    df_tarefas.loc[df_tarefas["ID"].isin(ids_selecionados), "Concluida_em"] = data_conclusao
    salvar_dados(df_tarefas)
    st.rerun()

def reverter_tarefas_selecionadas(ids_selecionados):
    """Retorna o status para 'Pendente' e remove a data de conclusão."""
    global df_tarefas
    
    # Garantia de tipagem object antes da atribuição pelo .loc
    df_tarefas["Concluida_em"] = df_tarefas["Concluida_em"].astype(object)
    
    df_tarefas.loc[df_tarefas["ID"].isin(ids_selecionados), "Status"] = "Pendente"
    df_tarefas.loc[df_tarefas["ID"].isin(ids_selecionados), "Concluida_em"] = ""
    salvar_dados(df_tarefas)
    st.rerun()

def excluir_tarefas_selecionadas(ids_selecionados):
    """Remove definitivamente as tarefas selecionadas do banco de dados."""
    global df_tarefas
    df_tarefas = df_tarefas[~df_tarefas["ID"].isin(ids_selecionados)]
    salvar_dados(df_tarefas)
    st.rerun()

# Inicialização do estado da sessão para autenticação
if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False

# Controle de exibição: Tela de Login ou Painel Principal
if not st.session_state["autenticado"]:
    col_esq, col_centro, col_dir = st.columns([1, 2, 1])
    
    with col_centro:
        st.title("Acesso ao Sistema")
        st.write("Por favor, insira suas credenciais para acessar o painel de tarefas.")
        
        st.text_input("Usuário", key="usuario")
        st.text_input("Senha", type="password", key="senha")
        st.button("Entrar", on_click=verificar_login, width='stretch')
else:
    df_tarefas = carregar_dados()

    st.title("Gestor de Tarefas e Agendamentos")
    
    with st.sidebar:
        st.write("Conectado como:", USUARIO_CORRETO)
        if st.button("Sair"):
            st.session_state["autenticado"] = False
            st.rerun()
    
    st.divider()

    st.subheader("Adicionar Nova Tarefa")
    
    col1, col2 = st.columns([3, 1])
    nova_tarefa = col1.text_input("Descrição da Tarefa", key="input_tarefa")
    data_tarefa = col2.date_input("Data do Agendamento (Alvo)", value=st.session_state["input_data"], key="input_data", format="DD/MM/YYYY")
    
    col_btn1, col_btn2 = st.columns([1, 1])
    with col_btn1:
        st.button("Registrar Tarefa", on_click=registrar_tarefa, type="primary", width='stretch')
    with col_btn2:
        st.button("Limpar", on_click=limpar_form, width='stretch')

    st.divider()

    colA, colB = st.columns([2, 1])

    hoje = date.today()

    with colA:
        st.subheader("Agenda de Tarefas")
        if not df_tarefas.empty:
            df_pendentes = df_tarefas[df_tarefas["Status"] == "Pendente"].copy()
            df_pendentes = df_pendentes.sort_values(by="Data")
            
            st.write("Tarefas Pendentes (Marque a caixa para selecionar e use o botão para concluir):")
            
            df_pendentes["Concluir"] = False
            
            # Formatação para exibição
            df_pendentes["Data Agendada"] = pd.to_datetime(df_pendentes["Data"]).dt.strftime('%d/%m/%Y')
            
            # Concluir permanece à esquerda
            edicoes_pendentes = st.data_editor(
                df_pendentes[["Concluir", "Data Agendada", "Tarefa", "Criada_em"]],
                column_config={
                    "Concluir": st.column_config.CheckboxColumn(label="✔️ Selecionar", help="Marque para concluir"),
                },
                hide_index=True,
                width='stretch',
                disabled=["Data Agendada", "Tarefa", "Criada_em"]
            )
            
            if edicoes_pendentes["Concluir"].any():
                st.button("✔️ Marcar Selecionadas como Concluídas", type="primary", width='stretch', key="btn_concluir")
                if st.session_state.get("btn_concluir"):
                    linhas_concluidas = edicoes_pendentes[edicoes_pendentes["Concluir"]].index
                    ids_concluidos = df_pendentes.loc[linhas_concluidas, "ID"]
                    concluir_tarefas_selecionadas(ids_concluidos)

            st.divider()
            
            st.write("Tarefas Concluídas (Marque a caixa para reverter ao status Pendente):")
            df_concluidas = df_tarefas[df_tarefas["Status"] == "Concluída"].copy()
            
            if not df_concluidas.empty:
                df_concluidas = df_concluidas.sort_values(by="Concluida_em", ascending=False)
                df_concluidas["Reverter"] = False
                df_concluidas["Data Agendada"] = pd.to_datetime(df_concluidas["Data"]).dt.strftime('%d/%m/%Y')
                
                # Reverter movido para a direita
                edicoes_reverter = st.data_editor(
                    df_concluidas[["Data Agendada", "Tarefa", "Criada_em", "Concluida_em", "Reverter"]],
                    column_config={
                        "Reverter": st.column_config.CheckboxColumn(label="↩️ Desfazer", help="Marque para retornar para pendente"),
                    },
                    hide_index=True,
                    width='stretch',
                    disabled=["Data Agendada", "Tarefa", "Criada_em", "Concluida_em"]
                )
                
                if edicoes_reverter["Reverter"].any():
                    st.button("🔄 Retornar para Pendente", width='stretch', key="btn_reverter")
                    if st.session_state.get("btn_reverter"):
                        linhas_revertidas = edicoes_reverter[edicoes_reverter["Reverter"]].index
                        ids_revertidos = df_concluidas.loc[linhas_revertidas, "ID"]
                        reverter_tarefas_selecionadas(ids_revertidos)
            else:
                st.info("Nenhuma tarefa concluída no momento.")
                
            st.divider()
            st.write("Resumo Geral de Lançamentos (Marque a vassoura para excluir):")
            
            df_exibicao = df_tarefas.copy()
            df_exibicao["Data Agendada"] = pd.to_datetime(df_exibicao["Data"]).dt.strftime('%d/%m/%Y')
            df_exibicao["Excluir"] = False
            
            # Excluir movido para a direita
            edicoes_excluir = st.data_editor(
                df_exibicao[["Data Agendada", "Tarefa", "Status", "Criada_em", "Concluida_em", "Excluir"]].sort_values(by="Data Agendada", ascending=False), 
                column_config={
                    "Excluir": st.column_config.CheckboxColumn(label="🧹 Excluir", help="Marque para deletar definitivamente"),
                },
                hide_index=True, 
                width='stretch',
                disabled=["Data Agendada", "Tarefa", "Status", "Criada_em", "Concluida_em"]
            )
            
            if edicoes_excluir["Excluir"].any():
                st.button("🧹 Excluir Tarefas Selecionadas", type="primary", width='stretch', key="btn_excluir")
                if st.session_state.get("btn_excluir"):
                    linhas_excluidas = edicoes_excluir[edicoes_excluir["Excluir"]].index
                    df_exibicao_ordenado = df_exibicao.sort_values(by="Data Agendada", ascending=False)
                    ids_excluir = df_exibicao_ordenado.loc[linhas_excluidas, "ID"]
                    excluir_tarefas_selecionadas(ids_excluir)
        else:
            st.info("O banco de dados de tarefas está vazio. Insira uma nova tarefa acima.")
            
    with colB:
        st.subheader("Estatísticas de Produtividade")
        if not df_tarefas.empty:
            def definir_status_grafico(row):
                if row['Status'] == 'Concluída':
                    return 'Concluído'
                elif row['Status'] == 'Pendente' and pd.to_datetime(row['Data']).date() < hoje:
                    return 'Atrasado'
                else:
                    return 'Pendente'
            
            df_grafico = df_tarefas.copy()
            df_grafico['Status_Grafico'] = df_grafico.apply(definir_status_grafico, axis=1)
            
            contagem = df_grafico["Status_Grafico"].value_counts().reset_index()
            contagem.columns = ["Status_Grafico", "Quantidade"]
            
            fig = px.pie(
                contagem, 
                values="Quantidade", 
                names="Status_Grafico", 
                title="Proporção de Tarefas",
                color="Status_Grafico",
                color_discrete_map={
                    "Concluído": "#00CC96",
                    "Atrasado": "#EF553B",
                    "Pendente": "#1F77B4"
                }
            )
            st.plotly_chart(fig, width='stretch')
        else:
            st.write("Dados insuficientes para a geração de métricas.")