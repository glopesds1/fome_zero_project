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

################################ Inicio da Sidebar ################################

st.markdown( '# 🍽 Visão Culinaria' )
st.sidebar.markdown( 'Filtros' )
country_options = st.sidebar.multiselect(
    'Escolha os Paises que deseja visualizar as Informações', 
    ['Philippines', 'Brazil', 'Australia', 'United States of America',
       'Canada', 'Singapure', 'United Arab Emirates', 'India',
       'Indonesia', 'New Zeland', 'England', 'Qatar', 'South Africa',
       'Sri Lanka', 'Turkey'], 
    default=['Brazil', 'Australia', 'Canada', 'England', 'Qatar', 'South Africa'] )

st.sidebar.markdown( """---""" )

cuisines = st.sidebar.multiselect(
    'Escolha os tipos de culinarias que deseja visualizar as informações', 
    ['Italian', 'European', 'Filipino', 'American', 'Korean', 'Pizza',
       'Taiwanese', 'Japanese', 'Coffee', 'Chinese', 'Seafood',
       'Singaporean', 'Vietnamese', 'Latin American', 'Healthy Food',
       'Cafe', 'Fast Food', 'Brazilian', 'Argentine', 'Arabian', 'Bakery',
       'Tex-Mex', 'Bar Food', 'International', 'French', 'Steak',
       'German', 'Sushi', 'Grill', 'Peruvian', 'North Eastern',
       'Ice Cream', 'Burger', 'Mexican', 'Vegetarian', 'Contemporary',
       'Desserts', 'Juices', 'Beverages', 'Spanish', 'Thai', 'Indian',
       'Mineira', 'BBQ', 'Mongolian', 'Portuguese', 'Greek', 'Asian',
       'Author', 'Gourmet Fast Food', 'Lebanese', 'Modern Australian',
       'African', 'Coffee and Tea', 'Australian', 'Middle Eastern',
       'Malaysian', 'Tapas', 'New American', 'Pub Food', 'Southern',
       'Diner', 'Donuts', 'Southwestern', 'Sandwich', 'Irish',
       'Mediterranean', 'Cafe Food', 'Korean BBQ', 'Fusion', 'Canadian',
       'Breakfast', 'Cajun', 'New Mexican', 'Belgian', 'Cuban', 'Taco',
       'Caribbean', 'Polish', 'Deli', 'British', 'California', 'Others',
       'Eastern European', 'Creole', 'Ramen', 'Ukrainian', 'Hawaiian',
       'Patisserie', 'Yum Cha', 'Pacific Northwest', 'Tea', 'Moroccan',
       'Burmese', 'Dim Sum', 'Crepes', 'Fish and Chips', 'Russian',
       'Continental', 'South Indian', 'North Indian', 'Salad',
       'Finger Food', 'Mandi', 'Turkish', 'Kerala', 'Pakistani',
       'Biryani', 'Street Food', 'Nepalese', 'Goan', 'Iranian', 'Mughlai',
       'Rajasthani', 'Mithai', 'Maharashtrian', 'Gujarati', 'Rolls',
       'Momos', 'Parsi', 'Modern Indian', 'Andhra', 'Tibetan', 'Kebab',
       'Chettinad', 'Bengali', 'Assamese', 'Naga', 'Hyderabadi', 'Awadhi',
       'Afghan', 'Lucknowi', 'Charcoal Chicken', 'Mangalorean',
       'Egyptian', 'Malwani', 'Armenian', 'Roast Chicken', 'Indonesian',
       'Western', 'Dimsum', 'Sunda', 'Kiwi', 'Asian Fusion', 'Pan Asian',
       'Balti', 'Scottish', 'Cantonese', 'Sri Lankan', 'Khaleeji',
       'South African', 'Drinks Only', 'Durban', 'World Cuisine',
       'Izgara', 'Home-made', 'Giblets', 'Fresh Fish', 'Restaurant Cafe',
       'Kumpir', 'Döner', 'Turkish Pizza', 'Ottoman', 'Old Turkish Bars',
       'Kokoreç'], default=['Home-made', 'BBQ', 'Japanese', 'Brazilian', 'Arabian', 'American','Italian'])

feltro = st.sidebar.slider(
    'Até qual valor?',
    value=10,
    min_value=1,
    max_value=20
)

st.sidebar.markdown( """---""" )

linhas_selecionadas = df1['country_code'].isin( country_options )
df1 = df1.loc[linhas_selecionadas, :]

linhas_selecionadas1 = df1['restaurant_id'] = feltro
df = df.loc[linhas_selecionadas1, :]

linhas_selecionadas2 = df1['cuisines'].isin( cuisines )
df1 = df1.loc[linhas_selecionadas2, :]

################################ Fim da Sidebar ################################

################################ Inicio do Layout ################################
with st.container():
    st.markdown('### Melhores Restaurantes dos Principais tipos Culinários')
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        dfaux_melhores_cul = (df1.loc[:,['restaurant_name', 'aggregate_rating', 'cuisines']]
                              .groupby(['cuisines','restaurant_name'])
                              .mean()
                              .reset_index()
                              .sort_values('aggregate_rating', ascending=False))
        col1.metric(dfaux_melhores_cul.iloc[0,1],'{}/5.0'.format(dfaux_melhores_cul.iloc[0,2]))
        
    with col2:
        dfaux_melhores_cul = (df1.loc[:,['restaurant_name', 'aggregate_rating', 'cuisines']]
                              .groupby(['cuisines','restaurant_name'])
                              .mean()
                              .reset_index()
                              .sort_values('aggregate_rating', ascending=False))
        col2.metric(dfaux_melhores_cul.iloc[1,1],'{}/5.0'.format(dfaux_melhores_cul.iloc[1,2]))
        
    with col3:
        dfaux_melhores_cul = (df1.loc[:,['restaurant_name', 'aggregate_rating', 'cuisines']]
                              .groupby(['cuisines','restaurant_name'])
                              .mean()
                              .reset_index()
                              .sort_values('aggregate_rating', ascending=False))
        col3.metric(dfaux_melhores_cul.iloc[2,1],'{}/5.0'.format(dfaux_melhores_cul.iloc[2,2]))
        
    with col4:
        dfaux_melhores_cul = (df1.loc[:,['restaurant_name', 'aggregate_rating', 'cuisines']]
                              .groupby(['cuisines','restaurant_name'])
                              .mean()
                              .reset_index()
                              .sort_values('aggregate_rating', ascending=False))
        col4.metric(dfaux_melhores_cul.iloc[3,1],'{}/5.0'.format(dfaux_melhores_cul.iloc[3,2]))
        
    with col5:
        dfaux_melhores_cul = (df1.loc[:,['restaurant_name', 'aggregate_rating', 'cuisines']]
                              .groupby(['cuisines','restaurant_name'])
                              .mean()
                              .reset_index()
                              .sort_values('aggregate_rating', ascending=False))
        col5.metric(dfaux_melhores_cul.iloc[4,1],'{}/5.0'.format(dfaux_melhores_cul.iloc[4,2]))
        
        
with st.container():
    st.markdown('## Top ' + str(feltro) + ' restaurantes')
    top_melhores_restaurantes = (df1.loc[:,['aggregate_rating', 'cuisines', 'restaurant_name', 'country_code', 'city','average_cost_for_two','votes']]
                                   .groupby(['cuisines', 'restaurant_name', 'country_code', 'city','average_cost_for_two','votes'])
                                   .max()
                                   .sort_values('aggregate_rating', ascending=False).head(feltro))
    st.dataframe(top_melhores_restaurantes, use_container_width=True)
        
        
with st.container():
    col1, col2 = st.columns(2)
    
    with col1:
        top_melhores_culinarias = (df1.loc[:,['aggregate_rating', 'cuisines']].groupby('cuisines')
                                   .mean()
                                   .reset_index()
                                   .sort_values('aggregate_rating', ascending=False)
                                   .head(feltro))

        fig = px.bar(top_melhores_culinarias, x='cuisines', y='aggregate_rating', title='Top ' + str(feltro) + ' melhores culinarias', text_auto=True)
        
        st.plotly_chart(fig, theme = None, use_container_width=True)
        
    with col2:
        top_piores_culinarias = (df1.loc[:,['aggregate_rating', 'cuisines']].groupby('cuisines')
                                 .mean()
                                 .reset_index()
                                 .sort_values('aggregate_rating', ascending=True)
                                 .head(feltro))

        fig = px.bar(top_piores_culinarias, x='cuisines', y='aggregate_rating', title='Top ' + str(feltro) + ' piores culinarias', text_auto=True)
        st.plotly_chart(fig, theme = None, use_container_width=True)

################################ Fim do Layout ################################
            