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

#Essa função retorna um gráfico de barras com as 10 cidades com mais restaurantes registrados
def dftops(df1):
    dfaux = (df1.loc[: , ['restaurant_id', 'city','country_code']]
             .groupby(['country_code','city'])
             .nunique()
             .reset_index()
             .sort_values('restaurant_id', ascending=False))
    dftops = dfaux.head(10)
    fig = px.bar(dftops, x='city', y='restaurant_id', title = 'Top 10 cidades com mais restaurantes na base de dados', color='country_code', text_auto=True)   
    return fig

#Essa função retorna um gráfico de barras com os 7 melhores restaurantes com avalição média acima de 4.0
def avg_mean_4(df1):
    dfaux_rating1 = df1.copy()
    lines_rating1 = dfaux_rating1['aggregate_rating'] > 4
    dfaux_rating1 = dfaux_rating1.loc[lines_rating1, :].copy()
    df_good_rating = (dfaux_rating1.loc[: , ['aggregate_rating', 'city','country_code']]
                          .groupby(['city','country_code'])
                          .count()
                          .reset_index()
                          .sort_values('aggregate_rating', ascending=False))
    city_with_more_good_restaurants = df_good_rating.head(7)
    fig = px.bar(city_with_more_good_restaurants , x='city', y='aggregate_rating' , title='Top 7 restaurantes com média de avaliação maior que 4', color='city', text_auto=True)
    return fig

#Essa função retorna um gráfico de barras com os 7 melhores restaurantes com avalição média abaixo de 2.5
def avg_mean_2(df1):
    dfaux_rating2 = df1.copy()
    lines_rating2 = dfaux_rating2['aggregate_rating'] < 2.5
    dfaux_rating2 = dfaux_rating2.loc[lines_rating2, :].copy()
    df_bad_rating = (dfaux_rating2.loc[: , ['aggregate_rating', 'city','country_code']]
                         .groupby(['city','country_code'])
                         .count()
                         .reset_index()
                         .sort_values('aggregate_rating', ascending=False))
    city_with_more_bad_restaurants = df_bad_rating.head(7)
    fig = px.bar(city_with_more_bad_restaurants, x='city', y='aggregate_rating', color= 'city', title='Cidades com restaurantes com média abaixo de 2,5', text_auto=True)
    return fig

#Essa função retorna um gráfico de barras com as 10 cidades com mais tipos de culinarias distintas
def diferent_cuisines(df1):
    dfaux_cuisines = (df1.loc[:,['city', 'cuisines','country_code']]
                            .groupby(['city','country_code'])
                            .nunique()
                            .sort_values('cuisines', ascending=False)
                            .reset_index())
    df_diferent_cuisines = dfaux_cuisines.head(10)
    fig=px.bar(df_diferent_cuisines, x='city', y='cuisines', color = 'city', title= 'Top 10 cidades com mais tipos culinarios distintos', text_auto=True)
    return fig

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

################################ Inicio da Sidebar ################################
st.sidebar.markdown( 'Filtros' )
country_options = st.sidebar.multiselect(
    'Escolha os Paises que deseja visualizar as Informações?', 
    ['Philippines', 'Brazil', 'Australia', 'United States of America',
       'Canada', 'Singapure', 'United Arab Emirates', 'India',
       'Indonesia', 'New Zeland', 'England', 'Qatar', 'South Africa',
       'Sri Lanka', 'Turkey'], 
    default=['Brazil', 'Australia', 'Canada', 'England', 'Qatar', 'South Africa'] )

st.sidebar.markdown( """---""" )

linhas_selecionadas = df1['country_code'].isin( country_options )
df1 = df1.loc[linhas_selecionadas, :]

################################ Fim da Sidebar ################################

################################ Inicio do Layout ################################

st.markdown('# 🏤Visão Cidades')
with st.container():
    fig = dftops(df1)
    st.plotly_chart(fig, theme = None, use_container_width=True)
    
with st.container():
    col1,col2 = st.columns(2)
    
    with col1: 
        fig = avg_mean_4(df1)
        st.plotly_chart(fig, theme = None, use_container_width=True)
    
    with col2:
        fig = avg_mean_2(df1)
        st.plotly_chart(fig, theme = None, use_container_width=True)

with st.container():
    fig = diferent_cuisines(df1)
    st.plotly_chart(fig, theme = None, use_container_width=True)
    
################################ Fim do Layout ################################