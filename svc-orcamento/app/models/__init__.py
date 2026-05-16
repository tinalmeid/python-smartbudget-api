"""
@module: svc-orcamento.app.models
@file: __init__.py
@description: Exporta os modelos de dados para o serviço de orçamento (svc-orcamento).
              Inclui as entidades Categoria, Orcamento e Transacao.
@author: Tina de Almeida
@date: Maio 2026
@version: 1.0.0
"""

from app.models.categoria import Categoria
from app.models.orcamento import Orcamento
from app.models.transacao import Transacao

__all__ = ["Categoria", "Orcamento", "Transacao"]

# @file: svc-orcamento/app/models/__init__.py
