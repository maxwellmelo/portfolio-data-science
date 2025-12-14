# Sistema de Compliance LGPD - Auditoria de Dados Pessoais

Ferramenta automatizada para identificação, classificação e anonimização de dados pessoais (PII) em conformidade com a Lei Geral de Proteção de Dados (LGPD).

## Problema de Negócio

Organizações enfrentam desafios para:
- **Identificar** onde estão os dados pessoais em suas bases
- **Classificar** o nível de sensibilidade dos dados
- **Anonimizar** dados para análises sem violar a privacidade
- **Documentar** o tratamento para auditorias regulatórias

Este projeto demonstra técnicas de Data Privacy aplicadas a cenários reais.

## Tecnologias Utilizadas

| Categoria | Tecnologia |
|-----------|------------|
| Linguagem | Python 3.10+ |
| Validação | Pydantic |
| Análise | Pandas |
| CLI | argparse |
| Logging | Loguru |
| Dados Fake | Faker |
| Relatórios | Jinja2 |
| Hashing | hashlib |

## Funcionalidades

### 1. Scanner de PII (Personally Identifiable Information)
- Detecção por **padrões regex** (CPF, CNPJ, email, telefone)
- Detecção por **nomes de colunas** (nome, endereco, salario)
- Classificação por **nível de risco** (crítico, alto, médio, baixo)
- Suporte a CSV, Excel e Parquet

### 2. Anonimização de Dados
| Método | Descrição | Exemplo |
|--------|-----------|---------|
| `mask` | Mascara caracteres | `123.456.789-00` → `***.***.***-**` |
| `hash` | Hash SHA-256 truncado | `João Silva` → `a1b2c3d4e5f6` |
| `pseudonymize` | Substitui por pseudônimo | `Maria` → `Pessoa_00001` |
| `generalize` | Generaliza valores | `25` → `20-30` |
| `suppress` | Remove completamente | `email@test.com` → `[SUPRIMIDO]` |
| `tokenize` | Token reversível | `dado` → `TKN_xyz123` |
| `noise` | Adiciona ruído numérico | `1000` → `1047` |

### 3. Relatórios de Auditoria
- Relatório HTML detalhado
- Resumo executivo
- Matriz de risco
- Recomendações de conformidade

## Estrutura do Projeto

```
projeto5-compliance-lgpd/
├── config/
│   └── settings.py           # Configurações LGPD
├── src/
│   ├── scanners/
│   │   └── pii_scanner.py    # Detector de PII
│   ├── anonymizers/
│   │   └── data_anonymizer.py # Anonimizador
│   └── reporters/
│       └── lgpd_reporter.py  # Gerador de relatórios
├── data/
│   ├── input/                # Dados de entrada
│   ├── output/               # Dados anonimizados
│   └── reports/              # Relatórios gerados
├── templates/
│   └── audit_report.html     # Template do relatório
├── tests/
├── notebooks/
├── main.py                   # CLI principal
├── requirements.txt
└── README.md
```

## Como Executar

### 1. Instalação

```bash
cd projeto5-compliance-lgpd

# Criar ambiente virtual
python -m venv venv
venv\Scripts\activate  # Windows

# Instalar dependências
pip install -r requirements.txt
```

### 2. Gerar Dados de Exemplo

```bash
python main.py generate-sample
```

Cria arquivo `data/input/sample_data.csv` com dados fictícios.

### 3. Escanear Arquivo

```bash
# Scan básico
python main.py scan data/input/sample_data.csv

# Scan com relatório HTML
python main.py scan data/input/sample_data.csv --report
```

### 4. Anonimizar Dados

```bash
# Anonimização automática (baseada no scan)
python main.py anonymize data/input/sample_data.csv

# Com configuração personalizada
python main.py anonymize data/input/sample_data.csv --config config.json
```

## Exemplo de Uso

### Scan de PII

```bash
$ python main.py scan data/input/sample_data.csv

============================================================
RESULTADO DO SCAN DE DADOS PESSOAIS
============================================================
Arquivo: sample_data.csv
Linhas: 100
Colunas analisadas: 10
PIIs encontrados: 6

Resumo de Risco:
  - CRITICO: 1
  - ALTO: 3
  - MEDIO: 2

Detalhes:
  [CRITICO] cpf: cpf (100 ocorrências)
  [ALTO] nome_completo: nome (100 ocorrências)
  [ALTO] email: email (100 ocorrências)
  [ALTO] telefone: telefone (100 ocorrências)
  [MEDIO] endereco: endereco (100 ocorrências)
  [MEDIO] data_nascimento: data_nascimento (100 ocorrências)

Recomendações:
  • Aplicar hash ou tokenização em cpf
  • Implementar controle de acesso para nome_completo
  • Considerar pseudonimização para email
```

### Configuração de Anonimização (JSON)

```json
{
  "cpf": {"method": "hash", "truncate": 12},
  "nome_completo": {"method": "pseudonymize", "prefix": "Cliente"},
  "email": {"method": "mask", "char": "*", "visible_chars": 3},
  "telefone": {"method": "suppress"},
  "salario": {"method": "noise", "percentage": 10}
}
```

### Uso Programático

```python
from src.scanners import PIIScanner
from src.anonymizers import DataAnonymizer
from src.reporters import LGPDReporter
import pandas as pd

# Carregar dados
df = pd.read_csv("dados.csv")

# Escanear
scanner = PIIScanner()
result = scanner.scan(df, source_name="dados.csv")

print(f"PIIs encontrados: {len(result.pii_found)}")
for pii in result.pii_found:
    print(f"  - {pii.column}: {pii.pii_type.value} ({pii.risk_level.value})")

# Anonimizar
anonymizer = DataAnonymizer()
config = {
    "cpf": {"method": "hash"},
    "nome": {"method": "pseudonymize"}
}
df_anon = anonymizer.anonymize_dataframe(df, config)

# Gerar relatório
reporter = LGPDReporter()
report_path = reporter.generate_audit_report([result])
```

## Tipos de PII Detectados

| Categoria | Tipos |
|-----------|-------|
| **Identificadores** | CPF, CNPJ, RG, CNH, Passaporte |
| **Contato** | Email, Telefone, Celular |
| **Financeiro** | Cartão de Crédito, Conta Bancária |
| **Localização** | CEP, Endereço, Coordenadas |
| **Pessoal** | Nome, Data de Nascimento |
| **Sensível** | Dados de Saúde, Biometria |

## Bases Legais da LGPD

O sistema considera as 10 bases legais do Art. 7º da LGPD:

1. Consentimento do titular
2. Obrigação legal ou regulatória
3. Execução de políticas públicas
4. Estudos por órgão de pesquisa
5. Execução de contrato
6. Exercício regular de direitos
7. Proteção da vida
8. Tutela da saúde
9. Interesses legítimos
10. Proteção ao crédito

## Níveis de Risco

| Nível | Descrição | Exemplos | Ação Recomendada |
|-------|-----------|----------|------------------|
| **Crítico** | Identificadores únicos | CPF, CNPJ | Anonimização obrigatória |
| **Alto** | Dados pessoais diretos | Nome, Email, Telefone | Pseudonimização |
| **Médio** | Dados potencialmente identificáveis | Endereço, Data Nasc. | Generalização |
| **Baixo** | Dados genéricos | Cargo, Departamento | Avaliar necessidade |

## Testes

```bash
pytest tests/ -v
```

## Conformidade

Este projeto implementa conceitos de:
- **Privacy by Design**: Privacidade desde a concepção
- **Data Minimization**: Coleta mínima de dados
- **Purpose Limitation**: Dados usados apenas para fins específicos
- **Accountability**: Documentação e rastreabilidade

## Roadmap

- [x] Scanner de PII com regex
- [x] Anonimização multi-método
- [x] Relatórios de auditoria HTML
- [ ] Interface web (Streamlit)
- [ ] Integração com bancos de dados
- [ ] API REST para scan remoto
- [ ] Suporte a dados não-estruturados (PDF, imagens)

## Licença

MIT License

## Autor

**Maxwell** - Projeto de Portfólio em Data Science

---

*Ferramenta educacional para demonstração de técnicas de Data Privacy*
