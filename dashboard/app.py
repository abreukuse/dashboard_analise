import streamlit as st
import pandas as pd
import numpy as np
from funcoes.tabela_cruzamentos import criar_tabela
from funcoes.graficos import grafico_barra, grafico_facetado

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

variavel = st.sidebar.selectbox('Selecionar variável', 
								options=[''] + opcoes_dropdown(DATAFRAME))

cruzamento = st.sidebar.selectbox('Selecionar o cruzamento', 
								  options=[''] + opcoes_dropdown(DATAFRAME))


def tabela_cruzada(ordem_indices=[], ordem_colunas=[]):
	tabela = criar_tabela(DATAFRAME,
						  variavel=variavel,
						  cruzamento=cruzamento,
						  mostrar_porcentagem=mostrar_porcentagem)

	primeira_coluna = list(tabela.columns[:1])
	ultimo_indice = list(tabela.index[-1:])

	if len(ordem_indices) != 0 and len(ordem_colunas) == 0:
		tabela = tabela.loc[ordem_indices + ultimo_indice, :]

	if len(ordem_indices) == 0 and len(ordem_colunas) != 0:
		tabela = tabela.loc[:, primeira_coluna + ordem_colunas]

	if ordem_indices and ordem_colunas:
		tabela = tabela.loc[ordem_indices + ultimo_indice, primeira_coluna + ordem_colunas]

	return tabela.astype('int32')


if __name__ == '__main__':
	if variavel and cruzamento:
		if variavel == cruzamento:
			st.write('Variável e cruzamento são iguais. Troque um dos dois.')

		else:
			mostrar_porcentagem = st.sidebar.checkbox('Porcentagem', 
													  value=True)

			tabela = tabela_cruzada()

			indices = list(tabela.index[:-1])
			nova_ordem_indices = st.sidebar.multiselect('Nova ordem das linhas', 
														options=indices)

			colunas = list(tabela.columns[1:])
			nova_ordem_colunas = st.sidebar.multiselect('Nova ordem das colunas',
														options=colunas)

		
			if nova_ordem_indices or nova_ordem_colunas:
				tabela = tabela_cruzada(nova_ordem_indices, nova_ordem_colunas)

			
			st.header('\n\nTabela cruzada')
			show_table = tabela.loc[tabela.index[:-1]].copy()
			show_table = show_table.append(pd.Series(np.sum(show_table), name='Total'))

			st.dataframe(show_table)

			if tabela is not None:

				n_cols = len(tabela.columns[1:])
				largura_default = 10
				altura_default = 5

				# Gráfico de barras
				path_plot_barras = 'dashboard/plot_barras.png'
				st.header(f'{variavel}')

				bar_plot_container = st.beta_container()
				col1_bar, col2_bar, empty = st.beta_columns([1,1,5])

				largura_bar_plot = col1_bar.slider(label='Largura', 
					min_value=1, 
					max_value=20, 
					value=largura_default, 
					step=1,
					key=1)

				altura_bar_plot = col2_bar.slider(label='Altura', 
					min_value=1, 
					max_value=20, 
					value=altura_default, 
					step=1,
					key=2)

				plot_barras = grafico_barra(tabela, 
											variavel, 
											mostrar_porcentagem,
											largura_bar_plot, 
											altura_bar_plot)
				
				plot_barras.save(filename=path_plot_barras)
				bar_plot_container.image(path_plot_barras, width=None)
				

				# Gráfico facetado
				path_plot_facetado = 'dashboard/plot_facetado.png'
				st.header(f'{variavel} | {cruzamento}')

				facet_plot_container = st.beta_container()
				col1_facet, col2_facet, empty = st.beta_columns([1,1,5])

				largura_facet_plot = col1_facet.slider(label='Largura', 
					min_value=1, 
					max_value=20, 
					value=largura_default, 
					step=1,
					key=3)

				altura_facet_plot = col2_facet.slider(label='Altura', 
					min_value=1, 
					max_value=20, 
					value=altura_default, 
					step=1,
					key=4)

				nrow_default = 1
				ncol_default = n_cols

				nrow = col1_facet.number_input(label='Trazer paineis para baixo', 
					value = nrow_default, 
					step=1, 
					min_value=1, 
					max_value=len(colunas))
				
				ncol = ncol_default-nrow+1
				
				plot_facetado = grafico_facetado(DATAFRAME,
												 tabela, 
												 variavel, 
												 cruzamento, 
												 mostrar_porcentagem,
												 largura_facet_plot,
												 altura_facet_plot,
												 nrow,
												 ncol)

				plot_facetado.save(filename=path_plot_facetado)
				facet_plot_container.image(path_plot_facetado, width=None)

				

			