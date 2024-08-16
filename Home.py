import streamlit as st
from PIL import Image

st.set_page_config(
    page_title="Home")

#image_path = 'C:/Users/thiag/Documents/repos/ftc/'
image = Image.open('Notebook.jpg')
st.sidebar.image(image, width=120)

st.sidebar.markdown(' # Cury Company')
st.sidebar.markdown(' ## Fastest Delivery in Town')
st.sidebar.markdown("""---""")

st.write("# Curry Company Growth Dashborard")
st.markdown(
    """
    Growth Dashboard foi construído para a companhar as métricas de crescimento dos Entregadores e Restaurantes.
    ### Como utilizar esse Growth Dashboard?
    - Visão Empresa:
        - Visão Gerencial: métricas gerais de comportamento.
        - Visão Tática: Indicadores semanais de crescimento.
        - Visão Geográfica: Insights de geolocalização.
    - Visão Entregador:
        - Acompanhamento dos indicadores semanais de crescimento
    - Visão Restaurante:
        - Indicadores semanais de crescimento dos restaurantes
    ### Ask for Help
    - Thiago W. G. de Oliveira no Discord
        - @thiagooliveira100
    """)

