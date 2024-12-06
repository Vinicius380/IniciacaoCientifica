import numpy as np
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
def grafico_barras(df, coluna_data, colunas, titulo):
    plt.figure(figsize=(12, 6))
    for i, coluna in enumerate(colunas):
        plt.bar(df[coluna_data], df[coluna], label=coluna, alpha=0.7, align='center')
    plt.title(titulo)
    plt.xlabel("Data")
    plt.ylabel("Concentração")
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
    st.pyplot(plt)


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

    except Exception as e:
        st.error(f"Erro ao gerar correlações: {e}")


def grafico_barras_empilhadas(poluentes_df, co2_df, sintomas_df):
    try:
        # Garantir que as colunas de tempo estão em datetime
        poluentes_df['tempo_registro'] = pd.to_datetime(poluentes_df['tempo_registro'], errors='coerce')
        co2_df['tempo_registro'] = pd.to_datetime(co2_df['tempo_registro'], errors='coerce')
        sintomas_df['tempo_registro'] = pd.to_datetime(sintomas_df['tempo_registro'], errors='coerce')

        # Agrupar os dados por dia
        poluentes_aggregated = poluentes_df.groupby(pd.Grouper(key='tempo_registro', freq='D'))[['pm25', 'pm10', 'o3', 'no2', 'so2', 'co']].mean().reset_index()
        co2_aggregated = co2_df.groupby(pd.Grouper(key='tempo_registro', freq='D'))['co2'].mean().reset_index()
        sintomas_aggregated = sintomas_df.groupby(pd.Grouper(key='tempo_registro', freq='D')).size().reset_index(name='frequencia_sintomas')

        # Combinar os dados
        merged_df = pd.merge(poluentes_aggregated, co2_aggregated, on='tempo_registro', how='outer')
        merged_df = pd.merge(merged_df, sintomas_aggregated, on='tempo_registro', how='outer')
        merged_df.fillna(0, inplace=True)

        # Normalizar os dados para o gráfico, excluindo os sintomas
        for col in ['pm25', 'pm10', 'o3', 'no2', 'so2', 'co', 'co2']:
            if merged_df[col].max() > 0:
                merged_df[col] = merged_df[col] / merged_df[col].max()

        # Plotando o gráfico de barras empilhadas usando Matplotlib
        fig, ax = plt.subplots(figsize=(12, 8))

        # Preparar os dados para o gráfico empilhado
        data = merged_df.set_index('tempo_registro')[['pm25', 'pm10', 'o3', 'no2', 'so2', 'co', 'co2', 'frequencia_sintomas']]
        
        # Plotando as barras empilhadas
        data.plot(kind='bar', stacked=True, ax=ax, colormap='tab20', width=0.8, edgecolor='none')

        # Ajustando o título, labels e outros detalhes estéticos
        ax.set_title("Concentração de Poluentes X Sintomas", fontsize=16, fontweight='bold')
        ax.set_xlabel('Data de Registro', fontsize=12)
        ax.set_ylabel('Valor Normalizado', fontsize=12)
        date_labels = data.index.strftime('%d %b %Y')
        ax.set_xticks(range(0, len(date_labels), 3))  # Exibindo uma data a cada 3 dias
        ax.set_xticklabels(date_labels[::3], rotation=45, ha='right', fontsize=10)


        # Ajuste da legenda
        ax.legend(title="Poluentes/Sintomas", bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=10)

        # Melhorar a estética: grid, barra de cores e espaciamento
        ax.grid(True, which='both', axis='y', linestyle='--', linewidth=0.5, alpha=0.7)
        plt.tight_layout()

        # Exibir o gráfico no Streamlit
        st.pyplot(fig)

    except Exception as e:
        st.error(f"Erro ao gerar o gráfico: {e}")

def grafico_linhas_2(poluentes_df, co2_df, sintomas_df):
    try:
        # Garantir que as colunas de tempo estão em datetime
        poluentes_df['tempo_registro'] = pd.to_datetime(poluentes_df['tempo_registro'], errors='coerce')
        co2_df['tempo_registro'] = pd.to_datetime(co2_df['tempo_registro'], errors='coerce')
        sintomas_df['tempo_registro'] = pd.to_datetime(sintomas_df['tempo_registro'], errors='coerce')

        # Agrupar os dados por dia
        poluentes_aggregated = poluentes_df.groupby(pd.Grouper(key='tempo_registro', freq='D'))[['pm25', 'pm10', 'o3', 'no2', 'so2', 'co']].mean().reset_index()
        co2_aggregated = co2_df.groupby(pd.Grouper(key='tempo_registro', freq='D'))['co2'].mean().reset_index()
        sintomas_aggregated = sintomas_df.groupby(pd.Grouper(key='tempo_registro', freq='D')).size().reset_index(name='frequencia_sintomas')

        # Combinar os dados
        merged_df = pd.merge(poluentes_aggregated, co2_aggregated, on='tempo_registro', how='outer')
        merged_df = pd.merge(merged_df, sintomas_aggregated, on='tempo_registro', how='outer')
        merged_df.fillna(0, inplace=True)

        # Normalizar os dados para o gráfico
        for col in ['pm25', 'pm10', 'o3', 'no2', 'so2', 'co', 'co2', 'frequencia_sintomas']:
            if merged_df[col].max() > 0:
                merged_df[col] = merged_df[col] / merged_df[col].max()

        # Transformar os dados para formato longo (necessário para Plotly Express)
        long_df = merged_df.melt(
            id_vars='tempo_registro',
            value_vars=['pm25', 'pm10', 'o3', 'no2', 'so2', 'co', 'co2', 'frequencia_sintomas'],
            var_name='Poluente/Sintoma',
            value_name='Valor Normalizado'
        )

        # Criar o gráfico de linhas com Plotly
        fig = px.line(
            long_df,
            x='tempo_registro',
            y='Valor Normalizado',
            color='Poluente/Sintoma',
            title="Concentração de Poluentes e Sintomas ao Longo do Tempo (Normalizado)",
            labels={'tempo_registro': 'Tempo de Registro', 'Valor Normalizado': 'Valor'},
            template='plotly_white'
        )

        fig.update_layout(
            xaxis=dict(title='Tempo de Registro'),
            yaxis=dict(title='Valores Normalizados'),
            legend=dict(title='Poluente/Sintoma'),
            hovermode="x unified"  # Exibe os valores de cada linha quando o cursor passar por cima
        )

        # Exibir o gráfico no Streamlit
        st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(f"Erro ao gerar o gráfico: {e}")