import streamlit as st
import pandas as pd

# Configuração da página
st.set_page_config(page_title="Consulta Contábil", layout="wide")

st.title("📊 Consulta de Contas Contábeis")

# Caminho do arquivo definido por você
FILE_PATH = r'C:\Users\gabriel.silva\VS Code\Dashboard\pages\Contabil.xlsx'

@st.cache_data
def load_data():
    try:
        # Carrega a planilha
        df = pd.read_excel(FILE_PATH)
        # Garante que os campos de pesquisa sejam tratados como string para evitar erro no filtro
        df['C1O_CODIGO'] = df['C1O_CODIGO'].astype(str)
        df['C1O_DESCRI'] = df['C1O_DESCRI'].astype(str)
        return df
    except Exception as e:
        st.error(f"Erro ao carregar o arquivo: {e}")
        return pd.DataFrame()

df = load_data()

if not df.empty:
    # Área de filtros
    col1, col2 = st.columns(2)
    
    with col1:
        search_codigo = st.text_input("Pesquisar por Código:")
    
    with col2:
        search_descri = st.text_input("Pesquisar por Descrição:")

    # Lógica de filtragem (Case Insensitive e busca parcial)
    filtered_df = df[
        (df['C1O_CODIGO'].str.contains(search_codigo, case=False, na=False)) &
        (df['C1O_DESCRI'].str.contains(search_descri, case=False, na=False))
    ]

    # Exibição dos resultados
    st.subheader(f"Resultados encontrados: {len(filtered_df)}")
    
    # Exibe apenas as colunas solicitadas, ou o DF inteiro se preferir
    st.dataframe(
    filtered_df[['C1O_CODIGO', 'C1O_DESCRI']].rename(
        columns={'C1O_CODIGO': 'CÓDIGO', 'C1O_DESCRI': 'DESCRIÇÃO'}
    ), 
    width='stretch'
)
else:
    st.warning("Aguardando carregamento dos dados ou arquivo não encontrado.")