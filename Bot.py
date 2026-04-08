import os
import datetime
import pandas as pd
import openpyxl as px
from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from dotenv import load_dotenv

# Carrega as variáveis do arquivo .env que você criou
load_dotenv("Password.env")

# Pega os dados ocultos
user = os.getenv("DW_USER")
password = os.getenv("DW_PASS")
host = os.getenv("DW_HOST")
port = os.getenv("DW_PORT")
db_name = os.getenv("DW_NAME")

# Cria o objeto de URL de forma segura (trata caracteres especiais na senha automaticamente)
url_conexao = URL.create(
    drivername="mysql+pymysql",
    username=user,
    password=password,
    host=host,
    port=int(port) if port else 3306,
    database=db_name
)

# Cria o engine com o pool configurado para evitar timeout
engine = create_engine(
    url_conexao,
    pool_pre_ping=True,
    pool_recycle=1800
)

def gravar_log(mensagem):
    # Formata a data e hora no padrão BR
    timestamp = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    # Salva no arquivo .txt (o 'a' garante que ele não apague o histórico anterior)
    with open("log_execucao.txt", "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {mensagem}\n")

def ler_arquivo_sql(caminho):
    # Função para ler o texto de dentro do seu arquivo .sql
    with open(caminho, 'r', encoding='utf-8') as arquivo:
        return arquivo.read()

def executar_bot():
    diretorio = r'C:\Users\gabriel.silva\VS Code\Dashboard\pages'
    
    # Adicionei a chave "aba" para você controlar qual planilha vai ser atualizada
    tarefas = [
        {"arquivo_sql": "Consult_Aprovadores.sql", "arquivo_saida": "Aprovadores.xlsx", "aba": "Plan1"},
        {"arquivo_sql": "Consult_Roncador.sql", "arquivo_saida": "Roncador.xlsx", "aba": "Plan1"},
        {"arquivo_sql": "Consult_C.Custo.sql", "arquivo_saida": "Aprovadores.xlsx", "aba": "Plan2"},
        {"arquivo_sql": "Consult_Form.sql", "arquivo_saida": "Aprovadores.xlsx", "aba": "Form"}
    ]
    
    gravar_log("--- INICIANDO EXECUÇÃO DO BOT ---")
    
    for tarefa in tarefas:
        arquivo = tarefa['arquivo_saida']
        print(f"Executando consulta para {arquivo}...")
        try:
            query = ler_arquivo_sql(tarefa['arquivo_sql'])
            df = pd.read_sql(query, engine)
            
            caminho_final = os.path.join(diretorio, arquivo)
            nome_da_aba = tarefa['aba']
            
            # Verifica se o arquivo já existe para não dar erro no modo 'a' (append)
            if os.path.exists(caminho_final):
                with pd.ExcelWriter(caminho_final, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
                    df.to_excel(writer, sheet_name=nome_da_aba, index=False)
            else:
                # Se o arquivo não existir, cria ele do zero
                df.to_excel(caminho_final, sheet_name=nome_da_aba, index=False)
            
            msg_sucesso = f"SUCESSO: Aba {nome_da_aba} de {arquivo} atualizada."
            print(msg_sucesso)
            gravar_log(msg_sucesso) # Grava o sucesso no log
            
        except Exception as e:
            msg_erro = f"ERRO: Erro ao processar {arquivo}. Motivo: {e}"
            print(msg_erro)
            gravar_log(msg_erro) # Grava o erro no log

    gravar_log("--- FINALIZANDO EXECUÇÃO DO BOT ---\n")

if __name__ == "__main__":
    executar_bot()