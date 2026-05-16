"""
@module: svc-orcamento.app.models.orcamento
@file: orcamento.py
@description: Modelagem da entidade Orcamento para o serviço de orçamento.
              Representa o orçamento mensal do usuário, associada a categorias.
@author: Tina de Almeida
@date: Maio 2026
@version: 1.0.0
"""
import logging

from sqlalchemy import Column, ForeignKey, Integer, Numeric, String, UniqueConstraint
from sqlalchemy.orm import relationship

from app.database import Base

logger = logging.getLogger(__name__)


class Orcamento(Base):
    """
    Representa o orçamento mensal do usuário.

    Atributos:
    id: Identificador único do orçamento.
    usuario_id: ID do usuário dono do orçamento.
    categoria_id: FK para a categoria do limite.
    limite: Valor máximo permitido no mês.
    mes_ano: Mês de referência no formato YYYY-MM.
    categoria: Relação com a categoria.
    """

    __tablename__ = 'orcamentos'
    __table_args__ = (
        UniqueConstraint("usuario_id", "categoria_id", "mes_ano",
                         name="uq_orcamento_usuario_categoria_mes"),
        {"schema": "orcamento"},
    )

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, nullable=False)
    categoria_id = Column(Integer, ForeignKey(
        'orcamento.categorias.id'), nullable=False)
    limite = Column(Numeric(10, 2), nullable=False)
    mes_ano = Column(String(7), nullable=False)  # Formato YYYY-MM

    # Relacionamento com Categoria
    categoria = relationship("Categoria", back_populates="orcamentos")
