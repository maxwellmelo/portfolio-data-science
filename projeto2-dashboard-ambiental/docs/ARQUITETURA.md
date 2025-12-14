# 🏗️ Arquitetura do Dashboard Ambiental

## Visão Geral

O Dashboard Ambiental segue uma arquitetura modular em camadas, separando responsabilidades entre coleta de dados, processamento, visualização e apresentação.

## Diagrama de Arquitetura

```
┌─────────────────────────────────────────────────────────────┐
│                    CAMADA DE APRESENTAÇÃO                    │
│                        (Streamlit)                           │
│  ┌────────────┬────────────┬────────────┬────────────────┐  │
│  │  Visão     │   Mapas    │ Análises   │     Foco       │  │
│  │  Geral     │ Interativos│ Detalhadas │    Piauí       │  │
│  └────────────┴────────────┴────────────┴────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                  CAMADA DE COMPONENTES                       │
│                   (Visualização)                             │
│  ┌──────────────────────┬──────────────────────────────┐    │
│  │   ChartBuilder       │       MapBuilder             │    │
│  │  - Gráficos Plotly   │   - Mapas Folium             │    │
│  │  - Time Series       │   - Choropleths              │    │
│  │  - Comparações       │   - Heat Maps                │    │
│  │  - KPIs Visuais      │   - Markers                  │    │
│  └──────────────────────┴──────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                 CAMADA DE PROCESSAMENTO                      │
│                    (Business Logic)                          │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              DataProcessor                           │   │
│  │  - Agregações                                        │   │
│  │  - Cálculo de métricas                              │   │
│  │  - Análises estatísticas                            │   │
│  │  - Tendências e projeções                           │   │
│  │  - Comparações temporais                            │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                    CAMADA DE DADOS                           │
│                   (Data Access)                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │            DataLoaderPRODES                          │   │
│  │  - Conexão com APIs TerraBrasilis/WFS               │   │
│  │  - Geração de dados sintéticos                      │   │
│  │  - Cache local                                       │   │
│  │  - Validação de dados                               │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                    FONTES DE DADOS                           │
│  ┌────────────────┬─────────────────┬───────────────────┐   │
│  │ TerraBrasilis  │   API WFS       │  Dados Sintéticos │   │
│  │   (INPE)       │   GeoServer     │  (Baseados em     │   │
│  │                │                 │   estatísticas)   │   │
│  └────────────────┴─────────────────┴───────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## Componentes Principais

### 1. Camada de Apresentação (app.py)

**Responsabilidades:**
- Interface do usuário com Streamlit
- Gerenciamento de estado da aplicação
- Filtros e controles interativos
- Organização em tabs/páginas
- Layout responsivo

**Principais Features:**
- 5 tabs principais (Visão Geral, Mapas, Análises, Foco Piauí, Sobre)
- Sidebar com filtros dinâmicos
- Cache de dados com `@st.cache_data`
- CSS customizado para estilização

### 2. Camada de Componentes

#### 2.1 ChartBuilder (components/charts.py)

**Responsabilidades:**
- Criação de gráficos interativos com Plotly
- Padronização visual (cores, templates)
- Configurações de interatividade

**Métodos Principais:**
```python
- create_time_series()          # Séries temporais
- create_bar_chart()            # Gráficos de barras
- create_comparison_chart()     # Comparações entre períodos
- create_pie_chart()            # Gráficos de pizza
- create_area_chart()           # Gráficos de área
- create_heatmap()              # Mapas de calor
- create_trend_with_forecast()  # Tendências com projeção
- create_gauge_chart()          # Medidores/Gauges
```

**Características:**
- Paleta de cores consistente
- Template Plotly White
- Hover interativo
- Legendas posicionadas
- Responsivo

#### 2.2 MapBuilder (components/maps.py)

**Responsabilidades:**
- Criação de mapas interativos com Folium
- Visualizações geoespaciais
- Camadas de informação

**Métodos Principais:**
```python
- create_choropleth_map()       # Mapas coropléticos
- create_heat_map()             # Mapas de calor
- create_marker_map()           # Mapas com marcadores
- create_piaui_focus_map()      # Foco específico no Piauí
- create_biome_comparison_map() # Comparação por bioma
```

**Características:**
- Coordenadas pré-definidas dos estados
- Popups informativos
- Legendas customizadas
- Múltiplos estilos de tiles
- Zoom e pan interativos

### 3. Camada de Processamento

#### 3.1 DataProcessor (utils/data_processor.py)

**Responsabilidades:**
- ETL (Extract, Transform, Load)
- Agregações e cálculos estatísticos
- Validação e limpeza de dados
- Geração de métricas derivadas

**Métodos Principais:**
```python
- calculate_yearly_metrics()    # Métricas anuais agregadas
- calculate_state_metrics()     # Métricas por estado
- calculate_biome_metrics()     # Métricas por bioma
- get_top_states()              # Rankings
- calculate_trends()            # Análise de tendências
- detect_anomalies()            # Detecção de outliers
- create_comparison_matrix()    # Comparações temporais
- export_processed_data()       # Exportação de dados
```

**Funções Auxiliares:**
```python
- create_kpis()                 # Geração de KPIs
```

**Análises Implementadas:**
- Regressão linear para tendências
- Cálculo de R² para qualidade do ajuste
- Média móvel (rolling)
- Z-score para anomalias
- Variações percentuais e absolutas

### 4. Camada de Dados

#### 4.1 DataLoaderPRODES (utils/data_loader.py)

**Responsabilidades:**
- Conexão com APIs externas
- Cache de dados locais
- Geração de dados sintéticos
- Validação de dados

**Métodos Principais:**
```python
- fetch_wfs_data()              # Busca via WFS/GeoServer
- create_synthetic_data()       # Dados sintéticos realistas
- load_data()                   # Carregamento principal
- get_estado_data()             # Filtro por estado
- get_bioma_data()              # Filtro por bioma
- get_yearly_totals()           # Totais anuais
- get_state_rankings()          # Rankings por estado
```

**Estratégia de Dados:**
1. **Primeira opção**: Buscar dados reais da API TerraBrasilis/WFS
2. **Fallback**: Usar dados sintéticos baseados em estatísticas reais
3. **Cache**: Salvar dados localmente para otimizar performance

**Dados Sintéticos:**
- Baseados em estatísticas reais do PRODES 2025
- Tendências históricas realistas
- Distribuição proporcional entre estados
- Dados preliminares de 2025 incluídos

### 5. Camada de Configuração

#### 5.1 Config (utils/config.py)

**Responsabilidades:**
- Configurações centralizadas
- URLs de APIs
- Constantes do projeto
- Textos e mensagens

**Principais Configurações:**
```python
# APIs
TERRABRASILIS_BASE_URL
TERRABRASILIS_GEOSERVER
WFS_SERVICES

# Geografia
ESTADOS_BRASIL
ESTADOS_CERRADO
ESTADOS_AMAZONIA
BIOMAS

# Dados 2025
DADOS_2025_PRELIM

# Visualização
CHART_CONFIG
ANOS_DISPONIVEIS

# Textos
TEXTOS
```

## Fluxo de Dados

### 1. Carregamento Inicial

```
Usuário acessa dashboard
       ↓
app.py inicia
       ↓
load_data() com cache
       ↓
DataLoaderPRODES.load_data()
       ↓
Tenta fetch_wfs_data()
       ↓
Se falhar → create_synthetic_data()
       ↓
Salva cache local
       ↓
Retorna DataFrame
```

### 2. Processamento de Filtros

```
Usuário seleciona filtros (bioma, estado, período)
       ↓
app.py aplica filtros ao DataFrame
       ↓
df_filtered criado
       ↓
DataProcessor(df_filtered)
       ↓
Cálculos e agregações
       ↓
Resultados para visualização
```

### 3. Geração de Visualizações

```
Dados processados
       ↓
ChartBuilder.create_*() ou MapBuilder.create_*()
       ↓
Configuração de parâmetros visuais
       ↓
Geração de Figure (Plotly) ou Map (Folium)
       ↓
Renderização no Streamlit
       ↓
Interatividade no navegador
```

## Padrões de Design Utilizados

### 1. **Separation of Concerns**
- Cada camada tem responsabilidade específica
- Componentes desacoplados
- Fácil manutenção e testes

### 2. **Builder Pattern**
- ChartBuilder e MapBuilder
- Métodos fluentes para construção de visualizações
- Configurações centralizadas

### 3. **Singleton Pattern** (implícito)
- Configurações em config.py
- Cache de dados com Streamlit

### 4. **Factory Pattern**
- DataLoader gera diferentes tipos de dados
- create_* methods criam diferentes visualizações

### 5. **Strategy Pattern**
- Diferentes estratégias de carregamento (API vs sintético)
- Múltiplos tipos de visualização intercambiáveis

## Performance e Otimizações

### 1. Cache de Dados
```python
@st.cache_data(ttl=3600)
def load_data():
    # Cache por 1 hora
```

### 2. Cache Local de Arquivos
- Dados salvos em `data/processed/`
- Evita requisições repetidas à API
- Fallback rápido

### 3. Lazy Loading
- Dados carregados apenas quando necessário
- Processamentos sob demanda

### 4. Agregações Otimizadas
- Uso de groupby do Pandas
- Cálculos vetorizados com NumPy

## Segurança

### 1. Variáveis de Ambiente
- Configurações sensíveis em `.env`
- Exemplo em `.env.example`

### 2. Validação de Dados
- Verificação de colunas obrigatórias
- Conversão e limpeza de tipos
- Tratamento de valores nulos

### 3. Tratamento de Erros
- Try-catch em chamadas de API
- Fallback para dados sintéticos
- Mensagens de erro informativas

## Extensibilidade

### Adicionar Novo Bioma
1. Atualizar `BIOMAS` em `config.py`
2. Incluir estados correspondentes
3. Ajustar `create_synthetic_data()` se necessário

### Adicionar Nova Visualização
1. Criar método em `ChartBuilder` ou `MapBuilder`
2. Seguir padrão de parâmetros existentes
3. Utilizar cores da paleta padrão
4. Adicionar ao dashboard em `app.py`

### Adicionar Nova Métrica
1. Implementar cálculo em `DataProcessor`
2. Adicionar ao `create_kpis()` se for KPI
3. Criar visualização correspondente
4. Integrar ao dashboard

### Conectar Nova Fonte de Dados
1. Adicionar configuração em `config.py`
2. Implementar método em `DataLoaderPRODES`
3. Seguir padrão de fallback
4. Adicionar cache apropriado

## Testes

### Estrutura Sugerida
```
tests/
├── test_data_loader.py      # Testes de carregamento
├── test_data_processor.py   # Testes de processamento
├── test_charts.py            # Testes de visualização
└── test_integration.py       # Testes de integração
```

### Tipos de Testes Recomendados
1. **Unitários**: Cada método isoladamente
2. **Integração**: Fluxo completo de dados
3. **Visual**: Regressão visual de gráficos
4. **Performance**: Benchmarks de processamento

## Monitoramento e Logs

### Logs Implementados
- Mensagens de progresso no carregamento
- Erros de API capturados e logados
- Informações de cache

### Métricas de Uso
- Número de registros carregados
- Estados e biomas disponíveis
- Período de dados

## Deploy

### Opções de Deploy

#### 1. Streamlit Cloud (Recomendado)
```bash
# Criar requirements.txt
# Commit no GitHub
# Conectar Streamlit Cloud ao repositório
```

#### 2. Heroku
```bash
# Criar Procfile
web: streamlit run app.py --server.port=$PORT
```

#### 3. Docker
```dockerfile
FROM python:3.8-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["streamlit", "run", "app.py"]
```

## Melhorias Futuras

### Curto Prazo
- [ ] Testes automatizados
- [ ] CI/CD pipeline
- [ ] Logs estruturados
- [ ] Métricas de uso

### Médio Prazo
- [ ] Autenticação de usuários
- [ ] Export de relatórios PDF
- [ ] Comparações customizadas
- [ ] Alertas de desmatamento

### Longo Prazo
- [ ] Machine Learning para previsões
- [ ] Análise de imagens de satélite
- [ ] API REST própria
- [ ] Mobile app

## Documentação Adicional

- [README.md](../README.md): Documentação geral
- [API_REFERENCE.md](API_REFERENCE.md): Referência de APIs
- [USER_GUIDE.md](USER_GUIDE.md): Guia do usuário
