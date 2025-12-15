"""
Utilitário para parsing de respostas da API SIDRA do IBGE.

Este módulo centraliza a lógica de conversão de dados JSON retornados
pela API SIDRA para DataFrames estruturados do pandas, eliminando
duplicação de código entre diferentes extractors.
"""

from typing import Dict, List
import pandas as pd

from src.utils.logger import get_logger

logger = get_logger(__name__)


def parse_sidra_response(data: List[Dict]) -> pd.DataFrame:
    """
    Converte resposta da API SIDRA para DataFrame estruturado.

    A API SIDRA retorna dados em formato JSON hierárquico com estrutura:
    - variavel: informações sobre a variável estatística
    - resultados: array de resultados
        - series: array de séries temporais
            - localidade: informações geográficas
            - serie: dicionário {ano: valor}

    Esta função "achata" essa estrutura hierárquica em registros tabulares,
    facilitando análise e transformação posterior.

    Args:
        data: Lista de dicionários representando a resposta bruta da API SIDRA.
              Cada elemento contém dados de uma variável estatística.

    Returns:
        DataFrame com colunas:
            - variavel_id: ID da variável estatística
            - variavel_nome: Nome/descrição da variável
            - unidade: Unidade de medida
            - localidade_id: Código da localidade (município, estado, etc.)
            - localidade_nome: Nome da localidade
            - localidade_nivel: Nível geográfico (Brasil, Estado, Município, etc.)
            - ano: Ano de referência
            - valor: Valor numérico da variável
            - classificacoes adicionais (se presentes): campos dinâmicos
              dependendo da variável (ex: setores econômicos para PIB)

    Example:
        >>> data = [
        ...     {
        ...         "id": "1234",
        ...         "variavel": "População residente",
        ...         "unidade": "Pessoas",
        ...         "resultados": [
        ...             {
        ...                 "series": [
        ...                     {
        ...                         "localidade": {
        ...                             "id": "22",
        ...                             "nome": "Piauí",
        ...                             "nivel": {"nome": "Estado"}
        ...                         },
        ...                         "serie": {"2020": "3281480", "2021": "3289290"}
        ...                     }
        ...                 ]
        ...             }
        ...         ]
        ...     }
        ... ]
        >>> df = parse_sidra_response(data)
        >>> print(df.columns)
        Index(['variavel_id', 'variavel_nome', 'unidade', 'localidade_id',
               'localidade_nome', 'localidade_nivel', 'ano', 'valor'], dtype='object')

    Notes:
        - Valores nulos, "-" e "..." são automaticamente ignorados
        - Valores numéricos em formato string brasileiro (com pontos e vírgulas)
          são convertidos para float
        - Classificações adicionais (como setores econômicos) são incluídas
          dinamicamente como colunas extras
    """
    if not data:
        logger.debug("Resposta SIDRA vazia, retornando DataFrame vazio")
        return pd.DataFrame()

    records = []

    for variavel in data:
        variavel_id = variavel.get("id")
        variavel_nome = variavel.get("variavel")
        unidade = variavel.get("unidade")

        resultados = variavel.get("resultados", [])

        for resultado in resultados:
            # Extrair classificações adicionais (ex: setores da economia para PIB)
            classificacoes = resultado.get("classificacoes", [])
            classificacao_info = {}

            for classif in classificacoes:
                classif_nome = classif.get("nome", "")
                categorias = classif.get("categoria", {})
                for cat_id, cat_nome in categorias.items():
                    # Prefixar com 'classif_' para identificar campos de classificação
                    classificacao_info[f"classif_{classif_nome}"] = cat_nome

            series = resultado.get("series", [])

            for serie in series:
                localidade = serie.get("localidade", {})
                localidade_id = localidade.get("id")
                localidade_nome = localidade.get("nome")
                localidade_nivel = localidade.get("nivel", {}).get("nome")

                valores = serie.get("serie", {})

                for ano, valor in valores.items():
                    # Filtrar valores inválidos ou marcadores de dados ausentes
                    if valor and valor != "-" and valor != "...":
                        # Preparar valor numérico
                        # Alguns valores vêm como string com formato brasileiro
                        valor_numerico = _parse_numeric_value(valor)

                        if valor_numerico is not None:
                            record = {
                                "variavel_id": variavel_id,
                                "variavel_nome": variavel_nome,
                                "unidade": unidade,
                                "localidade_id": localidade_id,
                                "localidade_nome": localidade_nome,
                                "localidade_nivel": localidade_nivel,
                                "ano": int(ano),
                                "valor": valor_numerico
                            }

                            # Adicionar classificações adicionais se existirem
                            record.update(classificacao_info)
                            records.append(record)

    df = pd.DataFrame(records)

    if not df.empty:
        logger.debug(
            f"SIDRA response parsed | "
            f"registros={len(df)} | "
            f"colunas={list(df.columns)}"
        )

    return df


def _parse_numeric_value(valor):
    """
    Converte valor string em formato brasileiro para float.

    Args:
        valor: Valor que pode ser string ou número

    Returns:
        Float convertido ou None se conversão falhar

    Example:
        >>> _parse_numeric_value("1.234.567,89")
        1234567.89
        >>> _parse_numeric_value(123.45)
        123.45
    """
    try:
        # Se já é numérico, retornar direto
        if isinstance(valor, (int, float)):
            return float(valor)

        # Se é string, remover pontos (separador de milhar) e trocar vírgula por ponto
        if isinstance(valor, str):
            # Remove espaços em branco
            valor = valor.strip()
            # Formato brasileiro: 1.234.567,89 -> 1234567.89
            valor = valor.replace(".", "").replace(",", ".")
            return float(valor)

        return None

    except (ValueError, AttributeError, TypeError) as e:
        logger.warning(f"Erro ao converter valor numérico '{valor}': {str(e)}")
        return None
