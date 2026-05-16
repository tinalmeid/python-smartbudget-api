"""
@module: svc-orcamento.app.models.categoria
@file: categoria.py
@description: Modelagem da entidade Categoria para o serviço de orçamento.
              Representa os tipos de gasto do usuário (ex: Alimentação, Transporte).
@author: Tina de Almeida
@date: Maio 2026
@version: 1.0.0
"""

import logging

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base

logger = logging.getLogger(__name__)


class Categoria(Base):
    """
    Representa uma categoria de gasto.

    Atributos:
    id: Identificador único da categoria
    nome: Nome da categoria (Ex: Alimentação).
    tipo: Tipo de gasto (Ex: Fixo, Variável).
    transacoes: Relação com as transações desta categoria.
    orcamentos: Relações com os orçamentos desta categoria.
    """

    __tablename__ = 'categorias'
    __table_args__ = {'schema': 'orcamento'}

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    tipo = Column(String(50), nullable=False)

    # Relacionamento com Transacao
    transacoes = relationship("Transacao", back_populates="categoria")

    # Relacionamento com Orcamento
    orcamentos = relationship("Orcamento", back_populates="categoria")


# Fim do arquivo svc-orcamento/app/models/categoria.py
