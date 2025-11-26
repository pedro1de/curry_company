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
    df1['City'] = df1['City'].astype('string').str.strip().replace({'NaN': pd.NA, 'nan': pd.NA, 'NULL': pd.NA, 'null': pd.NA, '': pd.NA})

    # Limpar Festival -> normalizar para 'Yes'/'No'/pd.NA
    fest = df1['Festival'].astype('string').str.strip().str.lower()
    fest = fest.replace({'nan': pd.NA, 'none': pd.NA, '': pd.NA})
    # map possible values to Yes/No
    fest = fest.map(lambda v: 'Yes' if str(v) in ['yes', 'sim', 'true', 'y', '1'] else ('No' if str(v) in ['no', 'nao', 'não', 'false', 'n', '0'] else pd.NA))
    df1['Festival'] = fest

    # Limpar Weatherconditions -> Weather_clean
    s = df1['Weatherconditions'].astype('string').str.strip()
    s = s.replace(['conditions NaN', 'NaN', 'nan', 'None', 'none', ''], pd.NA)
    s = s.str.replace(r'^conditions\s+', '', regex=True)
    df1['Weather_clean'] = s

    # Time_taken(min) -> extrair número e conv. para numeric
    df1['Time_taken(min)'] = df1['Time_taken(min)'].astype(str).str.extract(r'(\d+)')
    df1['Time_taken(min)'] = pd.to_numeric(df1['Time_taken(min)'], errors='coerce')

    # Normalizar Road_traffic_density (preparar para filtro)
    df1['Road_traffic_density'] = df1['Road_traffic_density'].astype('string').str.strip().str.capitalize().replace({'Nan': pd.NA, '': pd.NA})

    return df1

def distance_mean_km(df1):
    """Calcula a distância média (km) entre restaurante e entrega.
    Retorna float arredondado com 2 casas.
    """
    cols = ['Delivery_location_latitude', 'Delivery_location_longitude', 'Restaurant_latitude', 'Restaurant_longitude']
    # Checar se colunas existem e têm valores não nulos
    if not all(c in df1.columns for c in cols):
        return np.nan
    df_aux = df1.dropna(subset=cols).copy()
    if df_aux.shape[0] == 0:
        return np.nan

    distances = df_aux.loc[:, cols].apply(
        lambda x: haversine(
            (x['Restaurant_latitude'], x['Restaurant_longitude']),
            (x['Delivery_location_latitude'], x['Delivery_location_longitude'])
        ), axis=1
    )
    return float(np.round(distances.mean(), 2))

def mostrar_metricas_filtro(df, filtro_col, valor_col, col_sim, col_nao, label_sim='Com', label_nao='Sem'):
    """Mostra média e desvio padrão para duas classes ('Yes' e 'No') de uma coluna filtro.
       A função é robusta a valores faltantes e normaliza múltiplas formas de sim/não.
    """
    # Normalizar filtro: mapear valores 'yes','sim','no'...
    filtro = df[filtro_col].astype('string').str.strip().str.lower().replace({'nan': None, 'none': None})
    is_yes = filtro.isin(['yes', 'sim', 'true', 'y', '1'])
    is_no = filtro.isin(['no', 'nao', 'não', 'false', 'n', '0'])

    # Calcular
    media_sim = np.round(df.loc[is_yes, valor_col].mean(skipna=True), 2) if df.loc[is_yes, :].shape[0] > 0 else np.nan
    std_sim = np.round(df.loc[is_yes, valor_col].std(skipna=True), 2) if df.loc[is_yes, :].shape[0] > 0 else np.nan
    media_nao = np.round(df.loc[is_no, valor_col].mean(skipna=True), 2) if df.loc[is_no, :].shape[0] > 0 else np.nan
    std_nao = np.round(df.loc[is_no, valor_col].std(skipna=True), 2) if df.loc[is_no, :].shape[0] > 0 else np.nan

    col_sim.metric(f'Tempo Médio ({label_sim})', str(media_sim))
    col_sim.metric(f'Desv. Padrão ({label_sim})', str(std_sim))
    col_nao.metric(f'Tempo Médio ({label_nao})', str(media_nao))
    col_nao.metric(f'Desv. Padrão ({label_nao})', str(std_nao))

def avg_std_time_graph(df1, fig_height=420):
    tempo_std = df1.groupby('City')['Time_taken(min)'].agg(['mean', 'std']).reset_index()
    tempo_std.columns = ['City', 'Tempo Médio', 'Desvio Padrão']
    # preencher NaNs (p.ex. std NaN quando 1 amostra) com 0 para plotagem
    tempo_std['Desvio Padrão'] = tempo_std['Desvio Padrão'].fillna(0)
    tempo_std['Tempo Médio'] = tempo_std['Tempo Médio'].fillna(0)
    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            name='Tempo Médio',
            x=tempo_std['City'],
            y=tempo_std['Tempo Médio'],
            error_y=dict(type='data', array=tempo_std['Desvio Padrão'].tolist())
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
st.sidebar.markdown("""---""")

# Slider: ajustar valores mínimos e máximos coerentes com o dataset
data_min = df1['Order_Date'].min()
data_max = df1['Order_Date'].max()
# Garante fallback caso dados estejam vazios
if pd.isna(data_min) or pd.isna(data_max):
    data_min = datetime(2022, 2, 11)
    data_max = datetime(2022, 4, 6)

data_slider = st.sidebar.slider(
    'Mostrar pedidos até a data:',
    value=data_max,
    min_value=data_min,
    max_value=data_max,
    format='DD-MM-YYYY'
)
st.sidebar.markdown("""---""")

traffic_options = st.sidebar.multiselect(
    'Quais as condições de trânsito',
    options=['Low', 'Medium', 'High', 'Jam'],
    default=['Low']
)
st.sidebar.markdown("""---""")
# Removida identificação pessoal do sidebar (privacidade)
# st.sidebar.markdown('Powered By ...')

# ---------------- FILTROS ----------------
df1 = df1[df1['Order_Date'] <= data_slider].copy()
if traffic_options:
    normalized_options = [opt.capitalize() for opt in traffic_options]
    # proteger contra valores nulos
    df1 = df1[df1['Road_traffic_density'].isin(normalized_options)].copy()

# ---------------- LAYOUT ----------------
st.header('Marketplace - Visão Restaurantes')
tab1, tab2, tab3 = st.tabs(['Visão Gerencial', '_', '_'])

with tab1:
    # Overall Metrics
    with st.container():
        st.title('Overall Metrics')
        col1, col2 = st.columns(2, gap='medium')
        col1.metric('Ent. Únicos', int(df1['Delivery_person_ID'].nunique()))
        col2.metric('Dist. Média (km)', distance_mean_km(df1))
        st.markdown("""---""")

        col3, col4, col5, col6 = st.columns(4, gap='medium')
        mostrar_metricas_filtro(df1, 'Festival', 'Time_taken(min)', col3, col5, label_sim='Com Festival', label_nao='Sem Festival')

    # Distribution of deliveries by City (Pie) - porcentagem de pedidos por cidade
    with st.container():
        st.title('Distribuição de Pedidos por Cidade')
        counts = df1['City'].value_counts(dropna=True)
        labels, values = counts.index.tolist(), counts.values.tolist()
        if len(values) > 0:
            min_idx = int(values.index(min(values)))
        else:
            min_idx = 0
        pull = [0.0] * len(values)
        if values:
            pull[min_idx] = 0.1
        fig = go.Figure(
            data=[go.Pie(labels=labels, values=values, pull=pull, textinfo='percent+label', hole=0,
                         marker=dict(line=dict(color='white', width=2)))]
        )
        fig.update_layout(title_text='Porcentagem de Pedidos por Cidade')
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
            tabela_tempo_tipo = df1.groupby('Type_of_order')['Time_taken(min)'].mean().reset_index().rename(columns={'Time_taken(min)': 'Tempo_medio'})
            st.dataframe(tabela_tempo_tipo, height=fig_height)

    # Distance Distribution (Sunburst)
    with st.container():
        st.title('Distance Distribution')
        cols = ['City', 'Time_taken(min)', 'Road_traffic_density']
        df_aux = df1.loc[:, cols].groupby(['City', 'Road_traffic_density']).agg({'Time_taken(min)': ['mean', 'std']})
        df_aux.columns = ['avg_time', 'std_time']
        df_aux = df_aux.reset_index()
        # preencher std_time NaN para evitar erros no color mapping
        df_aux['std_time'] = df_aux['std_time'].fillna(0)
        fig = px.sunburst(
            df_aux,
            path=['City', 'Road_traffic_density'],
            values='avg_time',
            color='std_time',
            color_continuous_scale='RdBu',
            color_continuous_midpoint=np.average(df_aux['std_time']) if not df_aux['std_time'].isna().all() else 0
        )
        st.plotly_chart(fig)
