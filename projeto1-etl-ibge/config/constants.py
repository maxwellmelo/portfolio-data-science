"""
Constantes do projeto ETL IBGE.

Este módulo centraliza valores constantes utilizados em todo o pipeline,
principalmente IDs de agregados e variáveis da API SIDRA do IBGE.
"""

# ========== Agregados SIDRA ==========

# Agregado 6579 - Estimativas da população residente
# Fonte: IBGE - Diretoria de Pesquisas (DPE), Coordenação de População e Indicadores Sociais (COPIS)
# Periodicidade: Anual (2001 em diante)
AGREGADO_POPULACAO = 6579

# Agregado 5938 - Produto Interno Bruto dos Municípios
# Fonte: IBGE - Coordenação de Contas Nacionais
# Periodicidade: Anual (dados disponíveis desde 2002)
AGREGADO_PIB = 5938


# ========== Variáveis PIB ==========

# Variável 513 - PIB per capita (R$ 1.000)
# Representa o PIB dividido pela população residente
VARIAVEL_PIB_PERCAPITA = 513

# Variável 37 - PIB a preços correntes (Mil Reais)
# Valor total do PIB sem ajuste inflacionário
VARIAVEL_PIB_TOTAL = 37


# ========== Níveis Geográficos ==========

# Níveis territoriais utilizados nas consultas SIDRA
NIVEL_BRASIL = "N1"      # Brasil
NIVEL_REGIAO = "N2"      # Grandes Regiões
NIVEL_ESTADO = "N3"      # Unidades da Federação (UF)
NIVEL_MESORREGIAO = "N7" # Mesorregiões Geográficas
NIVEL_MICRORREGIAO = "N9" # Microrregiões Geográficas
NIVEL_MUNICIPIO = "N6"   # Municípios


# ========== Limites de Anos ==========

# Faixa de anos válidos para validação
# Ajustado para cobrir dados históricos e projeções próximas
ANO_MINIMO = 2000
ANO_MAXIMO = 2030
