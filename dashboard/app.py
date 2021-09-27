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
			plot_facetado = grafico_facetado(DATAFRAME,
											 tabela, 
											 variavel, 
											 cruzamento, 
											 mostrar_porcentagem)

			plot_facetado.save(filename=path_plot_facetado)
			st.image(path_plot_facetado, width=None)

		