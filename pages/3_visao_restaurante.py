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
import numpy as np
from streamlit_folium import folium_static


st.set_page_config ( page_title = "Visão Restaurantes", layout="wide")

#-----------------------------------------------
# Funções
#-----------------------------------------------

def avg_std_time_on_traffic(df1):
    df_aux = df1.loc[:, ['City', 'Time_taken(min)', 'Road_traffic_density']].groupby(['City', 'Road_traffic_density']).agg({'Time_taken(min)': ['mean', 'std']})
    df_aux.columns = ['avg_time', 'std_time']
    df_aux = df_aux.reset_index()
    
    fig = px.sunburst(df_aux, path=['City', 'Road_traffic_density'], values='avg_time',
                      color='std_time', color_continuous_scale='RdBu',
                      color_continuous_midpoint=np.average(df_aux['std_time']))
    return fig

def avg_std_time_graph(df1):
    cols = ['City', 'Time_taken(min)']
    df_aux = df1.loc[:, cols].groupby('City').agg({'Time_taken(min)': ['mean', 'std']})
    df_aux.columns = ['avg_time', 'std_time']
    df_aux = df_aux.reset_index()
                
    fig=go.Figure()
    fig.add_trace(go.Bar(name='Control', x= df_aux['City'], y=df_aux['avg_time'], error_y = dict(type='data', array=df_aux['std_time'])))
    fig.update_layout(barmode='group')
    return fig

def avg_std_time_delivery(df1, fest,op):
    """ 
    Esta função calcula o tempo médio e o desvio padrão do tempo de entrega.
    Parâmetros:
    input:
        - df = dataframe com os dados necessários para cálculo
        - fest - se teve ou não festival ('Yes', 'No')
        - op = tipo de operação que precisa ser calculado
        'avg_time' - calcula o tempo médio
        'std_time' - calcula o desvio padrão do tempo
    output:
        - df: Dataframe com 2 colunas e 1 linha

    """
    cols = ['Time_taken(min)', 'Festival']
    df_aux = df1.loc[:, cols].groupby('Festival').agg({'Time_taken(min)':['mean', 'std']})
    df_aux.columns = ['avg_time', 'std_time']
    df_aux = df_aux.reset_index()
    df_aux = np.round( df_aux.loc[df_aux['Festival']==fest, op],2)
    return df_aux


def distance(df1, fig):
    if fig == False:
        cols = ['Delivery_location_latitude', 'Delivery_location_longitude', 'Restaurant_latitude', 'Restaurant_longitude']
        df1['distance']= df1.loc[:, cols].apply( lambda x: haversine( (x['Restaurant_latitude'], x['Restaurant_longitude']),(x['Delivery_location_latitude'], x['Delivery_location_longitude'])), axis=1)
        avg_distance = np.round(df1['distance'].mean(),2)
        return avg_distance
    else:
        cols = ['Delivery_location_latitude', 'Delivery_location_longitude', 'Restaurant_latitude', 'Restaurant_longitude']
        df1['distance']= df1.loc[:, cols].apply( lambda x: haversine( (x['Restaurant_latitude'], x['Restaurant_longitude']),(x['Delivery_location_latitude'], x['Delivery_location_longitude'])), axis=1)
        avg_distance = df1.loc[:,['City', 'distance']].groupby('City').mean().reset_index()
        fig = go.Figure( data=[ go.Pie(labels = avg_distance['City'], values=avg_distance['distance'], pull=[0,0.1,0])])
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


# Import dataset
df = pd.read_csv('dataset/train.csv')

# Cleaing code
df1 = clean_code(df)

# Visão restaurantes

#=====================================================================
# Barra Lateral
#=====================================================================

st.header('Marketplace - Visão Restaurantes')

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
# Layout do Streamlit
#=====================================================================
tab1, tab2, tab3 = st.tabs(['Visão Gerencial', '_', '_'])

with tab1:
    with st.container():
        st.title("Overral Metrics")
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        
        with col1:
            delivery_unique = len(df1.loc[:, 'Delivery_person_ID'].unique())
            col1.metric('Entregadores úncios', delivery_unique)                                  

        with col2:
            avg_distance = distance(df1, fig=False)
            col2.metric('A distância média das entregas', avg_distance)
          
        with col3:
            df_aux = avg_std_time_delivery(df1, 'Yes',op='avg_time')
            col3.metric('Tempo médio c/ Festival', df_aux)

        with col4:
            df_aux = avg_std_time_delivery(df1,'Yes', op='std_time')
            col4.metric('Std de entrega c/ Festival', df_aux)

        with col5:
            df_aux = avg_std_time_delivery(df1, 'No',op='avg_time')
            col5.metric('Tempo médio s/ Festival', df_aux)

        with col6:
            df_aux = avg_std_time_delivery(df1,'No', op='std_time')
            col6.metric('Std de entrega s/ Festival', df_aux)


    with st.container():
        st.markdown("""---""")
        st.title("Delivey mean time")
        col1, col2 = st.columns(2)
        with col1:
            fig = avg_std_time_graph(df1)
            st.plotly_chart(fig)

        with col2:
            cols = ['City', 'Time_taken(min)', 'Type_of_order']
            df_aux = df1.loc[:, cols].groupby(['City', 'Type_of_order']).agg({'Time_taken(min)':['mean', 'std']})
            df_aux.columns = ['avg_time', 'std_time']
            df_aux = df_aux.reset_index()
            st.dataframe(df_aux)


    with st.container():
        st.markdown("""---""")
        st.title("Delivey mean disntance")
        col1, col2 = st.columns(2)
        with col1:
            fig=distance(df1, fig=True)
            st.plotly_chart(fig)
            
        with col2:
            fig = avg_std_time_on_traffic(df1)
            st.plotly_chart(fig)
            

    
























