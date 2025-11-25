import plotly.express as px
import pandas as pd
from haversine import haversine
import io
import numpy as np
import folium
import streamlit as st
from datetime import datetime
from PIL import Image
from streamlit_folium import folium_static

st.set_page_config( page_title="Visão Entregadores", layout="wide")
#----------------FUNÇÕES--------------
#-------------------------------------
def clean_code(df1):
    # Esta função é usada para limpar o dataframe.

    # Tratar idade do entregador
    df1['Delivery_person_Age'] = df1['Delivery_person_Age'].astype(str).str.strip()
    df1['Delivery_person_Age'] = df1['Delivery_person_Age'].replace(['NaN', '', 'NaN '], np.nan)
    df1['Delivery_person_Age'] = df1['Delivery_person_Age'].astype(float).astype('Int64')

    # Transformar data em datetime
    df1['Order_Date'] = pd.to_datetime(df1["Order_Date"], format='%d-%m-%Y')

    # Criar week_of_year
    df1 = df1.dropna(subset=['Order_Date']).copy()
    df1['week_of_year'] = df1['Order_Date'].dt.isocalendar().week.astype(int)

    # Transformar rating em numérico
    df1['Delivery_person_Ratings'] = pd.to_numeric(df1['Delivery_person_Ratings'], errors='coerce')

    # Limpar City
    df1['City'] = (
        df1['City']
        .astype('string')
        .str.strip()
        .replace({'NaN': np.nan, 'nan': np.nan, 'NULL': np.nan, 'null': np.nan, '': np.nan})
    )

    # Limpar Festival
    df1['Festival'] = (
        df1['Festival']
        .astype('string')
        .str.strip()
        .str.capitalize()
        .replace({'Nan': np.nan, '': np.nan})
    )

    # Limpar Weatherconditions -> criar Weather_clean
    s = df1['Weatherconditions'].astype('string').str.strip()
    s = s.replace(['conditions NaN', 'NaN', 'nan', 'None', 'none', ''], pd.NA)
    s = s.str.replace(r'^conditions\s+', '', regex=True)
    df1['Weather_clean'] = s

    # Garantir que 'Time_taken(min)' seja numérico
    df1['Time_taken(min)'] = df1['Time_taken(min)'].astype(str).str.extract('(\d+)')
    df1['Time_taken(min)'] = pd.to_numeric(df1['Time_taken(min)'], errors='coerce')


    return df1




        
def top_delivery(df1, top_asc):
        df2 = (
        df1.loc[:, ['Delivery_person_ID', 'City', 'Time_taken(min)']]
           .groupby(['City', 'Delivery_person_ID'])
           .mean()
           .sort_values(['City', 'Time_taken(min)'], ascending = top_asc)
           .reset_index() )




        df_aux01 = df2.loc[df2['City'] == 'Metropolitan', :].head(10)
        df_aux02 = df2.loc[df2['City'] == 'Urban', :].head(10)
        df_aux03 = df2.loc[df2['City'] == 'Semi-Urban', :].head(10)

        df3 = pd.concat([df_aux01, df_aux02, df_aux03]).reset_index(drop=True)
        return df3

#-------------------------------------
#----------Início da Logica-----------
#-------------------------------------
value = datetime(2022, 4, 13)

df = pd.read_csv(r"dataset\train.csv")
df1 = df.copy()

#LIMPEZA===========LIMPEZA#
df1 = clean_code( df )


#=======================SIDEBAR=======================#


Image = Image.open('curry_companyPNG.png')

st.sidebar.image( Image, width=120)

st.sidebar.markdown( '# Cury Company')
st.sidebar.markdown( '## Fastest Delivery in Town')
st.sidebar.markdown( """---""")
st.sidebar.markdown( '## Selecione uma data limite')
data_slider = st.sidebar.slider(
    'Até qual valor?',
    value=datetime(2022, 4, 13 ),
    min_value=datetime(2022, 2, 11),
    max_value=datetime(2022, 4, 6),
    format='DD-MM-YYYY' )
st.sidebar.markdown( """---""")

# === SIDEBAR: multiselect com default como lista ===
traffic_options = st.sidebar.multiselect(
    'Quais as condições de trânsito',
    ['Low', 'Medium', 'High', 'Jam'],
    default=['Low']  # <-- sempre lista
)

st.sidebar.markdown("""---""")
st.sidebar.markdown('Powered By Pedro Oliveira')

# === FILTRO DE DATA ===
linhas_selecionadas = df1['Order_Date'] < data_slider
df1 = df1.loc[linhas_selecionadas, :].copy()

# === NORMALIZAR coluna de trÃ¢nsito (apenas uma vez, antes dos filtros) ===
df1['Road_traffic_density'] = (
    df1['Road_traffic_density']
      .astype('string')   # garante tipo texto
      .str.strip()        # remove espaços extras
      .str.capitalize()   # deixa 'low' -> 'Low', 'LOW' -> 'Low'
)

# === FILTRO DE TRANSITO (com comportamento seguro se nada for selecionado) ===
if traffic_options:  # se lista não vazia, filtra; senão mantem tudo
    # Garantir que opções também estejam no mesmo formato (capitalize)
    normalized_options = [opt.capitalize() for opt in traffic_options]
    df1 = df1[df1['Road_traffic_density'].isin(normalized_options)].copy()
# else: não filtra (mantém todas as linhas)

#=======================LAYOUT STREAMLIT=======================#

st.header('Marketplace - Visão Entregadores')

tab1, tab2, tab3 = st.tabs(['Visão Gerencial', '_', '_'])

with tab1:
    with st.container():
        st.title('Overall Metrics')
        col1, col2, col3, col4 = st.columns(4, gap='medium')

        with col1:
            maior_idade = df1['Delivery_person_Age'].max()
            col1.metric('Maior Idade', maior_idade)

        with col2:
            menor_idade = df1['Delivery_person_Age'].min()
            col2.metric('Menor Idade', menor_idade)

        with col3:
            melhor_cond = df1['Vehicle_condition'].max()
            col3.metric('Melhor Condição', melhor_cond)

        with col4:
            pior_cond = df1['Vehicle_condition'].min()
            col4.metric('Pior Condição', pior_cond)

    with st.container():
        st.markdown("""---""")
        st.title('Ratings')

        col1, col2 = st.columns(2, gap='medium')

        with col1:
            st.markdown('##### Avaliações médias por entregador')
            # A avaliação média por entregador
            media_avaliacao_por_entregador = (
                df1.groupby('Delivery_person_ID')['Delivery_person_Ratings']
                .mean()
                .reset_index()
            )
            st.dataframe(media_avaliacao_por_entregador)

        with col2:
            st.markdown('##### Avaliações médias por transito')
            av_media_transito = (
                df1.loc[:, ['Delivery_person_Ratings', 'Road_traffic_density']]
                .groupby('Road_traffic_density')
                .agg({'Delivery_person_Ratings': ['mean']})
            )
            av_media_transito = av_media_transito.reset_index()
            st.dataframe(av_media_transito)

            st.markdown('##### Avaliações médias por clima')
            av_media_clima = (
                df1.groupby('Weather_clean')
                .agg({'Delivery_person_Ratings': ['mean']})
            )
            av_media_clima = av_media_clima.reset_index()
            st.dataframe(av_media_clima)

# ============================================
# ENTREGADORES MAIS RAPIDOS E MAIS LENTOS
# ============================================
with st.container():
    st.markdown("""---""")
    st.title('Velocidade de Entrega')

    col1, col2 = st.columns(2)

    with col1:
        st.markdown('##### Top Entregadores mais rápidos')
        df3 = top_delivery(df1, top_asc=True)
        st.dataframe(df3)

    with col2:
        st.markdown('##### Top Entregadores mais lentos')
        df3 = top_delivery(df1, top_asc=False)
        st.dataframe(df3)


