# Sistema de Compliance LGPD - Auditoria de Dados Pessoais

<div align="center">

![Python](https://img.shields.io/badge/Python-3.11+-3776ab.svg?style=flat&logo=python&logoColor=white)
![LGPD](https://img.shields.io/badge/LGPD-Compliance-28A745.svg?style=flat)
![Plotly](https://img.shields.io/badge/Plotly-Interativo-3F4F75.svg?style=flat&logo=plotly&logoColor=white)
![Pydantic](https://img.shields.io/badge/Pydantic-2.0+-E92063.svg?style=flat)
![License](https://img.shields.io/badge/License-MIT-green.svg)

**Ferramenta automatizada para identificacao e anonimizacao de dados pessoais (LGPD)**

[Demo Notebook](#-notebook-demonstrativo) | [Funcionalidades](#funcionalidades) | [Como Executar](#como-executar)

</div>

---

## Resultados em Destaque

| Metrica | Valor |
|---------|-------|
| **Tipos de PII Detectados** | 15+ (CPF, CNPJ, Email, Telefone, etc.) |
| **Metodos de Anonimizacao** | 7 metodos (hash, mask, pseudonymize, etc.) |
| **Reducao de Risco** | ~80% apos anonimizacao |
| **Visualizacoes** | 5+ graficos interativos (Plotly) |
| **Validacao** | Pydantic + JSON Schema |

---

## Notebook Demonstrativo

O notebook [`notebooks/demo_compliance_lgpd.ipynb`](notebooks/demo_compliance_lgpd.ipynb) demonstra o fluxo completo de auditoria LGPD:

### Fluxo Demonstrado

```
1. Geracao de Dados     2. Scan de PII     3. Classificacao     4. Anonimizacao     5. Verificacao
   (Faker)         -->    (Scanner)    -->   (Risco)        -->   (7 metodos)   -->   (Re-scan)
```

### Visualizacoes Incluidas

| Analise | Tipo de Grafico |
|---------|-----------------|
| PIIs por Coluna | Barras com cores de risco |
| Distribuicao de Risco | Pizza com drill-down |
| Antes vs Depois | Tabela comparativa |
| Reducao de Risco | Barras agrupadas |
| Sumario Executivo | Metricas consolidadas |

### Exemplo de Output

```
SUMARIO EXECUTIVO - AUDITORIA LGPD
====================================
SCAN DE DADOS PESSOAIS
   PIIs detectados (antes): 10
   Riscos criticos: 0
   Riscos altos: 5

ANONIMIZACAO APLICADA
   Colunas processadas: 8
   Metodos utilizados: 5

RESULTADO
   PIIs apos anonimizacao: 2
   Reducao de risco: 80%

STATUS: CONFORME
```

---

## Problema de Negocio

Organizacoes enfrentam desafios para:
- **Identificar** onde estao os dados pessoais em suas bases
- **Classificar** o nivel de sensibilidade dos dados
- **Anonimizar** dados para analises sem violar a privacidade
- **Documentar** o tratamento para auditorias regulatorias

Este projeto demonstra tecnicas de Data Privacy aplicadas a cenarios reais.

## Funcionalidades

### 1. Scanner de PII (Personally Identifiable Information)
- Deteccao por **padroes regex** (CPF, CNPJ, email, telefone)
- Deteccao por **nomes de colunas** (nome, endereco, salario)
- Classificacao por **nivel de risco** (critico, alto, medio, baixo)
- Suporte a CSV, Excel e Parquet

### 2. Anonimizacao de Dados

| Metodo | Descricao | Exemplo | Reversivel? |
|--------|-----------|---------|-------------|
| `mask` | Mascara caracteres | `123.456.789-00` -> `***.***.***-**` | Nao |
| `hash` | Hash SHA-256 + salt | `Joao Silva` -> `a1b2c3d4e5f6` | Nao |
| `pseudonymize` | Substitui por pseudonimo | `Maria` -> `Ana Santos` | Nao |
| `generalize` | Generaliza valores | `25` -> `20-30` | Nao |
| `suppress` | Remove completamente | `email@test.com` -> `[SUPRIMIDO]` | Nao |
| `tokenize` | Token reversivel | `dado` -> `TOK_00000001` | Sim |
| `noise` | Adiciona ruido numerico | `1000` -> `1047` | Nao |

### 3. Seguranca

- **Hash Salt Configuravel**: Salt via variavel de ambiente
- **Validacao de Salt**: Alerta para salts inseguros
- **Modo Strict**: Bloqueia execucao com salt fraco
- **Configuracao JSON**: Validacao com Pydantic

### 4. Relatorios de Auditoria
- Relatorio HTML detalhado
- Resumo executivo
- Matriz de risco
- Recomendacoes de conformidade

## Estrutura do Projeto

```
projeto5-compliance-lgpd/
├── config/
│   └── settings.py           # Configuracoes LGPD + validacao salt
├── src/
│   ├── scanners/
│   │   └── pii_scanner.py    # Detector de PII
│   ├── anonymizers/
│   │   └── data_anonymizer.py # Anonimizador + validacao
│   └── reporters/
│       └── lgpd_reporter.py  # Gerador de relatorios
├── notebooks/
│   └── demo_compliance_lgpd.ipynb  # Notebook demonstrativo
├── data/
│   ├── input/                # Dados de entrada
│   ├── output/               # Dados anonimizados
│   └── reports/              # Relatorios gerados
├── tests/
│   ├── test_anonymizers.py   # 42 testes
│   └── test_config_validation.py  # 20 testes
├── main.py                   # CLI principal
└── README.md
```

## Como Executar

### 1. Instalacao

```bash
cd projeto5-compliance-lgpd

# Criar ambiente virtual
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Instalar dependencias
pip install -r requirements.txt
```

### 2. Configurar Salt de Seguranca (Producao)

```bash
# Criar arquivo .env
echo "HASH_SALT=seu_salt_aleatorio_de_32_caracteres_ou_mais" > .env
```

### 3. Visualizar Notebook Demonstrativo

```bash
jupyter notebook notebooks/demo_compliance_lgpd.ipynb
```

### 4. Uso via CLI

```bash
# Gerar dados de exemplo
python main.py generate-sample

# Scan basico
python main.py scan data/input/sample_data.csv

# Scan com relatorio HTML
python main.py scan data/input/sample_data.csv --report

# Anonimizacao com configuracao
python main.py anonymize data/input/sample_data.csv --config config.json
```

## Exemplo de Uso Programatico

```python
from src.scanners import PIIScanner, PIIType, RiskLevel
from src.anonymizers import DataAnonymizer, AnonymizationMethod
import pandas as pd

# Carregar dados
df = pd.read_csv("dados.csv")

# 1. Escanear dados pessoais
scanner = PIIScanner()
resultado = scanner.scan(df, source_name="dados.csv")

print(f"PIIs encontrados: {len(resultado.pii_found)}")
for pii in resultado.pii_found:
    print(f"  [{pii.risk_level.value}] {pii.column}: {pii.pii_type.value}")

# 2. Configurar anonimizacao
config = {
    "cpf": {"method": "hash", "truncate": 12},
    "nome": {"method": "pseudonymize", "pii_type": "name"},
    "email": {"method": "mask", "visible_start": 2},
    "salario": {"method": "generalize", "bins": 5}
}

# 3. Anonimizar
anonymizer = DataAnonymizer()  # Usa salt do .env ou settings
df_anon = anonymizer.anonymize_dataframe(df, config)

# 4. Verificar resultado
resultado_pos = scanner.scan(df_anon)
print(f"PIIs apos anonimizacao: {len(resultado_pos.pii_found)}")
```

## Configuracao JSON

```json
{
  "cpf": {"method": "hash", "truncate": 12},
  "nome_completo": {"method": "pseudonymize", "pii_type": "name"},
  "email": {"method": "mask", "visible_start": 3},
  "telefone": {"method": "suppress", "replacement": "[PROTEGIDO]"},
  "salario": {"method": "noise", "noise_level": 0.1},
  "idade": {"method": "generalize", "bins": 4, "labels": ["18-30", "31-45", "46-60", "60+"]}
}
```

## Niveis de Risco

| Nivel | Descricao | Exemplos | Acao Recomendada |
|-------|-----------|----------|------------------|
| **Critico** | Dados sensiveis (Art. 11) | Saude, Biometria | Anonimizacao obrigatoria |
| **Alto** | Identificadores unicos | CPF, RG, Cartao | Hash ou pseudonimizacao |
| **Medio** | Dados pessoais diretos | Nome, Email, Telefone | Mascaramento |
| **Baixo** | Dados potencialmente identificaveis | CEP, IP | Avaliar necessidade |

## Bases Legais da LGPD (Art. 7)

O sistema considera as 10 bases legais:

1. Consentimento do titular
2. Obrigacao legal ou regulatoria
3. Execucao de politicas publicas
4. Estudos por orgao de pesquisa
5. Execucao de contrato
6. Exercicio regular de direitos
7. Protecao da vida
8. Tutela da saude
9. Interesses legitimos
10. Protecao ao credito

## Testes

```bash
# Executar todos os testes
pytest tests/ -v

# Testes de anonimizacao (42 testes)
pytest tests/test_anonymizers.py -v

# Testes de validacao de config (20 testes)
pytest tests/test_config_validation.py -v
```

## Conformidade

Este projeto implementa conceitos de:
- **Privacy by Design**: Privacidade desde a concepcao
- **Data Minimization**: Coleta minima de dados
- **Purpose Limitation**: Dados usados apenas para fins especificos
- **Accountability**: Documentacao e rastreabilidade

## Roadmap

- [x] Scanner de PII com regex
- [x] Anonimizacao multi-metodo
- [x] Relatorios de auditoria HTML
- [x] **Notebook demonstrativo com visualizacoes**
- [x] **Validacao de seguranca do salt**
- [x] **Validacao de config JSON com Pydantic**
- [ ] Interface web (Streamlit)
- [ ] API REST para scan remoto
- [ ] Suporte a dados nao-estruturados (PDF, imagens)

## Licenca

MIT License

## Autor

**Maxwell** - Especialista em Dados

---

<div align="center">

**[Ver Notebook Demonstrativo](notebooks/demo_compliance_lgpd.ipynb)**

*Ferramenta educacional para demonstracao de tecnicas de Data Privacy e conformidade com LGPD*

</div>
