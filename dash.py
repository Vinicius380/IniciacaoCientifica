import numpy as np
import streamlit as st
import pandas as pd
import plotly.express as px
from query import *
from datetime import datetime
from streamlit_modal import Modal
from graficos import *
import seaborn as sns

st.set_page_config(
    page_title="Dashboard",  # título da página
    layout="wide",  # ou "wide", se preferir layout mais amplo
    initial_sidebar_state='expanded')

#Consultas no banco de dados
query_temperatura = """
    SELECT 
    date AS tempo_registro, 
    min AS temperatura_minima, 
    max AS temperatura_maxima, 
    median AS temperatura_media
    FROM dados_temperatura_SP
    WHERE date BETWEEN '2024-11-01' AND '2024-11-30'
    AND median BETWEEN  20 AND 40
  """  
df_temperatura = conexao(query_temperatura)
  
query_poluentes = """
	SELECT tempo_registro, pm25, pm10, o3, no2, so2, co
    FROM dados_poluentes
	WHERE tempo_registro BETWEEN '2024-11-01' AND '2024-12-06'
     """
df_poluentes = conexao(query_poluentes)       

query_co2 = """
  SELECT tempo_registro, co2 
  FROM tb_registro 
  WHERE tempo_registro BETWEEN '2024-11-01' AND '2024-12-06'
    """
df_co2 = conexao(query_co2)  

query_sintomas = """
    SELECT data_notificacao AS tempo_registro, sintomas 
    FROM principais_sintomas
    WHERE data_notificacao BETWEEN '2024-11-01' AND '2024-12-06'
    """
df_sintomas = conexao(query_sintomas)


# Configuração do Dashboard
def dashboard():
    st.title("Clima e Saúde: Monitoramento do Ar")

    # Criação das abas para cada gráfico
    aba_Poluentes, aba_temperatura, aba_sintomas = st.tabs(
        ["Poluentes", "Temperatura", "Distribuição de Sintomas"]
    )

    with aba_Poluentes:
        st.subheader("Poluentes")       

        # Seção para seleção de intervalo de tempo
        intervalo_poluentes = st.selectbox(
            "Intervalo de Agrupamento poluentes", 
            options=["15Min", "30Min", "1H", "6H", "1D"], 
            index=2, 
            key="Poluentes"
        )
        intervalo_co2 = st.selectbox(
            "Intervalo de Agrupamento para CO2", 
            options=["15Min", "30Min", "1H", "6H", "1D"], 
            index=2, 
            key="CO2"
        )
        
        # Função para aplicar o agrupamento de tempo (com base na seleção do usuário)
        def agrupar_por_intervalo(df, coluna_data, intervalo):
            df[coluna_data] = pd.to_datetime(df[coluna_data])
            df.set_index(coluna_data, inplace=True)  # Define a coluna como índice
            agrupado = df.resample(intervalo).mean().reset_index()  # Resample e volta o índice para coluna
            return agrupado
                
        # Aplicar o agrupamento nos dados dos poluentes
        poluentes_agrupados = agrupar_por_intervalo(df_poluentes, 'tempo_registro', intervalo_poluentes)

        # Gerar gráfico de barras para os poluentes, passando o título
        grafico_barras(poluentes_agrupados, "tempo_registro", ["pm25", "pm10", "o3", "no2", "so2", "co"], "Concentração de Poluentes ao Longo do Tempo")
                
        # Gerar gráfico de barras empilhadas para poluentes e CO2 com sintomas (exemplo de como os dados poderiam ser passados)
        grafico_barras_empilhadas(poluentes_agrupados, df_co2, df_sintomas)
        grafico_linhas_2(poluentes_agrupados, df_co2, df_sintomas)


    with aba_temperatura:
        st.subheader("Temperatura")
        
        # Gráfico de linha com preenchimento
        fig = px.area(
            df_temperatura,
            x='tempo_registro',
            y='temperatura_media',
            title="Variação de Temperatura ao Longo do Tempo",
            template='plotly_white'
        )
        st.plotly_chart(fig, use_container_width=True)        
        
        # Gráfico de dispersão temperatura vs CO
        df_merge = pd.merge(df_temperatura, df_poluentes, on="tempo_registro", how="inner")
        grafico_dispersao(df_merge, "temperatura_media", "concentracao_co", "Temperatura vs Concentração de CO")        
    
    with aba_sintomas:
        st.subheader("Distribuição de Sintomas")
 
        # Gráfico de barras horizontais para frequência dos sintomas
        sintomas_freq = df_sintomas['sintomas'].value_counts().reset_index()
        sintomas_freq.columns = ['sintomas', 'frequencia']
        fig = px.bar(
            sintomas_freq, 
            y='sintomas', 
            x='frequencia', 
            orientation='h', 
            title="Frequência dos Sintomas Relatados", 
            template='plotly_white'
        )
        st.plotly_chart(fig, use_container_width=True)
 
        # Gráfico de linha para evolução dos sintomas ao longo do tempo
        df_sintomas_grouped = df_sintomas.groupby(['tempo_registro', 'sintomas']).size().reset_index(name='frequencia')
        fig = px.line(
            df_sintomas_grouped,
            x='tempo_registro',
            y='frequencia',
            color='sintomas',
            title="Evolução de Sintomas ao Longo do Tempo",
            template='plotly_white'
        )
        st.plotly_chart(fig, use_container_width=True)

        correlacionar_temperatura_sintomas(df_temperatura, df_sintomas)
 
if __name__ == "__main__":
    dashboard()