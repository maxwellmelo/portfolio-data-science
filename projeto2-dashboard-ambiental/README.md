# 🌳 Dashboard Ambiental - Desmatamento no Brasil

Dashboard interativo para análise de dados de desmatamento no Brasil, com foco no bioma Cerrado e no estado do Piauí, utilizando dados oficiais do PRODES/INPE.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.29-red.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

## 📋 Sobre o Projeto

Este projeto é parte do portfólio de Ciência de Dados e apresenta uma análise completa dos dados de desmatamento no Brasil, com recursos como:

- **Visualizações Interativas**: Gráficos dinâmicos com Plotly
- **Mapas Geoespaciais**: Mapas coropléticos e de calor com Folium
- **Análises Temporais**: Séries históricas e projeções de tendências
- **Comparações Regionais**: Rankings e comparações entre estados e biomas
- **KPIs em Tempo Real**: Indicadores-chave atualizados automaticamente
- **Foco Especial**: Análise detalhada do estado do Piauí

## 🎯 Objetivos

1. Democratizar o acesso a dados ambientais importantes
2. Facilitar a compreensão de tendências de desmatamento
3. Fornecer insights para políticas públicas ambientais
4. Destacar a situação do Piauí no contexto do Cerrado
5. Demonstrar habilidades em ciência de dados e visualização

## 📊 Fontes de Dados

### PRODES (Programa de Monitoramento do Desmatamento)
- Sistema do INPE para monitoramento por satélites do desmatamento
- Dados anuais desde 2000
- Cobertura de todos os biomas brasileiros
- Precisão próxima a 95%

### TerraBrasilis
- Plataforma de dados geográficos do INPE
- Acesso via Web Feature Service (WFS)
- Downloads de arquivos vetoriais e raster
- API para integração de dados

**Links Oficiais:**
- [TerraBrasilis](http://terrabrasilis.dpi.inpe.br/)
- [INPE - Instituto Nacional de Pesquisas Espaciais](https://www.gov.br/inpe/)
- [Portal de Dados Abertos INPE](https://www.gov.br/inpe/pt-br/acesso-a-informacao/dados-abertos)

## 🚀 Tecnologias Utilizadas

### Backend e Processamento
- **Python 3.8+**: Linguagem principal
- **Pandas**: Manipulação e análise de dados
- **NumPy**: Computação numérica
- **GeoPandas**: Processamento de dados geoespaciais
- **Requests**: Comunicação com APIs

### Visualização
- **Streamlit**: Framework para dashboard interativo
- **Plotly**: Gráficos interativos avançados
- **Folium**: Mapas interativos
- **Streamlit-Folium**: Integração de mapas no Streamlit

### Análise Geoespacial
- **Shapely**: Manipulação de geometrias
- **Fiona**: Leitura/escrita de dados vetoriais
- **PyProj**: Transformações de coordenadas

## 📁 Estrutura do Projeto

```
projeto2-dashboard-ambiental/
│
├── app.py                          # Aplicação principal do Streamlit
├── requirements.txt                # Dependências do projeto
├── .env.example                    # Exemplo de variáveis de ambiente
├── README.md                       # Documentação
│
├── .streamlit/
│   └── config.toml                 # Configurações do Streamlit
│
├── src/
│   ├── __init__.py
│   │
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── config.py               # Configurações centralizadas
│   │   ├── data_loader.py          # Carregamento de dados PRODES
│   │   └── data_processor.py       # Processamento e ETL
│   │
│   └── components/
│       ├── __init__.py
│       ├── charts.py               # Componentes de gráficos
│       └── maps.py                 # Componentes de mapas
│
├── data/
│   ├── raw/                        # Dados brutos
│   └── processed/                  # Dados processados
│
├── docs/                           # Documentação técnica
│
└── assets/
    └── images/                     # Imagens e recursos
```

## 🔧 Instalação e Configuração

### 1. Clone o repositório

```bash
cd E:\Portifolio-cienciadedados
```

### 2. Crie um ambiente virtual

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3. Instale as dependências

```bash
cd projeto2-dashboard-ambiental
pip install -r requirements.txt
```

### 4. Configure variáveis de ambiente (opcional)

```bash
cp .env.example .env
# Edite o arquivo .env conforme necessário
```

## ▶️ Como Executar

### Executar o Dashboard

```bash
streamlit run app.py
```

O dashboard será aberto automaticamente no navegador em `http://localhost:8501`

### Opções de Linha de Comando

```bash
# Especificar porta
streamlit run app.py --server.port 8502

# Desabilitar auto-reload
streamlit run app.py --server.runOnSave false

# Modo de desenvolvimento
streamlit run app.py --logger.level debug
```

## 📖 Funcionalidades Principais

### 1. Visão Geral
- **KPIs Principais**: Desmatamento atual, variação anual, média histórica
- **Série Temporal**: Evolução com projeções futuras
- **Distribuição por Bioma**: Gráfico de pizza interativo
- **Ranking de Estados**: Top 10 estados com maior desmatamento

### 2. Mapas Interativos
- **Mapa Coroplético**: Visualização por intensidade de desmatamento
- **Mapa de Calor**: Densidade de ocorrências
- **Mapa de Marcadores**: Pontos por estado com informações detalhadas
- **Filtros Dinâmicos**: Por ano, estado e bioma

### 3. Análises Detalhadas
- **Comparação Entre Anos**: Análise comparativa temporal
- **Heatmap Temporal**: Intensidade ao longo do tempo
- **Estatísticas por Bioma**: Métricas agregadas
- **Tendências e Projeções**: Regressão linear e forecasting

### 4. Foco: Piauí
- **KPIs Específicos**: Indicadores exclusivos do Piauí
- **Evolução Temporal**: Série histórica local
- **Mapa Focado**: Visualização geográfica do estado
- **Comparação Regional**: Piauí vs outros estados do Cerrado
- **Dados Detalhados**: Tabela completa com histórico

### 5. Informações
- **Sobre o Projeto**: Descrição e objetivos
- **Fontes de Dados**: Links e referências
- **Metodologia**: Explicação das análises
- **Tecnologias**: Stack tecnológica utilizada

## 📊 Dados Disponíveis

### Período de Cobertura
- **Início**: 2000
- **Fim**: 2025 (dados preliminares)
- **Consolidação 2025**: Prevista para primeiro semestre de 2026

### Biomas Cobertos
1. **Amazônia** - Estados da Amazônia Legal
2. **Cerrado** - Inclui Piauí, Maranhão, Tocantins, etc.
3. **Mata Atlântica**
4. **Caatinga**
5. **Pantanal**
6. **Pampa**

### Métricas Disponíveis
- Área desmatada (km²)
- Variação anual (absoluta e percentual)
- Tendências históricas
- Projeções futuras
- Rankings por estado
- Distribuição por bioma

## 🎨 Customização

### Temas e Cores

Edite o arquivo `.streamlit/config.toml` para customizar:

```toml
[theme]
primaryColor = "#1f7a1f"        # Verde floresta
backgroundColor = "#ffffff"      # Branco
secondaryBackgroundColor = "#f0f2f6"
textColor = "#262730"
font = "sans serif"
```

### Filtros Padrão

Edite `src/utils/config.py`:

```python
DEFAULT_BIOME = "Cerrado"
DEFAULT_STATE = "PI"
DEFAULT_YEAR_START = 2018
DEFAULT_YEAR_END = 2024
```

## 📈 Exemplos de Análises

### 1. Análise de Tendência

```python
from src.utils.data_loader import DataLoaderPRODES
from src.utils.data_processor import DataProcessor

loader = DataLoaderPRODES()
df = loader.load_data()

processor = DataProcessor(df)
trends = processor.calculate_trends(estado="PI", bioma="Cerrado")

print(f"Tendência anual: {trends['tendencia_anual_km2']} km²/ano")
print(f"R²: {trends['r_squared']}")
```

### 2. Comparação Entre Estados

```python
ranking = processor.get_top_states(n=10, ano=2025, bioma="Cerrado")
print(ranking[['estado_nome', 'area_desmatada_km2']])
```

### 3. KPIs Customizados

```python
from src.utils.data_processor import create_kpis

kpis = create_kpis(df, ano_atual=2025, estado="PI", bioma="Cerrado")
print(f"Desmatamento atual: {kpis['desmatamento_atual_km2']} km²")
print(f"Variação anual: {kpis['variacao_anual_percentual']}%")
```

## 🔍 Destaques dos Dados (2025 - Preliminar)

### Cerrado
- **Taxa Total**: 7.235 km²
- **Redução**: 11,49% em relação a 2024
- **Maiores Desmatadores**:
  1. Maranhão: 2.006 km²
  2. Tocantins: 1.489 km²
  3. **Piauí: 1.350 km²**

### Piauí
- 3º maior desmatador do Cerrado em 2025
- Importante área de transição entre Cerrado e Caatinga
- Dados históricos desde 2000 disponíveis

## 🤝 Contribuições

Este é um projeto de portfólio pessoal, mas sugestões são bem-vindas!

Para contribuir:
1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📝 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## 👨‍💻 Autor

**Maxwell**
- Portfólio de Ciência de Dados
- Data: Dezembro 2025

## 🙏 Agradecimentos

- **INPE** - Instituto Nacional de Pesquisas Espaciais
- **TerraBrasilis** - Plataforma de dados geográficos
- **PRODES** - Programa de Monitoramento do Desmatamento
- Comunidade Open Source de Python e Streamlit

## 📚 Referências

1. [INPE - Dados do PRODES](https://www.gov.br/inpe/pt-br/assuntos/ultimas-noticias/dados-do-prodes-apontam-reducao-no-desmatamento-na-amazonia-e-no-cerrado-brasileiros-1)
2. [TerraBrasilis - Plataforma](http://terrabrasilis.dpi.inpe.br/)
3. [Base dos Dados - PRODES](https://basedosdados.org/dataset/e5c87240-ecce-4856-97c5-e6b84984bf42)
4. [Streamlit Documentation](https://docs.streamlit.io/)
5. [Plotly Python](https://plotly.com/python/)
6. [Folium Documentation](https://python-visualization.github.io/folium/)

## 📞 Contato

Para dúvidas, sugestões ou oportunidades:
- GitHub: [Seu perfil]
- LinkedIn: [Seu perfil]
- Email: [Seu email]

---

**⚠️ Aviso Legal**: Este dashboard utiliza dados públicos do INPE para fins educacionais e de pesquisa. Os dados de 2025 são preliminares e serão consolidados no primeiro semestre de 2026.

**🌱 Última atualização**: Dezembro 2025
