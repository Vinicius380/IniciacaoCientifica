import numpy as np
import streamlit as st
import pandas as pd
import plotly.express as px
from query import *
from datetime import datetime
from streamlit_modal import Modal
from graficos import *

st.set_page_config(
    page_title="Dashboard",  # título da página
    layout="wide",  # ou "wide", se preferir layout mais amplo
    initial_sidebar_state='expanded')

#Consultas no banco de dados
query_temperatura = """
    SELECT date AS tempo_registro, min AS temperatura_minima, max AS temperatura_maxima, median AS temperatura_media 
    FROM dados_temperatura_SP
    """
df_temperatura = conexao(query_temperatura)
  
query_co = """
     SELECT data_da_coleta AS tempo_registro, media_do_horario AS concentracao_co 
    FROM dados_CO
    """
df_co = conexao(query_co)       

query_sintomas = """
    SELECT data_notificacao AS tempo_registro, sintomas 
    FROM principais_sintomas
    """
df_sintomas = conexao(query_sintomas)


# Configuração do Dashboard
def dashboard():
    st.title("Dashboard de Dados Ambientais e Sintomas")

    # Criação das abas para cada gráfico
    aba_barras, aba_linhas, aba_sintomas, aba_combinada = st.tabs(
        ["Gráfico de Barras", "Gráfico de Linhas", "Distribuição de Sintomas", "Gráficos Combinados"]
    )

    # Gráfico de Barras
    with aba_barras:
        st.subheader("Gráfico de Barras")       
        intervalo_co = st.selectbox("Intervalo de Agrupamento para CO", options=["15Min", "30Min", "1H", "6H", "1D"], index=2)
        grafico_barras(df_co, "tempo_registro", "concentracao_co", intervalo_co, "Concentração de CO ao Longo do Tempo")
        

    # Gráfico de Linhas
    with aba_linhas:
        st.subheader("Gráfico de Linhas")
        intervalo_temp = st.selectbox("Intervalo de Agrupamento", options=["15Min", "30Min", "1H", "6H", "1D"], index=2)
        grafico_linhas(df_temperatura, "tempo_registro", "temperatura_media", intervalo_temp, "Temperatura Média ao Longo do Tempo")
    
    # Gráfico de Sintomas
    with aba_sintomas:
        st.subheader("Distribuição de Sintomas")
        sintomas_contagem = df_sintomas["sintomas"].value_counts().reset_index()
        sintomas_contagem.columns = ["sintomas", "frequencia"]
        fig_sintomas = px.bar(
            sintomas_contagem,
            x="sintomas",
            y="frequencia",
            title="Frequência dos Principais Sintomas",
            template="plotly_white"
        )
        st.plotly_chart(fig_sintomas, use_container_width=True)
    
    #Graficos Combinados
    with aba_combinada:
        st.subheader("Gráficos Combinados")
        intervalo = st.selectbox("Intervalo", options=["15Min", "30Min", "1H", "6H", "1D"], index=2)
        grafico_combinado(df_temperatura, df_co,intervalo,"Temperatura vs CO")
        grafico_sintomas_relacionados(df_temperatura, df_co, df_sintomas,intervalo, "Temperatura, CO e Sintomas")

if __name__ == "__main__":
    dashboard()