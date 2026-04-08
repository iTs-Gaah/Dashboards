import pandas as pd
import google.generativeai as genai
import streamlit as st
import json
import os
import toml 
import time
import datetime

def carregar_config():
    """Carrega a API Key do secrets.toml para funcionamento no terminal e no Streamlit."""
    try:
        return st.secrets["GEMINI_API_KEY"]
    except:
        config = toml.load(".streamlit/secrets.toml")
        return config["GEMINI_API_KEY"]

api_key = carregar_config()
genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-2.5-flash')

def extrair_dados_projeto(texto_chat, texto_planner, tentativas=3):
    """
    Realiza a extracao e auditoria de dados do projeto cruzando informacoes do Planner e Chat.
    Filtra tarefas indesejadas, identifica novas demandas e aplica regra de inatividade absoluta de 7 dias.
    """
    data_hoje = datetime.datetime.now().strftime("%d/%m/%Y")
    
    prompt = f"""
    Você é um auditor de dados e gestor de projetos sênior.
    A data de hoje é: {data_hoje}.
    Analise o histórico do chat do Teams e a lista de tarefas atual do Planner fornecidos abaixo.

    REGRAS CRÍTICAS DE AUDITORIA E EXTRAÇÃO:
    1. CONSOLIDAÇÃO E DESCOBERTA: Liste as tarefas do Planner. Além disso, leia ATENTAMENTE o histórico do chat. QUALQUER solicitação ou demanda feita no chat DEVE ser incluída como uma tarefa independente na lista, definindo a chave 'origem' como 'Chat'.
    2. DEDUPLICAÇÃO: Se o chat menciona o andamento de uma tarefa que já existe no Planner, NÃO crie uma tarefa nova. Atualize as informações da tarefa existente.
    3. CARA CRACHÁ (AUDITORIA): O Planner envia o status numérico (0 = 'A iniciar', 50 = 'Em andamento', 100 = 'Concluído'). Compare isso com o chat e aponte divergências claras.
    4. REGRA DOS 7 DIAS (INATIVIDADE TOTAL): Identifique a data da ÚLTIMA mensagem registrada no chat (a mensagem mais recente de todo o histórico). Se a diferença entre essa data e a data de hoje ({data_hoje}) for maior que 7 dias, crie OBRIGATORIAMENTE uma tarefa chamada 'Aviso: Inatividade no Chat (>7 dias)', defina o status dessa tarefa como 'Atrasado' e force o 'status_projeto' para 'Atrasado'. O conteúdo da mensagem não importa, apenas o silêncio no grupo.
    5. STATUS PERMITIDOS: Utilize estritamente 'A iniciar', 'Em andamento', 'Atrasado' ou 'Concluído'.
    6. EXCLUSÃO DE ROTINAS: Ignore completamente e NÃO inclua na lista final nenhuma tarefa que se refira a "acompanhamento semanal", "reunião semanal" ou rotinas similares.
    7. FORMATAÇÃO DE DATAS: Converta as datas em formato ISO (ex: 2025-08-01T10:00:00Z) geradas pelo Planner para o formato DD/MM/AAAA.

    Retorne APENAS um objeto JSON válido. Siga estritamente este formato com estas chaves exatas:
    {{
      "resumo_projeto": "Resumo analítico direto (max 3 frases) do andamento do projeto. Destaque pendências e divergências.",
      "status_projeto": "A iniciar/Em andamento/Atrasado/Concluído",
      "data_ultima_mensagem": "DD/MM/AAAA",
      "texto_ultima_mensagem": "Texto exato ou resumo da última mensagem do grupo",
      "tarefas": [
        {{
          "origem": "Planner / Chat / Ambos",
          "tarefa": "Nome da tarefa",
          "status": "A iniciar/Em andamento/Atrasado/Concluído",
          "responsavel": "Nome ou Não definido",
          "data_solicitacao": "DD/MM/AAAA ou Não definido",
          "prazo": "DD/MM/AAAA ou Não definido",
          "divergencia_encontrada": "Sim / Não",
          "detalhe_divergencia": "Explicação objetiva da divergência ou vazio se não houver."
        }}
      ]
    }}
    """
    
    conteudo_analise = f"\n\n--- DADOS DO PLANNER ---\n{texto_planner}\n\n--- HISTÓRICO DO CHAT ---\n{texto_chat}"
    
    for tentativa in range(tentativas):
         try:
             response = model.generate_content(prompt + conteudo_analise)
             texto_limpo = response.text.strip()

             if texto_limpo.startswith("```json"):
                 texto_limpo = texto_limpo[7:]
             if texto_limpo.endswith("```"):
                 texto_limpo = texto_limpo[:-3]

             return json.loads(texto_limpo.strip())
         except Exception as e:
            erro_str = str(e)
            if "429" in erro_str or "Quota" in erro_str:
                tempo_espera = 30 * (tentativa + 1)
                # Adiciona essa linha aqui pra gente ver o erro cru da Google:
                print(f"ERRO REAL DA GOOGLE: {erro_str}")
                
                print(f"Torneira secou (Cota/429). Aguardando {tempo_espera} segundos...")
                time.sleep(tempo_espera)
            else:
                 print(f"Erro inesperado na extracao ou JSON invalido: {e}")
                 return None

    print("Falha na extracao apos multiplas tentativas devido a limites de cota.")
    return None

def main():
    arquivo_entrada = r'C:\Users\gabriel.silva\OneDrive - compasa.com.br\Dashboards\Grupo de Projetos - Teams.xlsx'
    arquivo_saida = 'Projetos_Estruturados_Streamlit.xlsx'
    
    if not os.path.exists(arquivo_entrada):
        print(f"ERRO: Arquivo nao localizado em {arquivo_entrada}")
        return

    df_bruto = pd.read_excel(arquivo_entrada)
    
    df_bruto['Data_Extracao'] = pd.to_datetime(df_bruto['Data_Extracao'], dayfirst=True, errors='coerce')
    df_bruto = df_bruto.sort_values(by=['Projeto', 'Data_Extracao'], ascending=[True, True])
    df_para_processar = df_bruto.drop_duplicates(subset=['Projeto'], keep='last')
    df_para_processar = df_para_processar[df_para_processar['Projeto'].str.contains('4767', na=False)]

    
    print(f"Filtrando dados... {len(df_para_processar)} projetos unicos identificados para processamento.")

    resultados = []
    for index, row in df_para_processar.iterrows():
        projeto = str(row['Projeto'])
        chat_bruto = str(row['Historico_Chat'])
        planner_bruto = str(row.get('Tarefas_Planner', 'Sem tarefas no Planner'))
        
        data_ext_str = row['Data_Extracao'].strftime('%d/%m/%Y') if pd.notna(row['Data_Extracao']) else "Não definido"
        
        print(f"Processando projeto: {projeto}...")
        dados = extrair_dados_projeto(chat_bruto, planner_bruto)
        
        if dados and 'tarefas' in dados:
            resumo = dados.get('resumo_projeto', 'Sem resumo disponível.')
            status_macro = dados.get('status_projeto', 'Em andamento')
            dt_ultima_msg = dados.get('data_ultima_mensagem', 'Não definido')
            txt_ultima_msg = dados.get('texto_ultima_mensagem', 'Não definido')
            
            for item in dados['tarefas']:
                item['Projeto'] = projeto
                item['Data_Extracao'] = data_ext_str
                item['Resumo_Projeto'] = resumo
                item['Status_Projeto'] = status_macro
                item['Data_Ultima_Mensagem'] = dt_ultima_msg
                item['Ultima_Mensagem'] = txt_ultima_msg
                resultados.append(item)
        
        time.sleep(15)
                
    if resultados:
        df_novo = pd.DataFrame(resultados)
        
        df_novo['data_temp'] = pd.to_datetime(df_novo['data_solicitacao'], format='%d/%m/%Y', errors='coerce')
        df_novo = df_novo.sort_values(by=['Projeto', 'data_temp'], ascending=[True, True])
        df_novo = df_novo.drop(columns=['data_temp'])
        
        if os.path.exists(arquivo_saida):
            df_antigo = pd.read_excel(arquivo_saida)
            projetos_atualizados = df_novo['Projeto'].unique()
            df_antigo = df_antigo[~df_antigo['Projeto'].isin(projetos_atualizados)]
            
            df_consolidado = pd.concat([df_antigo, df_novo])
            df_consolidado.to_excel(arquivo_saida, index=False)
        else:
            df_novo.to_excel(arquivo_saida, index=False)
            
        print(f"Sucesso! Dados consolidados e salvos em: {arquivo_saida}")
    else:
        print("Nenhum dado extraido.")

if __name__ == "__main__":
    main()