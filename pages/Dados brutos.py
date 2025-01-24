import streamlit as st
import requests
import pandas as pd
import time
from Dashboard import load_data

@st.cache_data
def convert_csv(df):
    return df.to_csv(index = False).encode("UTF-8")

def success_msg():
    success = st.success("Arquivo baixado com sucesso!", icon="✅")
    time.sleep(5)
    success.empty()

st.title('DADOS BRUTOS')

data = load_data(query_string = None)
data["Frete"] = data["Frete"].round(2)

with st.expander('Colunas'):
    columns = st.multiselect('Selecione as colunas', list(data.columns), list(data.columns))

st.sidebar.title('Filtros')
with st.sidebar.expander('Nome do produto'):
    products = st.multiselect('Selecione os produtos', data['Produto'].unique(), data['Produto'].unique())
with st.sidebar.expander('Categoria do Produto'):
    categories = st.multiselect('Categoria do produto', data['Categoria do Produto'].unique(), data['Categoria do Produto'].unique())
with st.sidebar.expander('Preço do produto'):
    price = st.slider('Selecione o preço', 0.0, data['Preço'].max(), (0.0, data['Preço'].max()))
with st.sidebar.expander('Frete'):
    shipping = st.slider('Valor do frete', data['Frete'].min(), data['Frete'].max(), (data['Frete'].min(), data['Frete'].max()))
with st.sidebar.expander('Data da compra'):
    sale_date = st.date_input('Selecione a data', (data['Data da Compra'].min(), data['Data da Compra'].max()))
with st.sidebar.expander('Vendedor'):
    sellers = st.sidebar.multiselect("Vendedores", data["Vendedor"].unique(), data["Vendedor"].unique())
with st.sidebar.expander('Tipo de pagamento'):
    payment_method = st.sidebar.multiselect("Tipo de pagamento", data["Tipo de pagamento"].unique(), data["Tipo de pagamento"].unique())
with st.sidebar.expander('Parcelamento'):
    qt_rates = st.slider('Selecione a quantidade de parcelas', 1, 24, (1,24))
with st.sidebar.expander('Local da venda'):
    sale_place = st.sidebar.multiselect("Estados", data["Local da compra"].unique(), data["Local da compra"].unique())
with st.sidebar.expander('Avaliação da venda'):
    rating = st.slider('Selecione a avaliação da compra',1,5, (1,5))

query = '''
Produto in @products and \
`Categoria do Produto` in @categories and \
@price[0] <= Preço <= @price[1] and \
@shipping[0] <= Frete <= @shipping[1] and \
@sale_date[0] <= `Data da Compra` <= @sale_date[1] and \
@rating[0]<= `Avaliação da compra` <= @rating[1] and \
`Tipo de pagamento` in @payment_method and \
`Local da compra` in @sale_place and \
@qt_rates[0] <= `Quantidade de parcelas` <= @qt_rates[1] and \
Vendedor in @sellers
'''

filtered_data = data.query(query)
filtered_data = filtered_data[columns]

st.dataframe(filtered_data)

st.markdown(f"A tabela possui :blue[{filtered_data.shape[0]}] e :blue[{filtered_data.shape[1]}] colunas")
st.markdown("Escreva um nome para o arquivo")

col1, col2 = st.columns(2)
with col1:
    file_name = st.text_input("", label_visibility="collapsed", value = "dados")
    file_name += ".csv"
with col2:
    st.download_button("Fazer download da tabela em CSV", data = convert_csv(filtered_data), file_name = file_name, mime = "text/csv", on_click = success_msg)