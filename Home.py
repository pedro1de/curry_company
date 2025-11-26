import streamlit as st
from PIL import Image

st.set_page_config(
    page_title='Home')

#image_path = r'D:\Downloads\Downloads\CURSO\7 Python\Arquivo\\'
Image = Image.open('curry_companyPNG.png')
st.sidebar.image(Image, width=120)


st.sidebar.markdown( '# Cury Company')
st.sidebar.markdown( '## Fastest Delivery in Town')
st.sidebar.markdown( """---""")

st.write('# Curry Company Growth Dashboard')
import streamlit as st

st.markdown(
    """
    st.markdown(
    """
    📊 Bem-vindo ao Dashboard da Curry Company
    Este painel apresenta as principais métricas de desempenho da operação. Incluindo volume de pedidos, desempenho dos entregadores, eficiência dos restaurantes e padrões semanais de entrega.

    Utilize os filtros à esquerda para explorar os dados por cidade, tipo de tráfego e período.  
    Todas as visualizações são atualizadas automaticamente conforme suas escolhas.
    """

    ### Como utilizar esse Growth Dashboard?
    - **Visão Empresa:**
        - Visão Gerencial: Métricas gerais de comportamento.
        - Visão Tática: Indicadores semanais de crescimento.
        - Visão Geográfica: Insights de geolocalização.
    - **Visão Entregador:**
        - Acompanhamento dos indicadores semanais de crescimento
    - **Visão Restaurante:**
        - Indicadores semanais de crescimento dos restaurantes

    ### Ask for Help
        - Time de Data Science no Discord
        - @Pedro
    """
)
