"""
@module svc-orcamento.app.routers.extrato
@file extrato.py
@description Endpoint HTTP para importação de extrato bancário via CSV.
@author Tina Almeida
@date Maio 2026
@version 1.0.0
"""

import logging

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.extrato_service import ExtratoService

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/v1",
    tags=["extrato"],
)

service = ExtratoService()


def get_usuario_id() -> int:
    """
    Simula a obtenção do ID do usuário autenticado.
    Em um cenário real, isso seria extraído do token de autenticação ou sessão.

    Returns:
        int: ID do usuário autenticado.
    """
    return 1  # Simulação de usuário autenticado


@router.post("/importar-extrato", status_code=status.HTTP_200_OK)
async def importar_extrato(
    categoria_id: int = Query(
        ..., description="ID da categoria para associar às transações importadas"),  # NOSONAR
    arquivo: UploadFile = File(...,
                               description="Arquivo CSV contendo o extrato bancário"),  # NOSONAR
    db: Session = Depends(get_db),  # NOSONAR
    usuario_id: int = Depends(get_usuario_id)  # NOSONAR
) -> dict:
    """
    Importa transações em lote a partir de um arquivo CSV contendo o extrato bancário.

    Args:
        categoria_id (int): ID da categoria para associar às transações importadas.
        arquivo (UploadFile): Arquivo CSV contendo o extrato bancário.
        db (Session): Sessão do banco de dados para operações de inserção.
        usuario_id (int): ID do usuário autenticado das transações importadas.

    Returns:
        dict: Resultado da importação contendo o número de transações importadas e detalhes de erros, se houver.

    Raises:
        HTTPException 400: Se o arquivo CSV estiver em um formato inválido ou vazio.
    """
    if not arquivo.filename.endswith('.csv'):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="O arquivo deve ser do tipo CSV."
                            )
    conteudo = await arquivo.read()

    try:
        resultado = service.importar_extrato(
            db, conteudo, usuario_id, categoria_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e

    return resultado

# @file Fim do arquivo svc-orcamento/app/routers/extrato.py
