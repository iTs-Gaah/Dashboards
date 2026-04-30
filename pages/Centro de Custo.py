import streamlit as st
import pandas as pd
import io
import os
from datetime import datetime

# Caminho da sua planilha
caminho_fixo = r"C:\Users\gabriel.silva\VS Code\Dashboard\pages\Aprovadores.xlsx"

st.set_page_config(page_title="Painel de Gestão", layout="wide", initial_sidebar_state="collapsed")

# --- CSS CUSTOMIZADO (Melhorias no Modo Claro e Rolagem) ---
css = """
<style>
    /* Importando fonte Inter */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    .stApp {
        font-family: 'Inter', sans-serif;
    }
    
    header[data-testid="stHeader"] {
        display: none;
    }
    

    /* Cards */
    .metric-card {
        background-color: var(--secondary-background-color);
        padding: 15px 20px;
        border-radius: 10px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        border: 1px solid rgba(128, 128, 128, 0.2);
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.03);
        height: 90px;
        transition: transform 0.2s;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
    }
    
    .metric-info {
        display: flex;
        flex-direction: column;
        justify-content: center;
    }

    .metric-title {
        color: var(--text-color);
        opacity: 0.7;
        font-size: 11px;
        font-weight: 600;
        text-transform: uppercase;
        margin-bottom: 4px;
        white-space: nowrap;
    }
    
    .metric-value {
        color: var(--text-color);
        font-size: 26px;
        font-weight: 700;
        line-height: 1.2;
    }

    .metric-chart {
        width: 45px;
        height: 45px;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    
    /* Donut chart shapes */
    .donut-green {
        width: 40px; height: 40px;
        border-radius: 50%;
        background: conic-gradient(#10b981 75%, rgba(128,128,128,0.2) 0);
        display: flex; justify-content: center; align-items: center;
    }
    .donut-green::before { content: ""; width: 24px; height: 24px; background: var(--secondary-background-color); border-radius: 50%; }

    .donut-red {
        width: 40px; height: 40px;
        border-radius: 50%;
        background: conic-gradient(#ef4444 25%, rgba(128,128,128,0.2) 0);
        display: flex; justify-content: center; align-items: center;
    }
    .donut-red::before { content: ""; width: 24px; height: 24px; background: var(--secondary-background-color); border-radius: 50%; }

    /* Estilização da Tabela HTML com Rolagem */
    .table-container {
        width: 100%;
        max-height: 500px; /* Altura máxima para permitir rolagem vertical */
        overflow-y: auto;
        overflow-x: auto;
        margin-top: 15px;
        background-color: var(--background-color);
        border-radius: 8px;
        border: 1px solid rgba(128, 128, 128, 0.2);
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.03);
    }
    
    /* Estilização da scrollbar para ficar mais elegante */
    .table-container::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    .table-container::-webkit-scrollbar-track {
        background: var(--background-color); 
        border-radius: 4px;
    }
    .table-container::-webkit-scrollbar-thumb {
        background: rgba(128, 128, 128, 0.3); 
        border-radius: 4px;
    }
    .table-container::-webkit-scrollbar-thumb:hover {
        background: rgba(128, 128, 128, 0.5); 
    }

    .custom-table {
        width: 100%;
        border-collapse: collapse;
        font-size: 12px;
        color: var(--text-color);
        white-space: nowrap;
    }
    .custom-table thead th {
        position: sticky;
        top: 0;
        z-index: 10;
        background-color: #f8fafc; /* Fallback para tema claro */
        color: var(--text-color);
        text-transform: uppercase;
        padding: 12px 15px;
        text-align: left;
        font-weight: 700;
        letter-spacing: 0.5px;
        border-bottom: 2px solid rgba(128, 128, 128, 0.2);
    }

    /* Variação de cor para o modo escuro do navegador */
    @media (prefers-color-scheme: dark) {
        .custom-table thead th {
            background-color: #1a1e26; /* Tom levemente mais claro que o fundo escuro padrão para dar destaque */
        }
    }

    /* Variação de cor para o modo claro do navegador */
    @media (prefers-color-scheme: light) {
        .custom-table thead th {
            background-color: #f8fafc; /* Tom leve mais escuro que o branco puro para dar destaque */
        }
    }
    .custom-table td {
        padding: 12px 15px;
        text-align: left;
        border-bottom: 1px solid rgba(128, 128, 128, 0.1);
    }
    .custom-table tbody tr {
        transition: background-color 0.2s;
    }
    .custom-table tbody tr:hover {
        background-color: rgba(128, 128, 128, 0.08);
    }
    
    .empresa-col { display: flex; align-items: center; gap: 8px; font-weight: 500; }
    .action-icons { display: flex; gap: 12px; font-size: 15px; color: var(--text-color); opacity: 0.6; }
    .action-icons span { cursor: pointer; transition: all 0.2s; }
    .action-icons span:hover { color: var(--primary-color); opacity: 1; transform: scale(1.1); }
    .action-icons .delete:hover { color: #ef4444; opacity: 1; }

    /* Tags de Status */
    .status-tag {
        padding: 4px 10px;
        border-radius: 12px;
        font-size: 10px;
        font-weight: 700;
        display: inline-flex;
        align-items: center;
        gap: 4px;
        border: 1px solid transparent;
        text-transform: uppercase;
        letter-spacing: 0.3px;
    }
    .status-ativo {
        background-color: rgba(16, 185, 129, 0.15);
        color: #10b981;
        border-color: rgba(16, 185, 129, 0.3);
    }
    .status-inativo {
        background-color: rgba(239, 68, 68, 0.15);
        color: #ef4444;
        border-color: rgba(239, 68, 68, 0.3);
    }

    .btn-limpar button {
        background-color: transparent !important;
        border: 1px solid #ef4444 !important;
        color: #ef4444 !important;
        padding: 4px 15px !important;
        border-radius: 6px !important;
        height: 38px !important;
        margin-top: 28px !important;
        font-weight: 600 !important;
    }
    .btn-limpar button:hover {
        background-color: rgba(239, 68, 68, 0.1) !important;
    }

    .pag-text {
        color: var(--text-color);
        opacity: 0.7;
        font-size: 13px;
        font-weight: 500;
        margin-top: 15px;
    }
    
    .btn-excel button {
        background-color: rgba(16, 185, 129, 0.1) !important;
        color: #10b981 !important;
        border: 1px solid #10b981 !important;
        border-radius: 6px !important;
        float: right;
        margin-top: 10px;
        font-weight: 600 !important;
    }
    .btn-excel button:hover {
        background-color: rgba(16, 185, 129, 0.2) !important;
    }
</style>
"""
st.markdown(css, unsafe_allow_html=True)

if os.path.exists(caminho_fixo):
    timestamp = os.path.getmtime(caminho_fixo)
    data_formatada = datetime.fromtimestamp(timestamp).strftime('%d/%m/%Y %H:%M')
    st.sidebar.success(f"✅ Base atualizada em: {data_formatada}")
    arquivo_unico = caminho_fixo
else:
    st.sidebar.error("❌ Arquivo não encontrado no caminho padrão.")
    arquivo_unico = st.sidebar.file_uploader("Upload da Base Unificada", type=["xlsx"])


@st.cache_data
def carregar_dados(caminho_arquivo, timestamp):
    plan2 = pd.read_excel(caminho_arquivo, sheet_name='Plan2', dtype=str)
    base = pd.read_excel(caminho_arquivo, sheet_name='Base', dtype=str)
    
    df_empresas = base[['COD EMPRESA Z01', 'DESC EMPRESA']].dropna(subset=['COD EMPRESA Z01'])
    df_empresas['COD EMPRESA Z01'] = df_empresas['COD EMPRESA Z01'].str.replace(r'\.0$', '', regex=True).str.zfill(2)
    
    df_filiais = base[['COD EMPRESA', 'COD FILIAL', 'DESC']].dropna(subset=['COD FILIAL'])
    df_filiais['COD EMPRESA'] = df_filiais['COD EMPRESA'].str.replace(r'\.0$', '', regex=True).str.zfill(2)
    df_filiais['COD FILIAL'] = df_filiais['COD FILIAL'].str.replace(r'\.0$', '', regex=True).str.zfill(6)
    
    plan2['CTT_EMPRESA'] = plan2['CTT_EMPRESA'].str.replace(r'\.0$', '', regex=True).str.zfill(2)
    plan2['CTT_FILIAL'] = plan2['CTT_FILIAL'].str.replace(r'\.0$', '', regex=True).str.zfill(6)
    
    base_unificada = df_filiais.merge(df_empresas, left_on='COD EMPRESA', right_on='COD EMPRESA Z01', how='left')
    return plan2, base_unificada

if arquivo_unico:
    timestamp_atual = os.path.getmtime(arquivo_unico) if os.path.exists(arquivo_unico) and isinstance(arquivo_unico, str) else 0
    plan2, base_unificada = carregar_dados(arquivo_unico, timestamp_atual)

    df_completo = plan2.merge(base_unificada, left_on=['CTT_EMPRESA', 'CTT_FILIAL'], right_on=['COD EMPRESA', 'COD FILIAL'], how='left')

    df_completo['EMPRESA_COMPLETA'] = df_completo['COD EMPRESA Z01'].fillna('') + " - " + df_completo['DESC EMPRESA'].fillna('')
    df_completo['FILIAL_COMPLETA'] = df_completo['COD FILIAL'].fillna('') + " - " + df_completo['DESC'].fillna('')

    if 'filtro_empresa' not in st.session_state: st.session_state.filtro_empresa = 'TODAS'
    if 'filtro_filial' not in st.session_state: st.session_state.filtro_filial = 'TODAS'
    if 'filtro_busca' not in st.session_state: st.session_state.filtro_busca = ''
    if 'filtro_bloq' not in st.session_state: st.session_state.filtro_bloq = 'TODOS'
    if 'filtro_financeiro' not in st.session_state: st.session_state.filtro_financeiro = False

    def limpar_filtros():
        st.session_state.filtro_empresa = 'TODAS'
        st.session_state.filtro_filial = 'TODAS'
        st.session_state.filtro_busca = ''
        st.session_state.filtro_bloq = 'TODOS'
        st.session_state.filtro_financeiro = False

    lista_empresas = sorted([e for e in df_completo['EMPRESA_COMPLETA'].dropna().unique().tolist() if e != " - "])
    lista_empresas.insert(0, 'TODAS')

    if st.session_state.filtro_empresa != 'TODAS':
        df_filiais_disponiveis = df_completo[df_completo['EMPRESA_COMPLETA'] == st.session_state.filtro_empresa]
    else:
        df_filiais_disponiveis = df_completo

    lista_filiais = sorted([f for f in df_filiais_disponiveis['FILIAL_COMPLETA'].dropna().unique().tolist() if f != " - "])
    lista_filiais.insert(0, 'TODAS')
    opcoes_bloq = ['TODOS', 'ATIVO', 'INATIVO']

    st.title("📋 Painel de Gestão - Centros de Custo")
    st.write("---")

    f_col1, f_col2, f_col3, f_col4, f_col5 = st.columns([2, 2, 2, 3, 1.5])
    with f_col1:
        st.selectbox("🏢 EMPRESA:", lista_empresas, key='filtro_empresa')
    with f_col2:
        st.selectbox("📍 FILIAL:", lista_filiais, key='filtro_filial')
    with f_col3:
        st.selectbox("🟢 STATUS OPERACIONAL:", opcoes_bloq, key='filtro_bloq')
    with f_col4:
        st.text_input("🔍 Pesquisar Código ou Descrição...", key='filtro_busca')
    with f_col5:
        st.markdown('<div class="btn-limpar">', unsafe_allow_html=True)
        st.button("🗑️ Limpar Filtros", on_click=limpar_filtros, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.write("")

    df_filtrado = df_completo.copy()
    if st.session_state.filtro_empresa != 'TODAS':
        df_filtrado = df_filtrado[df_filtrado['EMPRESA_COMPLETA'] == st.session_state.filtro_empresa]
    if st.session_state.filtro_filial != 'TODAS':
        df_filtrado = df_filtrado[df_filtrado['FILIAL_COMPLETA'] == st.session_state.filtro_filial]
    if st.session_state.filtro_bloq != 'TODOS':
        df_filtrado = df_filtrado[df_filtrado['CTT_BLOQ'] == st.session_state.filtro_bloq]
    if st.session_state.get('filtro_financeiro', False):
        df_filtrado = df_filtrado[df_filtrado['CTT_XFINAN'].astype(str).str.strip().str.upper() == 'S']
    if st.session_state.filtro_busca:
        busca = str(st.session_state.filtro_busca)
        mask = (
            df_filtrado['CTT_CUSTO'].astype(str).str.contains(busca, case=False, na=False) |
            df_filtrado['CTT_DESC01'].astype(str).str.contains(busca, case=False, na=False)
        )
        df_filtrado = df_filtrado[mask]

    total_cc = len(df_filtrado)
    ativos = len(df_filtrado[df_filtrado['CTT_BLOQ'] == 'ATIVO'])
    inativos = len(df_filtrado[df_filtrado['CTT_BLOQ'] == 'INATIVO'])
    financeiros = len(df_filtrado[df_filtrado['CTT_XFINAN'].astype(str).str.strip().str.upper() == 'S'])
    
    kpi_html = (
        '<div style="display: flex; gap: 15px; margin-bottom: 20px;">'
        '<div class="metric-card" style="flex: 1;">'
        '<div class="metric-info">'
        '<span class="metric-title">TOTAL DE CENTROS DE CUSTO</span>'
        f'<span class="metric-value">{total_cc}</span>'
        '</div>'
        '<div class="metric-chart">'
        '<svg viewBox="0 0 100 30" width="60" height="30">'
        '<path d="M0,20 L20,25 L40,10 L60,15 L80,5 L100,0" fill="none" stroke="#3b82f6" stroke-width="2"/>'
        '</svg>'
        '</div>'
        '</div>'
        '<div class="metric-card" style="flex: 1;">'
        '<div class="metric-info">'
        '<span class="metric-title">CENTRO DE CUSTO ATIVOS</span>'
        f'<span class="metric-value">{ativos}</span>'
        '</div>'
        '<div class="metric-chart"><div class="donut-green"></div></div>'
        '</div>'
        '<div class="metric-card" style="flex: 1;">'
        '<div class="metric-info">'
        '<span class="metric-title">CENTROS DE CUSTO INATIVOS</span>'
        f'<span class="metric-value">{inativos}</span>'
        '</div>'
        '<div class="metric-chart"><div class="donut-red"></div></div>'
        '</div>'
        '<div class="metric-card" style="flex: 1;">'
        '<div class="metric-info">'
        '<span class="metric-title">SÓ FINANCEIRO</span>'
        f'<span class="metric-value">{financeiros}</span>'
        '</div>'
        '<div class="metric-chart"><div style="font-size: 28px;">💰</div></div>'
        '</div>'
        '</div>'
    )
    st.markdown(kpi_html, unsafe_allow_html=True)

    if df_filtrado.empty:
        st.warning("Nenhum registro encontrado para os filtros selecionados.")
    else:
        df_exibicao = df_filtrado.fillna('')
        
        # Montando as linhas (agora iteramos em todo o DataFrame de exibição, sem limite de página)
        tbody_html = ""
        for _, row in df_exibicao.iterrows():
            empresa = row.get('EMPRESA_COMPLETA', '')
            filial = row.get('FILIAL_COMPLETA', '')
            ccusto = row.get('CTT_CUSTO', '')
            descricao = row.get('CTT_DESC01', '')
            status = row.get('CTT_BLOQ', '')
            financeiro = row.get('CTT_XFINAN', '')
            regional = row.get('CTT_REGION', 'SEDE')
            
            if status == 'ATIVO':
                tag_html = '<span class="status-tag status-ativo">ATIVO</span>'
            else:
                tag_html = '<span class="status-tag status-inativo">INATIVO</span>'
                
            fin_icon = financeiro

            tbody_html += (
                '<tr>'
                '<td>'
                '<div class="empresa-col">'
                '<span style="font-size:14px;">🏢</span>'
                f'{empresa}'
                '</div>'
                '</td>'
                f'<td>{filial}</td>'
                f'<td>{ccusto}</td>'
                f'<td>{descricao}</td>'
                f'<td>{tag_html}</td>'
                f'<td>{fin_icon}</td>'
                f'<td>{regional}</td>'
                '<td>'
                '<div class="action-icons">'
                '<span>📝</span>'
                '</div>'
                '</td>'
                '</tr>'
            )

        # Montando a tabela completa
        table_html = (
            '<div class="table-container">'
            '<table class="custom-table">'
            '<thead>'
            '<tr>'
            '<th>EMPRESA</th>'
            '<th>FILIAL</th>'
            '<th>C. CUSTO</th>'
            '<th>DESCRIÇÃO</th>'
            '<th>STATUS</th>'
            '<th>FINANCEIRO?</th>'
            '<th>REGIONAL</th>'
            '<th>AÇÕES</th>'
            '</tr>'
            '</thead>'
            '<tbody>'
            f'{tbody_html}'
            '</tbody>'
            '</table>'
            '</div>'
        )
        st.markdown(table_html, unsafe_allow_html=True)

        st.write("")
        col_text, col_blank, col_btn = st.columns([4, 1, 2])
        
        with col_text:
            st.markdown(f'<div class="pag-text">Exibindo todos os <b>{len(df_exibicao)}</b> resultados encontrados.</div>', unsafe_allow_html=True)

        with col_btn:
            colunas_pra_remover = ['COD EMPRESA', 'COD FILIAL', 'DESC', 'CNPJ', 'COD EMPRESA Z01', 'DESC EMPRESA', 'CTT_EMPRESA', 'CTT_FILIAL']
            df_export = df_exibicao.drop(columns=[col for col in colunas_pra_remover if col in df_exibicao.columns], errors='ignore')
            df_export.rename(columns={'EMPRESA_COMPLETA': 'EMPRESA', 'FILIAL_COMPLETA': 'FILIAL', 'CTT_CUSTO': 'C CUSTO', 'CTT_DESC01': 'DESCRICAO', 'CTT_BLOQ': 'BLOQUEADO?', 'CTT_XFINAN': 'FINANCEIRO?', 'CTT_REGION': 'REGIONAL'}, inplace=True)
            
            buffer = io.BytesIO()
            df_export.to_excel(buffer, index=False, engine='openpyxl')
            
            st.markdown('<div class="export-btn-container">', unsafe_allow_html=True)
            st.download_button(
                label="📊 Exportar Resultados (Excel)",
                data=buffer.getvalue(),
                file_name="filtro_centro_custo.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            st.markdown('</div>', unsafe_allow_html=True)