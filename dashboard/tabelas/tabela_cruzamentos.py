import pandas as pd
import numpy as np
from typing import Union, List
from collections import Counter
from functools import reduce
from iteround import saferound


def tabela_contingencia(dados: pd.DataFrame, 
                        linhas: Union[str, List[str]], 
                        colunas: Union[str, List[str]],
                        percentage: bool) -> pd.DataFrame:
    """
    Cria tabela de contingência.
    ----------------------------
    Parâmetros
    dados: Pandas dataframe.
    linhas, colunas: String para uma variável e lista para mais de uma variável. 
    percentage: True para mostrar o resultado em porcentagem

    Retorna um dataframe pandas com a tabela de contingência
    """

    # Passar os argumentos de string para lista se necessário
    if isinstance(linhas, str):
        linhas = [linhas]
        
    if isinstance(colunas, str):
        colunas = [colunas]
        
    # Verificar se tem variáveis repetidas entre as linhas e colunas
    variaveis_repetidas = [item for item, contagem in Counter(linhas + colunas).items() if contagem > 1]
    if len(variaveis_repetidas) > 0:
        print(f"""Por favor evite variáveis repetidas nas linhas e colunas.\nVariável repetida: '{variaveis_repetidas[0]}'.""")
    
    else:
        # Formatar as entradas para cumprir os requisitos da dunção crosstab
        linhas = [dados[item] for item in linhas]
        colunas = [dados[item] for item in colunas]

        normalizar = 'columns' if percentage else False
        multiplicar = 100 if percentage else 1

        # Criar uma tabela de cruzamento para cada "coluna" e armazenar na lista dataframes
        dataframes = []
        for coluna in colunas:
            tabela = pd.crosstab(index=linhas, 
                                 columns=coluna, 
                                 values=dados['peso'],
                                 aggfunc='sum',
                                 normalize=normalizar)

            tabela = tabela.fillna(0)

            for column in tabela.columns:
                tabela[column] = saferound(tabela[column].values*multiplicar, 0)

            tabela = tabela.append(tabela.sum().rename('All'))
            dataframes.append(tabela)
    
        # Juntar as tabela criadas
        final = reduce(lambda left, right: left.join(right), dataframes)
        final = final.rename({'All': 'Total'}, axis=0)

        return final
    

def criar_tabela(dados: pd.DataFrame,
                 variavel: str, 
                 cruzamento: List[str], 
                 mostrar_porcentagem: bool = True) -> pd.DataFrame:
     
    """
    Cria a tabela cruzada junto com a coluna 'Total'
    ----------------------------
    Parâmetros
    dados: Pandas dataframe.
    variavel, cruzamento: String para uma variável e lista para mais de uma variável. 
    mostrar_porcentagem: True para mostrar o resultado em porcentagem

    Retorna um dataframe pandas
    """
    contagem = dados.groupby(variavel)['peso'].sum()

    porcentagem = None
    if mostrar_porcentagem:
        total = np.sum(contagem)
        porcentagem = pd.Series(saferound((contagem/total)*100, 0), index=contagem.index)

        porcentagem = porcentagem.append(pd.Series(np.sum(porcentagem), index=pd.Index(['Total'])))

    else:
        contagem = pd.Series(saferound(contagem, 0), index=contagem.index)
        contagem = contagem.append(pd.Series(np.sum(contagem), index=pd.Index(['Total'])))
        

    valores = porcentagem if mostrar_porcentagem == True else contagem
    dataframe = pd.DataFrame(valores, columns=['Total'])

    tabela = tabela_contingencia(dados, variavel, cruzamento, mostrar_porcentagem)

    tabela_final = pd.concat([dataframe, tabela], axis=1).rename({0:variavel}, axis=1)
    tabela_final.index.name = variavel

    return tabela_final