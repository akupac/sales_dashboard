import streamlit as st
import requests
import pandas as pd
import plotly.express as px

st.set_page_config(layout = "wide")

@st.cache_data
def load_data(query_string = None):
    url = "https://labdados.com/produtos"
    try: 
        response = requests.get(url) if query_string is None else requests.get(url, params= query_string)
        data = pd.DataFrame.from_dict(response.json())
        data["Data da Compra"] = pd.to_datetime(data["Data da Compra"], format = "%d/%m/%Y")
        return data
    except Exception as e:
        print(e)
        return None
    

def format_number(value, prefix = ""):
    for unit in ["", "m"]:
        if value < 1000:
            return f"{prefix}{value:.2f}{unit}"
        value /= 1000
    return f'{prefix}{value:.2f}M'

# SIDEBAR

st.sidebar.title("Filtros")
regions = ['Brasil', 'Centro-Oeste', 'Nordeste', 'Norte', 'Sudeste', 'Sul']
region = st.sidebar.selectbox("Região", regions)
region = "" if region == 'Brasil' else region

all_years = st.sidebar.checkbox('Dados de todo o período', value = True)
yr = None if all_years else st.sidebar.slider('Ano', 2020, 2023)
query_string = {'regiao':region.lower(), 'ano':yr}

data = load_data(query_string) # API DATA ACCESS

filter_sellers = st.sidebar.multiselect("Vendedores", data["Vendedor"].unique())
data = data[data['Vendedor'].isin(filter_sellers)] if filter_sellers else data

data["Frete"] = data["Frete"].round(2)
# TABLES
## Revenue tables

revenue_states = data.groupby("Local da compra")[["Preço"]].sum().sort_values("Preço", ascending=False)
revenue_states_coords = data\
    .drop_duplicates(subset = "Local da compra")[["Local da compra", "lat", "lon"]]\
    .merge(revenue_states, left_on= "Local da compra", right_index=True)\
    .sort_values("Preço", ascending=False)
revenue_monthly = data\
    .set_index("Data da Compra")\
    .groupby(pd.Grouper(freq = "ME"))["Preço"]\
    .sum()\
    .reset_index()
revenue_monthly["Ano"] = revenue_monthly["Data da Compra"].dt.year
revenue_monthly["Mês"] = revenue_monthly["Data da Compra"].dt.month_name()

revenue_categories = data.groupby("Categoria do Produto")[["Preço"]].sum().sort_values("Preço", ascending=False)
## Sales tables
sales_states = data.groupby("Local da compra")[["Local da compra"]].value_counts().sort_values(ascending=False)
sales_states_coords = data\
    .drop_duplicates("Local da compra")[["Local da compra", "lat", "lon"]]\
    .merge(sales_states, left_on="Local da compra", right_index=True)\
    .sort_values("count", ascending=False)
sales_categories = data.groupby("Categoria do Produto")[["Categoria do Produto"]].value_counts().sort_values(ascending=False)
sales_monthly = data\
    .set_index("Data da Compra")\
    .groupby(pd.Grouper(freq = "ME"))["Preço"]\
    .count()\
    .reset_index()
sales_monthly["Ano"] = sales_monthly["Data da Compra"].dt.year
sales_monthly["Mês"] = sales_monthly["Data da Compra"].dt.month_name()

## Sellers tables

sellers = pd.DataFrame(data.groupby('Vendedor')['Preço'].agg(['sum', 'count']))

# GRAPHS

graph_revenue_map = px.scatter_geo(revenue_states_coords,
                                  lat="lat",
                                  lon="lon",
                                  scope="south america",
                                  size="Preço",
                                  template="seaborn",
                                  hover_name="Local da compra",
                                  hover_data={"lat": False, "lon": False},
                                  title="Receita por estado")

graph_revenue_monthly = px.line(revenue_monthly,
                             x="Mês",
                             y="Preço",
                             markers = True,
                             range_y=(0,revenue_monthly.max()),
                             color="Ano",
                             line_dash="Ano",
                             title="Receita mensal")
graph_revenue_monthly.update_layout(yaxis_title = "Receita")

graph_sales_monthly = px.line(sales_monthly,
                             x="Mês",
                             y="Preço",
                             markers = True,
                             range_y=(0,sales_monthly.max()),
                             color="Ano",
                             line_dash="Ano",
                             title="Vendas mensais")
graph_sales_monthly.update_layout(yaxis_title = "Qtd de vendas")

graph_revenue_states = px.bar(revenue_states.head(),
                             x = revenue_states.head().index,
                             y = "Preço",
                             text_auto=True,
                             title="Estados com mais receita"
                             )

graph_sales_states = px.bar(sales_states.head(),
                             x = sales_states.head().index,
                             y = "count",
                             text_auto=True,
                             title="Estados com mais vendas"
                             )
graph_revenue_states.update_layout(yaxis_title = 'Receita')

graph_sales_map = px.scatter_geo(sales_states_coords,
                                  lat="lat",
                                  lon="lon",
                                  scope="south america",
                                  size="count",
                                  template="seaborn",
                                  hover_name="Local da compra",
                                  hover_data={"lat": False, "lon": False},
                                  title="Vendas por estado")

graph_sales_states = px.bar(sales_states.head(),
                             x = sales_states.head().index,
                             y = "count",
                             text_auto=True,
                             title="Estados com mais vendas"
                             )

graph_revenue_categories = px.bar(revenue_categories,
                                text_auto = True,
                                title = 'Receita por categoria')
graph_revenue_categories.update_layout(yaxis_title = 'Receita')

graph_sales_categories = px.bar(sales_categories,
                                text_auto = True,
                                title = 'Vendas por categoria')
graph_sales_categories.update_layout(yaxis_title = 'Vendas')

# VISUALIZATIONS
st.title("Dashboard de vendas :shopping_trolley:")

tab1_revenue, tab2_sales, tab3_sellers = st.tabs(["Receita", "Quantidade de vendas", "Vendedores"])

with tab1_revenue:
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Receita", format_number(data["Preço"].sum(), "R$ "))
        st.plotly_chart(graph_revenue_map, use_container_width=True)
        st.plotly_chart(graph_revenue_states, use_container_width=True)

    with col2:
        st.metric("Quantidade de vendas", format_number(data.shape[0]))
        st.plotly_chart(graph_revenue_monthly, use_container_width=True)
        graph_revenue_categories.update_layout(showlegend=False)
        st.plotly_chart(graph_revenue_categories, use_container_width=True)

with tab2_sales:
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Receita", format_number(data["Preço"].sum(), "R$ "))

        st.plotly_chart(graph_sales_map, use_container_width=True)
        st.plotly_chart(graph_sales_states, use_container_width=True)       
    with col2:
        st.metric("Quantidade de vendas", format_number(data.shape[0]))
        st.plotly_chart(graph_sales_monthly, use_container_width=True)
        graph_sales_categories.update_layout(showlegend=False)
        
        st.plotly_chart(graph_sales_categories, use_container_width=True)

with tab3_sellers:
    qt_sellers = st.number_input("Quantidade de vendedores", 2, 10, 5)   
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Receita", format_number(data["Preço"].sum(), "R$ "))
        graph_revenue_sellers = px.bar(sellers[["sum"]].sort_values("sum", ascending = False).head(qt_sellers),
                                        x = "sum",
                                        y = sellers[["sum"]].sort_values("sum", ascending = False).head(qt_sellers).index,
                                        text_auto = True,
                                        title = f"Top {qt_sellers} vendedores (receita)",
                                        )
        graph_revenue_sellers.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(graph_revenue_sellers)
    with col2:
        st.metric("Quantidade de vendas", format_number(data.shape[0]))
        graph_sales_sellers = px.bar(sellers[["count"]].sort_values("count", ascending = False).head(qt_sellers),
                                        x = "count",
                                        y = sellers[["count"]].sort_values("count", ascending = False).head(qt_sellers).index,
                                        text_auto = True,
                                        title = f"Top {qt_sellers} vendedores (quantidade de vendas)"
                                        )
        graph_sales_sellers.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(graph_sales_sellers)