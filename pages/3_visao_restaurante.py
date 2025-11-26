import plotly.express as px
import pandas as pd
from haversine import haversine
import numpy as np
import streamlit as st
from datetime import datetime
from PIL import Image as PILImage
import plotly.graph_objects as go

st.set_page_config(page_title="Visão Restaurante", layout="wide")

# ---------------- FUNÇÕES ----------------
def clean_code(df1):
    """Limpeza e padronização básica do dataset."""
    # Limpar idade
    df1['Delivery_person_Age'] = df1['Delivery_person_Age'].astype(str).str.strip()
    df1['Delivery_person_Age'] = df1['Delivery_person_Age'].replace(['NaN', '', 'NaN '], np.nan)
    df1['Delivery_person_Age'] = pd.to_numeric(df1['Delivery_person_Age'], errors='coerce').astype('Int64')

    # Transformar data em datetime (forçando coerção)
    df1['Order_Date'] = pd.to_datetime(df1['Order_Date'], format='%d-%m-%Y', errors='coerce')
    df1 = df1.dropna(subset=['Order_Date']).copy()
    df1['week_of_year'] = df1['Order_Date'].dt.isocalendar().week.astype(int)

    # Ratings
    df1['Delivery_person_Ratings'] = pd.to_numeric(df1['Delivery_person_Ratings'], errors='coerce')

    # Limpar City
    df1['City'] = df1['City'].astype('string').str.strip().replace(
        {'NaN': pd.NA, 'nan': pd.NA, 'NULL': pd.NA, 'null': pd.NA, '': pd.NA}
    )

    # Limpar Festival
    df1['Festival'] = df1['Festival'].astype('string').str.strip().str.capitalize().replace({'Nan': pd.NA, '': pd.NA})

    # Limpar Weatherconditions -> Weather_clean
    s = df1['Weatherconditions'].astype('string').str.strip()
    s = s.replace(['conditions NaN', 'NaN', 'nan', 'None', 'none', ''], pd.NA)
    s = s.str.replace(r'^conditions\s+', '', regex=True)
    df1['Weather_clean'] = s.replace({pd.NA: np.nan})

    # Time_taken(min) — extrair números e converter
    df1['Time_taken(min)'] = df1['Time_taken(min)'].astype(str).str.extract('(\d+)')
    df1['Time_taken(min)'] = pd.to_numeric(df1['Time_taken(min)'], errors='coerce')

    return df1

def distance_mean_km(df1):
    """
    Calcula a distância (km) entre restaurante e destino para cada linha
    e retorna a média arredondada. A coluna 'distance' é adicionada ao df1.
    """
    cols = ['Delivery_location_latitude', 'Delivery_location_longitude', 'Restaurant_latitude', 'Restaurant_longitude']
    # Garante que colunas existam e sejam numéricas
    for c in cols:
        df1[c] = pd.to_numeric(df1[c], errors='coerce')

    df1['distance'] = df1.loc[:, cols].apply(
        lambda x: haversine(
            (x['Restaurant_latitude'], x['Restaurant_longitude']),
            (x['Delivery_location_latitude'], x['Delivery_location_longitude'])
        ) if not x.isnull().any() else np.nan, axis=1
    )
    return np.round(df1['distance'].mean(), 2)

def mostrar_metricas_filtro(df, filtro_col, valor_col, col_sim, col_nao, label_sim='Com', label_nao='Sem'):
    """
    Mostra média e desvio padrão de 'valor_col' quando 'filtro_col' == 'Yes' e == 'No'.
    """
    filtro_sim = df[filtro_col] == 'Yes'
    filtro_nao = df[filtro_col] == 'No'

    media_sim = np.round(df.loc[filtro_sim, valor_col].mean(), 2)
    std_sim = np.round(df.loc[filtro_sim, valor_col].std(), 2)
    media_nao = np.round(df.loc[filtro_nao, valor_col].mean(), 2)
    std_nao = np.round(df.loc[filtro_nao, valor_col].std(), 2)

    col_sim.metric(f'Temp. Médio ({label_sim})', media_sim)
    col_sim.metric(f'Desv. Padrão ({label_sim})', std_sim)
    col_nao.metric(f'Temp. Médio ({label_nao})', media_nao)
    col_nao.metric(f'Desv. Padrão ({label_nao})', std_nao)

def avg_std_time_graph(df1, fig_height=420):
    """
    Gráfico de barras com média e erro (desvio padrão) por City.
    """
    tempo_std = df1.groupby('City')['Time_taken(min)'].agg(['mean', 'std']).reset_index()
    tempo_std.columns = ['City', 'Tempo Médio', 'Desvio Padrão']
    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            name='Tempo Médio',
            x=tempo_std['City'],
            y=tempo_std['Tempo Médio'],
            error_y=dict(type='data', array=tempo_std['Desvio Padrão'].fillna(0).tolist())
        )
    )
    fig.update_layout(barmode='group', height=fig_height, autosize=False, margin=dict(t=40, b=40, l=20, r=20))
    return fig

# ---------------- MAIN ----------------
df = pd.read_csv("dataset/train.csv")
df1 = clean_code(df)

# ---------------- SIDEBAR ----------------
logo = PILImage.open('curry_companyPNG.png')
st.sidebar.image(logo, width=120)

st.sidebar.markdown('# Cury Company')
st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.markdown("---")

# Ajustei as datas para manter coerência (min <= value <= max).
data_slider = st.sidebar.slider(
    'Até qual valor?',
    value=datetime(2022, 4, 6),           # default coerente com max_value
    min_value=datetime(2022, 2, 11),
    max_value=datetime(2022, 4, 13),
    format='DD-MM-YYYY'
)
st.sidebar.markdown("---")

traffic_options = st.sidebar.multiselect(
    'Quais as condições de trânsito',
    ['Low', 'Medium', 'High', 'Jam'],
    default=['Low']
)
st.sidebar.markdown("---")
# Recomendo remover ou parametrizar o nome aqui, para evitar dados pessoais 'hardcoded'
st.sidebar.markdown('Powered By Pedro Oliveira')

# ---------------- FILTROS ----------------
df1 = df1[df1['Order_Date'] < data_slider].copy()
df1['Road_traffic_density'] = df1['Road_traffic_density'].astype('string').str.strip().str.capitalize()
if traffic_options:
    normalized_options = [opt.capitalize() for opt in traffic_options]
    df1 = df1[df1['Road_traffic_density'].isin(normalized_options)].copy()

# ---------------- LAYOUT ----------------
st.header('Marketplace - Visão Restaurantes')
tab1, tab2, tab3 = st.tabs(['Visão Gerencial', '_', '_'])

with tab1:
    # Overall Metrics
    with st.container():
        st.title('Overall Metrics')
        col1, col2 = st.columns(2, gap='medium')
        # Entregadores únicos (número de IDs distintos)
        col1.metric('Entregadores Únicos', df1['Delivery_person_ID'].nunique())
        col2.metric('Dist. Média (km)', distance_mean_km(df1))
        st.markdown("---")

        col3, col4, col5, col6 = st.columns(4, gap='medium')
        # Mostra métricas filtradas por Festival (assumindo valores 'Yes'/'No')
        mostrar_metricas_filtro(df1, 'Festival', 'Time_taken(min)', col3, col5, label_sim='Festival', label_nao='s/F')

    # Distribution of orders by city (Pie)
    with st.container():
        st.title('Distribuição de Pedidos por Cidade')
        counts = df1['City'].value_counts(dropna=True)
        labels, values = counts.index.tolist(), counts.values.tolist()
        # destacar a menor fatia
        min_idx = int(values.index(min(values))) if len(values) > 0 else 0
        pull = [0.0] * len(values)
        pull[min_idx] = 0.1
        fig = go.Figure(
            data=[go.Pie(labels=labels, values=values, pull=pull, textinfo='percent+label', hole=0,
                         marker=dict(line=dict(color='white', width=2)))]
        )
        fig.update_layout(title_text='Distribuição de Pedidos por Cidade')
        st.plotly_chart(fig)
        st.markdown('___')

    # Time Distribution
    fig_height = 420
    with st.container():
        st.title('Time Distribution')
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('##### Tempo médio e desvio padrão por cidade')
            st.plotly_chart(avg_std_time_graph(df1, fig_height), use_container_width=True)

        with col2:
            st.markdown('##### Tempo médio por tipo de entrega')
            tabela_tempo_tipo = df1.groupby('Type_of_order')['Time_taken(min)'].mean().reset_index().rename(
                columns={'Time_taken(min)': 'Tempo_medio'}
            )
            st.dataframe(tabela_tempo_tipo, height=fig_height)

    # Distance Distribution (Sunburst)
    with st.container():
        st.title('Distance Distribution')
        cols = ['City', 'Time_taken(min)', 'Road_traffic_density']
        df_aux = df1.loc[:, cols].groupby(['City', 'Road_traffic_density']).agg({'Time_taken(min)': ['mean', 'std']})
        df_aux.columns = ['avg_time', 'std_time']()_
