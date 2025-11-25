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

st.set_page_config( page_title="Visão Empresa", layout="wide")

#----------------FUNÇÕES--------------
#-------------------------------------
def clean_code( df1 ):
    """
    Esta função é usada para limpar o dataframe.

    Tipos de limpeza:
    1 - Limpeza de linhas
    2 - Transforma a coluna de data em tipo data
    3 - Cria uma coluna de semana do ano
    4 - Transforma a coluna de Rating em tipo número
    5 - Tira os nulos das colunas City, Weatherconditions, Road_traffic_density
    6 - Cria a coluna de distância (Km)
    7 - Transforma a coluna time_taken em número
    """


    limpeza_linha = df1['Delivery_person_Age'] != 'NaN '
    df1 = df1.loc[limpeza_linha, :]


    df1['Delivery_person_Age'] = df1['Delivery_person_Age'].astype(int)
    data_pedido = pd.to_datetime( df1["Order_Date"], format='%d-%m-%Y' )
    df1["Order_Date"] = data_pedido
    
    # criar week_of_year (usar isocalendar() — compatível com pandas recentes)
    # remove linhas sem Order_Date antes para evitar NaT
    df1 = df1.dropna(subset=['Order_Date']).copy()
    df1['week_of_year'] = df1['Order_Date'].dt.isocalendar().week.astype(int)
    
    # Converter a coluna 'Delivery_person_Ratings' para numérico, tratando erros
    df1['Delivery_person_Ratings'] = pd.to_numeric(df1['Delivery_person_Ratings'], errors='coerce')
    
    # limpar City
    df1['City'] = (
        df1['City']
           .astype('string')     # garante tipo texto
           .str.strip()          # remove espaços no início/fim -> "Urban " -> "Urban"
           .replace({'NaN': np.nan, 'nan': np.nan, 'NULL': np.nan, 'null': np.nan, '': np.nan})
    )
    
    # limpar Festival (normalizar valores como 'Yes'/'No')
    df1['Festival'] = (
        df1['Festival']
           .astype('string')
           .str.strip()
           .str.capitalize()     # 'yes'/'YES' -> 'Yes'
           .replace({'Nan': np.nan, '': np.nan})
    )
    
    condicoes_clima = (
        df1['Weatherconditions']
          .replace('conditions NaN', pd.NA)   # transforma a string em NA real
          .dropna()
          .unique()
    )
    
    
    
    
    s = df1['Weatherconditions'].astype('string').str.strip()
    
    # transformar variações óbvias em NA
    s = s.replace(['conditions NaN', 'NaN', 'nan', 'None', 'none', ''], pd.NA)
    
    # opcional: remover o prefixo "conditions " se existir
    s = s.str.replace(r'^conditions\s+', '', regex=True)
    
    # agora pegar os únicos sem nulos
    condicoes_clima = s.dropna().unique()
    
    condicao_transito = (
        df1['Road_traffic_density']
        .astype('string')                 # garante que é string tratável
        .str.strip()                      # remove espaços indesejados
        .replace(['NaN', 'nan', 'NULL', 'null', ''], None)  # converte textos em nulos reais
        .dropna()                         # agora sim remove
    )
    
    cidades = (
        df1['City']
        .astype('string')          # garante que tudo é texto
        .str.strip()               # remove espaços extras -> "NaN " vira "NaN"
        .replace('NaN', np.nan)    # transforma texto NaN em nulo real
        .dropna()                  # agora remove de verdade
    )
    
    nomes_cidades = cidades.unique()
    quantidade = cidades.nunique()
    
    s = df1['Weatherconditions'].astype('string').str.strip()
    s = s.replace(['conditions NaN', 'NaN', 'nan', 'None', 'none', ''], pd.NA)
    s = s.str.replace(r'^conditions\s+', '', regex=True)
    df1['Weather_clean'] = s
    
    df1['distancia_km'] = df1.apply(
        lambda linha: haversine(
            (linha['Restaurant_latitude'], linha['Restaurant_longitude']),
            (linha['Delivery_location_latitude'], linha['Delivery_location_longitude'])
        ),
        axis=1
    )
    
    df1['Time_taken(min)'] = (
        df1['Time_taken(min)']
        .astype(str)
        .str.extract('(\d+)')
        .astype(float)
    )
    
    df1['Time_Orderd'] = df1['Time_Orderd'].str.strip().replace(['NaN', 'NaN ', ''], pd.NA)
    df1['Time_Order_picked'] = df1['Time_Order_picked'].str.strip().replace(['NaN', 'NaN ', ''], pd.NA)
    
    df1['Time_Orderd'] = pd.to_datetime(df1['Time_Orderd'], errors='coerce')
    df1['Time_Order_picked'] = pd.to_datetime(df1['Time_Order_picked'], errors='coerce')
    
    df1 = df1.reset_index(drop=True)

    return df1



# Quantidade de pedidos por dia.-------------------------------------------------------------------------------
def order_metric(df1):
     st.markdown('# Order By Day')
    
     df_aux = df1.loc[:, ['ID', 'Order_Date']].groupby('Order_Date').count().reset_index()
     df_aux.columns = ['Order_Date', 'Qtd_Orders']
            
     fig = px.bar(df_aux, x='Order_Date', y='Qtd_Orders')
     return fig


#Traffic Order Share--------------------------------------------------------------------
def traffic_order_share(df1):
    st.markdown('# Traffic Order Share')
    columns = ['ID', 'Road_traffic_density']
    df_aux = ( df1.loc[:, columns].groupby( 'Road_traffic_density' )
                                 .count()
                                 .reset_index() )
    df_aux['perc_ID'] = 100 * ( df_aux['ID'] / df_aux['ID'].sum() )
# gráfico
    fig = px.pie( df_aux, values='perc_ID', names='Road_traffic_density' )
    return fig

#Traffic Order CITY---------------------------------------------------          
def traffic_order_city(df1):
    columns = ['ID', 'City', 'Road_traffic_density']

    df_aux = (
        df1.loc[:, columns]
           .groupby(['City', 'Road_traffic_density'])
           .count()
           .reset_index()
    )

    df_aux['perc_ID'] = 100 * (df_aux['ID'] / df_aux['ID'].sum())

    # gráfico
    fig = px.scatter(df_aux, x='City', y='Road_traffic_density', size='ID', color='Road_traffic_density')
    return fig


#Order By Week-----------------------------------------

def order_by_week(df1):
# (assumindo que week_of_year já existe)
    df_aux1 = (df1.loc[:, ['ID', 'week_of_year']].groupby('week_of_year')
                                                 .count()
                                                 .reset_index())
    df_aux2 =( df1.loc[:, ['Delivery_person_ID', 'week_of_year']].groupby('week_of_year')
                                                                 .nunique()
                                                                 .reset_index())
    df_aux = pd.merge(df_aux1, df_aux2, on='week_of_year', how='inner')
    df_aux.columns = ['week_of_year', 'ID', 'Delivery_person_ID']
    df_aux = df_aux.sort_values('week_of_year')
    df_aux['order_by_delivery'] = df_aux['ID'] / df_aux['Delivery_person_ID']
# gráfico principal: orders por entregador por semana
    fig = px.line(df_aux, x='week_of_year', y='order_by_delivery', markers=True)
    return fig
    
# Order SHARE By Week------------------
def order_share_by_week(df1):
    # montar df_aux com colunas ['week_of_year','ID'] (contagem de pedidos por semana)
    df_aux = (
        df1.loc[:, ['ID', 'week_of_year']]
           .groupby('week_of_year')
           .count()
           .reset_index()
           .rename(columns={'ID':'ID'})
           .sort_values('week_of_year')
    )

    # calcular share (%) por semana
    total = df_aux['ID'].sum()
    if total == 0 or pd.isna(total):
        return None
    df_aux['perc_ID'] = 100 * (df_aux['ID'] / total)

    fig = px.line(df_aux, x='week_of_year', y='perc_ID', markers=True,
                  title='Participação (%) de pedidos por semana',
                  labels={'week_of_year':'Semana','perc_ID':'% dos Pedidos'})
    return fig



# A localização central de cada cidade por tipo de tráfego.--------------------------------------------------------
def country_maps(df1):
    
    
     columns = [
         'City',
         'Road_traffic_density',
         'Delivery_location_latitude',
         'Delivery_location_longitude'
        ]
    
     columns_groupby = ['City', 'Road_traffic_density']
     data_plot =( df1.loc[:, columns]
                     .groupby(columns_groupby)
                     .median()
                     .reset_index() )
    
# Limpeza
     data_plot = data_plot[data_plot['City'].str.strip() != 'NaN']
     data_plot = data_plot[data_plot['Road_traffic_density'].str.strip() != 'NaN']
     
# Desenhar o mapa
     map_ = folium.Map(zoom_start=11)
    
     for index, location_info in data_plot.iterrows():
         folium.Marker(
            [location_info['Delivery_location_latitude'],
             location_info['Delivery_location_longitude']],
             popup=f"{location_info['City']} - {location_info['Road_traffic_density']}").add_to(map_)
    
     folium_static(map_, width=1024, height=600)
#-------------------------------------
#----------Início da Logica-----------
#-------------------------------------
value = datetime(2022, 4, 13)

df = pd.read_csv(r"dataset\train.csv")
df1 = df.copy()

#LIMPEZA===========LIMPEZA#
df1 = clean_code( df )

#=======================SIDEBAR=======================#


#image_path = r'D:\Downloads\Downloads\CURSO\7 Python\Arquivo\curry_companyPNG.png'

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

# === NORMALIZAR coluna de trânsito (apenas uma vez, antes dos filtros) ===
df1['Road_traffic_density'] = (
    df1['Road_traffic_density']
      .astype('string')   # garante tipo texto
      .str.strip()        # remove espaços extras
      .str.capitalize()   # deixa 'low' -> 'Low', 'LOW' -> 'Low'
)

# === FILTRO DE TRÂNSITO (com comportamento seguro se nada for selecionado) ===
if traffic_options:  # se lista não vazia, filtra; senão mantem tudo
    # Garantir que opções também estejam no mesmo formato (capitalize)
    normalized_options = [opt.capitalize() for opt in traffic_options]
    df1 = df1[df1['Road_traffic_density'].isin(normalized_options)].copy()
# else: não filtra (mantém todas as linhas)


#=======================LAYOUT STREAMLIT=======================#

st.header('Marketplace - Visão Cliente')

tab1, tab2, tab3 = st.tabs( ['Visão Gerencial', 'Visão Tática', 'Visão Geográfica'])

with tab1:
    with st.container():
        fig = order_metric( df1 )
        st.plotly_chart(fig , use_container_width = True)

        

    with st.container():
        col1, col2 = st.columns( 2 )
        with col1:
            fig = traffic_order_share( df1 )
            st.plotly_chart(fig , use_conatiner_width = True)
            
                
        with col2:
            st.markdown('# Order By Traffic')
            fig = traffic_order_city( df1 )
            st.plotly_chart(fig , use_conatiner_width = True)

with tab2:
    st.markdown('# Order By Week')
    fig = order_by_week( df1 )
    st.plotly_chart(fig, use_container_width=True, key='grafico_order_by_delivery_semana')
     
    with st.container():
        st.markdown('# Order Share By Week')
        fig = order_share_by_week(df1)
        st.plotly_chart(fig, use_container_width=True, key='grafico_qtd_pedidos_semana')

with tab3:
    st.markdown('# Country Maps')
    country_maps(df1)
    
    
    #print(df1.head())