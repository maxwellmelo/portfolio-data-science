"""
Configurações do Sistema de Compliance LGPD.
"""

from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List, Dict, Optional
from functools import lru_cache
from pathlib import Path
from enum import Enum


PROJECT_ROOT = Path(__file__).parent.parent


class SensitivityLevel(str, Enum):
    """Níveis de sensibilidade dos dados."""
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"


class DataCategory(str, Enum):
    """Categorias de dados pessoais (LGPD)."""
    IDENTIFICACAO = "identificacao"
    CONTATO = "contato"
    FINANCEIRO = "financeiro"
    SAUDE = "saude"
    BIOMETRICO = "biometrico"
    GENETICO = "genetico"
    OPINIAO_POLITICA = "opiniao_politica"
    RELIGIAO = "religiao"
    ORIENTACAO_SEXUAL = "orientacao_sexual"
    ORIGEM_RACIAL = "origem_racial"
    FILIACAO_SINDICAL = "filiacao_sindical"


class AuditSettings(BaseSettings):
    """Configurações de auditoria."""

    # Padrões de dados sensíveis (regex)
    patterns_cpf: str = r"\d{3}\.?\d{3}\.?\d{3}-?\d{2}"
    patterns_cnpj: str = r"\d{2}\.?\d{3}\.?\d{3}/?\d{4}-?\d{2}"
    patterns_email: str = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
    patterns_telefone: str = r"\(?\d{2}\)?\s?\d{4,5}-?\d{4}"
    patterns_cep: str = r"\d{5}-?\d{3}"
    patterns_rg: str = r"\d{1,2}\.?\d{3}\.?\d{3}-?[0-9Xx]"
    patterns_cartao_credito: str = r"\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}"
    patterns_ip: str = r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}"
    patterns_data_nascimento: str = r"\d{2}/\d{2}/\d{4}"

    # Colunas suspeitas (nomes comuns)
    suspicious_columns: List[str] = [
        "cpf", "cnpj", "rg", "email", "telefone", "celular",
        "nome", "nome_completo", "endereco", "cep", "data_nascimento",
        "nascimento", "salario", "renda", "senha", "password",
        "cartao", "conta", "agencia", "pis", "pasep", "ctps",
        "titulo_eleitor", "cns", "sus", "mae", "pai"
    ]

    # Limites
    sample_size: int = 1000  # Amostra para análise
    min_unique_ratio: float = 0.5  # Mínimo de valores únicos para considerar PII

    class Config:
        env_file = ".env"
        extra = "ignore"


class AnonymizationSettings(BaseSettings):
    """Configurações de anonimização."""

    # Métodos disponíveis
    method_hash: str = "sha256"
    method_mask: str = "mask"
    method_generalize: str = "generalize"
    method_suppress: str = "suppress"
    method_pseudonymize: str = "pseudonymize"

    # Configurações de mascaramento
    mask_char: str = "*"
    mask_cpf: str = "***.***.***-**"
    mask_email: str = "***@***.***"
    mask_telefone: str = "(**) *****-****"

    # Salt para hash (IMPORTANTE: mudar em produção!)
    # Valor padrão inseguro - será validado em runtime
    hash_salt: str = Field(default="CHANGE_THIS_SALT_IN_PRODUCTION", alias="HASH_SALT")

    # Comprimento mínimo do salt para segurança
    min_salt_length: int = 16

    class Config:
        env_file = ".env"
        extra = "ignore"

    def is_salt_secure(self) -> bool:
        """Verifica se o salt é seguro para uso em produção."""
        insecure_defaults = [
            "CHANGE_THIS_SALT_IN_PRODUCTION",
            "default_salt",
            "salt",
            "123456",
            ""
        ]
        return (
            self.hash_salt not in insecure_defaults and
            len(self.hash_salt) >= self.min_salt_length
        )

    def get_salt_warning(self) -> str:
        """Retorna mensagem de aviso sobre segurança do salt."""
        if self.hash_salt == "CHANGE_THIS_SALT_IN_PRODUCTION":
            return "AVISO CRITICO: Salt padrao em uso! Defina HASH_SALT no arquivo .env"
        elif len(self.hash_salt) < self.min_salt_length:
            return f"AVISO: Salt muito curto ({len(self.hash_salt)} chars). Minimo recomendado: {self.min_salt_length}"
        return ""


class ReportSettings(BaseSettings):
    """Configurações de relatórios."""

    output_format: str = "html"  # html, pdf, xlsx, json
    template_dir: str = "templates"
    output_dir: str = "data/reports"

    # Informações do relatório
    company_name: str = "Organização"
    dpo_name: str = "Encarregado de Dados"
    dpo_email: str = "dpo@organizacao.com"

    class Config:
        env_file = ".env"
        extra = "ignore"


class Settings(BaseSettings):
    """Configurações centralizadas."""

    project_name: str = "Sistema de Compliance LGPD"
    version: str = "1.0.0"

    audit: AuditSettings = AuditSettings()
    anonymization: AnonymizationSettings = AnonymizationSettings()
    report: ReportSettings = ReportSettings()

    # Diretórios
    data_dir: str = "data"
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()


# Classificação de dados sensíveis conforme LGPD
DADOS_SENSIVEIS_LGPD = {
    "dados_pessoais": {
        "descricao": "Informação relacionada a pessoa natural identificada ou identificável",
        "exemplos": ["nome", "cpf", "rg", "endereco", "email", "telefone"],
        "base_legal": "Art. 5º, I",
        "nivel_risco": "medio"
    },
    "dados_pessoais_sensiveis": {
        "descricao": "Dados sobre origem racial/étnica, convicção religiosa, opinião política, etc.",
        "exemplos": ["raca", "religiao", "partido_politico", "orientacao_sexual"],
        "base_legal": "Art. 5º, II",
        "nivel_risco": "alto"
    },
    "dados_saude": {
        "descricao": "Informações sobre saúde do titular",
        "exemplos": ["cid", "diagnostico", "medicamento", "exame", "prontuario"],
        "base_legal": "Art. 5º, II + Art. 11",
        "nivel_risco": "alto"
    },
    "dados_biometricos": {
        "descricao": "Características físicas utilizadas para identificação",
        "exemplos": ["digital", "face", "iris", "voz"],
        "base_legal": "Art. 5º, II",
        "nivel_risco": "alto"
    },
    "dados_geneticos": {
        "descricao": "Informações genéticas do titular",
        "exemplos": ["dna", "sequenciamento_genetico"],
        "base_legal": "Art. 5º, II",
        "nivel_risco": "critico"
    },
    "dados_criancas": {
        "descricao": "Dados de menores de idade",
        "exemplos": ["dados de menores de 18 anos"],
        "base_legal": "Art. 14",
        "nivel_risco": "alto"
    }
}

# Bases legais para tratamento (Art. 7º LGPD)
BASES_LEGAIS_LGPD = {
    "consentimento": "I - consentimento pelo titular",
    "obrigacao_legal": "II - cumprimento de obrigação legal ou regulatória",
    "administracao_publica": "III - pela administração pública, para tratamento de dados necessários à execução de políticas públicas",
    "estudos_pesquisa": "IV - para a realização de estudos por órgão de pesquisa",
    "execucao_contrato": "V - para a execução de contrato",
    "exercicio_direitos": "VI - para o exercício regular de direitos em processo judicial, administrativo ou arbitral",
    "protecao_vida": "VII - para a proteção da vida ou da incolumidade física",
    "tutela_saude": "VIII - para a tutela da saúde",
    "interesse_legitimo": "IX - para atender aos interesses legítimos do controlador",
    "protecao_credito": "X - para a proteção do crédito"
}

# Direitos dos titulares (Art. 18º LGPD)
DIREITOS_TITULARES = [
    "Confirmação da existência de tratamento",
    "Acesso aos dados",
    "Correção de dados incompletos, inexatos ou desatualizados",
    "Anonimização, bloqueio ou eliminação de dados desnecessários",
    "Portabilidade dos dados",
    "Eliminação dos dados tratados com consentimento",
    "Informação sobre compartilhamento de dados",
    "Informação sobre possibilidade de não consentir",
    "Revogação do consentimento"
]
