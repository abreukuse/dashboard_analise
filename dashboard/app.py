# import os
import streamlit as st
import pandas as pd
from tabelas.tabela_cruzamentos import criar_tabela
from plotnine import (ggplot, aes, facet_wrap, 
                      geom_bar, coord_flip,
                      theme, geom_text, element_blank, 
                      after_stat, element_text, element_rect, 
                      position_dodge)

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


def grafico_barra(tabela, variavel):

	# Pegar o tamanho da maior string para ajustar as labels
    maior_label = max([len(longer) 
					   for longer in tabela.index 
					   if '\n' not in longer])

    tabela = ajustes_tabela(tabela)

    figura = (
                ggplot(tabela, aes(x=variavel, y='Total'))

                + geom_bar(stat='identity', fill='#1fa8a9', width=0.4)

                + coord_flip()
                
                + theme(
                    axis_ticks = element_blank(),
                    axis_title_x = element_blank(),
                    axis_title_y = element_blank(),
                    axis_text_x = element_blank(),
                    axis_text_y = element_text(
                                               ha='center', 
                                               size=10, 
                                               margin={'r':maior_label*2}
                                               ),
                    panel_border = element_blank(),

                )

                + geom_text(
                    aes(label='Total'),
                    position=position_dodge(width=2),
                    color='black',
                    format_string='{}%',
                    nudge_y=1.7,
                    size=13

                )
                
            );

    return figura


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

                + geom_bar(stat='identity', fill='#1fa8a9')

                + facet_wrap(f'~{cruzamento}', ncol=n_cols)

                + coord_flip()

                + theme(
                		figure_size=(width, hight), 
                        axis_title_x=element_blank(),
                        axis_title_y=element_blank(),
                        axis_ticks=element_blank()
                        )
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

		return tabela.astype('int32')

tabela = tabela_cruzada()

if tabela is not None:
	path_plot_barras = 'dashboard/plot_barras.png'
	st.header(f'{variavel}')
	plot_barras = grafico_barra(tabela, variavel)
	plot_barras.save(filename=path_plot_barras)
	st.image(path_plot_barras, width=None)


	path_plot_facetado = 'dashboard/plot_facetado.png'
	st.header(f'{variavel} | {cruzamento}')
	plot_facetado = grafico_facetado(tabela, variavel, cruzamento)
	plot_facetado.save(filename=path_plot_facetado)
	st.image(path_plot_facetado, width=None)
