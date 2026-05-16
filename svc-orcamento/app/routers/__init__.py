"""
@module: svc-orcamento.app.routers
@file: __init__.py
@description: Exporta os roteadores relacionados ao orçamento (svc-orcamento).
@author: Tina de Almeida
@date: Maio 2026
@version: 1.0.0
"""

from app.routers import orcamentos
from app.routers import transacoes

__all__ = [
    "orcamentos",
    "transacoes"
]

# Fim do arquivo svc-orcamento/app/routers/__init__.py
