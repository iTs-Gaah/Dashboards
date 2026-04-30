import streamlit as st

st.set_page_config(
    page_title="Portal de Dados de Cadastros",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Customização do Menu Lateral Nativo (Sidebar) para um Visual Premium Corporativo
st.markdown("""
<style>
/* Cor Grafite Vibrante na Barra Lateral */
[data-testid="stSidebar"] {
    background-color: #2F3336 !important;
    border-right: 1px solid #1E2124 !important;
}

/* Arruma a cor dos títulos aglomeradores (Ex: Dashboards, Cadastros) */
[data-testid="stSidebarNavGroup"] div[dir="auto"], [data-testid="stSidebarNav"] > ul > li > div[dir="auto"] {
    color: #9AA0A6 !important;
    font-weight: 700 !important;
    letter-spacing: 0.5px;
}

/* Arruma a cor branca suave nos links nativos para dar contraste */
[data-testid="stSidebarNav"] a span {
    color: #E8EAED !important;
    font-weight: 500;
}

/* Ocultar a linha chata do fundo nativa se houver */
hr {
    border-color: #4A4D50 !important;
}

[data-testid="stSidebarNav"] a {
    border-radius: 8px !important;
    margin: 4px 15px !important;
    padding: 10px 15px !important;
    transition: all 0.3s ease !important;
    font-size: 1rem !important;
}
[data-testid="stSidebarNav"] a:hover {
    background: rgba(255, 255, 255, 0.08) !important;
    transform: translateX(5px);
}
[data-testid="stSidebarNavItems"] {
    padding-top: 15px !important;
}
</style>
""", unsafe_allow_html=True)

# Adiciona a Logo da Empresa de forma nativa e fixa na barra superior do Menu
import os
logo_path = os.path.join(os.path.dirname(__file__), "Portal dados logo.png")
if os.path.exists(logo_path):
    st.logo(logo_path)

# Nova engine de Navegação do Streamlit (Cria Sessões Profissionais no Menu)
pages = {
    "🏠 Visão Geral": [
        st.Page("pages/00_Home_UI.py", title="Home", icon="🏠", default=True, url_path="Home"),
    ],
    "📊 Dashboards": [
        st.Page("pages/Compasa x Roncador.py", title="Compasa x Roncador", icon="📈", url_path="Compasa_x_Roncador"),
        st.Page("pages/Grupo de Aprovadores.py", title="Grupo de Aprovadores", icon="👥", url_path="Grupo_de_Aprovadores"),
        st.Page("pages/Centro de Custo.py", title="Centro de Custo", icon="🏢", url_path="Centro_de_Custo"),
        st.Page("pages/Gestao_Projetos.py", title="Gestão Projetos", icon="📊", url_path="Gestao_Projetos"),
    ],
    "📝 Cadastros": [
        st.Page("pages/Atualização Fornecedor.py", title="Atualização Fornecedor", icon="📋", url_path="Atualização_Fornecedor"),
        st.Page("pages/Contabil.py", title="Contábil", icon="💼", url_path="Contabil"),
        st.Page("pages/Produtos.py", title="Produtos", icon="📦", url_path="Produtos"),
        st.Page("pages/Tarefas.py", title="Tarefas", icon="✅", url_path="Tarefas"),
    ]
}

pg = st.navigation(pages)
pg.run()