import streamlit as st
import pandas as pd
import os
from datetime import datetime

st.set_page_config(layout="wide")
st.title("📋 Painel de Aprovadores")

caminho_fixo = r"C:\Users\gabriel.silva\VS Code\Grupos Aprovadores\Aprovadores.xlsx"

if os.path.exists(caminho_fixo):
    timestamp = os.path.getmtime(caminho_fixo)
    data_formatada = datetime.fromtimestamp(timestamp).strftime('%d/%m/%Y %H:%M')
    st.sidebar.success(f"✅ Base atualizada em: {data_formatada}")
    arquivo_unico = caminho_fixo
else:
    st.sidebar.error("❌ Arquivo não encontrado. Cadê a planilha?")
    arquivo_unico = st.sidebar.file_uploader("Upload da Base Unificada", type=["xlsx"])

@st.cache_data
def carregar_dados(arquivo):
    if arquivo is not None:
        df_regras = pd.read_excel(arquivo, sheet_name='Plan1', dtype=str)
        df_base_cc = pd.read_excel(arquivo, sheet_name='Plan2', dtype=str)
        df_empresas = pd.read_excel(arquivo, sheet_name='Base', dtype=str)

        col_filial = 'Z01_FILIAL' if 'Z01_FILIAL' in df_regras.columns else 'FILIAL'
        col_cc_regras = 'Z01_CC' if 'Z01_CC' in df_regras.columns else 'C CUSTO'
        col_desc_regras = 'Z01_DECCC' if 'Z01_DECCC' in df_regras.columns else 'C CUSTO DESC'
        
        col_cc_mestre = 'CTT_CUSTO' if 'CTT_CUSTO' in df_base_cc.columns else 'Cod_cc'
        col_desc_mestre = 'CTT_DESC01' if 'CTT_DESC01' in df_base_cc.columns else 'Descrição'
        
        col_cod_emp = 'COD FILIAL' if 'COD FILIAL' in df_empresas.columns else 'Cod_gp'
        col_nome_emp = 'DESC' if 'DESC' in df_empresas.columns else 'Descrição'

        df_regras[col_cc_regras] = df_regras[col_cc_regras].str.strip()
        df_base_cc[col_cc_mestre] = df_base_cc[col_cc_mestre].str.strip()
        df_regras[col_filial] = df_regras[col_filial].str.strip()
        df_empresas[col_cod_emp] = df_empresas[col_cod_emp].str.strip()
        df_base_cc['FILIAL_FORMAT'] = df_base_cc['CTT_FILIAL'].str.strip().str.zfill(2) + "0101"
        
        return df_regras, df_base_cc, df_empresas, col_filial, col_cc_regras, col_desc_regras, col_cc_mestre, col_desc_mestre, col_cod_emp, col_nome_emp
    return None, None, None, None, None, None, None, None, None, None

df_regras, df_base_cc, df_empresas, col_filial, col_cc_regras, col_desc_regras, col_cc_mestre, col_desc_mestre, col_cod_emp, col_nome_emp = carregar_dados(arquivo_unico)

if df_regras is None:
    st.warning("Aguardando o arquivo para carregar os dados...")
    st.stop()

# --- INICIALIZAÇÃO DE SESSION STATE ---
if "filtro_cc" not in st.session_state: st.session_state.filtro_cc = ""
if "filtro_grupo" not in st.session_state: st.session_state.filtro_grupo = ""
if "filtro_aprovador" not in st.session_state: st.session_state.filtro_aprovador = ""
if "filtro_status_cc" not in st.session_state: st.session_state.filtro_status_cc = "Todos"
if "filtro_empresa" not in st.session_state: st.session_state.filtro_empresa = "Todas" 
if "expandir_todos" not in st.session_state: st.session_state.expandir_todos = False

def limpar_tudo():
    st.session_state.filtro_cc = ""
    st.session_state.filtro_grupo = ""
    st.session_state.filtro_aprovador = ""
    st.session_state.filtro_status_cc = "Todos"
    st.session_state.filtro_empresa = "Todas" 

def set_expandir(valor):
    st.session_state.expandir_todos = valor

# --- VALIDAÇÃO DE CCs FALTANTES (AUDITORIA GLOBAL) ---
lista_regras_cc = df_regras[col_cc_regras].unique()
df_faltantes = df_base_cc[~df_base_cc[col_cc_mestre].isin(lista_regras_cc)]

st.write("---")

col_bloq_auditoria = 'CTT_BLOQ' if 'CTT_BLOQ' in df_base_cc.columns else 'CTT_BLOQ'
df_base_cc[col_bloq_auditoria] = df_base_cc[col_bloq_auditoria].astype(str).str.strip().str.upper()

# Filtra APENAS quem tá ATIVO
cc_ativos_plan2 = df_base_cc[df_base_cc[col_bloq_auditoria].isin(['2', 'ATIVO'])].copy()
cc_sem_aprovador = cc_ativos_plan2[~cc_ativos_plan2[col_cc_mestre].isin(df_regras[col_cc_regras])]

if not cc_sem_aprovador.empty:
    st.error("🚨 **Atenção: Existem Centros de Custo sem grupo de aprovação cadastrado!**")
    
    with st.expander(f"Ver lista de pendências ({len(cc_sem_aprovador)} encontradas):"):
        for index, row in cc_sem_aprovador.iterrows():
            filial_erro = str(row['FILIAL_FORMAT']).strip() if 'FILIAL_FORMAT' in row else str(row['CTT_FILIAL']).strip()
            cc_erro = str(row[col_cc_mestre]).strip()
            desc_erro = str(row[col_desc_mestre]).strip() if col_desc_mestre in row else 'Sem descrição'
            status_cc = row[col_bloq_auditoria]
            
            status_texto = "ATIVO" if status_cc in ['2', 'ATIVO'] else status_cc
            
            st.write(f"❌ {filial_erro} - {cc_erro} - {desc_erro} - **{status_texto}**")
else:
    st.success("✅ Tudo certo, caralho! Todos os Centros de Custo ativos têm Grupo de Aprovadores.")

st.write("---")

# --- ÁREA DE FILTROS NO TOPO ---
st.write("### 🔍 Filtros de Pesquisa")

col_topo1, col_topo2 = st.columns(2)

with col_topo1:
    if df_empresas is not None and not df_empresas.empty:
        df_empresas[col_cod_emp] = df_empresas[col_cod_emp].astype(str).str.strip().str.zfill(6)
        df_empresas['NOME_LISTA'] = df_empresas[col_cod_emp] + " - " + df_empresas[col_nome_emp].astype(str)
        df_empresas = df_empresas.sort_values(by=col_cod_emp)
        lista_selecao = ["Todas"] + df_empresas['NOME_LISTA'].unique().tolist()
        empresa_focada = st.selectbox("🏢 Selecione a Empresa:", options=lista_selecao, key="filtro_empresa")
    else:
        empresa_focada = "Todas"

with col_topo2:
    busca_status_cc = st.selectbox("🚩 Status do Centro de Custo", ["Todos", "Ativo", "Bloqueado"], key="filtro_status_cc")

col1, col2, col3 = st.columns(3)
with col1: busca_cc = st.text_input("Centro de Custo:", key="filtro_cc")
with col2: busca_grupo = st.text_input("Grupo de Aprovação:", key="filtro_grupo")
with col3: busca_aprovador = st.text_input("Aprovador:", key="filtro_aprovador")

btn_col1, btn_col2, btn_col3, _ = st.columns([1, 1, 1, 3])
with btn_col1: st.button("🧹 Limpar Filtros", on_click=limpar_tudo, width="stretch")
with btn_col2: st.button("➕ Expandir Todos", on_click=set_expandir, args=(True,), width="stretch")
with btn_col3: st.button("➖ Recolher Todos", on_click=set_expandir, args=(False,), width="stretch")

# --- APLICAÇÃO DOS FILTROS ---
df_filtrado = df_regras.copy()

if empresa_focada != "Todas":
    cod_filial_selecionada = empresa_focada.split(" - ")[0].strip()
    df_filtrado = df_filtrado[df_filtrado[col_filial].str.strip() == cod_filial_selecionada.lstrip('0')]
    if df_filtrado.empty:
        df_filtrado = df_regras[df_regras[col_filial].str.strip() == cod_filial_selecionada]

df_filtrado['CHAVE_UNICA'] = df_filtrado[col_filial].astype(str) + " | " + df_filtrado[col_cc_regras].astype(str)

if busca_cc:
    df_filtrado = df_filtrado[
        df_filtrado[col_cc_regras].str.contains(busca_cc, case=False, na=False) |
        df_filtrado[col_desc_regras].str.contains(busca_cc, case=False, na=False)
    ]

if busca_grupo:
    col_grupo_busca = 'AL_DESC' if 'AL_DESC' in df_filtrado.columns else 'NOME GRUPO'
    df_filtrado = df_filtrado[df_filtrado[col_grupo_busca].str.contains(busca_grupo, case=False, na=False)]

if busca_aprovador:
    col_aprov_busca = 'AK_NOME' if 'AK_NOME' in df_filtrado.columns else 'NOME APROVADOR'
    df_filtrado = df_filtrado[df_filtrado[col_aprov_busca].str.contains(busca_aprovador, case=False, na=False)]

if busca_status_cc != "Todos":
    col_status_filtro = 'CTT_BLOQ' if 'CTT_BLOQ' in df_filtrado.columns else 'Status do CC'
    df_filtrado = df_filtrado[df_filtrado[col_status_filtro].astype(str).str.strip().str.upper() == busca_status_cc.upper()]

chaves_filtradas = df_filtrado['CHAVE_UNICA'].unique()

st.write("---")
st.write(f"### 🏢 Hierarquia de Aprovação Cadastrada ({len(chaves_filtradas)} resultados)")

if len(chaves_filtradas) == 0:
    st.warning("Nenhum resultado encontrado com esses filtros.")
else:
    df_regras['CHAVE_UNICA'] = df_regras[col_filial] + " | " + df_regras[col_cc_regras]
    
    for chave in chaves_filtradas:
        dados_cc = df_regras[df_regras['CHAVE_UNICA'] == chave]
        filial_str = dados_cc[col_filial].iloc[0]
        cc_str = dados_cc[col_cc_regras].iloc[0]
        desc_str = dados_cc[col_desc_regras].iloc[0]
        
        info_base = df_base_cc[df_base_cc[col_cc_mestre] == cc_str]
        
        if not info_base.empty:
            filial_mestre = info_base['FILIAL_FORMAT'].iloc[0]
            cc_desc_base = info_base[col_desc_mestre].iloc[0]
        else:
            filial_mestre = "S/ FILIAL"
            cc_desc_base = desc_str
            
        col_status_cc = 'CTT_BLOQ' if 'CTT_BLOQ' in dados_cc.columns else 'Status do CC'
        status_cc = str(dados_cc[col_status_cc].iloc[0]).strip().upper()
        
        icone_grupo = "🟢" if status_cc in ["2", "ATIVO"] else "🔴"
        alerta_cc = " ⚠️ [CC BLOQUEADO]" if status_cc in ["1", "BLOQUEADO", "INATIVO"] else ""
    
        titulo_expander = f"{icone_grupo} {filial_mestre} - {cc_str} - {cc_desc_base}{alerta_cc}"

        with st.expander(titulo_expander, expanded=st.session_state.expandir_todos):
            df_exibir = dados_cc.drop(columns=['CHAVE_UNICA', col_filial, col_cc_regras, col_desc_regras], errors='ignore')
            
            col_nivel = 'AL_NIVEL' if 'AL_NIVEL' in df_exibir.columns else 'NIVEL APROV'
            if col_nivel in df_exibir.columns:
                df_exibir = df_exibir.sort_values(by=col_nivel, ascending=True)
            
            nomes_amigaveis = {
                'CTT_BLOQ': 'Status do CC',
                'AL_DESC': 'Grupo de Aprovação',
                'AL_NIVEL': 'Nível',
                'AK_NOME': 'Nome do Aprovador',
                'DHL_DESCRI': 'Perfil',
                'AL_TPLIBER': 'Tipo Liberação',
                'AL_MSBLQL': 'Aprovador Ativo?'
            }
            
            df_exibir = df_exibir.rename(columns=nomes_amigaveis)
            
            def pintar_bloqueado(valor):
                if valor == 'BLOQUEADO':
                    return 'background-color: rgba(204, 153, 0, 0.4); color: white;'
                return ''
            
            if 'Status do CC' in df_exibir.columns:
                df_estilizado = df_exibir.style.map(pintar_bloqueado, subset=['Status do CC'])
            else:
                df_estilizado = df_exibir
            
            st.dataframe(df_estilizado, hide_index=True, width="stretch")