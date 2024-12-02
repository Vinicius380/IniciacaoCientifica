import numpy as np
import streamlit as st
import pandas as pd
import plotly.express as px
from query import *
from datetime import datetime
from streamlit_modal import Modal
import scipy.stats as stats
import plotly.graph_objects as go

def grafico_barras(df_selecionado):
    with st.expander("Selecione os eixos"): 
        colunaX = st.selectbox(
            "Eixo X",
            options=["tempo_registro"],
            index=0,
            key='eixox_barras'
        )

        colunaY = st.selectbox(
            "Eixo Y",
            options=["umidade", "temperatura", "pressao", "altitude", "co2", "poeira"],
            index=1,
            key='eixoy_barras'
        )

    if colunaX == colunaY:
        st.warning("Selecione uma opção diferente para os eixos X e Y")
        return

    with st.expander("Configuração de intervalo"):
        intervalo = st.selectbox(
            "Escolha o intervalo para calcular a média",
            options=["15Min", "30Min", "1H", "6H", "1D"],
            index=2,
            key="intervalo_barras"
        )

    try:
        # Agrupar e calcular a média por intervalo
        df_selecionado['tempo_registro'] = pd.to_datetime(df_selecionado['tempo_registro'])
        df_selecionado['tempo_alinhado'] = df_selecionado['tempo_registro'].dt.floor(intervalo)
        df_agrupado = df_selecionado.groupby(['regiao', 'tempo_alinhado'])[colunaY].mean().reset_index()

        # Gráfico de Barras
        cores_personalizadas = {'São Paulo': '#455354', 'Grande ABC': '#77A074'}
        fig_barras = px.bar(
            df_agrupado,
            x='tempo_alinhado',
            y=colunaY,
            color="regiao",
            title=f"Gráfico de Barras (Médias): {colunaX.capitalize()} vs {colunaY.capitalize()}",
            color_discrete_map=cores_personalizadas,
            template="plotly_white"
        )
        
       # Personalização de layout: rótulos, legenda e marcações
        fig_barras.update_layout(
            xaxis=dict(
                title=dict(text="Tempo de Registro", font=dict(color="#0D0D0D", size=14)),  # Rótulo eixo X
                tickfont=dict(color="#0D0D0D", size=12)  # Cor e tamanho dos valores eixo X
            ),
            yaxis=dict(
                title=dict(text=colunaY.capitalize(), font=dict(color="#0D0D0D", size=14)),  # Rótulo eixo Y
                tickfont=dict(color="#0D0D0D", size=12)  # Cor e tamanho dos valores eixo Y
            ),
            legend=dict(
                title=dict(text="Região", font=dict(color="#0D0D0D", size=14)),  # Título da legenda
                font=dict(color="#0D0D0D", size=12)  # Texto da legenda
            )
        )
        st.plotly_chart(fig_barras, use_container_width=True)

    except Exception as e:
        st.error(f"Erro ao criar gráfico de barras: {e}")
    
def grafico_linhas(df_selecionado):
    with st.expander("Selecione os eixos"):
        colunaX = st.selectbox(
            "Eixo X",
            options=["tempo_registro"],
            index=0,
            key='eixox_linhas'
        )

        colunaY = st.selectbox(
            "Eixo Y",
            options=["umidade", "temperatura", "pressao", "co2", "poeira"],
            index=1,
            key='eixoy_linhas'
        )
    
    if colunaX == colunaY:
        st.warning("Selecione uma opção diferente para os eixos X e Y")
        return
    
    # Seleção de intervalo de agrupamento
    with st.expander("Configuração de intervalo"):
        intervalo = st.selectbox(
            "Escolha o intervalo para calcular a média",
            options=["15Min", "30Min", "1H", "6H", "1D"],
            index=2,  # Default: 1 hora
            key="intervalo_medio"
        )

    try:
        # Converter a coluna de tempo para datetime
        df_selecionado['tempo_registro'] = pd.to_datetime(df_selecionado['tempo_registro'])
        
        # Agrupar por região e intervalo de tempo, calculando a média
        df_selecionado['tempo_alinhado'] = df_selecionado['tempo_registro'].dt.floor(intervalo)
        df_agrupado = df_selecionado.groupby(['regiao', 'tempo_alinhado'])[colunaY].mean().reset_index()

        # Gráfico com Plotly
        cores_personalizadas = {'São Paulo': '#455354', 'Grande ABC': '#77A074'}          
        fig_valores2 = px.line(
            df_agrupado,
            x='tempo_alinhado',
            y=colunaY,
            color="regiao",
            title=f"Gráfico de Linhas (Médias): {colunaX.capitalize()} vs {colunaY.capitalize()}",
            color_discrete_map=cores_personalizadas,
            line_shape='linear', 
            markers=True  # Mostrar marcadores nos pontos
        )
        
        # Configuração do layout do gráfico
        fig_valores2.update_layout(
            xaxis_title='Tempo (Intervalos Alinhados)',
            yaxis_title=f'{colunaY.capitalize()} Média',
            template='plotly_white'
        )
        
        # Configuração do layout do gráfico
        fig_valores2.update_layout(
            xaxis=dict(
                title=dict(text='Tempo (Intervalos Alinhados)', font=dict(color="#0D0D0D", size=14)),  # Rótulo eixo X
                tickfont=dict(color="#0D0D0D", size=12)  # Cor e tamanho dos valores eixo X
            ),
            yaxis=dict(
                title=dict(text=f'{colunaY.capitalize()} Média', font=dict(color="#0D0D0D", size=14)),  # Rótulo eixo Y
                tickfont=dict(color="#0D0D0D", size=12)  # Cor e tamanho dos valores eixo Y
            ),
            legend=dict(
                title=dict(text="Região", font=dict(color="#0D0D0D", size=14)),  # Título da legenda
                font=dict(color="#0D0D0D", size=12)  # Texto da legenda
            ),
            title=dict(
                font=dict(color="#0D0D0D", size=16)  # Cor e tamanho do título do gráfico
            ),
            template='plotly_white'
        )
        
    except Exception as e:
        st.error(f"Erro ao criar gráfico de linhas: {e}")
        return
    
    # Exibir gráfico no Streamlit
    st.plotly_chart(fig_valores2, use_container_width=True)
    
def grafico_dispersao(df_selecionado):
    with st.expander("Selecione os eixos"):
        colunaX = st.selectbox(
            "Eixo X",
            options=["tempo_registro", "umidade", "temperatura", "pressao", "altitude", "co2", "poeira"],
            index=0,
            key='eixox_dispersao'
        )

        colunaY = st.selectbox(
            "Eixo Y",
            options=["umidade", "temperatura", "pressao", "altitude", "co2", "poeira"],
            index=1,
            key='eixoy_dispersao'
        )

    if colunaX == colunaY:
        st.warning("Selecione uma opção diferente para os eixos X e Y")
        return

    try:
        
        # Se a coluna X for 'tempo_registro', converta para um valor numérico (exemplo: número de dias)
        if colunaX == "tempo_registro":
            df_selecionado[colunaX] = (df_selecionado[colunaX] - df_selecionado[colunaX].min()).dt.total_seconds() / (60 * 60 * 24)  # dias
        # Se a coluna Y for 'tempo_registro', converta para um valor numérico (exemplo: número de dias)
        if colunaY == "tempo_registro":
            df_selecionado[colunaY] = (df_selecionado[colunaY] - df_selecionado[colunaY].min()).dt.total_seconds() / (60 * 60 * 24)  # dias      
        
        # Calcula a regressão linear
        x = df_selecionado[colunaX]
        y = df_selecionado[colunaY]
        
        # Realiza a regressão linear usando scipy
        slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
        
        # Calcula a linha de regressão (y = mx + b)
        linha_regressao = slope * x + intercept
             
        cores_personalizadas = {'São Paulo': '#455354', 'Grande ABC': '#77A074'}
        fig_dispersao = px.scatter(
            df_selecionado,
            x=colunaX,
            y=colunaY,
            color="regiao",
            title=f"Gráfico de Dispersão: {colunaX.capitalize()} vs {colunaY.capitalize()}",
            color_discrete_map=cores_personalizadas,
            template="plotly_white"
        )
        
        # Adiciona a linha de regressão ao gráfico
        fig_dispersao.add_trace(
            go.Scatter(
                x=x,
                y=linha_regressao,
                mode='lines',
                name=f"Regressão Linear",
                line=dict(color='red', dash='dash')
            )
        )
         # Configurações do layout do gráfico
        fig_dispersao.update_layout(
            xaxis=dict(
                title=dict(text=colunaX.capitalize(), font=dict(color="#0D0D0D", size=14)),  # Rótulo eixo X
                tickfont=dict(color="#0D0D0D", size=12)  # Cor e tamanho dos valores eixo X
            ),
            yaxis=dict(
                title=dict(text=colunaY.capitalize(), font=dict(color="#0D0D0D", size=14)),  # Rótulo eixo Y
                tickfont=dict(color="#0D0D0D", size=12)  # Cor e tamanho dos valores eixo Y
            ),
            legend=dict(
                title=dict(text="Região", font=dict(color="#0D0D0D", size=14)),  # Título da legenda
                font=dict(color="#0D0D0D", size=12)  # Texto da legenda
            ),
            title=dict(
                font=dict(color="#0D0D0D", size=16)  # Cor e tamanho do título do gráfico
            )
        )
        
        st.plotly_chart(fig_dispersao, use_container_width=True)

    except Exception as e:
        st.error(f"Erro ao criar gráfico de dispersão: {e}")
        
def grafico_area(df_selecionado):
    with st.expander("Selecione os eixos"):
        colunaX = st.selectbox(
            "Eixo X",
            options=["tempo_registro"],
            index=0,
            key='eixox_area'
        )

        colunaY = st.selectbox(
            "Eixo Y",
            options=["umidade", "temperatura", "pressao", "altitude", "co2", "poeira"],
            index=1,
            key='eixoy_area'
        )

    if colunaX == colunaY:
        st.warning("Selecione uma opção diferente para os eixos X e Y")
        return

    with st.expander("Configuração de intervalo"):
        intervalo = st.selectbox(
            "Escolha o intervalo para calcular a soma",
            options=["15Min", "30Min", "1H", "6H", "1D"],
            index=2,
            key="intervalo_area"
        )

    try:
        df_selecionado['tempo_registro'] = pd.to_datetime(df_selecionado['tempo_registro'])
        df_selecionado['tempo_alinhado'] = df_selecionado['tempo_registro'].dt.floor(intervalo)
        df_agrupado = df_selecionado.groupby(['tempo_alinhado', 'regiao'])[colunaY].sum().reset_index()

        # Gráfico de Área
        cores_personalizadas = {'São Paulo': '#455354', 'Grande ABC': '#77A074'}
        fig_area = px.area(
            df_agrupado,
            x='tempo_alinhado',
            y=colunaY,
            color="regiao",
            title=f"Gráfico de Área (Somas): {colunaX.capitalize()} vs {colunaY.capitalize()}",
            color_discrete_map=cores_personalizadas,
            template="plotly_white"
        )
        
        # Ajustes de layout
        fig_area.update_layout(
            xaxis=dict(
                title=dict(text='Tempo (Intervalos Alinhados)', font=dict(color="#0D0D0D", size=14)),
                tickfont=dict(color="#0D0D0D", size=12)
            ),
            yaxis=dict(
                title=dict(text=f'{colunaY.capitalize()} (Soma)', font=dict(color="#0D0D0D", size=14)),
                tickfont=dict(color="#0D0D0D", size=12)
            ),
            legend=dict(
                title=dict(text="Região", font=dict(color="#0D0D0D", size=14)),
                font=dict(color="#0D0D0D", size=12)
            ),
            title=dict(
                font=dict(color="#0D0D0D", size=16)
            )
        )
        st.plotly_chart(fig_area, use_container_width=True)

    except Exception as e:
        st.error(f"Erro ao criar gráfico de área: {e}")
        
def grafico_barras_empilhadas(df_selecionado):
    with st.expander("Selecione os eixos"):
        colunaX = st.selectbox(
            "Eixo X",
            options=["tempo_registro", "umidade", "temperatura", "pressao", "altitude", "co2", "poeira"],
            index=0,
            key='eixox_empilhadas'
        )

        colunaY = st.selectbox(
            "Eixo Y",
            options=["umidade", "temperatura", "pressao", "altitude", "co2", "poeira"],
            index=1,
            key='eixoy_empilhadas'
        )

    if colunaX == colunaY:
        st.warning("Selecione uma opção diferente para os eixos X e Y")
        return

    with st.expander("Configuração de intervalo"):
        intervalo = st.selectbox(
            "Escolha o intervalo para calcular a soma",
            options=["15Min", "30Min", "1H", "6H", "1D"],
            index=2,
            key="intervalo_empilhadas"
        )

    try:
        df_selecionado['tempo_registro'] = pd.to_datetime(df_selecionado['tempo_registro'])
        df_selecionado['tempo_alinhado'] = df_selecionado['tempo_registro'].dt.floor(intervalo)
        df_agrupado = df_selecionado.groupby(['tempo_alinhado', 'regiao'])[colunaY].sum().reset_index()

        # Gráfico de Barras Empilhadas
        cores_personalizadas = {'São Paulo': '#455354', 'Grande ABC': '#77A074'}
        fig_empilhadas = px.bar(
            df_agrupado,
            x='tempo_alinhado',
            y=colunaY,
            color="regiao",
            barmode='stack',
            title=f"Gráfico de Barras Empilhadas (Somas): {colunaX.capitalize()} vs {colunaY.capitalize()}",
            color_discrete_map=cores_personalizadas,
            template="plotly_white"
        )
    
    # Ajustes de layout
        fig_empilhadas.update_layout(
            xaxis=dict(
                title=dict(text='Tempo (Intervalos Alinhados)', font=dict(color="#0D0D0D", size=14)),
                tickfont=dict(color="#0D0D0D", size=12)
            ),
            yaxis=dict(
                title=dict(text=f'{colunaY.capitalize()} (Soma)', font=dict(color="#0D0D0D", size=14)),
                tickfont=dict(color="#0D0D0D", size=12)
            ),
            legend=dict(
                title=dict(text="Região", font=dict(color="#0D0D0D", size=14)),
                font=dict(color="#0D0D0D", size=12)
            ),
            title=dict(
                font=dict(color="#0D0D0D", size=16)
            )
        )

        st.plotly_chart(fig_empilhadas, use_container_width=True)

    except Exception as e:
        st.error(f"Erro ao criar gráfico de barras empilhadas: {e}")