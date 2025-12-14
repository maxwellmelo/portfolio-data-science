# Projeto 5 - Compliance LGPD: Resultados da Execução

## Execução Realizada
**Data**: 14/12/2025

## Scan de Dados Pessoais

### Arquivo Analisado
- **Nome**: sample_data.csv
- **Linhas**: 100
- **Colunas**: 10

### PIIs Detectados

| Coluna | Tipo PII | Risco | Ocorrências |
|--------|----------|-------|-------------|
| cpf | CPF | ALTO | 100 |
| nome_completo | Nome | MÉDIO | 100 |
| email | Email | MÉDIO | 100 |
| telefone | Telefone | MÉDIO | 100 |
| endereco | Endereço | MÉDIO | 100 |
| endereco | CEP | BAIXO | 100 |
| data_nascimento | Data Nascimento | MÉDIO | 100 |
| salario | Dados Financeiros | ALTO | 100 |
| cargo | RG | ALTO | 100 |

### Resumo de Risco
| Nível | Quantidade |
|-------|------------|
| ALTO | 3 |
| MÉDIO | 5 |
| BAIXO | 1 |

## Anonimização Aplicada

### Métodos Utilizados
| Coluna | Método | Resultado |
|--------|--------|-----------|
| cpf | hash | `9f2a7366ce57` |
| nome_completo | mask | `************` |
| email | mask | `***********************` |
| telefone | mask | `*******************` |
| endereco | generalize | `Outros` |
| data_nascimento | mask | `**********` |
| salario | hash | `7e7a8891f11c` |
| cargo | hash | `fe6e12503497` |

### Comparação Antes/Depois

**Antes:**
```
nome_completo: Isaac Campos
cpf: 069.481.537-39
email: felipecosta@example.org
salario: 3494.04
```

**Depois:**
```
nome_completo: ************
cpf: 9f2a7366ce57
email: ***********************
salario: 7e7a8891f11c
```

## Relatório de Auditoria
- **Formato**: HTML
- **Local**: `data/reports/audit_report_20251214_150704.html`

### Recomendações Geradas
1. CPF/CNPJ detectados: Implementar pseudonimização com hash + salt ou tokenização
2. E-mails detectados: Considerar mascaramento parcial (ex: j***@email.com)
3. Documentar a finalidade do tratamento de cada dado pessoal (Art. 37 LGPD)

## Comandos Executados
```bash
# Gerar dados de exemplo
python main.py generate-sample

# Escanear arquivo
python main.py scan data/input/sample_data.csv

# Anonimizar dados
python main.py anonymize data/input/sample_data.csv

# Gerar relatório de auditoria
python main.py scan data/input/sample_data.csv --report
```

## Arquivos Gerados
- `data/input/sample_data.csv` - Dados originais (100 registros)
- `data/input/sample_data_anonimizado.csv` - Dados anonimizados
- `data/reports/audit_report_*.html` - Relatório de auditoria
