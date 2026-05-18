"""
@module: svc-orcamento.app.routers.transacoes
@file: transacoes.py
@description: Endpoints HTTP para gerenciamento de transações financeiras.
@author: Tina de Almeida
@date: Maio 2026
@version: 1.0.0
"""

import logging
from typing import Optional

from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session
from app.kafka import kafka_producer

from app.database import get_db
from app.schemas.transacao import TransacaoCreate, TransacaoOut
from app.services.transacao_service import TransacaoService

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/v1/transacoes",
    tags=["Transações"]
)

service = TransacaoService()


def get_usuario_id() -> int:
    """
    Extrai o ID do usuário autenticado do token JWT.
    Placeholder até integração com svc-usuario via middleware de autenticação.

    Returns:
        int: ID do usuário autenticado.
    """

    return 1  # Placeholder para desenvolvimento inicial


@router.post("", status_code=status.HTTP_201_CREATED)
async def criar_transacao(
        dados: TransacaoCreate,
        db: Session = Depends(get_db),  # NOSONAR
        usuario_id: int = Depends(get_usuario_id)  # NOSONAR
) -> TransacaoOut:
    """
    Registra uma nova transação financeira.
    E publica evento no Kafka.

    Args:
        dados: Dados validados
        db: Sessão do banco de dados
        usuario_id: ID do usuário autenticado

    Returns:
        TransacaoOut: Transação criada com status 201.
    """
    transacao = service.criar_transacao(db, dados, usuario_id)

    # Fire-and-forget — não bloqueia o retorno 201
    await kafka_producer.publicar_transacao_criada(
        usuario_id=usuario_id,
        valor=str(transacao.valor),
        categoria_id=transacao.categoria_id,
        data_transacao=str(transacao.data_transacao),
    )

    return transacao


@router.get("")
def listar_transacoes(
        mes: Optional[str] = Query(
            # NOSONAR
            default=None, pattern=r"^\d{4}-\d{2}$", description="Filtro de mês no formato YYYY-MM"),
        categoria: Optional[str] = Query(
            default=None, description="Filtro de categoria por nome"),  # NOSONAR
        pagina: int = Query(
            default=1, ge=1, description="Número da página"),  # NOSONAR
        tamanho: int = Query(default=20, ge=1, le=100,
                             description="Quantidade de itens por página"),  # NOSONAR
        db: Session = Depends(get_db),  # NOSONAR
        usuario_id: int = Depends(get_usuario_id)  # NOSONAR
) -> list[TransacaoOut]:
    """
    Lista transações do usuário com filtros opcionais.

    Args:
        mes: Filtro de mês no formato YYYY-MM.
        categoria: Filtro de categoria por nome.
        pagina: Número da página
        tamanho: Quantidade de itens por página
        db: Sessão do banco de dados
        usuario_id: ID do usuário autenticado

    Returns:
        list[TransacaoOut]: Lista paginada de transações financeiras.
    """
    return service.listar_transacoes(db, usuario_id, mes, categoria, pagina, tamanho)


@router.delete("/{transacao_id}", status_code=status.HTTP_204_NO_CONTENT)
def deletar_transacao(
        transacao_id: int,
        db: Session = Depends(get_db),  # NOSONAR
        usuario_id: int = Depends(get_usuario_id)  # NOSONAR
) -> None:
    """
    Deleta uma transação do usuário autenticado.

    Args:
        transacao_id: ID da transação a ser excluída.
        db: Sessão do banco de dados
        usuario_id: ID do usuário autenticado

    Raises:
        HTTPException 404: Se a transação não existir.
        HTTPException 403: Se a transação não pertencer ao usuário autenticado.
    """
    service.deletar_transacao(db, transacao_id, usuario_id)

# @file Fim do arquivo app/routers/transacoes.py
