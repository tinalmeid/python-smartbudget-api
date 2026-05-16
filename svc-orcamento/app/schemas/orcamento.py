"""
@module: svc-orcamento.app.schemas.orcamento
@file: orcamento.py
@description: Schemas Pydantic para validação de orçamentos financeiros do usuário.
              Define os modelos de dados para criação e leitura de orçamentos.
@author: Tina de Almeida
@date: Maio 2026
@version: 1.0.0
"""

from decimal import Decimal

from pydantic import BaseModel, Field, field_validator


class OrcamentoCreate(BaseModel):
    """
    Dados enviados pelo usuário para definir um limite mensal.

    Atributos:
    categoria_id: int = Field(..., description="ID da categoria associada")
    limite: Decimal = Field(..., gt=0, decimal_places=2,
                            description="Limite máximo para a categoria no mês")
    mes_ano: str = Field(..., description="Mês e ano para o qual o orçamento é definido (formato YYYY-MM)")
    """

    categoria_id: int = Field(..., description="ID da categoria associada")
    limite: Decimal = Field(..., gt=0, decimal_places=2,
                            description="Limite máximo para a categoria no mês")
    mes_ano: str = Field(pattern=r"^\d{4}-\d{2}$",
                         description="Mês e ano para o qual o orçamento é definido (formato YYYY-MM)")

    @field_validator("mes_ano")
    @classmethod
    def validar_mes_ano(cls, value: str) -> str:
        """
       Valida se mes_ano está no formato YYYY-MM e se o mês é válido.

       Args:
           value: Valor do campo mes_ano.

       Returns:
           str: Valor validado.

       Raises:
           ValueError: Se o mês for inválido.
       """

        mes = int(value.split("-")[1])
        if mes < 1 or mes > 12:
            raise ValueError("Mês inválido — use um valor entre 01 e 12")
        return value


class OrcamentoOut(BaseModel):
    """
    Dados retornados pela API após criar ou consultar um orçamento.

    Atributos:
    id: Identificador único do orçamento.
    usuario_id: Identificador do usuário associado ao orçamento.
    categoria_id: Chave estrangeira para a categoria associada.
    limite: Valor do limite mensal definido para a categoria.
    mes_ano: Mês e ano para o qual o orçamento é definido (formato YYYY-MM).
    """

    id: int = Field(..., description="Identificador único do orçamento")
    usuario_id: int = Field(...,
                            description="Identificador do usuário associado ao orçamento.")
    categoria_id: int = Field(...,
                              description="Chave estrangeira para a categoria associada.")
    limite: Decimal = Field(..., gt=0, decimal_places=2,
                            description="Valor do limite mensal definido para a categoria")
    mes_ano: str = Field(
        ..., description="Mês e ano para o qual o orçamento é definido (formato YYYY-MM)")

    model_config = {
        "from_attributes": True
    }

# @file Final do arquivo orcamento.py
