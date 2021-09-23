import pandas as pd
import numpy as np
from typing import Union, List
from collections import Counter
from functools import reduce

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

        # Criar uma tabela de cruzamento para cada "coluna" e armazenar na lista dataframes
        dataframes = []
        for coluna in colunas:
            tabela = pd.crosstab(index=linhas, 
                                 columns=coluna, 
                                 margins=True)
            
            tabela = tabela.drop(columns='All')

            dataframes.append(tabela)
    
        # Juntar as tabela criadas
        final = reduce(lambda left, right: left.join(right), dataframes)
        final = final.rename({'All': 'Total'}, axis=0)

        if percentage:
        # Calcular as porcentagens e arredondar o resultado
            contagem_total = final.loc['Total', final.columns]
            for total, coluna in zip(contagem_total, final.columns):
                final[coluna] = np.round((final[coluna] / total)*100, 0)

        return final
    

def criar_tabela(dados: pd.DataFrame,
                 variavel: str, 
                 cruzamento: List[str], 
                 mostrar_porcentagem: bool = True) -> pd.DataFrame:
                 
    contagem = dados[variavel].value_counts()
    contagem = contagem.append(pd.Series(np.sum(contagem), index=pd.Index(['Total'])))

    porcentagem = None
    if mostrar_porcentagem:
        total = contagem[contagem.index=='Total'].values[0]
        porcentagem = np.round((contagem/total)*100, 0)

    valores = porcentagem if mostrar_porcentagem == True else contagem
    dataframe = pd.DataFrame(valores, columns=['Total'])

    tabela = tabela_contingencia(dados, variavel, cruzamento, mostrar_porcentagem)

    tabela_final = pd.concat([dataframe, tabela], axis=1).rename({0:variavel}, axis=1)
    tabela_final.index.name = variavel

    return tabela_final