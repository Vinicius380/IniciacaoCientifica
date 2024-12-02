import numpy as np
import streamlit as st
import pandas as pd
import plotly.express as px
from query import *
from datetime import datetime
from streamlit_modal import Modal
from Dashboard.graficos import *

st.set_page_config(
    page_title="Dashboard",  # título da página
    layout="wide",  # ou "wide", se preferir layout mais amplo
    initial_sidebar_state='expanded')

# Consultas iniciais nas duas tabelas do banco
query = """
    SELECT * FROM tb_registro
"""

df = conexao(query)

df['tempo_registro'] = pd.to_datetime(df['tempo_registro'])

df_selecionado = df.copy()   # Cria uma copia do df original.:

# ****************************** MENU LATERAL ******************************

st.sidebar.markdown(f'<h1 style="text-transform: uppercase;">{'Selecione a região para gerar o gráfico'}</h1>', unsafe_allow_html=True)  

# if SP == False and ABC == False:
#     st.sidebar.markdown(f'<p style="font-size:16px;font-weight:bold;background-color:#D3D4CD;display:flex;justify-content:center;padding:10px;border-radius:10px;">{"SELECIONE UMA REGIÃO!"}<p>', unsafe_allow_html=True)
#     #st.sidebar.warning("Selecione uma região!")

def aplicar_filtros(df):
    # Filtro por intervalo de tempo
    if "tempo_registro" in df.columns:
        # Datas mínimas e máximas
        min_data = df["tempo_registro"].min()
        max_data = df["tempo_registro"].max()

        # Campos de data no menu lateral
        data_inicio = st.sidebar.date_input(
            "Data de Início", 
            min_data.date(), 
            min_value=min_data.date(), 
            max_value=max_data.date()
        )
        data_fim = st.sidebar.date_input(
            "Data de Fim", 
            max_data.date(), 
            min_value=min_data.date(), 
            max_value=max_data.date()
        )

        # Converter as datas selecionadas para datetime
        tempo_registro_range = (
            pd.to_datetime(data_inicio),
            pd.to_datetime(data_fim) + pd.DateOffset(days=1) - pd.Timedelta(seconds=1)
        )

        # Filtrar o DataFrame pelo intervalo de tempo
        df = df[
            (df["tempo_registro"] >= tempo_registro_range[0]) &
            (df["tempo_registro"] <= tempo_registro_range[1])
        ]

    # Retorna o DataFrame filtrado
    return df

# **************************** HOME****************************
def Home():
  
    # Título principal
    st.title("Dashboard de Monitoramento")

    
    button1 = st.columns([30])

    with button1: download = st.button('Baixar dados ')
    
    if download:
        df_filtrado.to_csv("dados.csv", index=False)
        st.success("Arquivo baixado com sucesso!")
    

    # Linha visível de delimitação
    st.markdown(
        """
        <hr style="
            border: none; 
            border-top: 2px solid #3E5050; /* Define a cor da linha */
            margin-top: 10px;             /* Espaçamento acima da linha */
            margin-bottom: 20px;          /* Espaçamento abaixo da linha */
        ">
        """,
        unsafe_allow_html=True
    )   

# ****************************MEDIAS****************************

    # Verifique se o DataFrame selecionado não está vazio
    if df_selecionado.empty:
        st.warning("Nenhum dado disponível para calcular as médias.")

    # Cálculo das médias
    media_umidade = df_selecionado["umidade"].mean()
    media_temperatura = df_selecionado["temperatura"].mean()
    media_co2 = df_selecionado["co2"].mean()

    # Layout em colunas para exibir as métricas
    col1, col2, col3 = st.columns(3)

    # Estilo personalizado para as caixas
    caixa_estilo = """
    <div style="
        background-color: #D3D4CD;
        border-radius: 10px;
        padding: 5px;
        box-shadow: 2px 2px 5px rgba(0, 0, 0, 0.1);
        text-align: center;
    ">
        <h3 style="color: #215132; margin-bottom: 10px;">{titulo}</h3>
        <p style="font-size: 23px; font-weight: bold; margin: 0;">{valor}</p>
    </div>
    """


    # Exibição das caixas em cada coluna
    with col1:
        st.markdown(
            caixa_estilo.format(
                titulo="Média de Umidade", valor=f"{media_umidade:.2f}%"
            ),
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            caixa_estilo.format(
                titulo="Média de Temperatura", valor=f"{media_temperatura:.2f}°C"
            ),
            unsafe_allow_html=True,
        )

    with col3:
        st.markdown(
            caixa_estilo.format(
                titulo="Média de CO2", valor=f"{media_co2:.2f} ppm"
            ),
            unsafe_allow_html=True,
        )
        
    st.markdown("<div style='height: 30px;'></div>", unsafe_allow_html=True)

# **************************** PLOTANDO GRÁFICOS ****************************
def graficos(df):
    # Verifica se há dados no DataFrame
    if df.empty:
        st.warning("Nenhum dado disponível para os filtros aplicados.")
        return

    # Criação das abas para cada gráfico
    aba_barras, aba_linhas, aba_dispersao, aba_area, aba_barras_empilhadas = st.tabs(
        ["Gráfico de Barras", "Gráfico de Linhas", "Gráfico de Dispersão", "Gráfico de Área", "Barras Empilhadas"]
    )

    # Gráfico de Barras
    with aba_barras:
        st.subheader("Gráfico de Barras")
        grafico_barras(df)

    # Gráfico de Linhas
    with aba_linhas:
        st.subheader("Gráfico de Linhas")
        grafico_linhas(df)

    # Gráfico de Dispersão
    with aba_dispersao:
        st.subheader("Gráfico de Dispersão")
        grafico_dispersao(df)

    # Gráfico de Área
    with aba_area:
        st.subheader("Gráfico de Área")
        grafico_area(df)

    # Gráfico de Barras Empilhadas
    with aba_barras_empilhadas:
        st.subheader("Gráfico de Barras Empilhadas")
        grafico_barras_empilhadas(df)


# **************************** CHAMANDO A FUNÇÃO ****************************

df_filtrado = aplicar_filtros(df)

Home()
if df_filtrado.empty:
    st.warning("Nenhum dado encontrado para os filtros selecionados!")
else:
    graficos(df_filtrado)
    rodape_html = """
    <style>
    footer {
        position: relative; /* Permite que o rodapé seja colocado após o conteúdo */
        bottom: 0;
        width: 100%;
        text-align: center;
        padding: 10px 0;
        font-size: 14px;
        color: #333;
        
    }
    </style>
    <footer>
        <p>Copyright © 2024 - Todos os direitos reservados - Equipe Lagartixa</p>
    </footer>
    """
    st.markdown(rodape_html, unsafe_allow_html=True)