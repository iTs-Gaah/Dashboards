import streamlit as st
import pandas as pd
import os
import base64
from datetime import datetime

# Configuração da página
st.set_page_config(
    page_title="Portal de Dados de Cadastros",
    layout="wide"
)

# Caminhos separados pra não dar merda
IMG_DIR = r"C:\Users\gabriel.silva\VS Code\Dashboard"
EXCEL_DIR = r"C:\Users\gabriel.silva\VS Code\Dashboard\pages"
CAMINHO_ONEDRIVE = r"C:\Users\gabriel.silva\OneDrive - compasa.com.br\QSMS - Administrativo - Área de Cadastros\Controle Cadastros.xlsx"

# Função pra ler as imagens locais
def carregar_imagem_base64(nome_arquivo):
    caminho = os.path.join(IMG_DIR, nome_arquivo)
    if os.path.exists(caminho):
        with open(caminho, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return ""

# Função pra ler a planilha no caminho novo
def analisar_planilha(nome_arquivo, aba=0): 
    caminho = os.path.join(EXCEL_DIR, nome_arquivo)
    if os.path.exists(caminho):
        try:
            # Agora usamos a variável 'aba' aqui dentro
            df = pd.read_excel(caminho, sheet_name=aba) 
            total_linhas = len(df)
            
            timestamp = os.path.getmtime(caminho)
            data_atualizacao = datetime.fromtimestamp(timestamp).strftime('%d/%m/%Y %H:%M')
            
            return f"~{total_linhas}", data_atualizacao
        except Exception as e:
            return "~0", "Erro de leitura"
    return "~0", "Arquivo não encontrado"

# Processando tudo
img_portal = carregar_imagem_base64("Portal dados logo.png")
img_aprovadores = carregar_imagem_base64("Aprovadores logo.png")
img_roncador = carregar_imagem_base64("Roncador logo.png") 
img_ccusto = carregar_imagem_base64("C.Custo logo.png") 
img_fornecedores = carregar_imagem_base64("Fornecedores logo.png")  
linhas_aprov, data_aprov = analisar_planilha("Aprovadores.xlsx")
linhas_ronc, data_ronc = analisar_planilha("Roncador.xlsx")
linhas_ccusto, data_ccusto = analisar_planilha("Aprovadores.xlsx", aba="Plan2")

# Cabeçalho - Maior e Centralizado
html_cabecalho = f"""
<div style="display: flex; align-items: center; justify-content: center; margin-bottom: 20px;">
    <img src="data:image/png;base64,{img_portal}" style="width: 80px; height: 80px; margin-right: 15px;">
    <h1 style="margin: 0; font-size: 3em;">Portal de Dados de Cadastros</h1>
</div>
"""
st.markdown(html_cabecalho, unsafe_allow_html=True)
st.write("---")

# Status com o verde no Operacional
st.markdown("**Status do Portal:** <span style='color: #32CD32; font-weight: bold;'>Operacional</span> • Todos os pipelines de dados atualizados", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

try:
    df_fornec = pd.read_excel(CAMINHO_ONEDRIVE, sheet_name="Alt_Att Fornec")
    linhas_fornecedores = f"~{len(df_fornec)}"
    timestamp_fornec = os.path.getmtime(CAMINHO_ONEDRIVE)
    data_fornecedores = datetime.fromtimestamp(timestamp_fornec).strftime('%d/%m/%Y %H:%M')
except Exception as e:
    linhas_fornecedores, data_fornecedores = "~0", "Erro no OneDrive"
# Caixas com relevo, transparência e cursor indicando clique
estilo_caixa = """
    background-color: rgba(128, 128, 128, 0.1); 
    padding: 20px; 
    border-radius: 10px; 
    display: flex; 
    align-items: center; 
    justify-content: space-between;
    margin-bottom: 20px;
    cursor: pointer;
"""

# Cartão: Aprovadores 
html_aprovadores = f"""
<a href="Grupo_de_Aprovadores" target="_self" style="text-decoration: none; color: inherit; display: block;">
    <div style="{estilo_caixa}">
        <div style="display: flex; align-items: center;">
            <img src="data:image/png;base64,{img_aprovadores}" style="width: 60px; height: 60px; margin-right: 20px;">
            <div>
                <h3 style="margin: 0; padding-bottom: 5px;">Módulo de Aprovadores</h3>
                <p style="margin: 0; color: #888; font-size: 0.9em;">Gestão e Validação de Regras de (Protheus & Fluig)</p>
            </div>
        </div>
        <div style="text-align: right;">
            <p style="margin: 0; font-size: 1.1em; font-weight: bold;">Total de Regras: {linhas_aprov}</p>
            <p style="margin: 0; color: #888; font-size: 0.85em; margin-top: 5px;">Data de Atualização: {data_aprov}</p>
        </div>
    </div>
</a>
"""
st.markdown(html_aprovadores, unsafe_allow_html=True)

# Cartão: Roncador 
html_roncador = f"""
<a href="Compasa_x_Roncador" target="_self" style="text-decoration: none; color: inherit; display: block;">
    <div style="{estilo_caixa}">
        <div style="display: flex; align-items: center;">
            <img src="data:image/png;base64,{img_roncador}" style="width: 60px; height: 60px; margin-right: 20px;">
            <div>
                <h3 style="margin: 0; padding-bottom: 5px;">Módulo Compasa x Roncador</h3>
                <p style="margin: 0; color: #888; font-size: 0.9em;">Análise e Consulta de Produtos e Fornecedores</p>
            </div>
        </div>
        <div style="text-align: right;">
            <p style="margin: 0; font-size: 1.1em; font-weight: bold;">Total de Registros: {linhas_ronc}</p>
            <p style="margin: 0; color: #888; font-size: 0.85em; margin-top: 5px;">Data de Atualização: {data_ronc}</p>
        </div>
    </div>
</a>
"""
st.markdown(html_roncador, unsafe_allow_html=True)

# Cartão: Centro de Custo
html_ccusto = f"""
<a href="Centro_de_Custo" target="_self" style="text-decoration: none; color: inherit; display: block;">
    <div style="{estilo_caixa}">
        <div style="display: flex; align-items: center;">
            <img src="data:image/png;base64,{img_ccusto}" style="width: 60px; height: 60px; margin-right: 20px;">
            <div>
                <h3 style="margin: 0; padding-bottom: 5px;">Módulo Centro de Custo</h3>
                <p style="margin: 0; color: #888; font-size: 0.9em;">Relação de Centro de Custo</p>
            </div>
        </div>
        <div style="text-align: right;">
            <p style="margin: 0; font-size: 1.1em; font-weight: bold;">Total de Registros: {linhas_ccusto}</p>
            <p style="margin: 0; color: #888; font-size: 0.85em; margin-top: 5px;">Data de Atualização: {data_ccusto}</p>
        </div>
    </div>
</a>
"""

st.markdown(html_ccusto, unsafe_allow_html=True)

# Cartão: Fornecedores
html_fornecedores = f"""
<a href="Atualização_Fornecedor" target="_self" style="text-decoration: none; color: inherit; display: block;">
    <div style="{estilo_caixa}">
        <div style="display: flex; align-items: center;">
            <img src="data:image/png;base64,{img_fornecedores}" style="width: 60px; height: 60px; margin-right: 20px;">
            <div>
                <h3 style="margin: 0; padding-bottom: 5px;">Módulo Atualização de Fornecedores</h3>
                <p style="margin: 0; color: #888; font-size: 0.9em;">Relação de Fornecedores Atualizados</p>
            </div>
        </div>
        <div style="text-align: right;">
            <p style="margin: 0; font-size: 1.1em; font-weight: bold;">Total de Registros: {linhas_fornecedores}</p>
            <p style="margin: 0; color: #888; font-size: 0.85em; margin-top: 5px;">Data de Atualização: {data_fornecedores}</p>
        </div>
    </div>
</a>
"""

st.markdown(html_fornecedores, unsafe_allow_html=True)