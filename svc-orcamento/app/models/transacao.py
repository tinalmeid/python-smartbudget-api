"""
@module: svc-orcamento.app.models.transacao
@file: transacao.py
@description: Modelagem da entidade Transacao para transações financeiras do usuário.
              Representa os gastos e receitas do usuário, associadas a categorias.
@author: Tina de Almeida
@date: Maio 2026
@version: 1.0.0
"""

import logging
from datetime import date

from sqlalchemy import Column, Date, ForeignKey, Index, Integer, Numeric, String
from sqlalchemy.orm import relationship

from app.database import Base

logger = logging.getLogger(__name__)


class Transacao(Base):
    """
    Representa uma transação financeira do usuário.

    Atributos:
    id: Identificador único da transação
    usuario_id: Identificador do usuário associado à transação.
    categoria_id: Chave estrangeira para a categoria associada.
    valor: Valor da transação.
    data_transacao: Data em que o gasto ocorreu.
    descricao: Descrição da transação (Ex: Compra no supermercado).
    categoria: Relacionamento com a categoria.
    """

    __tablename__ = 'transacoes'
    __table_args__ = (
        Index("ix_transacoes_usuario_data", "usuario_id", "data_transacao"),
        {"schema": "orcamento"},
    )

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, nullable=False)
    categoria_id = Column(Integer, ForeignKey(
        'orcamento.categorias.id'), nullable=False)
    valor = Column(Numeric(10, 2), nullable=False)
    data_transacao = Column(Date, nullable=False, default=date.today)
    descricao = Column(String(255), nullable=True)

    # Relacionamento com Categoria
    categoria = relationship("Categoria", back_populates="transacoes")

# Fim do arquivo svc-orcamento/app/models/transacao.py
