################################ Import libs ################################
import pandas as pd
pd.set_option('display.max_columns', None)
import inflection
import folium
import streamlit as st
from PIL import Image
import plotly.express as px
from streamlit_folium import folium_static


################################ Import dataset ################################
df_raw = pd.read_csv('zomato.csv')
df = df_raw.copy()


################################ Funções ################################

#Preenchimento do nome dos países
#Essa função acessa a coluna 'country_code' e substitui os numeros de cada país pelo seu nome
COUNTRIES = {
  1: "India",
  14: "Australia",
  30: "Brazil",
  37: "Canada",
  94: "Indonesia",
  148: "New Zeland",
  162: "Philippines",
  166: "Qatar",
  184: "Singapure",
  189: "South Africa",
  191: "Sri Lanka",
  208: "Turkey",
  214: "United Arab Emirates",
  215: "England",
  216: "United States of America",
}
def country_name(country_id):
  return COUNTRIES[country_id]

#Criação do Tipo de Categoria de Comida
#Essa função acessa a coluna 'price_range' e substitui os numeros de cada nível de preço por um nome
def create_price_tye(price_range):
    if price_range == 1:
        return "cheap"
    elif price_range == 2:
        return "normal"
    elif price_range == 3:
        return "expensive"
    else:
        return "gourmet"

#Criação do nome das Cores
#Essa função acessa a coluna 'color_code' e substitui os códigos de cada cor pelo seu nome
COLORS = {
"3F7E00": "darkgreen",
"5BA829": "green",
"9ACD32": "lightgreen",
"CDD614": "orange",
"FFBA00": "red",
"CBCBC8": "darkred",
"FF7800": "darkred",
}
def color_name(color_code):
    return COLORS[color_code]


#Renomear colunas do dataframe
#Essa função acessa todas as colunas do dataframe e:
      #- remove espaços e substitui por _
      #- tira as letras maiusculas por letras minusculas
def rename_columns(df):
  df = df.copy()
  title = lambda x: inflection.titleize(x)
  snakecase = lambda x: inflection.underscore(x)
  spaces = lambda x: x.replace(" ", "")
  cols_old = list(df.columns)
  cols_old = list(map(title, cols_old))
  cols_old = list(map(spaces, cols_old))
  cols_new = list(map(snakecase, cols_old))
  df.columns = cols_new
  return df

################################ Fim das Funções ################################

################################ Limpeza do Dataset ################################

#renomeando as colunas
df = rename_columns(df)

#convertendo tipos de colunas
df['restaurant_id'] = df['restaurant_id'].astype(int)
df['cuisines'] = df['cuisines'].astype(str)

#trocando os valores pelos numeros das colunas e separando os nomes em cada coluna
df['country_code'] = df['country_code'].apply(lambda x: country_name(x))
df['rating_color'] = df['rating_color'].apply(lambda x: color_name(x))
df['price_range'] = df['price_range'].apply(lambda x: create_price_tye(x))
df["cuisines"] = df.loc[:, "cuisines"].apply(lambda x: x.split(",")[0])

#limpando valores nulos
linhas_selecionadas = df['cuisines'] != 'nan' 
df = df.loc[linhas_selecionadas, :]
linhas_selecionadas2 = df['cuisines'] != '' 
df = df.loc[linhas_selecionadas, :]
df.dropna(axis=0,how='any')

#limpando coluna com apenas um valor
df = df.drop('switch_to_order_menu', axis=1, inplace=False)

#tirando linhas duplicadas
df.drop_duplicates(inplace=True)

#resetando index
df = df.reset_index(drop=True)

df1 = df.copy()

################################ Fim da Limpeza do Dataset ################################

st.set_page_config(page_title='Home',page_icon='🍕',layout='wide')

################################ Inicio da Sidebar ################################

st.sidebar.markdown( '# Fome Zero' )

st.sidebar.markdown( """---""" )

################################ Fim da Sidebar ################################

################################ Inicio do Layout ################################

st.write('# Fome Zero!')

st.markdown(
    """
    ## O Melhor lugar para encontrar seu mais novo restaurante favorito!
    ### Temos as seguintes marcas dentro da nossa plataforma:
    """
)

with st.container():
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        col1.metric('Restaurantes Cadastrados', df1['restaurant_id'].nunique())
        
    with col2:
        col2.metric('Países Cadastrados' , df1['country_code'].nunique())
        
    with col3:
        col3.metric('Cidades cadastradas' , df1['city'].nunique())
        
    with col4:
        col4.metric('Avaliações feitas', df1['votes'].sum())
        
    with col5:
        col5.metric('Tipos de culinari oferecida' , df1['cuisines'].nunique())
        
with st.container():
    dfaux = (df1.loc[: , ['city' , 'country_code' , 'latitude' , 'longitude', 'average_cost_for_two' , 'aggregate_rating']]
             .groupby( [ 'city' , 'country_code'])
             .median()
             .reset_index())

    map = folium.Map()

    for index , location_info in dfaux.iterrows():
        folium.Marker( [location_info['latitude'], 
                        location_info['longitude']],
                        popup=location_info[['average_cost_for_two' , 'aggregate_rating']]).add_to(map)

    folium_static( map, width= 1024, height=600)


################################ Fim do Layout ################################
