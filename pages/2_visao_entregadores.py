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

st.set_page_config ( page_title = "Visão Entregadores", layout="wide")

#-----------------------------------------------
# Funções
#-----------------------------------------------

def top_delivers(df1, top_asc):
    """ Calcula os 10 entregadores mais lentos """
    
    df2 = (df1.loc[:, ['Delivery_person_ID', 'City', 'Time_taken(min)']].groupby(['City', 'Delivery_person_ID']).mean().sort_values(['City', 'Time_taken(min)'],ascending=top_asc).reset_index())
    df_aux01 = df2.loc[df2['City']=='Metropolitian',:].head(10)
    df_aux02 = df2.loc[df2['City'] == 'Urban',:].head(10)
    df_aux03 = df2.loc[df2['City'] == 'Semi-Urban', :].head(10)
    df3 = pd.concat([df_aux01, df_aux02, df_aux03]).reset_index(drop=True)
    return(df3)

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








# Import dataset
df = pd.read_csv('dataset/train.csv')

# Cleaning dataset
df1 = clean_code(df)


#=====================================================================
# Barra Lateral
#=====================================================================

st.header('Marketplace - Visão Entregadores')

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

#climate_options = st.sidebar.multiselect(
#    'Quais as condições de clima',
#    ['conditions Cloudy', 'conditions Fog', 'conditions Sandstorms', 'conditions Stormy', 'conditions Sunny', 'conditions Windy', 'conditions NaN'],
#    default = ['Cloudy', 'Fog', 'Sandstorms', 'Stormy', 'Sunny', 'Windy', 'NaN'] )

st.sidebar.markdown("""---""")
st.sidebar.markdown( '### Powered by Thiago Oliveira')

# Filtro de data
linhas_selecionadas = df1['Order_Date'] < date_slider
df1 = df1.loc[linhas_selecionadas, :]

# Filtro de transito
linhas_selecionadas = df1['Road_traffic_density'].isin(traffic_options)
df1 = df1.loc[linhas_selecionadas, :]

# Filtro de condições climáticas
#linhas_selecionadas = df1['Weatherconditions'].isin(climate_options)
#df1 = df1.loc[linhas_selecionadas,:]



#=====================================================================
# Layout streamlit
#=====================================================================
tab1, tab2, tab3 = st.tabs(['Visão Gerencial', '_', '_'])

with tab1:
    with st.container():
        st.title( 'Overall Metrics')

        col1, col2, col3, col4 = st.columns(4, gap='large')
        with col1:
            # Maior idade dos entregadores
            maior_idade = df1.loc[:,'Delivery_person_Age'].max()
            col1.metric(' Maior idade', maior_idade)
            
        with col2:
            # Menor idade dos entregadores
            menor_idade = df1.loc[:,'Delivery_person_Age'].min()
            col2.metric(' Menor idade', menor_idade)

        with col3:
            # Melhor condição do veículo
            melhor_condicao = df1.loc[:,'Vehicle_condition'].max()
            col3.metric('Melhor condição', melhor_condicao)

        with col4:
            # Pior condição do veículo
            pior_condicao = df1.loc[:,'Vehicle_condition'].min()
            col4.metric('Pior condição', pior_condicao)

    with st.container():
        st.markdown("""---""")
        st.title ('Avaliações')

        col1, col2 = st.columns(2)

        with col1:
            st.markdown('##### Avaliação médias por entregador')
            df_avg_ratings_per_deliver = df1.loc[:,['Delivery_person_Ratings','Delivery_person_ID']].groupby('Delivery_person_ID').mean().reset_index()
            st.dataframe(df_avg_ratings_per_deliver)

        with col2:
            st.markdown( '##### Avalição média por trânsito')
            df_avg_std_ratings_by_traffic =( df1.loc[:,['Delivery_person_Ratings','Road_traffic_density']].groupby('Road_traffic_density').agg({'Delivery_person_Ratings':['mean', 'std']}))
            # mudança de nome das colunas
            df_avg_std_ratings_by_traffic.columns = ['delivery_mean', 'delivery_std']

            df_avg_std_ratings_by_traffic = df_avg_std_ratings_by_traffic.reset_index()
            st.dataframe(df_avg_std_ratings_by_traffic)
            
            st.markdown('##### Avaliação média por clima')
            df_avg_std_ratings_by_weather =( df1.loc[:,['Delivery_person_Ratings','Weatherconditions']].groupby('Weatherconditions').agg({'Delivery_person_Ratings':['mean', 'std']}))
            # mudança de nome das colunas
            df_avg_std_ratings_by_weather.columns = ['delivery_mean', 'delivery_std']

            df_avg_std_ratings_by_weather = df_avg_std_ratings_by_weather.reset_index()
            st.dataframe(df_avg_std_ratings_by_weather)


    with st.container():
        st.markdown("""---""")
        st.title ('Velocidade de Entrega')

        col1, col2 = st.columns(2)

        with col1:
            st.markdown('##### Top Entregadores mais rápidos')
            df3 = top_delivers(df1, top_asc=True)
            st.dataframe(df3)        

        with col2:
            st.markdown('##### Top Entregadores mais lentos')
            df3 = top_delivers(df1, top_asc=False)
            st.dataframe(df3)
