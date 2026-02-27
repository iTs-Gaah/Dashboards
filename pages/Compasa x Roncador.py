import streamlit as st
import pandas as pd
import plotly.express as px
import os
from datetime import datetime

# Configuração da página pra usar a tela toda
st.set_page_config(page_title="Controle de Cadastros", layout="wide")

# --- CSS ANABOLIZADO PRA DEIXAR O VISUAL DECENTE ---
st.markdown("""
<style>
/* Estilo dos cards (KPIs) com sombra e borda para dar profundidade */
[data-testid="stMetric"] {
    background-color: var(--secondary-background-color);
    padding: 15px;
    border-radius: 8px;
    box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.2);
    border: 1px solid rgba(128, 128, 128, 0.2);
}

/* Destaque nos títulos (Subheaders) pra não ficarem apagados */
h3 {
    font-weight: 700 !important;
    padding-bottom: 8px;
    border-bottom: 2px solid rgba(128, 128, 128, 0.3);
    margin-bottom: 20px;
}
</style>
""", unsafe_allow_html=True)

st.title(" 🚨 Painel de Inconsistências - COMPASA vs RONCADOR")
st.markdown("---")
st.markdown("")

# Caminho do arquivo
caminho_fixo = r"C:\Users\gabriel.silva\VS Code\Dashboard\pages\Roncador.xlsx"
arquivo_unico = None

# Verifica de onde vai vir o arquivo
if os.path.exists(caminho_fixo):
    timestamp = os.path.getmtime(caminho_fixo)
    data_formatada = datetime.fromtimestamp(timestamp).strftime('%d/%m/%Y %H:%M')
    st.sidebar.success(f"✅ Base atualizada em: {data_formatada}")
    arquivo_unico = caminho_fixo
else:
    st.sidebar.error("❌ Arquivo não encontrado no caminho padrão.")
    arquivo_unico = st.sidebar.file_uploader("Upload da Base Unificada", type=["xlsx"])

# Só roda o resto se tiver um arquivo válido carregado
if arquivo_unico:
    try:
        df = pd.read_excel(arquivo_unico)
        
        # MÁGICA PRA LIMPAR O LIXO DA BASE E MATAR O ERRO DO PYARROW
        colunas_pra_limpar = ['COD_COMPASA', 'COD_COMPAS', 'COD_RONCADOR']
        for col in colunas_pra_limpar:
            if col in df.columns:
                # Transforma em texto, limpa os lixos e tira espaços
                df[col] = df[col].astype(str).str.replace('.0', '', regex=False).str.replace('\t', '', regex=False).str.strip()
                # Mata a palavra "nan" que o Pandas cria nos campos vazios
                df[col] = df[col].replace('nan', None)
                
    except Exception as e:
        st.error(f"Não deu para ler a porra do arquivo: {e}")
        st.stop()

    # --- SETUP DOS CONTAINERS ---
    container_kpi = st.container()
    container_grafico = st.container()
    container_filtros = st.container()
    container_tabela = st.container()
    container_rodape = st.container()

    # --- LÓGICA DE ESTADO DOS FILTROS ---
    if 'filtro_tipo' not in st.session_state:
        st.session_state.filtro_tipo = "TODOS"
    if 'filtro_val' not in st.session_state:
        st.session_state.filtro_val = "TODAS"
    if 'busca_desc' not in st.session_state:
        st.session_state.busca_desc = ""
    if 'busca_cod' not in st.session_state:
        st.session_state.busca_cod = ""

    def limpar_filtros():
        st.session_state.filtro_tipo = "TODOS"
        st.session_state.filtro_val = "TODAS"
        st.session_state.busca_desc = ""
        st.session_state.busca_cod = ""

    def resetar_validacao():
        st.session_state.filtro_val = "TODAS"

    # --- RENDERIZA OS FILTROS ---
    with container_filtros:
        st.subheader("Filtros e Buscas")
        
        col_f1, col_f2, col_f3 = st.columns([2, 2, 1])
        
        with col_f1:
            opcoes_tipo = ["TODOS", "FORNECEDOR", "PRODUTO"]
            tipo_selecionado = st.selectbox("TIPO", options=opcoes_tipo, key='filtro_tipo', on_change=resetar_validacao)

        df_temp = df.copy()
        if tipo_selecionado != "TODOS":
            df_temp = df_temp[df_temp['TIPO'] == tipo_selecionado]
            
        val_disponiveis = df_temp['VALIDACAO'].dropna().unique().tolist() if 'VALIDACAO' in df_temp.columns else []

        with col_f2:
            if val_disponiveis:
                opcoes_val = ["TODAS"] + val_disponiveis
                val_selecionada = st.selectbox("Validação", options=opcoes_val, key='filtro_val')
            else:
                val_selecionada = "TODAS"
                st.warning("Coluna 'VALIDACAO' não encontrada.")

        with col_f3:
            st.write("") 
            st.write("")
            st.button("🧹 Limpar Filtros", on_click=limpar_filtros)

        col_b1, col_b2 = st.columns(2)
        with col_b1:
            busca_desc = st.text_input("Buscar por Descrição", key='busca_desc')
        with col_b2:
            busca_cod = st.text_input("Buscar por Código", key='busca_cod')

    # Aplicando filtros
    df_filtrado = df.copy()
    
    if tipo_selecionado != "TODOS":
        df_filtrado = df_filtrado[df_filtrado['TIPO'] == tipo_selecionado]
        
    if val_selecionada != "TODAS":
        df_filtrado = df_filtrado[df_filtrado['VALIDACAO'] == val_selecionada]

    if busca_desc:
        desc_comp = df_filtrado['DESC_COMPASA'].astype(str).str.contains(busca_desc, case=False, na=False) if 'DESC_COMPASA' in df_filtrado.columns else False
        desc_ronc = df_filtrado['DESC_RONCADOR'].astype(str).str.contains(busca_desc, case=False, na=False) if 'DESC_RONCADOR' in df_filtrado.columns else False
        df_filtrado = df_filtrado[desc_comp | desc_ronc]

    if busca_cod:
        col_compasa = 'COD_COMPASA' if 'COD_COMPASA' in df_filtrado.columns else ('COD_COMPAS' if 'COD_COMPAS' in df_filtrado.columns else None)
        cod_comp = df_filtrado[col_compasa].astype(str).str.contains(busca_cod, case=False, na=False) if col_compasa else False
        cod_ronc = df_filtrado['COD_RONCADOR'].astype(str).str.contains(busca_cod, case=False, na=False) if 'COD_RONCADOR' in df_filtrado.columns else False
        df_filtrado = df_filtrado[cod_comp | cod_ronc]

    # --- KPIs ---
    with container_kpi:
        col1, col2, col3, col4 = st.columns(4)
        
        total_itens = len(df_filtrado)
        
        if "VALIDACAO" in df.columns:
            df_val_lower = df_filtrado['VALIDACAO'].astype(str).str.lower()
            
            cadastros_iguais = len(df_val_lower[df_val_lower == 'cadastros iguais'])
            nao_cad_prod = len(df_val_lower[df_val_lower == 'produto não cadastrado'])
            nao_cad_forn = len(df_val_lower[df_val_lower == 'fornecedor não cadastrado'])
            nao_cadastrado = nao_cad_prod + nao_cad_forn
            divergentes = len(df_val_lower[df_val_lower == 'valores são diferentes entre as bases'])
        else:
            cadastros_iguais = nao_cadastrado = divergentes = 0

        col1.metric("Total de Cadastros", total_itens)
        col2.metric("Cadastros Iguais", cadastros_iguais)
        col3.metric("Não Cadastrados (Prod/Forn)", nao_cadastrado)
        col4.metric("Divergentes (Prod/Forn)", divergentes)

    # --- GRÁFICO ---
    with container_grafico:
        if "VALIDACAO" in df_filtrado.columns and not df_filtrado.empty:
            st.subheader("Distribuição dos Status")
            
            df_grafico_limpo = df_filtrado[~df_filtrado['VALIDACAO'].astype(str).str.contains('1900', na=False)]
            
            df_grafico = df_grafico_limpo['VALIDACAO'].value_counts().reset_index()
            df_grafico.columns = ['Status', 'Quantidade']
            
            fig = px.bar(
                df_grafico,
                x='Status',
                y='Quantidade',
                text='Quantidade',
                color='Status',
                color_discrete_map={
                    'Cadastros iguais': '#28a745',          # Verde
                    'Produto não cadastrado': '#003399',    # Azul Escuro
                    'Fornecedor não cadastrado': '#87CEFA'  # Azul Claro
                }
            )
            st.plotly_chart(fig, width='stretch')

        elif df_filtrado.empty:
            st.warning("Nenhum dado com esses filtros.")

    # --- TABELA DETALHADA ---
    with container_tabela:
        st.subheader("📊 Dados detalhados")
        
        colunas_exibir = df_filtrado.columns.tolist()
        
        colunas_lixo = ["RECNO_COMPASA", "RECNO_RONCADOR", "STAMP_COMPASA", "STAMP_RONCADOR"]
        colunas_exibir = [col for col in colunas_exibir if col not in colunas_lixo and col != "S_T_A_M_P_" and not col.startswith("Unnamed")]
        
        if tipo_selecionado == "PRODUTO":
            colunas_exibir = [col for col in colunas_exibir if col not in ["LOJA_COMPASA", "LOJA_RONCADOR"]]

        st.dataframe(df_filtrado[colunas_exibir], hide_index=True, width='stretch')

    # --- AUDITORIA DE RECNO E PRÓXIMO CÓDIGO ---
    with container_rodape:
        st.markdown("---")
        st.subheader("🕵️ Últimos Registros")

        tipo_ultimos = st.radio("Selecione o tipo:", ["PRODUTO", "FORNECEDOR"], horizontal=True)

        df_base_ultimos = df[df['TIPO'] == tipo_ultimos].copy() if 'TIPO' in df.columns else df.copy()

        col_comp, col_ronc = st.columns(2)

        # COMPASA por RECNO
        with col_comp:
            st.markdown(f"**Últimos 10 cadastros - COMPASA**")
            if "RECNO_COMPASA" in df_base_ultimos.columns:
                df_base_ultimos['RECNO_NUM_COMPASA'] = pd.to_numeric(df_base_ultimos['RECNO_COMPASA'], errors='coerce')
                
                ultimos_comp = df_base_ultimos.sort_values(by="RECNO_NUM_COMPASA", ascending=False).head(10)
                ultimos_comp = ultimos_comp.sort_values(by="RECNO_NUM_COMPASA", ascending=True)
                
                cols_comp = [c for c in ['COD_COMPASA', 'DESC_COMPASA', 'RECNO_COMPASA'] if c in ultimos_comp.columns]
                
                if "STAMP_COMPASA" in ultimos_comp.columns: 
                    cols_comp.append("STAMP_COMPASA")
                elif "S_T_A_M_P_" in ultimos_comp.columns: 
                    cols_comp.append("S_T_A_M_P_")
                
                st.dataframe(ultimos_comp[cols_comp], hide_index=True, width='stretch')
            else:
                st.warning("Sem coluna RECNO_COMPASA pra ordenar.")

        # RONCADOR por RECNO
        with col_ronc:
            st.markdown(f"**Últimos 10 cadastros - RONCADOR**")
            if "RECNO_RONCADOR" in df_base_ultimos.columns:
                df_base_ultimos['RECNO_NUM_RONCADOR'] = pd.to_numeric(df_base_ultimos['RECNO_RONCADOR'], errors='coerce')
                
                ultimos_ronc = df_base_ultimos.sort_values(by="RECNO_NUM_RONCADOR", ascending=False).head(10)
                ultimos_ronc = ultimos_ronc.sort_values(by="RECNO_NUM_RONCADOR", ascending=True)
                
                cols_ronc = [c for c in ['COD_RONCADOR', 'DESC_RONCADOR', 'RECNO_RONCADOR'] if c in ultimos_ronc.columns]
                
                if "STAMP_RONCADOR" in ultimos_ronc.columns: 
                    cols_ronc.append("STAMP_RONCADOR")
                
                st.dataframe(ultimos_ronc[cols_ronc], hide_index=True, width='stretch')
            else:
                st.warning("Sem coluna RECNO_RONCADOR pra ordenar.")

        # FUNÇÃO PARA CALCULAR PRÓXIMO CÓDIGO (BASEADA NO MAIOR RECNO)
        def calcular_proximo_codigo_por_recno(df_calc, col_cod, col_recno, prefixo, tamanho):
            if col_cod not in df_calc.columns or col_recno not in df_calc.columns: 
                return "Base Zoada"
            
            df_temp = df_calc[[col_cod, col_recno]].dropna().copy()
            
            df_temp['COD_LIMPO'] = df_temp[col_cod].astype(str).str.strip()
            df_temp['COD_LIMPO'] = df_temp['COD_LIMPO'].apply(lambda x: x[:-2] if x.endswith('.0') else x)
            df_temp['COD_LIMPO'] = df_temp['COD_LIMPO'].str.zfill(tamanho)
            
            df_temp = df_temp[df_temp['COD_LIMPO'].str.startswith(prefixo)]
            
            if df_temp.empty:
                return prefixo.ljust(tamanho, '0')[:-1] + '1'
            
            df_temp['RECNO_NUM'] = pd.to_numeric(df_temp[col_recno], errors='coerce')
            ultimo_registro = df_temp.sort_values(by='RECNO_NUM', ascending=False).iloc[0]
            
            max_code = int(ultimo_registro['COD_LIMPO'])
            return str(max_code + 1).zfill(tamanho)

        prefixo_codigo = "00000211" if tipo_ultimos == "PRODUTO" else "008"
        tamanho_padrao = 10 if tipo_ultimos == "PRODUTO" else 6

        col_cod_compasa = 'COD_COMPASA' if 'COD_COMPASA' in df.columns else ('COD_COMPAS' if 'COD_COMPAS' in df.columns else None)
        
        prox_comp = calcular_proximo_codigo_por_recno(df_base_ultimos, col_cod_compasa, 'RECNO_COMPASA', prefixo_codigo, tamanho_padrao) if col_cod_compasa else "N/A"

        st.success(f"✅ **Próximo código disponível para cadastro de {tipo_ultimos} (Baseado na COMPASA):**\n\n**{prox_comp}**")

else:
    st.info("Faz o upload do arquivo ali na barra lateral pra começar.")