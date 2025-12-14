"""
Validação de dados usando Pydantic.
Define schemas para garantir qualidade dos dados extraídos.
"""

from typing import Optional, List
from pydantic import BaseModel, Field, field_validator
from datetime import datetime


class RegiaoSchema(BaseModel):
    """Schema para validação de regiões."""

    id: int = Field(..., ge=1, le=5, description="ID da região (1-5)")
    sigla: str = Field(..., min_length=1, max_length=2)
    nome: str = Field(..., min_length=2, max_length=50)


class EstadoSchema(BaseModel):
    """Schema para validação de estados."""

    id: int = Field(..., ge=11, le=53, description="ID do estado (11-53)")
    sigla: str = Field(..., min_length=2, max_length=2)
    nome: str = Field(..., min_length=2, max_length=50)
    regiao_id: int = Field(..., ge=1, le=5)
    regiao_sigla: str = Field(..., min_length=1, max_length=2)
    regiao_nome: str = Field(..., min_length=2, max_length=50)

    @field_validator("sigla")
    @classmethod
    def validate_sigla(cls, v: str) -> str:
        if not v.isupper():
            return v.upper()
        return v


class MunicipioSchema(BaseModel):
    """Schema para validação de municípios."""

    id: int = Field(..., ge=1000000, le=9999999, description="Código IBGE 7 dígitos")
    nome: str = Field(..., min_length=2, max_length=100)
    microrregiao_id: Optional[int] = None
    microrregiao_nome: Optional[str] = None
    mesorregiao_id: Optional[int] = None
    mesorregiao_nome: Optional[str] = None
    uf_id: int = Field(..., ge=11, le=53)
    uf_sigla: str = Field(..., min_length=2, max_length=2)
    uf_nome: str = Field(..., min_length=2, max_length=50)
    regiao_id: int = Field(..., ge=1, le=5)
    regiao_sigla: str = Field(..., min_length=1, max_length=2)
    regiao_nome: str = Field(..., min_length=2, max_length=50)


class PopulacaoSchema(BaseModel):
    """Schema para validação de dados populacionais."""

    variavel_id: str
    variavel_nome: str
    unidade: str
    localidade_id: str = Field(..., description="Código da localidade")
    localidade_nome: str
    localidade_nivel: Optional[str] = None
    ano: int = Field(..., ge=1900, le=2100)
    valor: float = Field(..., ge=0, description="Valor não pode ser negativo")

    @field_validator("ano")
    @classmethod
    def validate_ano(cls, v: int) -> int:
        current_year = datetime.now().year
        if v > current_year + 1:
            raise ValueError(f"Ano {v} é maior que o ano atual + 1")
        return v


class PIBSchema(BaseModel):
    """Schema para validação de dados de PIB."""

    variavel_id: str
    variavel_nome: str
    unidade: str
    localidade_id: str
    localidade_nome: str
    localidade_nivel: Optional[str] = None
    ano: int = Field(..., ge=1900, le=2100)
    valor: float = Field(..., description="Valor do PIB")


class DataValidator:
    """
    Validador de dados utilizando schemas Pydantic.

    Valida DataFrames contra schemas definidos,
    reportando registros válidos e inválidos.
    """

    @staticmethod
    def validate_regioes(data: list) -> tuple[list, list]:
        """
        Valida lista de regiões.

        Returns:
            Tupla (registros_validos, registros_invalidos)
        """
        valid = []
        invalid = []

        for record in data:
            try:
                validated = RegiaoSchema(**record)
                valid.append(validated.model_dump())
            except Exception as e:
                invalid.append({"record": record, "error": str(e)})

        return valid, invalid

    @staticmethod
    def validate_estados(data: list) -> tuple[list, list]:
        """
        Valida lista de estados.

        Returns:
            Tupla (registros_validos, registros_invalidos)
        """
        valid = []
        invalid = []

        for record in data:
            try:
                validated = EstadoSchema(**record)
                valid.append(validated.model_dump())
            except Exception as e:
                invalid.append({"record": record, "error": str(e)})

        return valid, invalid

    @staticmethod
    def validate_municipios(data: list) -> tuple[list, list]:
        """
        Valida lista de municípios.

        Returns:
            Tupla (registros_validos, registros_invalidos)
        """
        valid = []
        invalid = []

        for record in data:
            try:
                validated = MunicipioSchema(**record)
                valid.append(validated.model_dump())
            except Exception as e:
                invalid.append({"record": record, "error": str(e)})

        return valid, invalid

    @staticmethod
    def validate_populacao(data: list) -> tuple[list, list]:
        """
        Valida lista de dados populacionais.

        Returns:
            Tupla (registros_validos, registros_invalidos)
        """
        valid = []
        invalid = []

        for record in data:
            try:
                validated = PopulacaoSchema(**record)
                valid.append(validated.model_dump())
            except Exception as e:
                invalid.append({"record": record, "error": str(e)})

        return valid, invalid

    @staticmethod
    def validate_pib(data: list) -> tuple[list, list]:
        """
        Valida lista de dados de PIB.

        Returns:
            Tupla (registros_validos, registros_invalidos)
        """
        valid = []
        invalid = []

        for record in data:
            try:
                validated = PIBSchema(**record)
                valid.append(validated.model_dump())
            except Exception as e:
                invalid.append({"record": record, "error": str(e)})

        return valid, invalid
