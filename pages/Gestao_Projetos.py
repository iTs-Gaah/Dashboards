import streamlit as st
import pandas as pd
import plotly.express as px

def obter_emoji_status(status):
    if status == 'Concluído':
        return '🟢'
    elif status == 'A iniciar':
        return '🟣'
    elif status == 'Em andamento':
        return '🟡'
    elif status in ['Atrasado', 'Atraso']:
        return '🔴'
    return '⚪'

def limpar_filtros():
    st.session_state.projeto_filtro = "Todos"
    st.session_state.status_filtro = "Todos"
    st.session_state.busca_filtro = ""

def renderizar_dashboard():
    st.set_page_config(page_title="Gestão de Projetos", layout="wide")
    
    if "projeto_filtro" not in st.session_state:
        st.session_state.projeto_filtro = "Todos"
    if "status_filtro" not in st.session_state:
        st.session_state.status_filtro = "Todos"
    if "busca_filtro" not in st.session_state:
        st.session_state.busca_filtro = ""

    st.markdown("""
    <style>
        .main-title {
            color: #E0E0E0;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            padding: 0.5rem 0rem;
            font-weight: 800;
            text-align: center;
        }
        .st-container {
            border-radius: 10px;
            padding: 1.5rem;
            box-shadow: 0 4px 6px rgba(0,0,0,0.3);
            color: white;
            margin-bottom: 1rem;
            position: relative;
        }
        .card-title { font-size: 1.1rem; font-weight: bold; margin-bottom: 0.5rem; }
        .card-value { font-size: 2.5rem; font-weight: bold; }
        .card-icon { font-size: 2.5rem; position: absolute; top: 1.2rem; right: 1.5rem; opacity: 0.4; }
        .card-progress { height: 6px; background-color: rgba(255,255,255,0.3); border-radius: 3px; overflow: hidden; margin-top: 10px;}
        .card-progress-bar { height: 100%; border-radius: 3px; }

        .card-total { background-color: #2F80ED; } 
        .card-total-bar { background-color: #56CCF2; }
        .card-completed { background-color: #27AE60; } 
        .card-completed-bar { background-color: #6FCF97; }
        .card-progressing { background-color: #8E44AD; } 
        .card-progressing-bar { background-color: #9B59B6; }
        .card-overdue { background-color: #E74C3C; } 
        .card-overdue-bar { background-color: #F1948A; }
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<h1 class="main-title">📊 Visão Geral de Projetos (Teams)</h1>', unsafe_allow_html=True)

    arquivo_limpo = 'Projetos_Estruturados_Streamlit.xlsx'

    try:
        df = pd.read_excel(arquivo_limpo)
        
        if 'Data_Extracao' in df.columns:
            df['Data_Extracao'] = pd.to_datetime(df['Data_Extracao'], dayfirst=True, errors='coerce')
            datas_recentes = df.groupby('Projeto')['Data_Extracao'].transform('max')
            df = df[df['Data_Extracao'] == datas_recentes]

        if 'Status_Projeto' not in df.columns:
            df['Status_Projeto'] = 'Em andamento'
        if 'Ultima_Mensagem' not in df.columns:
            df['Ultima_Mensagem'] = 'Dados não disponíveis'

        # CÁLCULO DE INATIVIDADE CORRIGIDO: Usando a Data_Ultima_Mensagem
        if 'Data_Ultima_Mensagem' in df.columns:
            df['data_calc_msg'] = pd.to_datetime(df['Data_Ultima_Mensagem'], format='%d/%m/%Y', errors='coerce')
            
            hoje = pd.Timestamp.today().normalize()
            datas_maximas_msg = df.groupby('Projeto')['data_calc_msg'].transform('max')
            
            df['Dias_Sem_Andamento'] = (hoje - datas_maximas_msg).dt.days
            df['Dias_Sem_Andamento'] = df['Dias_Sem_Andamento'].fillna(0).astype(int)
        elif 'Dias_Sem_Andamento' not in df.columns:
            df['Dias_Sem_Andamento'] = 0

        st.markdown("---")
        col_filt1, col_filt2, col_filt3, col_btn = st.columns([3, 3, 3, 1])
        
        projetos_unicos = ["Todos"] + list(df['Projeto'].unique())
        projeto_selecionado = col_filt1.selectbox("Filtrar por Projeto", projetos_unicos, key="projeto_filtro")
        
        status_unicos = ["Todos"] + list(df['Status_Projeto'].unique())
        status_selecionado = col_filt2.selectbox("Filtrar por Status do Projeto", status_unicos, key="status_filtro")

        termo_busca = col_filt3.text_input("Pesquisar Projeto (Texto Livre)", key="busca_filtro")

        col_btn.markdown("<br>", unsafe_allow_html=True)
        col_btn.button("Limpar Filtros", on_click=limpar_filtros, width='stretch')

        df_filtrado = df.copy()
        
        if projeto_selecionado != "Todos":
            df_filtrado = df_filtrado[df_filtrado['Projeto'] == projeto_selecionado]
        if status_selecionado != "Todos":
            df_filtrado = df_filtrado[df_filtrado['Status_Projeto'] == status_selecionado]
        if termo_busca:
            df_filtrado = df_filtrado[df_filtrado['Projeto'].str.contains(termo_busca, case=False, na=False)]

        if df_filtrado.empty:
            st.warning("Nenhum dado encontrado para os filtros selecionados.")
            return

        projetos_filtrados = df_filtrado['Projeto'].unique()
        df_projetos_unicos = df_filtrado.drop_duplicates(subset=['Projeto'])

        # REGRA DOS 30 DIAS APLICADA AQUI
        projetos_inativos = df_projetos_unicos[(df_projetos_unicos['Dias_Sem_Andamento'] > 30) & (df_projetos_unicos['Status_Projeto'] != 'Concluído')]
        
        if not projetos_inativos.empty:
            with st.expander(f"🚨 ALERTA: {len(projetos_inativos)} Projetos sem movimentação no chat há mais de 30 dias"):
                for _, row in projetos_inativos.iterrows():
                    st.markdown(f"- **{row['Projeto']}** | Inativo há **{row['Dias_Sem_Andamento']} dias** (Última msg: {row.get('Data_Ultima_Mensagem', 'Desconhecida')})")
        
        st.write("") 
        
        c1, c2, c3, c4 = st.columns(4)
        
        total_projetos = len(projetos_filtrados)
        qtd_concluidos = len(df_projetos_unicos[df_projetos_unicos['Status_Projeto'] == 'Concluído'])
        qtd_andamento = len(df_projetos_unicos[df_projetos_unicos['Status_Projeto'] == 'Em andamento'])
        qtd_atrasados = len(df_projetos_unicos[df_projetos_unicos['Status_Projeto'].isin(['Atrasado', 'Atraso'])])

        prog_concluidos = int((qtd_concluidos / total_projetos) * 100) if total_projetos > 0 else 0
        prog_andamento = int((qtd_andamento / total_projetos) * 100) if total_projetos > 0 else 0
        prog_atrasados = int((qtd_atrasados / total_projetos) * 100) if total_projetos > 0 else 0

        with c1:
            st.markdown(f'''
            <div class="st-container card-total">
                <div class="card-icon">📁</div>
                <div class="card-title">Total de Projetos</div>
                <div class="card-value">{total_projetos}</div>
                <div class="card-progress"><div class="card-progress-bar card-total-bar" style="width: 100%;"></div></div>
            </div>
            ''', unsafe_allow_html=True)

        with c2:
            st.markdown(f'''
            <div class="st-container card-completed">
                <div class="card-icon">✅</div>
                <div class="card-title">Concluídos</div>
                <div class="card-value">{qtd_concluidos}</div>
                <div class="card-progress"><div class="card-progress-bar card-completed-bar" style="width: {prog_concluidos}%;"></div></div>
            </div>
            ''', unsafe_allow_html=True)

        with c3:
            st.markdown(f'''
            <div class="st-container card-progressing">
                <div class="card-icon">⚙️</div>
                <div class="card-title">Em Andamento</div>
                <div class="card-value">{qtd_andamento}</div>
                <div class="card-progress"><div class="card-progress-bar card-progressing-bar" style="width: {prog_andamento}%;"></div></div>
            </div>
            ''', unsafe_allow_html=True)

        with c4:
            st.markdown(f'''
            <div class="st-container card-overdue">
                <div class="card-icon">⚠️</div>
                <div class="card-title">Atrasados</div>
                <div class="card-value">{qtd_atrasados}</div>
                <div class="card-progress"><div class="card-progress-bar card-overdue-bar" style="width: {prog_atrasados}%;"></div></div>
            </div>
            ''', unsafe_allow_html=True)

        st.divider()

        col_grafico, col_detalhes = st.columns([1, 2])
        
        with col_grafico:
            st.markdown("### 📊 Tarefas por Status")
            if 'status' in df_filtrado.columns:
                contagem_status = df_filtrado['status'].value_counts().reset_index()
                contagem_status.columns = ['Status', 'Quantidade']
                
                cores = {
                    'Concluído': '#27AE60', 
                    'Pendente': '#2F80ED', 
                    'Atrasado': '#FF4500', 
                    'Atraso': '#FF4500', 
                    'Em andamento': '#D4AC0D', 
                    'A iniciar': '#8E44AD'
                }
                
                fig = px.pie(contagem_status, names='Status', values='Quantidade', hole=0.5, color='Status', color_discrete_map=cores)
                fig.update_layout(margin=dict(t=20, b=20, l=0, r=0), showlegend=True, legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5))
                st.plotly_chart(fig, width='stretch')
            else:
                st.write("Coluna de status de tarefas não encontrada.")

        with col_detalhes:
            st.markdown("### 📋 Detalhamento dos Projetos")
            for proj in projetos_filtrados:
                df_proj = df_filtrado[df_filtrado['Projeto'] == proj]
                
                status_macro = df_proj['Status_Projeto'].iloc[0]
                dias_inativo = df_proj['Dias_Sem_Andamento'].iloc[0]
                emoji = obter_emoji_status(status_macro)
                
                indicador_inatividade = " ⏳" if dias_inativo > 30 and status_macro != 'Concluído' else ""
                
                with st.expander(f"{emoji} {proj} - {status_macro}{indicador_inatividade}"):
                    
                    if dias_inativo > 30 and status_macro != 'Concluído':
                        st.markdown(
                            f'<div style="margin-bottom: 15px;">'
                            f'<span title="Projeto sem movimento há {dias_inativo} dias" style="cursor: help; font-size: 1.5rem;">⚠️</span>'
                            f'<span style="margin-left: 10px; color: #E74C3C; font-weight: bold;">Inativo há {dias_inativo} dias</span>'
                            f'</div>',
                            unsafe_allow_html=True
                        )

                    if 'Resumo_Projeto' in df_proj.columns:
                        resumo = df_proj['Resumo_Projeto'].iloc[0]
                        st.info(f"**Resumo do Andamento:** {resumo}")

                    col_resumo1, col_resumo2 = st.columns(2)
                    col_resumo1.write(f"**Total de etapas:** {len(df_proj)}")
                    if 'status' in df_proj.columns:
                        col_resumo2.write(f"**Concluídas:** {len(df_proj[df_proj['status'] == 'Concluído'])}")
                    
                    # Colunas de auditoria adicionadas aqui para o cara-crachá aparecer na tabela
                    colunas_exibir = ['origem', 'data_solicitacao', 'tarefa', 'status', 'prazo', 'responsavel', 'divergencia_encontrada', 'detalhe_divergencia']
                    colunas_disponiveis = [col for col in colunas_exibir if col in df_proj.columns]
                    
                    if colunas_disponiveis:
                        st.dataframe(
                            df_proj[colunas_disponiveis], 
                            width='stretch', 
                            hide_index=True
                        )

    except FileNotFoundError:
        st.warning("O arquivo de dados estruturados ainda não foi gerado pelo script de extração.")
    except Exception as e:
        st.error(f"Erro ao carregar o dashboard: {e}")

if __name__ == "__main__":
    renderizar_dashboard()