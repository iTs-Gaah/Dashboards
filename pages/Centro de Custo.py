import streamlit as st
import pandas as pd
import io
import os
from datetime import datetime

# Caminho da sua planilha
caminho_fixo = r"C:\Users\gabriel.silva\VS Code\Dashboard\pages\Aprovadores.xlsx"

st.set_page_config(layout="wide")

try:
    tempo_mod = os.path.getmtime(caminho_fixo)
    data_atualizacao = datetime.fromtimestamp(tempo_mod).strftime('%d/%m/%Y %H:%M')
except Exception:
    data_atualizacao = "Erro ao buscar data"


# Cria a caixa verde escrota exatamente igual ao print usando HTML/CSS
if os.path.exists(caminho_fixo):
    timestamp = os.path.getmtime(caminho_fixo)
    data_formatada = datetime.fromtimestamp(timestamp).strftime('%d/%m/%Y %H:%M')
    st.sidebar.success(f"✅ Base atualizada em: {data_formatada}")
    arquivo_unico = caminho_fixo
else:
    st.sidebar.error("❌ Arquivo não encontrado no caminho padrão.")
    arquivo_unico = st.sidebar.file_uploader("Upload da Base Unificada", type=["xlsx"])


@st.cache_data
def carregar_dados():
    plan2 = pd.read_excel(caminho_fixo, sheet_name='Plan2', dtype=str)
    base = pd.read_excel(caminho_fixo, sheet_name='Base', dtype=str)
    
    df_empresas = base[['COD EMPRESA Z01', 'DESC EMPRESA']].dropna(subset=['COD EMPRESA Z01'])
    df_empresas['COD EMPRESA Z01'] = df_empresas['COD EMPRESA Z01'].str.replace(r'\.0$', '', regex=True).str.zfill(2)
    
    df_filiais = base[['COD EMPRESA', 'COD FILIAL', 'DESC']].dropna(subset=['COD FILIAL'])
    df_filiais['COD EMPRESA'] = df_filiais['COD EMPRESA'].str.replace(r'\.0$', '', regex=True).str.zfill(2)
    df_filiais['COD FILIAL'] = df_filiais['COD FILIAL'].str.replace(r'\.0$', '', regex=True).str.zfill(6)
    
    plan2['CTT_EMPRESA'] = plan2['CTT_EMPRESA'].str.replace(r'\.0$', '', regex=True).str.zfill(2)
    plan2['CTT_FILIAL'] = plan2['CTT_FILIAL'].str.replace(r'\.0$', '', regex=True).str.zfill(6)
    
    base_unificada = df_filiais.merge(df_empresas, left_on='COD EMPRESA', right_on='COD EMPRESA Z01', how='left')
    return plan2, base_unificada

plan2, base_unificada = carregar_dados()

df_completo = plan2.merge(base_unificada, left_on=['CTT_EMPRESA', 'CTT_FILIAL'], right_on=['COD EMPRESA', 'COD FILIAL'], how='left')

df_completo['EMPRESA_COMPLETA'] = df_completo['COD EMPRESA Z01'].fillna('') + " - " + df_completo['DESC EMPRESA'].fillna('')
df_completo['FILIAL_COMPLETA'] = df_completo['COD FILIAL'].fillna('') + " - " + df_completo['DESC'].fillna('')

st.title("Filtro de Centro de Custo")

if 'filtro_empresa' not in st.session_state: st.session_state.filtro_empresa = 'TODAS'
if 'filtro_filial' not in st.session_state: st.session_state.filtro_filial = 'TODAS'
if 'filtro_busca' not in st.session_state: st.session_state.filtro_busca = ''
if 'filtro_bloq' not in st.session_state: st.session_state.filtro_bloq = 'TODOS'

def limpar_filtros():
    st.session_state.filtro_empresa = 'TODAS'
    st.session_state.filtro_filial = 'TODAS'
    st.session_state.filtro_busca = ''
    st.session_state.filtro_bloq = 'TODOS'

lista_empresas = sorted([e for e in df_completo['EMPRESA_COMPLETA'].dropna().unique().tolist() if e != " - "])
lista_empresas.insert(0, 'TODAS')

if st.session_state.filtro_empresa != 'TODAS':
    df_filiais_disponiveis = df_completo[df_completo['EMPRESA_COMPLETA'] == st.session_state.filtro_empresa]
else:
    df_filiais_disponiveis = df_completo

lista_filiais = sorted([f for f in df_filiais_disponiveis['FILIAL_COMPLETA'].dropna().unique().tolist() if f != " - "])
lista_filiais.insert(0, 'TODAS')

opcoes_bloq = ['TODOS', 'ATIVO', 'INATIVO']

col1, col2, col3 = st.columns(3)
with col1:
    st.selectbox("Selecione a Empresa:", lista_empresas, key='filtro_empresa')
with col2:
    st.selectbox("Selecione a Filial:", lista_filiais, key='filtro_filial')
with col3:
    st.selectbox("Status Bloqueio:", opcoes_bloq, key='filtro_bloq')

col4, col5 = st.columns([2, 1]) 
with col4:
    st.text_input("Pesquisar Código C. Custo ou Descrição:", key='filtro_busca')
with col5:
    st.write("") 
    st.write("")
    st.button("🧹 Limpar Filtros", on_click=limpar_filtros)

df_filtrado = df_completo.copy()

if st.session_state.filtro_empresa != 'TODAS':
    df_filtrado = df_filtrado[df_filtrado['EMPRESA_COMPLETA'] == st.session_state.filtro_empresa]

if st.session_state.filtro_filial != 'TODAS':
    df_filtrado = df_filtrado[df_filtrado['FILIAL_COMPLETA'] == st.session_state.filtro_filial]

if st.session_state.filtro_bloq != 'TODOS':
    df_filtrado = df_filtrado[df_filtrado['CTT_BLOQ'] == st.session_state.filtro_bloq]

if st.session_state.filtro_busca:
    busca = str(st.session_state.filtro_busca)
    mask = (
        df_filtrado['CTT_CUSTO'].astype(str).str.contains(busca, case=False, na=False) |
        df_filtrado['CTT_DESC01'].astype(str).str.contains(busca, case=False, na=False)
    )
    df_filtrado = df_filtrado[mask]

st.markdown(f"### 📊 Total de Resultados: **{len(df_filtrado)}**")

if df_filtrado.empty:
    st.warning("Não localizado.")
else:
    df_filtrado = df_filtrado.loc[:, ~df_filtrado.columns.str.contains('^Unnamed')]
    
    # A MÁGICA PRA EMPRESA APARECER COMPLETA ACONTECE AQUI
    # Mandei a CTT_EMPRESA pro inferno e mantive a EMPRESA_COMPLETA
    colunas_pra_remover = ['COD EMPRESA', 'COD FILIAL', 'DESC', 'CNPJ', 'COD EMPRESA Z01', 'DESC EMPRESA', 'CTT_EMPRESA', 'FILIAL_COMPLETA']
    df_exibicao = df_filtrado.drop(columns=[col for col in colunas_pra_remover if col in df_filtrado.columns], errors='ignore')

    df_exibicao = df_exibicao.fillna('')

    # Renomeio a EMPRESA_COMPLETA pra EMPRESA pra não ficar cagado no cabeçalho
    df_exibicao.rename(columns={
        'EMPRESA_COMPLETA': 'EMPRESA',
        'CTT_FILIAL': 'FILIAL',
        'CTT_CUSTO': 'C CUSTO',
        'CTT_DESC01': 'DESCRICAO',
        'CTT_BLOQ': 'BLOQUEADO?',
        'CTT_XFINAN': 'FINANCEIRO?',
        'CTT_REGION': 'REGIONAL'
    }, inplace=True)

    # Força a ordem das colunas pra EMPRESA ficar no começo
    colunas_ordenadas = ['EMPRESA', 'FILIAL', 'C CUSTO', 'DESCRICAO', 'BLOQUEADO?', 'FINANCEIRO?', 'REGIONAL']
    df_exibicao = df_exibicao[[col for col in colunas_ordenadas if col in df_exibicao.columns]]

    def pintar_status(valor):
        if valor == 'INATIVO':
            return 'color: red'
        elif valor == 'ATIVO':
            return 'color: green'
        return ''

    # Forçando fundo cinza, letra preta, negrito e uma borda preta embaixo do cabeçalho
    estilo_cabecalho = [
        {'selector': 'th', 'props': [
            ('background-color', '#dcdcdc !important'), 
            ('color', '#000000 !important'), 
            ('font-weight', 'bold !important'),
            ('border-bottom', '2px solid #000000 !important')
        ]}
    ]

    df_estilizado = df_exibicao.style.map(pintar_status, subset=['BLOQUEADO?']).set_table_styles(estilo_cabecalho)

    st.dataframe(df_estilizado, hide_index=True, width='stretch')

    buffer = io.BytesIO()
    df_exibicao.to_excel(buffer, index=False, engine='openpyxl')
    
    st.write("") 
    st.download_button(
        label="📥 Baixar Tabela em Excel",
        data=buffer.getvalue(),
        file_name="filtro_centro_custo.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )