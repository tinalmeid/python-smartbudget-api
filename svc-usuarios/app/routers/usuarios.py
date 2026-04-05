"""
@file: svc-usuarios/app/routers/usuarios.py
@description: Router de perfil do usuário do svc-usuarios.
              Define os endpoints de consulta e atualização de perfil.
@author: Tina de Almeida
@date: Abril 2026
@version: 1.0.0
"""
import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.usuario import UsuarioResponse, UsuarioUpdate
from app.services import auth_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/usuarios", tags=["usuarios"])


def get_usuario_atual(
    token: str,
    db: Session = Depends(get_db)
) -> dict:
    """
    Dependency do FastAPI — valida o token e retorna o usuário autenticado.

    Args:
        token: Access token JWT do header Authorization.
        db: Session do banco injetada pelo FastAPI.

    Returns:
        dict: Payload do token com user_id e email.

    Raises:
        HTTPException 401: Se o token for inválido ou expirado.
    """
    try:
        payload = auth_service.verificar_token(token, tipo="access")
        return payload
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.get("/me", response_model=UsuarioResponse)
async def get_me(
    payload: dict = Depends(get_usuario_atual),
    db: Session = Depends(get_db)
):
    """
    Retorna os dados do usuário autenticado.

    Args:
        payload: Dados do token JWT com user_id e email.
        db: Session do banco injetada pelo FastAPI.

    Returns:
        UsuarioResponse: Dados do perfil do usuário.

    Raises:
        HTTPException 404: Se o usuário não for encontrado.
    """
    usuario = auth_service.buscar_por_email(payload.get("email"), db)
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )
    return usuario


@router.patch("/me", response_model=UsuarioResponse)
async def update_me(
    dados: UsuarioUpdate,
    payload: dict = Depends(get_usuario_atual),
    db: Session = Depends(get_db)
):
    """
    Atualiza os dados do perfil do usuário autenticado.

    Args:
        dados: Campos a atualizar — apenas o que for enviado é alterado.
        payload: Dados do token JWT com user_id e email.
        db: Session do banco injetada pelo FastAPI.

    Returns:
        UsuarioResponse: Dados atualizados do perfil.

    Raises:
        HTTPException 404: Se o usuário não for encontrado.
    """
    usuario = auth_service.buscar_por_email(payload.get("email"), db)
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )

    if dados.nome is not None:
        usuario.nome = dados.nome
    if dados.renda_mensal is not None:
        usuario.renda_mensal = dados.renda_mensal

    db.commit()
    db.refresh(usuario)

    logger.info("Perfil atualizado", extra={"usuario_id": usuario.id})
    return usuario


# @file Fim do arquivo routers/usuarios.py
