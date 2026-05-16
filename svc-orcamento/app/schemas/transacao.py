"""
@module: svc-orcamento.app.schemas.transacao
@file: transacao.py
@description: Schemas Pydantic para validação de transações financeiras do usuário.
              Define os modelos de dados para criação e leitura de transações, associadas a categorias.
@author: Tina de Almeida
@date: Maio 2026
@version: 1.0.0
"""

from datetime import date
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field


class TransacaoCreate(BaseModel):
    """
    Dados enviados pelo usuário para criar uma transação.

    Atributos:
    categoria_id: Chave estrangeira para a categoria associada.
    valor: Valor da transação.
    descricao: Descrição da transação (Ex: Compra no supermercado).
    data_transacao: Data em que o gasto ocorreu.
    """

    categoria_id: int = Field(..., description="ID da categoria associada")
    valor: Decimal = Field(..., gt=0, decimal_places=2,
                           description="Valor da transação (positivo)")
    descricao: Optional[str] = Field(
        None, max_length=255, description="Descrição da transação")
    data_transacao: date = Field(
        default_factory=date.today, description="Data da transação")


class TransacaoOut(BaseModel):
    """
    Dados retornados pela API após criar ou consultar uma transação.

    Atributos:
    id: Identificador único da transação
    usuario_id: Identificador do usuário associado à transação.
    categoria_id: Chave estrangeira para a categoria associada.
    valor: Valor da transação.
    descricao: Descrição da transação (Ex: Compra no supermercado).
    data_transacao: Data da transação.
    """

    id: int = Field(..., description="Identificador único da transação")
    usuario_id: int = Field(...,
                            description="Identificador do usuário associado à transação.")
    categoria_id: int = Field(...,
                              description="Chave estrangeira para a categoria associada.")
    valor: Decimal = Field(..., gt=0, decimal_places=2,
                           description="Valor da transação (positivo)")
    descricao: Optional[str] = Field(
        None, max_length=255, description="Descrição da transação")
    data_transacao: date = Field(
        default_factory=date.today, description="Data da transação")

    model_config = {
        "from_attributes": True
    }

# @file Final do arquivo transacao.py
