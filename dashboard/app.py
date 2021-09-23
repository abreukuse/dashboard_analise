# import os
import streamlit as st
import pandas as pd
from tabelas.tabela_cruzamentos import criar_tabela
from plotnine import (ggplot, aes, facet_wrap, 
                      geom_bar, coord_flip,
                      theme, geom_text, element_blank, 
                      after_stat)

import plotnine
from plotnine.themes import theme_bw
plotnine.theme_set(theme_bw())

import warnings
warnings.filterwarnings("ignore")

st.set_page_config(layout='wide')

st.sidebar.image('dashboard/quaest.jpg', width=None)
st.header('Amostra dos dados')

FILE = st.sidebar.file_uploader('Upload do Bando de Dados', type=['xlsx'])

@st.cache(show_spinner=False)
def load_data():
	if FILE is not None:
		df = pd.read_excel(FILE, 
							sheet_name='dados', 
							engine='openpyxl')

		return df
	else:
		return pd.DataFrame()

DATAFRAME = load_data()
st.dataframe(DATAFRAME.head())

@st.cache(show_spinner=False)
def opcoes_dropdown(df):
	opcoes = df.select_dtypes('object').columns
	return list(opcoes)

@st.cache(show_spinner=False)
def ajustes_tabela(tabela):
    table = tabela.iloc[:-1]

    return table.reset_index()

@st.cache(show_spinner=False)
def tabela_formato_longo(tabela, variavel, cruzamento):
    table = pd.melt(tabela, id_vars=[variavel], 
                    value_vars=tabela.columns[2:],
                    var_name=cruzamento,
                    value_name='Valores'
                    )
    return table

def grafico_facetado(tabela, variavel, cruzamento):

    tabela = ajustes_tabela(tabela)
    tabela = tabela_formato_longo(tabela, variavel, cruzamento)

    n_cols = len(tabela[cruzamento].unique())
    width = 3*n_cols
    hight = n_cols

    if width > 25:
    	width = 25

    figura = (
                ggplot(tabela, aes(x=variavel, y='Valores'))
                + geom_bar(stat='identity')
                + facet_wrap(f'~{cruzamento}', ncol=n_cols)
                + coord_flip()
                + theme(figure_size=(width, hight), 
                        axis_title_x=element_blank(),
                        axis_title_y=element_blank(),
                        axis_ticks=element_blank())
            )
    
    return figura



variavel = st.sidebar.selectbox('Selecionar variável', 
							    options=[''] + opcoes_dropdown(DATAFRAME))

cruzamento = st.sidebar.selectbox('Selecionar o cruzamento', 
							      options=[''] + opcoes_dropdown(DATAFRAME))

def tabela_cruzada():
	if variavel and cruzamento:
		mostrar_porcentagem = st.sidebar.checkbox('Porcentagem', 
												  value=True)
		tabela = criar_tabela(DATAFRAME,
							  variavel=variavel,
							  cruzamento=cruzamento,
							  mostrar_porcentagem=mostrar_porcentagem)

		st.header('\n\nTabela cruzada')
		st.dataframe(tabela)

		return tabela

tabela = tabela_cruzada()

if tabela is not None:
	filePath = 'dashboard/plot.png'
	st.header('Gráfico facetado')
	plot = grafico_facetado(tabela, variavel, cruzamento)
	plot.save(filename=filePath)
	st.image(filePath, width=None)
