"""
@module: svc-orcamento.app.routers.orcamentos
@file: orcamentos.py
@description: Endpoints HTTP para orçamentos mensais e resumo financeiro.
@author: Tina de Almeida
@date: Maio 2026
@version: 1.0.0
"""

import logging

from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.orcamento import OrcamentoCreate, OrcamentoOut
from app.services.orcamento_service import OrcamentoService

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/v1/orcamentos",
    tags=["Orçamentos"]
)

service = OrcamentoService()


def get_usuario_id() -> int:
    """
    Extrai o ID do usuário autenticado do token JWT.
    Placeholder até integração com svc-usuario via middleware de autenticação.

    Returns:
        int: ID do usuário autenticado.
    """

    return 1  # Placeholder para desenvolvimento inicial


@router.post("", status_code=status.HTTP_201_CREATED)
def criar_orcamento(
        dados: OrcamentoCreate,
        db: Session = Depends(get_db),  # NOSONAR
        usuario_id: int = Depends(get_usuario_id)  # NOSONAR
) -> OrcamentoOut:
    """
    Define um limite mensal por categoria.

    Args:
        dados: Dados validados para criação do orçamento
        db: Sessão do banco de dados
        usuario_id: ID do usuário autenticado via token JWT

    Returns:
        OrcamentoOut: Orçamento criado com status 201.
    """
    return service.criar_orcamento(db, dados, usuario_id)


@router.get("/resumo")
def resumo_mensal(
        mes: str = Query(..., pattern=r"^\d{4}-\d{2}$",
                         description="Mês no formato YYYY-MM"),  # NOSONAR
        db: Session = Depends(get_db),  # NOSONAR
        usuario_id: int = Depends(get_usuario_id)  # NOSONAR
) -> list[dict]:
    """
    Retorna o gasto real vs limite por categoria no mês informado.

    Args:
        mes: Mês no formato YYYY-MM
        db: Sessão do banco de dados
        usuario_id: ID do usuário autenticado via token JWT

    Returns:
        list[dict]: Resumo financeiro mensal por categoria, incluindo limite, gasto real e status.
    """
    return service.calcular_resumo(db, usuario_id, mes)

# @file Fim do arquivo svc-orcamento/app/routers/orcamentos.py
