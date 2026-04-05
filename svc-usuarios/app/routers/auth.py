"""
@file: svc-usuarios/app/routers/auth.py
@description: Router de autenticação do svc-usuarios.
              Define os endpoints de registro, login e refresh de token JWT.
@author: Tina de Almeida
@date: Abril 2026
@version: 1.0.0
"""
import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.usuario import (
    TokenRefreshRequest,
    TokenResponse,
    UsuarioCreate,
    UsuarioLogin,
    UsuarioResponse,
)
from app.services import auth_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register",
    response_model=UsuarioResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register(dados: UsuarioCreate, db: Session = Depends(get_db)):
    """
    Registra um novo usuário no sistema.

    Args:
        dados: Dados do usuário validados pelo schema UsuarioCreate.
        db: Session do banco injetada pelo FastAPI.

    Returns:
        UsuarioResponse: Dados do usuário criado.

    Raises:
        HTTPException 409: Se o e-mail já estiver cadastrado.
    """
    try:
        usuario = auth_service.criar_usuario(dados, db)
        return usuario
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )


@router.post("/login", response_model=TokenResponse)
async def login(dados: UsuarioLogin, db: Session = Depends(get_db)):
    """
    Autentica o usuário e retorna os tokens JWT.

    Args:
        dados: E-mail e senha do usuário.
        db: Session do banco injetada pelo FastAPI.

    Returns:
        TokenResponse: Access token e refresh token.

    Raises:
        HTTPException 401: Se as credenciais forem inválidas.
    """
    try:
        usuario = auth_service.autenticar_usuario(dados.email, dados.senha, db)
        payload = {"user_id": usuario.id, "email": usuario.email}
        return TokenResponse(
            access_token=auth_service.criar_access_token(payload),
            refresh_token=auth_service.criar_refresh_token(payload),
            token_type="bearer"
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )


@router.post("/refresh", response_model=TokenResponse)
async def refresh(dados: TokenRefreshRequest):
    """
    Renova o access token usando o refresh token.

    Args:
        dados: Refresh token enviado pelo cliente.

    Returns:
        TokenResponse: Novo access token.

    Raises:
        HTTPException 401: Se o refresh token for inválido ou expirado.
    """
    try:
        payload = auth_service.verificar_token(dados.refresh_token, tipo="refresh")
        novo_access_token = auth_service.criar_access_token({
            "user_id": payload.get("user_id"),
            "email": payload.get("email")
        })
        return TokenResponse(
            access_token=novo_access_token,
            refresh_token=dados.refresh_token,
            token_type="bearer"
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token inválido ou expirado"
        )


# @file Fim do arquivo routers/auth.py
