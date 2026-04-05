"""
@file: svc-usuarios/app/schemas/usuario.py
@description: Schemas Pydantic do usuário.
              Define os contratos de entrada e saída da API — o que o cliente manda e o que recebe.

@author: Tina de Almeida
@date: Abril 2026
@version: 1.0.0
"""

import logging
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, field_validator

# Configuração de Logging
logger = logging.getLogger(__name__)

class UsuarioCreate(BaseModel):
    """
    Schema de entrada para criação de usuário — o que o cliente envia na criação
    Usado no POST /auth/register.
    """
    email: EmailStr = Field(..., description="Email do usuário", example="[EMAIL_ADDRESS]")
    senha: str = Field(min_length=8, max_length=128, description="Senha do usuário", example="senha123")
    nome: str | None = Field(None, description="Nome do usuário", example="Usuário Teste")

    @field_validator("senha")
    @classmethod
    def validate_senha(cls, valor: str) -> str:
        """
        Valida a força da senha do usuário

        Args:
            valor: Senha informada pelo usuário

        Returns:
            str: Senha validada

        Raises:
            ValueError: Se a senha não atender aos critérios mínimos.
        """
        if len(valor) < 8:
            raise ValueError("Senha deve ter pelo menos 8 caracteres")

        if not any(c.isupper() for c in valor):
            raise ValueError("Senha deve conter pelo menos uma letra maiúscula")

        if not any(c.isdigit() for c in valor):
            raise ValueError("Senha deve conter pelo menos um número")

        if not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in valor):
            raise ValueError("Senha deve conter pelo menos um caractere especial")
        return valor

class UsuarioLogin(BaseModel):
    """
    Schema de entrada para login de usuário — o que o cliente envia no login
    Usado no POST /auth/login.
    """
    email: EmailStr = Field(..., description="Email do usuário", example="[EMAIL_ADDRESS]")
    senha: str = Field(..., description="Senha do usuário", example="senha123")

class UsuarioResponse(BaseModel):
    """
    Schema de saída — o que a API retorna sobre o usuário.
    A senha NUNCA aparece aqui.
    Usado no GET /usuarios/{id} e no POST /auth/register.
    """
    id: str = Field(..., description="UUID do usuário", example="123e4567-e89b-12d3-a456-426614174000")
    email: EmailStr = Field(..., description="Email do usuário", example="[EMAIL_ADDRESS]")
    nome: str | None = Field(None, description="Nome do usuário", example="Usuário Teste")
    ativo: bool = Field(..., description="Indica se a conta do usuário está ativa", example=True)
    criado_em: datetime = Field(..., description="Data e hora de criação do registro", example="2022-01-01T00:00:00")

    class Config:
        from_attributes = True

class UsuarioUpdate(BaseModel):
    """
    Schema de entrada para atualização de usuário — o que o cliente envia na atualização
    Usado no PATCH /usuarios/me.
    Todos os campos são opcionais, atualiza apenas o que for enviado.
    """
    nome: str | None = Field(None, description="Nome do usuário", example="Usuário Teste")
    renda_mensal: str | None = Field(None, description="Renda mensal do usuário", example="1000.00")

class TokenResponse(BaseModel):
    """
    Schema de saída — o que a API retorna sobre o token.
    Usado no POST /auth/login.

    Retorna o token de acesso e o tipo do token.
    """
    access_token: str = Field(..., description="Token de acesso", example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...")
    refresh_token: str = Field(..., description="Token de refresh", example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...")
    token_type: str = Field(..., description="Tipo do token", example="bearer")

class TokenRefreshRequest(BaseModel):
    """
    Schema de entrada para refresh de token — o que o cliente envia no refresh
    Usado no POST /auth/refresh.
    """
    refresh_token: str = Field(..., description="Token de refresh", example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...")


# @file Fim do arquivo schemas/usuario.py
