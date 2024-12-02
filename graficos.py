import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import pymysql
from scipy.stats import linregress
import matplotlib.pyplot as plt
import seaborn as sns


# Funções de gráficos
def grafico_barras(df, coluna_x, coluna_y, intervalo, titulo):
    try:
        df['tempo_alinhado'] = pd.to_datetime(df[coluna_x]).dt.floor(intervalo)
        df_agrupado = df.groupby(['tempo_alinhado'])[coluna_y].mean().reset_index()

        fig = px.bar(
            df_agrupado,
            x='tempo_alinhado',
            y=coluna_y,
            title=titulo,
            template='plotly_white'
        )
        fig.update_layout(
            xaxis_title='Tempo',
            yaxis_title=coluna_y.capitalize(),
        )
        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.error(f"Erro ao criar gráfico de barras: {e}")

def grafico_linhas(df, coluna_x, coluna_y, intervalo, titulo):
    try:
        df['tempo_alinhado'] = pd.to_datetime(df[coluna_x]).dt.floor(intervalo)
        df_agrupado = df.groupby(['tempo_alinhado'])[coluna_y].mean().reset_index()

        fig = px.line(
            df_agrupado,
            x='tempo_alinhado',
            y=coluna_y,
            title=titulo,
            template='plotly_white',
            markers=True
        )
        fig.update_layout(
            xaxis_title='Tempo',
            yaxis_title=coluna_y.capitalize(),
        )
        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.error(f"Erro ao criar gráfico de linhas: {e}")

def grafico_dispersao(df, coluna_x, coluna_y, titulo):
    try:
        x = df[coluna_x]
        y = df[coluna_y]
        slope, intercept, r_value, p_value, std_err = linregress(x, y)

        linha_regressao = slope * x + intercept

        fig = px.scatter(
            df,
            x=coluna_x,
            y=coluna_y,
            title=titulo,
            template='plotly_white'
        )
        fig.add_trace(go.Scatter(x=x, y=linha_regressao, mode='lines', name='Regressão Linear', line=dict(color='red', dash='dash')))
        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.error(f"Erro ao criar gráfico de dispersão: {e}")
        
# Função para criar um heatmap
def criar_heatmap(df, coluna_hora, coluna_valor, titulo):
    try:
        df['hora'] = pd.to_datetime(df[coluna_hora]).dt.hour
        heatmap_data = df.groupby('hora')[coluna_valor].mean().reset_index()
        
        fig = px.density_heatmap(
            heatmap_data, 
            x='hora', 
            y=coluna_valor, 
            nbinsx=24, 
            title=titulo,
            template='plotly_white',
            color_continuous_scale='viridis'
        )
        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.error(f"Erro ao criar heatmap: {e}")

# Função para exibir estatísticas básicas
def estatisticas_basicas(df, coluna):
    try:
        # Calculando estatísticas básicas
        min_val = df[coluna].min()
        mean_val = df[coluna].mean()
        max_val = df[coluna].max()

        # Estilo personalizado para as caixas
        caixa_estilo = """
        <div style="
            background-color: #D3D4CD;
            border-radius: 10px;
            padding: 15px;
            box-shadow: 2px 2px 5px rgba(0, 0, 0, 0.1);
            margin-bottom: 10px;
            text-align: center;
        ">
            <h3 style="color: #215132; margin-bottom: 10px;">{titulo}</h3>
            <p style="font-size: 23px; font-weight: bold; margin: 0;">{valor}</p>
        </div>
        """

        # Renderizando caixas de estatísticas
        col1, col2, col3 = st.columns(3)  # Dividindo em 3 colunas
        with col1:
            st.markdown(caixa_estilo.format(titulo="Mínimo ppm", valor=f"{min_val:.2f}"), unsafe_allow_html=True)
        with col2:
            st.markdown(caixa_estilo.format(titulo="Média ppm", valor=f"{mean_val:.2f}"), unsafe_allow_html=True)
        with col3:
            st.markdown(caixa_estilo.format(titulo="Máximo ppm", valor=f"{max_val:.2f}"), unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Erro ao calcular estatísticas: {e}")

def correlacionar_temperatura_sintomas(temperatura_df, sintomas_df):
    try:
        # Exibe as primeiras linhas para depuração
        st.write("Prévia dos dados de temperatura:")
        st.dataframe(temperatura_df.head())
        
        st.write("Prévia dos dados de sintomas:")
        st.dataframe(sintomas_df.head())

        # Verificar colunas de temperatura
        required_temp_columns = {'tempo_registro', 'temperatura_minima', 'temperatura_maxima', 'temperatura_media'}
        if not required_temp_columns.issubset(temperatura_df.columns):
            st.error(f"As colunas necessárias {required_temp_columns} não estão presentes no DataFrame de temperatura.")
            return
        
        # Verificar colunas de sintomas
        if 'tempo_registro' not in sintomas_df.columns or 'sintomas' not in sintomas_df.columns:
            st.error("As colunas 'tempo_registro' e 'sintomas' não estão presentes no DataFrame de sintomas.")
            return

        # Processando dados de temperatura
        temperatura_df['tempo_registro'] = pd.to_datetime(temperatura_df['tempo_registro'])
        temperatura_df = temperatura_df[['tempo_registro', 'temperatura_minima', 'temperatura_maxima', 'temperatura_media']]

        # Processando dados de sintomas
        sintomas_df['tempo_registro'] = pd.to_datetime(sintomas_df['tempo_registro'])
        sintomas_frequencia = (
            sintomas_df.groupby('tempo_registro')
            .size()
            .reset_index(name='frequencia_sintomas')
        )

        # Mesclando datasets
        correlacao_df = pd.merge(
            temperatura_df,
            sintomas_frequencia,
            on='tempo_registro',
            how='inner'
        )

        # Exibindo gráfico de dispersão
        st.subheader("Correlação: Temperatura e Sintomas")
        st.write("Gráfico de dispersão para observar tendências.")

        fig, ax = plt.subplots(figsize=(8, 5))
        sns.scatterplot(
            x=correlacao_df['temperatura_media'],
            y=correlacao_df['frequencia_sintomas'],
            ax=ax,
            color='darkgreen',
        )
        ax.set_xlabel("Temperatura Média (°C)")
        ax.set_ylabel("Frequência de Sintomas")
        ax.set_title("Relação entre Temperatura e Sintomas")
        st.pyplot(fig)

        # Exibindo correlograma (heatmap)
        st.subheader("Correlograma: Matriz de Correlação")
        st.write("A matriz de correlação visualiza a relação entre as variáveis numéricas.")

        corr_matrix = correlacao_df[['temperatura_minima', 'temperatura_maxima', 'temperatura_media', 'frequencia_sintomas']].corr()
        fig, ax = plt.subplots(figsize=(8, 6))
        sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', ax=ax, fmt=".2f")
        st.pyplot(fig)

        # Série temporal: Temperatura e Sintomas ao longo do tempo
        st.subheader("Série Temporal: Sintomas e Temperatura")
        st.write("Acompanhe as variações de temperatura e frequência de sintomas ao longo do tempo.")
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(correlacao_df['tempo_registro'], correlacao_df['frequencia_sintomas'], label="Frequência de Sintomas", color="darkred")
        ax.plot(correlacao_df['tempo_registro'], correlacao_df['temperatura_media'], label="Temperatura Média (°C)", color="blue")
        ax.fill_between(correlacao_df['tempo_registro'], correlacao_df['temperatura_media'], color="blue", alpha=0.2)
        ax.set_xlabel("Data")
        ax.set_ylabel("Valores")
        ax.legend()
        st.pyplot(fig)

    except Exception as e:
        st.error(f"Erro ao gerar correlações: {e}")
