import streamlit as st
import pandas as pd
import numpy as np
from plotnine import (ggplot, aes, facet_wrap, 
					  geom_bar, coord_flip,
					  theme, geom_text, element_blank, 
					  after_stat, element_text, element_rect, 
					  position_dodge, scale_x_discrete)

from iteround import saferound

import plotnine
from plotnine.themes import theme_bw
plotnine.theme_set(theme_bw())


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


def grafico_facetado(banco_de_dados, tabela, variavel, cruzamento, mostrar_porcentagem):

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

	base = calcular_base(banco_de_dados, cruzamento)
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