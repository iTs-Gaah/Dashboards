import streamlit as st
import pandas as pd

# Configuração inicial da página
st.set_page_config(page_title="Consulta Produto Protheus", layout="wide")

# Título do painel
st.title("Consulta Produto Protheus")

# Caminho do arquivo de base de dados (utilizando raw string 'r' para evitar erros de escape no caminho do Windows)
FILE_PATH = r"C:\Users\gabriel.silva\VS Code\Dashboard\pages\Produtos.xlsx"

# Lista estática de tipos e grupos fornecida pelo usuário
TIPO_GRUPO_MAP = {
    'DI': [
        'MAT ESCRITORIO, ALIMENT E LIMP',
        'LOCACAO DE IMOVEIS',
        'MOVEIS, ELETRODOM, EQ INFORMAT',
        'OUTROS ADM LOCAL',
        'LOCACAO DE BANHEIRO QUIMICO',
        'ENERGIA ELETRICA',
        'AGUA, INTERNET E TELEFONE',
        'FRETES DE MATERIAIS DIVERSOS',
        'SERV COMUNICACAO E MARKETING',
        'TAXAS, MULTAS E AUTOS INFRACAO'
    ],
    'EQ': [
        'MANUTENCOES GERAIS',
        'EQUIPAMENTOS MANUAIS',
        'LUBRIFICANTES E GRAXAS',
        'MATERIAIS DE DESGASTE',
        'BETONEIRA',
        'CAMINHAO ESPARGIDOR',
        'CAMINHAO BETONEIRA',
        'CAMINHAO COMBOIO',
        'CAMINHAO DE APOIO',
        'CAMINHAO PIPA',
        'CAMINHAO PRANCHA',
        'CONJUNTO DE BRITAGEM',
        'ESCAVADEIRAS',
        'FRESADORAS',
        'PNEUS',
        'MINICARREGADEIRA E IMPLEMENTOS',
        'MOBILIZACAO DE EQUIPAMENTOS',
        'MOTONIVELADORAS',
        'ONIBUS',
        'PA CARREGADEIRA',
        'RECICLADORA',
        'RETROESCAVADEIRAS',
        'ROLOS COMPACTAD PNEU E CHAPA',
        'TANQUE',
        'TORRE DE ILUMINACAO',
        'TRATORES DE ESTEIRA',
        'TRATORES DE PNEUS',
        'USINAS ASF, SOLOS E CONCRETO',
        'USINAS DE MICRO',
        'VIBROACABADORAS',
        'GRUPO GERADOR',
        'OUTROS EQUIPAMENTOS',
        'VEICULOS LEVES'
    ],
    'LI': [
        'ASFALTO DILUIDO',
        'CAP CONVENCIONAL',
        'CAP MODIFICADO',
        'EMULSOES',
        'MELHORADORES ADESIV E REJUVENE'
    ],
    'MO': [
        "EPI'S",
        'BENEFICIOS',
        'CESTA BASICA',
        'DEBANDAS',
        'ENCARGOS SOCIAIS',
        'EXAMES',
        'HORAS EXTRAS',
        "PJ'S",
        'REFEICAO',
        'SALARIOS',
        'TREINAMENTOS'
    ],
    'MT': [
        'DEMAIS MATERIAIS',
        'INSUMOS FABRICA',
        'AGREGADOS',
        'GEOCOMPOSTO',
        'COMBUSTIVEIS',
        'MAT ELETRICO ILUMIN REDE ENERG',
        'MADEIRAS',
        'MATERIAIS DE SINALIZACAO',
        'ACO',
        'ESTRUTURAS METALICAS',
        'SOLOS, CASCALHO E SAIBRO',
        'CIMENTOS',
        'CONCRETO ASFALTICO',
        'CONCRETO PORTLAND',
        'FERRAMENTAS MANUAIS',
        'PRE-MOLDADOS DE CONCRETO',
        'REVESTIMENTO VEGETAL'
    ],
    'ST': [
        'SERV DE TERRAPLENAGEM',
        'SERV DE PAVIMENTACAO',
        'SERV DE OAC E DRENAGEM',
        'SERV DE OAE',
        'SERV MEIO AMBIENTE E PAISAGISM',
        'SERV DE SINALIZACAO',
        'SERV DE DETONACAO DE ROCHA',
        'SERV DE CONSTRUCAO CIVIL',
        'SERV DE CONTENCAO E FUNDACAO',
        'SERV DE CONSULT E ESTUDOS TEC',
        'SERV TOPOGRAFIA, SOND E PROJET',
        'SERV DE CONTROLE TECNOLOGICO',
        'SERV DE SEGURANCA PATRIMONIAL',
        'SERV ZELADORIA E MANUT PREDIAL',
        'SERV OBRAS COMPLEMENTARES'
    ],
    'TR': [
        'CAMINHAO BASCULANTE',
        'FRETE DE CBUQ POR PRODUCAO',
        'FRETE MAT PETREO POR PRODUCAO',
        'FRETE DE SOLOS POR PRODUCAO',
        'FRETE DE LIGANTES ASFALTICOS'
    ]
}

# Função com cache para otimizar o carregamento da planilha
@st.cache_data
def load_data():
    try:
        df = pd.read_excel(FILE_PATH, sheet_name='Plan1')
        df_filtros = pd.read_excel(FILE_PATH, sheet_name='Plan2')
        
        # Converter colunas de pesquisa para string, evitando erros com dados numéricos nulos ou mistos
        if 'B1_COD' in df.columns:
            df['B1_COD'] = df['B1_COD'].astype(str).str.strip()
            df['B1_COD_FMT'] = df['B1_COD'].fillna('').astype(str).str.zfill(10)
        if 'B1_DESC' in df.columns:
            df['B1_DESC'] = df['B1_DESC'].astype(str)
        if 'B1_GRUPO' in df.columns:
            df['B1_GRUPO'] = df['B1_GRUPO'].astype(str).str.strip()
        if 'B1_TIPO' in df.columns:
            df['B1_TIPO'] = df['B1_TIPO'].astype(str).str.strip()
        if 'BM_DESC' in df.columns:
            df['BM_DESC'] = df['BM_DESC'].astype(str).str.strip()
        if 'STATUS' in df.columns:
            df['STATUS'] = df['STATUS'].astype(str).str.strip()

        if 'B1_TIPO' in df_filtros.columns:
            df_filtros['B1_TIPO'] = df_filtros['B1_TIPO'].astype(str).str.strip()
        if 'BM_DESC' in df_filtros.columns:
            df_filtros['BM_DESC'] = df_filtros['BM_DESC'].astype(str).str.strip()

        if df_filtros.empty or 'B1_TIPO' not in df_filtros.columns or 'BM_DESC' not in df_filtros.columns:
            df_filtros = pd.DataFrame([
                {'B1_TIPO': tipo, 'BM_DESC': grupo}
                for tipo, grupos in TIPO_GRUPO_MAP.items()
                for grupo in grupos
            ])
            df_filtros['B1_TIPO'] = df_filtros['B1_TIPO'].astype(str).str.strip()
            df_filtros['BM_DESC'] = df_filtros['BM_DESC'].astype(str).str.strip()
            
        return df, df_filtros
    except Exception as e:
        st.error(f"Erro ao carregar a planilha: {e}")
        return pd.DataFrame(), pd.DataFrame()

# Carregar os dados
df_produtos, df_filtros = load_data()

if not df_produtos.empty:
    st.subheader("Filtros de Pesquisa")
    
    # Criação das 4 colunas para os campos de pesquisa
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        pesquisa_codigo = st.text_input("1. Pesquisa por Código")
    with col2:
        pesquisa_desc_1 = st.text_input("2. Descrição")
    with col3:
        pesquisa_desc_2 = st.text_input("3. Descrição")
    with col4:
        pesquisa_desc_3 = st.text_input("4. Descrição")

    tipo_options = ['Todos']
    grupos_all = []
    if 'B1_TIPO' in df_filtros.columns:
        tipo_options += list(dict.fromkeys(df_filtros['B1_TIPO'].dropna().astype(str).str.strip().tolist()))
    if 'BM_DESC' in df_filtros.columns:
        grupos_all = list(dict.fromkeys(df_filtros['BM_DESC'].dropna().astype(str).str.strip().tolist()))

    col5, col6 = st.columns(2)
    with col5:
        tipo_selecionado = st.selectbox('5. Filtrar por TIPO', tipo_options)
    with col6:
        if tipo_selecionado != 'Todos' and 'B1_TIPO' in df_filtros.columns and 'BM_DESC' in df_filtros.columns:
            grupo_options = list(dict.fromkeys(df_filtros.loc[df_filtros['B1_TIPO'] == tipo_selecionado, 'BM_DESC'].dropna().astype(str).str.strip().tolist()))
        else:
            grupo_options = grupos_all
        grupo_options = ['Todos'] + grupo_options
        grupo_selecionado = st.selectbox('6. Filtrar por GRUPO', grupo_options)

    # Criação de uma cópia do DataFrame para aplicar os filtros
    df_filtrado = df_produtos.copy()

    # Aplicação do filtro de Código
    if pesquisa_codigo:
        codigo_digits = ''.join(ch for ch in pesquisa_codigo if ch.isdigit())
        if codigo_digits:
            codigo_fmt = codigo_digits.zfill(10)
            if len(codigo_digits) == 10:
                # Busca exata quando o usuário informa o código completo
                df_filtrado = df_filtrado[df_filtrado['B1_COD_FMT'] == codigo_fmt]
            else:
                # Busca por prefixo quando informa parte do código
                df_filtrado = df_filtrado[df_filtrado['B1_COD_FMT'].str.startswith(codigo_fmt)]
        else:
            df_filtrado = df_filtrado[df_filtrado['B1_COD'].str.contains(pesquisa_codigo, case=False, na=False)]
    
    # Aplicação dos filtros de Descrição (atuam em conjunto / lógica AND)
    if pesquisa_desc_1:
        df_filtrado = df_filtrado[df_filtrado['B1_DESC'].str.contains(pesquisa_desc_1, case=False, na=False)]
    
    if pesquisa_desc_2:
        df_filtrado = df_filtrado[df_filtrado['B1_DESC'].str.contains(pesquisa_desc_2, case=False, na=False)]
        
    if pesquisa_desc_3:
        df_filtrado = df_filtrado[df_filtrado['B1_DESC'].str.contains(pesquisa_desc_3, case=False, na=False)]

    if 'B1_TIPO' in df_filtrado.columns and tipo_selecionado != 'Todos':
        df_filtrado = df_filtrado[df_filtrado['B1_TIPO'] == tipo_selecionado]
    if 'BM_DESC' in df_filtrado.columns and grupo_selecionado != 'Todos':
        df_filtrado = df_filtrado[df_filtrado['BM_DESC'] == grupo_selecionado]

    # Dicionário de mapeamento para renomear as colunas
    colunas_exibicao = {
        "B1_COD": "CÓDIGO",
        "B1_DESC": "DESCRIÇÃO",
        "B1_UM": "UNID. MEDIDA",
        "B1_TIPO": "TIPO",
        "B1_GRUPO": "GRUPO",
        "BM_DESC": "DESC GRUPO",
        "STATUS": "STATUS"
    }

    # Selecionar apenas as colunas solicitadas que existem no DataFrame para evitar KeyError
    colunas_presentes = [col for col in colunas_exibicao.keys() if col in df_filtrado.columns]
    
    # Aplicar o filtro de colunas e renomeá-las
    df_final = df_filtrado[colunas_presentes].rename(columns=colunas_exibicao)

    # Formatar CÓDIGO com 10 dígitos usando zeros à esquerda
    if 'CÓDIGO' in df_final.columns:
        df_final['CÓDIGO'] = df_final['CÓDIGO'].fillna('').astype(str).str.zfill(10)

    # Formatar GRUPO com 4 dígitos usando zeros à esquerda
    if 'GRUPO' in df_final.columns:
        df_final['GRUPO'] = df_final['GRUPO'].fillna('').astype(str).str.zfill(4)

    # Exibição do resultado
    st.write("---")
    st.subheader(f"Resultados encontrados: {len(df_final)}")
    
    # Exibir o DataFrame na tela
    st.dataframe(df_final, width='stretch', hide_index=True)