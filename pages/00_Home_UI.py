import streamlit as st
import pandas as pd
import os
import base64
from datetime import datetime

# Caminhos
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

# Função auxiliar para pegar timestamp do arquivo de forma barata (para invalidar o cache)
def obter_timestamp(caminho):
    try: return os.path.getmtime(caminho)
    except: return 0

# Função pra ler a planilha COM CACHE
@st.cache_data(show_spinner=False)
def analisar_planilha(nome_arquivo, aba=0, timestamp=0): 
    caminho = os.path.join(EXCEL_DIR, nome_arquivo)
    if os.path.exists(caminho):
        try:
            xls = pd.ExcelFile(caminho)
            
            # Função auxiliar pra encontrar aba com variações de nome
            def encontrar_aba(nome_procurado):
                if isinstance(nome_procurado, (list, tuple)):
                    abas_achadas = []
                    for nome in nome_procurado:
                        # Tenta encontrar exatamente
                        if nome in xls.sheet_names:
                            abas_achadas.append(nome)
                        else:
                            # Procura por variação de caso/espaço
                            for sheet in xls.sheet_names:
                                if sheet.strip().upper() == nome.strip().upper():
                                    abas_achadas.append(sheet)
                                    break
                            else:
                                # Procura contendo o texto
                                for sheet in xls.sheet_names:
                                    if nome.upper() in sheet.strip().upper():
                                        abas_achadas.append(sheet)
                                        break
                    return abas_achadas if abas_achadas else nome_procurado
                else:
                    # Se for número (índice), usa direto
                    if isinstance(nome_procurado, int):
                        if nome_procurado < len(xls.sheet_names):
                            return xls.sheet_names[nome_procurado]
                        else:
                            return 0  # Fallback para primeira aba
                    # Se for string
                    if nome_procurado in xls.sheet_names:
                        return nome_procurado
                    # Procura por variação de caso/espaço
                    for sheet in xls.sheet_names:
                        if sheet.strip().upper() == nome_procurado.strip().upper():
                            return sheet
                    # Procura contendo o texto
                    for sheet in xls.sheet_names:
                        if nome_procurado.upper() in sheet.strip().upper():
                            return sheet
                    # Se não achar, usa primeira aba por padrão
                    return xls.sheet_names[0] if xls.sheet_names else nome_procurado
            
            aba_corrigida = encontrar_aba(aba)
            
            # Verifica se foi passada uma lista de abas para somar
            if isinstance(aba_corrigida, list):
                dfs = {}
                for nome_aba in aba_corrigida:
                    try:
                        df_temp = pd.read_excel(xls, sheet_name=nome_aba)
                        # Remove linhas completamente vazias
                        df_temp = df_temp.dropna(how='all')
                        df_temp = df_temp[~df_temp.astype(str).apply(lambda x: (x.str.strip() == '').all(), axis=1)]
                        dfs[nome_aba] = df_temp
                    except:
                        pass
                total_linhas = sum(len(df) for df in dfs.values())
            else:
                df = pd.read_excel(xls, sheet_name=aba_corrigida) 
                # Remove linhas completamente vazias
                df = df.dropna(how='all')
                df = df[~df.astype(str).apply(lambda x: (x.str.strip() == '').all(), axis=1)]
                total_linhas = len(df)
            
            timestamp = os.path.getmtime(caminho)
            data_atualizacao = datetime.fromtimestamp(timestamp).strftime('%d/%m/%Y %H:%M')
            
            return f"~{total_linhas}", data_atualizacao
        except Exception as e:
            erro_msg = f"Erro: {str(e)[:50]}"
            return "~0", erro_msg
    return "~0", "Arquivo não encontrado"


# Cache do OneDrive
@st.cache_data(show_spinner=False)
def obter_fornecedores(timestamp=0):
    try:
        if timestamp == 0:
            return "~0", "Erro no OneDrive"
        df_fornec = pd.read_excel(CAMINHO_ONEDRIVE, sheet_name="Alt_Att Fornec")
        return f"~{len(df_fornec)}", datetime.fromtimestamp(timestamp).strftime('%d/%m/%Y %H:%M')
    except Exception as e:
        return "~0", "Erro no OneDrive"

# Processando tudo
img_portal = carregar_imagem_base64("Portal dados logo.png")
img_aprovadores = carregar_imagem_base64("Aprovadores logo.png")
img_roncador = carregar_imagem_base64("Roncador logo.png") 
img_ccusto = carregar_imagem_base64("C.Custo logo.png") 
img_fornecedores = carregar_imagem_base64("Fornecedores logo.png")  

# Obtemos os timestamps na hora pra decidir se o cache deve atualizar
ts_aprov = obter_timestamp(os.path.join(EXCEL_DIR, "Aprovadores.xlsx"))
ts_ronc = obter_timestamp(os.path.join(EXCEL_DIR, "Roncador.xlsx"))
ts_fornec = obter_timestamp(CAMINHO_ONEDRIVE)

# Notar o uso de TUPLA em ("Plan1", "Form") ao invés de lista, pois Cache do Streamlit exige argumentos imutáveis
linhas_aprov, data_aprov = analisar_planilha("Aprovadores.xlsx", aba=("Plan1", "Form"), timestamp=ts_aprov)
linhas_ronc, data_ronc = analisar_planilha("Roncador.xlsx", aba=0, timestamp=ts_ronc)
linhas_ccusto, data_ccusto = analisar_planilha("Aprovadores.xlsx", aba="Plan2", timestamp=ts_aprov)
linhas_fornecedores, data_fornecedores = obter_fornecedores(timestamp=ts_fornec)

# Lógica de Cor dos números
def cor_alerta(valor):
    return "#FF3333" if str(valor).strip() in ["~0", "0"] else "inherit"

cor_aprov = cor_alerta(linhas_aprov)
cor_ronc = cor_alerta(linhas_ronc)
cor_ccusto = cor_alerta(linhas_ccusto)
cor_fornec = cor_alerta(linhas_fornecedores)

# Cabeçalho
html_cabecalho = f"""
<div style="display: flex; align-items: center; justify-content: center; margin-bottom: 20px;">
    <img src="data:image/png;base64,{img_portal}" style="width: 80px; height: 80px; margin-right: 15px;">
    <h1 style="margin: 0; font-size: 3em;">Portal de Dados de Cadastros</h1>
</div>
"""
st.markdown(html_cabecalho, unsafe_allow_html=True)
st.write("---")

# --- LÓGICA DO STATUS GERAL ---
# Se qualquer um dos pipelines retornar ~0, a gente avisa que deu merda
pipelines_zerados = any(str(val).strip() in ["~0", "0"] for val in [linhas_aprov, linhas_ronc, linhas_ccusto, linhas_fornecedores])

if pipelines_zerados:
    status_texto = "Um ou mais módulos estão inoperantes"
    status_cor = "#FF3333"
    status_msg_secundaria = "Verifique falhas na leitura ou bases vazias"
else:
    status_texto = "Operacional"
    status_cor = "#32CD32"
    status_msg_secundaria = "Todos os pipelines de dados atualizados"

st.markdown(f"**Status do Portal:** <span style='color: {status_cor}; font-weight: bold;'>{status_texto}</span> • {status_msg_secundaria}", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

# Estilo da caixa
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
            <p style="margin: 0; font-size: 1.1em; font-weight: bold; color: {cor_aprov};">Total de Regras: {linhas_aprov}</p>
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
            <p style="margin: 0; font-size: 1.1em; font-weight: bold; color: {cor_ronc};">Total de Registros: {linhas_ronc}</p>
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
            <p style="margin: 0; font-size: 1.1em; font-weight: bold; color: {cor_ccusto};">Total de Registros: {linhas_ccusto}</p>
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
            <p style="margin: 0; font-size: 1.1em; font-weight: bold; color: {cor_fornec};">Total de Registros: {linhas_fornecedores}</p>
            <p style="margin: 0; color: #888; font-size: 0.85em; margin-top: 5px;">Data de Atualização: {data_fornecedores}</p>
        </div>
    </div>
</a>
"""
st.markdown(html_fornecedores, unsafe_allow_html=True)