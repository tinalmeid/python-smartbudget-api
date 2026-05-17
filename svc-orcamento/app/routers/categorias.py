"""
@module svc-orcamento.app.routers.categorias
@file: categorias.py
@description: Endpoints HTTP para gerenciamento de categorias de gastos.
@author: Tina de Almeida
@date: Maio 2026
@version: 1.0.0
"""

import logging

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.categoria import Categoria
from app.schemas.categoria import CategoriaCreate, CategoriaOut

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/v1/categorias", tags=["categorias"])


@router.post("", status_code=status.HTTP_201_CREATED)
def criar_categoria(
    dados: CategoriaCreate,
    db: Session = Depends(get_db),
) -> CategoriaOut:
    """
    Cria uam nova categoria de gasto.

    Args:
        dados (CategoriaCreate): Dados para criar a categoria.
        db (Session): Sessão de banco de dados.

    Returns:
        CategoriaOut: Dados da categoria criada com Status 201.

    Raises:
        HTTPException 409: Se a categoria já existir, retorna status 409.
    """

    existente = db.query(Categoria).filter(
        Categoria.nome == dados.nome).first()
    if existente:
        from fastapi import HTTPException
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Já existe uma categoria com este nome."
        )

    categoria = Categoria(nome=dados.nome, tipo=dados.tipo)
    db.add(categoria)
    db.commit()
    db.refresh(categoria)

    logger.info("Categoria criada: id=%s nome=%s",
                categoria.id, categoria.nome)
    return categoria
