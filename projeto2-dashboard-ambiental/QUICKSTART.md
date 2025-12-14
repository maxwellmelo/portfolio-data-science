# 🚀 Guia de Início Rápido - Dashboard Ambiental

## Instalação em 3 Passos

### 1️⃣ Navegue até o diretório do projeto

```bash
cd E:\Portifolio-cienciadedados\projeto2-dashboard-ambiental
```

### 2️⃣ Instale as dependências

```bash
pip install -r requirements.txt
```

### 3️⃣ Execute o dashboard

```bash
streamlit run app.py
```

O dashboard será aberto automaticamente em seu navegador em `http://localhost:8501`

## Primeiros Passos

### Navegando pelo Dashboard

#### 📈 Tab "Visão Geral"
1. Veja os **KPIs principais** no topo da página
2. Explore a **série temporal** com projeções futuras
3. Analise o **ranking de estados** com maior desmatamento
4. Confira a **distribuição por bioma**

#### 🗺️ Tab "Mapas Interativos"
1. Selecione o tipo de mapa (Coroplético, Calor ou Marcadores)
2. Clique nos marcadores para ver detalhes
3. Use zoom e pan para navegar
4. Visualize mapas específicos por bioma

#### 📊 Tab "Análises Detalhadas"
1. Compare dois anos diferentes
2. Explore o heatmap temporal
3. Analise estatísticas por bioma
4. Veja tabelas interativas com dados

#### 🌳 Tab "Foco: Piauí"
1. Visualize KPIs específicos do Piauí
2. Acompanhe a evolução temporal
3. Compare com outros estados do Cerrado
4. Explore dados detalhados em tabela

### Usando os Filtros (Sidebar)

#### Filtro de Bioma
- Selecione "Todos" para visão geral
- Escolha "Cerrado" para foco no bioma do Piauí
- Outros biomas: Amazônia, Mata Atlântica, etc.

#### Filtro de Estado
- Selecione "Todos" para comparação nacional
- Escolha "PI" (Piauí) para análise local
- Qualquer outro estado disponível

#### Filtro de Período
- Use o slider para selecionar intervalo de anos
- Padrão: 2000-2025
- Ajuste conforme sua análise

## Exemplos de Uso

### Exemplo 1: Análise do Piauí em 2025

1. **Sidebar**: Selecione
   - Bioma: Cerrado
   - Estado: PI
   - Período: 2020-2025

2. **Tab Visão Geral**: Veja a tendência recente
3. **Tab Foco Piauí**: Analise detalhes específicos
4. **Tab Análises**: Compare 2024 vs 2025

### Exemplo 2: Comparação Cerrado vs Amazônia

1. **Sidebar**: Selecione
   - Bioma: Todos
   - Estado: Todos
   - Período: 2000-2025

2. **Tab Visão Geral**: Compare distribuição por bioma
3. **Tab Mapas**: Visualize geograficamente
4. **Tab Análises**: Veja heatmap temporal

### Exemplo 3: Top 10 Estados em 2025

1. **Sidebar**: Selecione
   - Bioma: Todos
   - Estado: Todos
   - Período: 2025-2025 (apenas 2025)

2. **Tab Visão Geral**: Veja ranking automático
3. **Tab Mapas**: Visualize no mapa coroplético
4. **Tab Análises**: Compare com ano anterior

## Dicas Úteis

### Performance
- O primeiro carregamento pode demorar um pouco (cache sendo criado)
- Carregamentos seguintes são muito mais rápidos
- Use filtros para focar sua análise

### Interpretação de Dados
- 🟢 **Verde**: Valores baixos/redução (positivo)
- 🔴 **Vermelho**: Valores altos/aumento (negativo)
- ⚠️ **Amarelo**: Dados preliminares de 2025

### Interatividade
- **Hover**: Passe o mouse sobre gráficos para detalhes
- **Zoom**: Use scroll em mapas e gráficos
- **Clique**: Clique em legendas para ocultar/mostrar séries
- **Export**: Botão de câmera no Plotly para salvar imagens

## Troubleshooting

### Dashboard não abre?
```bash
# Verifique se a porta 8501 está livre
streamlit run app.py --server.port 8502
```

### Erro de dependências?
```bash
# Reinstale as dependências
pip install --upgrade -r requirements.txt
```

### Dados não carregam?
- Verifique sua conexão com internet
- O dashboard usa dados sintéticos como fallback
- Cache pode estar corrompido: delete pasta `data/processed/`

### Gráficos não aparecem?
- Limpe o cache do Streamlit: pressione "C" no dashboard
- Ou use: `streamlit cache clear`

## Atalhos do Teclado

Enquanto estiver no dashboard:

- **R**: Rerun da aplicação
- **C**: Limpar cache
- **?**: Mostrar atalhos
- **ESC**: Fechar janela de ajuda

## Próximos Passos

### Exploração Avançada
1. Experimente diferentes combinações de filtros
2. Explore todos os tipos de mapas
3. Analise tendências em períodos diferentes
4. Compare múltiplos estados e biomas

### Customização
1. Edite `.streamlit/config.toml` para mudar cores
2. Ajuste `src/utils/config.py` para valores padrão
3. Adicione suas próprias análises em `app.py`

### Aprofundamento
1. Leia a [Documentação Completa](README.md)
2. Consulte a [Arquitetura](docs/ARQUITETURA.md)
3. Explore o código-fonte em `src/`

## Recursos Adicionais

### Links Externos
- [Dados Oficiais PRODES](http://terrabrasilis.dpi.inpe.br/)
- [Documentação Streamlit](https://docs.streamlit.io/)
- [Documentação Plotly](https://plotly.com/python/)

### Documentação do Projeto
- `README.md`: Visão geral e instalação completa
- `docs/ARQUITETURA.md`: Arquitetura técnica detalhada
- `requirements.txt`: Lista de dependências

## Precisa de Ajuda?

Se encontrar problemas:

1. Verifique se seguiu todos os passos de instalação
2. Confirme que tem Python 3.8+ instalado
3. Tente reinstalar as dependências
4. Consulte a documentação completa
5. Verifique os logs de erro no terminal

## Comandos Úteis

```bash
# Ver versão do Python
python --version

# Ver versão do Streamlit
streamlit --version

# Listar dependências instaladas
pip list

# Atualizar Streamlit
pip install --upgrade streamlit

# Limpar cache do Streamlit
streamlit cache clear

# Executar em modo desenvolvimento
streamlit run app.py --logger.level debug
```

---

**Pronto!** Agora você está preparado para explorar o Dashboard Ambiental! 🌳📊

Se tiver dúvidas, consulte a [documentação completa](README.md) ou explore o código-fonte.
