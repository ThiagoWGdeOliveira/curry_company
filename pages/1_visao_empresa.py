# Libraries
from haversine import haversine
from datetime import datetime
from PIL import Image
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import plotly.express as px
import streamlit as st
import folium
from streamlit_folium import folium_static

st.set_page_config ( page_title = "Visão Empresa", layout="wide")

#------------------------------------------------
# Funções 
#------------------------------------------------

def country_maps(df1):
    """ Essa função desenha um mapa com a localidade das entregas """
    df_aux = df1.loc[:, ['City','Road_traffic_density', 'Delivery_location_latitude', 'Delivery_location_longitude']].groupby(['City','Road_traffic_density']).median().reset_index()
    
    map = folium.Map()

    for index, location_info in df_aux.iterrows():
        folium.Marker([location_info['Delivery_location_latitude'],
                       location_info['Delivery_location_longitude']],
                       popup=location_info[['City', 'Road_traffic_density']]).add_to(map)
        folium_static(map, width=1024, height=600)

def order_share_by_week(df1):
    """ Essa função extrai faz a contagem de pedidos por semana e retonrna um gráfico de linhas """
    df_aux01 = df1.loc[:, ['ID', 'week_of_year']].groupby('week_of_year').count().reset_index()
    df_aux02 = df1.loc[:, ['Delivery_person_ID', 'week_of_year']].groupby('week_of_year').nunique().reset_index()
    df_aux = pd.merge(df_aux01, df_aux02, how='inner', on='week_of_year')
    df_aux['order_by_deliver'] =df_aux['ID']/df_aux['Delivery_person_ID']
    fig = px.line(df_aux, x= 'week_of_year', y='order_by_deliver')
    return fig


def order_by_week(df1):
    """ Essa função faz a contagem de pedidos entregues por semana e retorna um gráfico de linhas """
    df1['week_of_year'] = df1['Order_Date'].dt.strftime('%U')
    df_aux = df1.loc[:, ['ID', 'week_of_year']].groupby('week_of_year').count().reset_index()
    fig = px.line(df_aux, x= 'week_of_year', y='ID')
    return fig
            
def traffic_order_city(df1):
    """ Essa função faz a contagem de pedidos por cidade e tipo de tráfego """
    df_aux = df1.loc[:, ['ID', 'City','Road_traffic_density']].groupby(['City','Road_traffic_density']).count().reset_index()
    df_aux = df_aux.loc[df_aux['City'] != "NaN",:]
    df_aux = df_aux.loc[df_aux['Road_traffic_density'] != "NaN",:]
    fig = px.scatter(df_aux, x='City', y='Road_traffic_density', size='ID', color='City')
    return fig

def traffic_order_share(df1):
    """ Essa função faz a soma de pedidos por tipo de tráfego """
    df_aux = df1.loc[:, ['ID', 'Road_traffic_density']].groupby('Road_traffic_density').count().reset_index()
    df_aux = df_aux.loc[df_aux['Road_traffic_density'] != "NaN",:]
    df_aux['entregas_perc']= df_aux['ID']/df_aux['ID'].sum()
    fig = px.pie(df_aux, values = 'entregas_perc', names= 'Road_traffic_density')
    return fig

def order_metric(df1):
    """ Essa função faz a contagem de pedidos por data """
    cols = ['ID', 'Order_Date']
    df_aux = df1.loc[:, cols].groupby('Order_Date').count().reset_index()
    fig = px.bar(df_aux, x= 'Order_Date', y = 'ID')
    return fig


def clean_code(df1):
    """ Está função tem a responsabilidade de limpar o dataframe

        Tipos de limpeze:
        1. Remoção dos dados NaN
        2. Mudança do tipo da coluna de dados
        3. Remoção dos espaços das variáveis de texto
        4. Formatação da coluna de data
        5. Limpeza da coluna de Time ( remoção do texto da variável numérica )

        input: dataframe
        output: dataframe
    
    """
    # Excluir valores NaN para Age
    linhas_selecionadas = df1['Delivery_person_Age'] != 'NaN '
    df1 = df1.loc[linhas_selecionadas, :]
    df1['Delivery_person_Age'] = df1['Delivery_person_Age'].astype(int)
    
    # Excluir valores NaN para Ratings
    linhas_selecionadas = df1['Delivery_person_Ratings'] != 'NaN '
    df1 = df1.loc[linhas_selecionadas, :]
    df1['Delivery_person_Ratings'] = df1['Delivery_person_Ratings'].astype(float)
    
    # Excluindo valor NaN para multiple_deliveries
    linhas_selecionadas = (df1['multiple_deliveries'] != "NaN ")
    df1 = df1.loc[linhas_selecionadas, :]
    df1['multiple_deliveries'] = df1['multiple_deliveries'].astype(int)

    # Excluindo valor NaN para City
    linhas_selecionadas = (df1['City'] != "NaN ")
    df1 = df1.loc[linhas_selecionadas, :]

    # Excluindo valor NaN para Road_traffic_density
    linhas_selecionadas = (df1['Road_traffic_density'] != "NaN ")
    df1 = df1.loc[linhas_selecionadas, :]
    
    # Ajustando as datas:
    df1['Order_Date'] = pd.to_datetime(df1['Order_Date'], format='%d-%m-%Y')
    
    # Removendo espaços dentro de strings/texto: forma de fazer sem o uso do for
    df1.loc[:, 'ID'] = df1.loc[:, 'ID'].str.strip()
    df1.loc[:, 'Road_traffic_density'] = df1.loc[:, 'Road_traffic_density'].str.strip()
    df1.loc[:, 'Type_of_order'] = df1.loc[:, 'Type_of_order'].str.strip()
    df1.loc[:, 'Type_of_vehicle'] = df1.loc[:, 'Type_of_vehicle'].str.strip()
    df1.loc[:, 'City'] = df1.loc[:, 'City'].str.strip()
    df1.loc[:, 'Festival'] = df1.loc[:, 'Festival'].str.strip()
    
    # Limpando a coluna de time taken
    df1['Time_taken(min)'] = df1['Time_taken(min)'].apply( lambda x: x.split( '(min) ')[1] )
    df1['Time_taken(min)'] = df1['Time_taken(min)'].astype( int )

    return df1

#---------------------------------------------- Inicio da estrutura lógica do código -----------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------------------
# Import dataset
df = pd.read_csv('dataset/train.csv')

# Limpar o código
df1 = clean_code (df)

# Visão Empresa

#=====================================================================
# Barra Lateral
#=====================================================================
st.header('Marketplace - Visão Cliente')

#image_path = 'C:/Users/thiag/Documents/repos/ftc/Notebook.jpg'
image = Image.open('Notebook.jpg')
st.sidebar.image( image, width = 180)

st.sidebar.markdown(' # Cury Company')
st.sidebar.markdown(' ## Fastest Delivery in Town')
st.sidebar.markdown("""---""")

st.sidebar.markdown( '## Selecione uma data limite')

date_slider = st.sidebar.slider(
    'Até qual valor?',
    value=datetime( 2022, 4, 13 ),
    min_value=datetime( 2022, 2, 11 ),
    max_value=datetime( 2022, 4, 6 ),
    format='DD-MM-YYYY')

st.sidebar.markdown("""---""")

traffic_options = st.sidebar.multiselect(
    'Quais as condições de trânsito',
    ['Low', 'Medium', 'High', 'Jam'],
    default = ['Low', 'Medium', 'High', 'Jam'] )

st.sidebar.markdown("""---""")
st.sidebar.markdown( '### Powered by Thiago Oliveira')

# Filtro de data
linhas_selecionadas = df1['Order_Date'] < date_slider
df1 = df1.loc[linhas_selecionadas, :]

# Filtro de transito
linhas_selecionadas = df1['Road_traffic_density'].isin(traffic_options)
df1 = df1.loc[linhas_selecionadas, :]


#=====================================================================
# Layout do Streamlit
#=====================================================================

tab1, tab2, tab3 = st.tabs(['Visão Gerencial', 'Visão Tática', 'Visão Geográfica'])

with tab1:
    with st.container():
        st.markdown(' # Orders by Day')
        fig = order_metric(df1)
        st.plotly_chart(fig, use_container_width=True)
    
    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            st.header("Traffic Order Share")
            fig = traffic_order_share(df1)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.header("Traffic Order City")
            fig = traffic_order_city(df1)
            st.plotly_chart(fig, use_container_width=True)

with tab2:
    with st.container():
        st.markdown( '# Order by Week')
        fig = order_by_week(df1)
        st.plotly_chart(fig, use_container_width=True)

    with st.container():
        st.markdown("# Order share by Week")
        fig = order_share_by_week(df1)
        st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.markdown( '# Country Maps')
    country_maps (df1)


           










