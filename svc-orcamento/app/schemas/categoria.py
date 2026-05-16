"""
@module: svc-orcamento.app.schemas.categoria
@file: categoria.py
@description: Schemas Pydantic para validação de categorias financeiras do usuário.
              Define os modelos de dados para criação e leitura de categorias.
@author: Tina de Almeida
@date: Maio 2026
@version: 1.0.0
"""

from pydantic import BaseModel, Field


class CategoriaCreate(BaseModel):
    """
    Dados enviados pelo usuário para criar uma categoria.

    Atributos:
    nome: Nome da categoria (Ex: Alimentação, Transporte).
    tipo: Tipo da categoria (Ex: Despesa, Receita).
    """

    nome: str = Field(min_length=2, max_length=100,
                      description="Nome da categoria")
    tipo: str = Field(min_length=2, max_length=50,
                      description="Tipo da categoria")


class CategoriaOut(BaseModel):
    """
    Dados retornados pela API após criar ou consultar uma categoria.

    Atributos:
    id: Identificador único da categoria.
    nome: Nome da categoria (Ex: Alimentação, Transporte).
    tipo: Tipo da categoria (Ex: Despesa, Receita).
    """

    id: int = Field(..., description="Identificador único da categoria")
    nome: str = Field(min_length=2, max_length=100,
                      description="Nome da categoria")
    tipo: str = Field(min_length=2, max_length=50,
                      description="Tipo da categoria")

    model_config = {
        "from_attributes": True
    }

# @file Final do arquivo categoria.py
