import streamlit as st
import pandas as pd
import numpy as np
from funcoes.tabela_cruzamentos import criar_tabela
from plotnine import (ggplot, aes, facet_wrap, 
					  geom_bar, coord_flip,
					  theme, geom_text, element_blank, 
					  after_stat, element_text, element_rect, 
					  position_dodge, scale_x_discrete)

from iteround import saferound

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
		return pd.DataFrame(columns=['Faça o upload do banco de dados'])

DATAFRAME = load_data()
st.dataframe(DATAFRAME.head())

@st.cache(show_spinner=False)
def opcoes_dropdown(df):
	opcoes = df.select_dtypes('object').columns
	return list(opcoes)

@st.cache(show_spinner=False)
def ajustes_tabela(tabela, variavel):
    table = tabela.iloc[:-1]
    table = table.reset_index()
    ordem = table[variavel].to_list()[::-1]
    table[variavel] = pd.Categorical(table[variavel], categories=ordem)
    
    return table

@st.cache(show_spinner=False)
def tabela_formato_longo(tabela, variavel, cruzamento):
	table = pd.melt(tabela, id_vars=[variavel], 
					value_vars=tabela.columns[2:],
					var_name=cruzamento,
					value_name='Valores'
					)
	return table


@st.cache(show_spinner=False)
def calcular_base(dados, cruzamento):
	parcial = dados.groupby(cruzamento)['peso'].sum()
	total = np.sum(parcial)
	base = pd.Series(saferound((parcial/total)*100, 0), 
					 index=parcial.index,
					 name='Base').astype('int32').reset_index()

	base['Base'] = base['Base'].apply(lambda x: f'Base: {x}%')
	return base


def grafico_barra(tabela, variavel, mostrar_porcentagem):

	# Pegar o tamanho da maior string para ajustar as labels
	maior_label = max([len(longer) 
					   for longer in tabela.index 
					   if '\n' not in longer])

	n_cols = len(tabela.columns[1:])
	width = 3*n_cols
	hight = n_cols

	if width > 25: width = 25

	tabela = ajustes_tabela(tabela, variavel)

	format_string = '{}%' if mostrar_porcentagem else '{}'

	figura = (
				ggplot(tabela, aes(x=variavel, y='Total'))

				+ theme_bw(base_family='Montserrat')

				+ geom_bar(stat='identity', fill='#1fa8a9', width=0.4, alpha=0.85)

				# + scale_x_discrete(limits=tabela[variavel].to_list()[::-1])

				+ coord_flip()
				
				+ theme(
					figure_size=(width, hight),
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
					format_string=format_string,
					nudge_y=1.7,
					size=13

				)
				
			);

	return figura


def grafico_facetado(tabela, variavel, cruzamento, mostrar_porcentagem):

	maior_label = max([len(longer) 
					   for longer in tabela.index 
					   if '\n' not in longer])

	n_cols = len(tabela.columns[1:])
	width = 3*n_cols
	hight = n_cols

	if width > 25: width = 25

	colunas_do_cruzamento = list(tabela.columns[1:])

	tabela = ajustes_tabela(tabela, variavel)
	tabela = tabela_formato_longo(tabela, variavel, cruzamento)

	base = calcular_base(DATAFRAME, cruzamento)
	tabela = tabela.merge(base, on=cruzamento)
	tabela[cruzamento] = tabela[cruzamento].astype('category').cat.reorder_categories(colunas_do_cruzamento)
	
	format_string = '{}%' if mostrar_porcentagem else '{}'

	figura = (
				ggplot(tabela, aes(x=variavel, y='Valores'))

				+ theme_bw(base_family='Montserrat')

				+ geom_bar(stat='identity', fill='#1fa8a9', width=0.4, alpha=0.85)

				+ facet_wrap(f'~{cruzamento} + Base', ncol=n_cols)

				+ coord_flip()

				+ theme(
						figure_size=(width, hight), 
						axis_ticks=element_blank(),
						axis_title_x=element_blank(),
						axis_title_y=element_blank(),
						axis_text_x = element_blank(),
						axis_text_y = element_text(
													ha='center', 
													size=10, 
													margin={'r':maior_label*3}
												),           
						)
				
				+ geom_text(
					aes(label='Valores'),
					position=position_dodge(width=2),
					color='black',
					format_string=format_string,
					nudge_y=2.5,
					size=10

				)
			)
	
	return figura

variavel = st.sidebar.selectbox('Selecionar variável', 
								options=[''] + opcoes_dropdown(DATAFRAME))

cruzamento = st.sidebar.selectbox('Selecionar o cruzamento', 
								  options=[''] + opcoes_dropdown(DATAFRAME))


def tabela_cruzada(ordem_indices=[], ordem_colunas=[]):
	tabela = criar_tabela(DATAFRAME,
						  variavel=variavel,
						  cruzamento=cruzamento,
						  mostrar_porcentagem=mostrar_porcentagem)

	indices = list(tabela.index[:-1])
	colunas = list(tabela.columns[1:])

	if (len(ordem_indices) == len(indices)) and (len(ordem_colunas) == len(colunas)):
		primeira_coluna = list(tabela.columns[:1])
		ultimo_indice = list(tabela.index[-1:])
		tabela = tabela.loc[ordem_indices + ultimo_indice, primeira_coluna + ordem_colunas]

	return tabela.astype('int32')


if __name__ == '__main__':
	if variavel and cruzamento:
		mostrar_porcentagem = st.sidebar.checkbox('Porcentagem', 
												  value=True)

		tabela = tabela_cruzada()

		indices = list(tabela.index[:-1])
		nova_ordem_indices = st.sidebar.multiselect('Nova ordem das linhas', 
													options=indices)

		colunas = list(tabela.columns[1:])
		nova_ordem_colunas = st.sidebar.multiselect('Nova ordem das colunas',
													options=colunas)

		executar = st.sidebar.button('Executar')
		if executar:
			if (len(nova_ordem_indices) == len(indices)) and (len(nova_ordem_colunas) == len(colunas)):
				tabela = tabela_cruzada(nova_ordem_indices, nova_ordem_colunas)
				executar = False
			else:
				print('era pra vim aqui')
				st.sidebar.write('Selecione todos os itens\nnas linhas e colunas')
				executar = False

		
		st.header('\n\nTabela cruzada')
		st.dataframe(tabela)

		if tabela is not None:

			# Gráfico de barras
			path_plot_barras = 'dashboard/plot_barras.png'
			st.header(f'{variavel}')
			plot_barras = grafico_barra(tabela, 
										variavel, 
										mostrar_porcentagem)
			
			plot_barras.save(filename=path_plot_barras)
			st.image(path_plot_barras, width=None)

			# Gráfico faetado
			path_plot_facetado = 'dashboard/plot_facetado.png'
			st.header(f'{variavel} | {cruzamento}')
			plot_facetado = grafico_facetado(tabela, 
											 variavel, 
											 cruzamento, 
											 mostrar_porcentagem)

			plot_facetado.save(filename=path_plot_facetado)
			st.image(path_plot_facetado, width=None)

		