import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import pymysql
from scipy.stats import linregress

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
        
        
# Funções de gráficos
def grafico_combinado(df_temp, df_co, intervalo, titulo):
    try:
        # Alinhar ambos os datasets por intervalo
        df_temp['tempo_alinhado'] = pd.to_datetime(df_temp['tempo_registro']).dt.floor(intervalo)
        df_co['tempo_alinhado'] = pd.to_datetime(df_co['tempo_registro']).dt.floor(intervalo)

        # Agregar dados
        df_temp_agg = df_temp.groupby(['tempo_alinhado'])['temperatura_media'].mean().reset_index()
        df_co_agg = df_co.groupby(['tempo_alinhado'])['concentracao_co'].mean().reset_index()

        # Merge dos datasets
        df_combined = pd.merge(df_temp_agg, df_co_agg, on='tempo_alinhado', how='inner')

        # Criar gráfico combinado
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df_combined['tempo_alinhado'], y=df_combined['temperatura_media'],
                                 mode='lines+markers', name='Temperatura Média'))
        fig.add_trace(go.Bar(x=df_combined['tempo_alinhado'], y=df_combined['concentracao_co'],
                             name='Concentração de CO'))

        # Layout do gráfico
        fig.update_layout(
            title=titulo,
            xaxis_title="Tempo (Intervalos Alinhados)",
            yaxis_title="Valores",
            legend_title="Medições",
            barmode='group',
            template='plotly_white'
        )
        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.error(f"Erro ao criar gráfico combinado: {e}")

def grafico_sintomas_relacionados(df_temp, df_co, df_sintomas, intervalo, titulo):
    try:
        # Alinhar datasets por intervalo
        df_temp['tempo_alinhado'] = pd.to_datetime(df_temp['tempo_registro']).dt.floor(intervalo)
        df_co['tempo_alinhado'] = pd.to_datetime(df_co['tempo_registro']).dt.floor(intervalo)
        df_sintomas['tempo_alinhado'] = pd.to_datetime(df_sintomas['tempo_registro']).dt.floor(intervalo)

        # Agregar dados
        df_temp_agg = df_temp.groupby(['tempo_alinhado'])['temperatura_media'].mean().reset_index()
        df_co_agg = df_co.groupby(['tempo_alinhado'])['concentracao_co'].mean().reset_index()
        df_sintomas_agg = df_sintomas.groupby(['tempo_alinhado'])['sintomas'].count().reset_index()
        df_sintomas_agg.rename(columns={'sintomas': 'frequencia_sintomas'}, inplace=True)

        # Merge dos datasets
        df_combined = pd.merge(df_temp_agg, df_co_agg, on='tempo_alinhado', how='inner')
        df_combined = pd.merge(df_combined, df_sintomas_agg, on='tempo_alinhado', how='inner')

        # Criar gráfico
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df_combined['tempo_alinhado'], y=df_combined['temperatura_media'],
                                 mode='lines+markers', name='Temperatura Média'))
        fig.add_trace(go.Bar(x=df_combined['tempo_alinhado'], y=df_combined['concentracao_co'],
                             name='Concentração de CO'))
        fig.add_trace(go.Scatter(x=df_combined['tempo_alinhado'], y=df_combined['frequencia_sintomas'],
                                 mode='markers', name='Frequência de Sintomas'))

        # Layout do gráfico
        fig.update_layout(
            title=titulo,
            xaxis_title="Tempo (Intervalos Alinhados)",
            yaxis_title="Valores",
            legend_title="Medições",
            barmode='group',
            template='plotly_white'
        )
        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.error(f"Erro ao criar gráfico de sintomas relacionados: {e}")