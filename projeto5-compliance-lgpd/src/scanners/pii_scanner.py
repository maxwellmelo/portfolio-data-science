"""
Scanner de Dados Pessoais Identificáveis (PII).

Detecta dados sensíveis em DataFrames conforme LGPD:
- CPF, CNPJ, RG
- E-mail, telefone
- Endereço, CEP
- Dados de saúde
- E outros dados pessoais
"""

import re
from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import pandas as pd
import numpy as np
from loguru import logger

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from config.settings import settings, DADOS_SENSIVEIS_LGPD


class PIIType(str, Enum):
    """Tipos de dados pessoais identificáveis."""
    CPF = "cpf"
    CNPJ = "cnpj"
    RG = "rg"
    EMAIL = "email"
    TELEFONE = "telefone"
    CEP = "cep"
    CARTAO_CREDITO = "cartao_credito"
    IP = "ip"
    DATA_NASCIMENTO = "data_nascimento"
    NOME = "nome"
    ENDERECO = "endereco"
    DADOS_SAUDE = "dados_saude"
    DADOS_FINANCEIROS = "dados_financeiros"
    OUTROS = "outros"


class RiskLevel(str, Enum):
    """Níveis de risco."""
    BAIXO = "baixo"
    MEDIO = "medio"
    ALTO = "alto"
    CRITICO = "critico"


@dataclass
class PIIMatch:
    """Representa uma ocorrência de PII encontrada."""
    column: str
    pii_type: PIIType
    sample_values: List[str]
    count: int
    percentage: float
    risk_level: RiskLevel
    detection_method: str  # "regex" ou "column_name"


@dataclass
class ScanResult:
    """Resultado completo do scan."""
    timestamp: datetime
    source_name: str
    total_rows: int
    total_columns: int
    columns_scanned: int
    pii_found: List[PIIMatch]
    risk_summary: Dict[str, int]
    recommendations: List[str]
    scan_duration_seconds: float

    def to_dict(self) -> dict:
        """Converte para dicionário."""
        return {
            "timestamp": self.timestamp.isoformat(),
            "source_name": self.source_name,
            "total_rows": self.total_rows,
            "total_columns": self.total_columns,
            "columns_scanned": self.columns_scanned,
            "pii_found": [
                {
                    "column": m.column,
                    "pii_type": m.pii_type.value,
                    "count": m.count,
                    "percentage": m.percentage,
                    "risk_level": m.risk_level.value,
                    "detection_method": m.detection_method
                }
                for m in self.pii_found
            ],
            "risk_summary": self.risk_summary,
            "recommendations": self.recommendations,
            "scan_duration_seconds": self.scan_duration_seconds
        }


class PIIScanner:
    """
    Scanner de Dados Pessoais Identificáveis.

    Analisa DataFrames em busca de:
    1. Padrões de dados sensíveis (regex)
    2. Nomes de colunas suspeitos
    3. Características estatísticas de PII
    """

    # Padrões regex para detecção
    PATTERNS = {
        PIIType.CPF: r"\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b",
        PIIType.CNPJ: r"\b\d{2}\.?\d{3}\.?\d{3}/?\d{4}-?\d{2}\b",
        PIIType.EMAIL: r"\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b",
        PIIType.TELEFONE: r"\b\(?\d{2}\)?\s?\d{4,5}-?\d{4}\b",
        PIIType.CEP: r"\b\d{5}-?\d{3}\b",
        PIIType.CARTAO_CREDITO: r"\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b",
        PIIType.IP: r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b",
        PIIType.DATA_NASCIMENTO: r"\b\d{2}/\d{2}/\d{4}\b"
    }

    # Mapeamento de nomes de colunas para tipos de PII
    COLUMN_PATTERNS = {
        PIIType.CPF: ["cpf", "cpf_titular", "nr_cpf", "num_cpf", "documento"],
        PIIType.CNPJ: ["cnpj", "cnpj_empresa", "nr_cnpj"],
        PIIType.RG: ["rg", "rg_titular", "identidade"],
        PIIType.EMAIL: ["email", "e_mail", "email_contato", "correio"],
        PIIType.TELEFONE: ["telefone", "tel", "celular", "fone", "phone", "mobile"],
        PIIType.CEP: ["cep", "codigo_postal", "zip"],
        PIIType.NOME: ["nome", "nome_completo", "nome_titular", "name", "primeiro_nome", "sobrenome"],
        PIIType.ENDERECO: ["endereco", "logradouro", "rua", "avenida", "address", "bairro"],
        PIIType.DATA_NASCIMENTO: ["data_nascimento", "dt_nascimento", "nascimento", "birth"],
        PIIType.DADOS_SAUDE: ["cid", "diagnostico", "doenca", "medicamento", "prontuario", "cns"],
        PIIType.DADOS_FINANCEIROS: ["salario", "renda", "conta", "agencia", "pis", "pasep"]
    }

    # Mapeamento de risco por tipo
    RISK_MAPPING = {
        PIIType.CPF: RiskLevel.ALTO,
        PIIType.CNPJ: RiskLevel.MEDIO,
        PIIType.RG: RiskLevel.ALTO,
        PIIType.EMAIL: RiskLevel.MEDIO,
        PIIType.TELEFONE: RiskLevel.MEDIO,
        PIIType.CEP: RiskLevel.BAIXO,
        PIIType.CARTAO_CREDITO: RiskLevel.CRITICO,
        PIIType.IP: RiskLevel.BAIXO,
        PIIType.DATA_NASCIMENTO: RiskLevel.MEDIO,
        PIIType.NOME: RiskLevel.MEDIO,
        PIIType.ENDERECO: RiskLevel.MEDIO,
        PIIType.DADOS_SAUDE: RiskLevel.CRITICO,
        PIIType.DADOS_FINANCEIROS: RiskLevel.ALTO,
        PIIType.OUTROS: RiskLevel.BAIXO
    }

    def __init__(self, sample_size: int = 1000):
        """
        Inicializa o scanner.

        Args:
            sample_size: Tamanho da amostra para análise
        """
        self.sample_size = sample_size
        self._compiled_patterns = {
            pii_type: re.compile(pattern, re.IGNORECASE)
            for pii_type, pattern in self.PATTERNS.items()
        }

        logger.info(f"PIIScanner inicializado | sample_size={sample_size}")

    def scan(
        self,
        df: pd.DataFrame,
        source_name: str = "unknown",
        columns: Optional[List[str]] = None
    ) -> ScanResult:
        """
        Escaneia um DataFrame em busca de PII.

        Args:
            df: DataFrame a analisar
            source_name: Nome da fonte de dados
            columns: Colunas específicas a analisar (None = todas)

        Returns:
            ScanResult com detalhes das descobertas
        """
        start_time = datetime.now()
        logger.info(f"Iniciando scan de '{source_name}' | {len(df)} linhas")

        # Selecionar colunas
        cols_to_scan = columns or df.columns.tolist()
        cols_to_scan = [c for c in cols_to_scan if c in df.columns]

        pii_matches = []

        # Analisar cada coluna
        for col in cols_to_scan:
            matches = self._scan_column(df, col)
            pii_matches.extend(matches)

        # Calcular resumo de risco
        risk_summary = self._calculate_risk_summary(pii_matches)

        # Gerar recomendações
        recommendations = self._generate_recommendations(pii_matches)

        # Calcular duração
        duration = (datetime.now() - start_time).total_seconds()

        result = ScanResult(
            timestamp=datetime.now(),
            source_name=source_name,
            total_rows=len(df),
            total_columns=len(df.columns),
            columns_scanned=len(cols_to_scan),
            pii_found=pii_matches,
            risk_summary=risk_summary,
            recommendations=recommendations,
            scan_duration_seconds=round(duration, 2)
        )

        logger.info(
            f"Scan concluído | PIIs encontrados: {len(pii_matches)} | "
            f"Duração: {duration:.2f}s"
        )

        return result

    def _scan_column(self, df: pd.DataFrame, column: str) -> List[PIIMatch]:
        """
        Escaneia uma coluna específica.

        Args:
            df: DataFrame
            column: Nome da coluna

        Returns:
            Lista de PIIMatch encontrados
        """
        matches = []

        # 1. Verificar nome da coluna
        column_lower = column.lower()
        for pii_type, keywords in self.COLUMN_PATTERNS.items():
            if any(kw in column_lower for kw in keywords):
                non_null = df[column].dropna()
                if len(non_null) > 0:
                    sample = non_null.head(5).astype(str).tolist()
                    matches.append(PIIMatch(
                        column=column,
                        pii_type=pii_type,
                        sample_values=sample,
                        count=len(non_null),
                        percentage=round(len(non_null) / len(df) * 100, 2),
                        risk_level=self.RISK_MAPPING[pii_type],
                        detection_method="column_name"
                    ))
                break

        # 2. Verificar padrões regex (apenas em colunas string)
        if df[column].dtype == object:
            sample_df = df[column].dropna().head(self.sample_size)

            for pii_type, pattern in self._compiled_patterns.items():
                # Pular se já detectado pelo nome
                if any(m.column == column and m.pii_type == pii_type for m in matches):
                    continue

                matching_values = sample_df[
                    sample_df.astype(str).str.contains(pattern, na=False)
                ]

                if len(matching_values) > 0:
                    # Estimar contagem total
                    ratio = len(matching_values) / len(sample_df) if len(sample_df) > 0 else 0
                    estimated_count = int(ratio * len(df[column].dropna()))

                    if estimated_count > 0:
                        matches.append(PIIMatch(
                            column=column,
                            pii_type=pii_type,
                            sample_values=matching_values.head(5).astype(str).tolist(),
                            count=estimated_count,
                            percentage=round(ratio * 100, 2),
                            risk_level=self.RISK_MAPPING[pii_type],
                            detection_method="regex"
                        ))

        return matches

    def _calculate_risk_summary(self, matches: List[PIIMatch]) -> Dict[str, int]:
        """Calcula resumo de risco."""
        summary = {level.value: 0 for level in RiskLevel}

        for match in matches:
            summary[match.risk_level.value] += 1

        return summary

    def _generate_recommendations(self, matches: List[PIIMatch]) -> List[str]:
        """Gera recomendações baseadas nos achados."""
        recommendations = []

        # Verificar tipos críticos
        critical_types = [m for m in matches if m.risk_level == RiskLevel.CRITICO]
        if critical_types:
            recommendations.append(
                f"URGENTE: {len(critical_types)} coluna(s) com dados CRÍTICOS detectadas. "
                "Considere anonimização imediata ou remoção."
            )

        # Verificar CPF/CNPJ
        cpf_cnpj = [m for m in matches if m.pii_type in [PIIType.CPF, PIIType.CNPJ]]
        if cpf_cnpj:
            recommendations.append(
                "CPF/CNPJ detectados: Implemente pseudonimização com hash + salt "
                "ou tokenização para proteger esses identificadores."
            )

        # Verificar dados de saúde
        saude = [m for m in matches if m.pii_type == PIIType.DADOS_SAUDE]
        if saude:
            recommendations.append(
                "DADOS SENSÍVEIS (Saúde): Requer base legal específica (Art. 11 LGPD). "
                "Verifique se há consentimento explícito ou outra base legal aplicável."
            )

        # Verificar e-mails
        emails = [m for m in matches if m.pii_type == PIIType.EMAIL]
        if emails:
            recommendations.append(
                "E-mails detectados: Considere mascaramento parcial "
                "(ex: j***@email.com) para logs e relatórios."
            )

        # Recomendação geral
        if matches:
            recommendations.append(
                "Documente a finalidade do tratamento de cada dado pessoal "
                "identificado e mantenha registro atualizado (Art. 37 LGPD)."
            )

        return recommendations

    def validate_cpf(self, cpf: str) -> bool:
        """
        Valida se um CPF é válido (dígitos verificadores).

        Args:
            cpf: String do CPF

        Returns:
            True se CPF válido
        """
        cpf = re.sub(r'\D', '', cpf)

        if len(cpf) != 11:
            return False

        if cpf == cpf[0] * 11:
            return False

        # Cálculo do primeiro dígito
        soma = sum(int(cpf[i]) * (10 - i) for i in range(9))
        resto = soma % 11
        d1 = 0 if resto < 2 else 11 - resto

        # Cálculo do segundo dígito
        soma = sum(int(cpf[i]) * (11 - i) for i in range(10))
        resto = soma % 11
        d2 = 0 if resto < 2 else 11 - resto

        return cpf[-2:] == f"{d1}{d2}"

    def validate_cnpj(self, cnpj: str) -> bool:
        """
        Valida se um CNPJ é válido.

        Args:
            cnpj: String do CNPJ

        Returns:
            True se CNPJ válido
        """
        cnpj = re.sub(r'\D', '', cnpj)

        if len(cnpj) != 14:
            return False

        if cnpj == cnpj[0] * 14:
            return False

        # Primeiro dígito
        pesos = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
        soma = sum(int(cnpj[i]) * pesos[i] for i in range(12))
        resto = soma % 11
        d1 = 0 if resto < 2 else 11 - resto

        # Segundo dígito
        pesos = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
        soma = sum(int(cnpj[i]) * pesos[i] for i in range(13))
        resto = soma % 11
        d2 = 0 if resto < 2 else 11 - resto

        return cnpj[-2:] == f"{d1}{d2}"


# Exemplo de uso
if __name__ == "__main__":
    # Criar dados de teste
    from faker import Faker
    fake = Faker('pt_BR')

    df_test = pd.DataFrame({
        "id": range(100),
        "nome_completo": [fake.name() for _ in range(100)],
        "cpf": [fake.cpf() for _ in range(100)],
        "email": [fake.email() for _ in range(100)],
        "telefone": [fake.phone_number() for _ in range(100)],
        "endereco": [fake.address() for _ in range(100)],
        "data_nascimento": [fake.date_of_birth().strftime("%d/%m/%Y") for _ in range(100)],
        "salario": [round(np.random.uniform(1000, 10000), 2) for _ in range(100)],
        "observacao": ["Texto normal sem PII" for _ in range(100)]
    })

    scanner = PIIScanner()
    result = scanner.scan(df_test, source_name="dados_teste")

    print("\n=== RESULTADO DO SCAN ===")
    print(f"Fonte: {result.source_name}")
    print(f"Linhas: {result.total_rows}")
    print(f"PIIs encontrados: {len(result.pii_found)}")
    print(f"\nResumo de Risco: {result.risk_summary}")
    print(f"\nRecomendações:")
    for rec in result.recommendations:
        print(f"  - {rec}")
