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
from pydantic import BaseModel, EmailStr, Field, field_validator, ConfigDict


# Configuração de Logging
logger = logging.getLogger(__name__)

# --- Constantes para exemplos do Swagger ---
EXAMPLE_EMAIL = "tina@smartbudget.com"
EXAMPLE_NOME = "Tina Smartbudget"
EXAMPLE_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
EXAMPLE_DATA = "2026-01-01T00:00:00"
EXAMPLE_ID = "123e4567-e89b-12d3-a456-426614174000"
EXAMPLE_SENHA = "Senha@123"

# --- Constantes para descriptions ---
DESC_EMAIL = "Email do usuário"
DESC_NOME = "Nome do usuário"
DESC_SENHA = "Senha do usuário"
DESC_TOKEN_REFRESH = "Token de refresh"
DESC_TOKEN_ACESSO = "Token de acesso"
DESC_TOKEN_TIPO = "Tipo do token"
DESC_DATA = "Data e hora de criação do registro"
DESC_ID = "UUID do usuário"
DESC_ATIVO = "Indica se a conta do usuário está ativa"

class UsuarioCreate(BaseModel):
    """
    Schema de entrada para criação de usuário — o que o cliente envia na criação
    Usado no POST /auth/register.
    """
    email: EmailStr = Field(..., description=DESC_EMAIL, json_schema_extra={"example": EXAMPLE_EMAIL})
    senha: str = Field(min_length=8, max_length=128, json_schema_extra={"example": EXAMPLE_SENHA})
    nome: str | None = Field(None, description=DESC_NOME, json_schema_extra={"example": EXAMPLE_NOME})

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
    email: EmailStr = Field(..., description=DESC_EMAIL, json_schema_extra={"example": EXAMPLE_EMAIL})
    senha: str = Field(..., description=DESC_SENHA, json_schema_extra={"example": EXAMPLE_SENHA})

class UsuarioResponse(BaseModel):
    """
    Schema de saída — o que a API retorna sobre o usuário.
    A senha NUNCA aparece aqui.
    Usado no GET /usuarios/{id} e no POST /auth/register.
    """
    model_config = ConfigDict(from_attributes=True)
    id: str = Field(..., description=DESC_ID, json_schema_extra={"example": EXAMPLE_ID})
    email: EmailStr = Field(..., description=DESC_EMAIL, json_schema_extra={"example": EXAMPLE_EMAIL})
    nome: str | None = Field(None, description=DESC_NOME, json_schema_extra={"example": EXAMPLE_NOME})
    ativo: bool = Field(..., description=DESC_ATIVO, json_schema_extra={"example": True})
    criado_em: datetime = Field(..., description=DESC_DATA, json_schema_extra={"example": EXAMPLE_DATA})

class UsuarioUpdate(BaseModel):
    """
    Schema de entrada para atualização de usuário — o que o cliente envia na atualização
    Usado no PATCH /usuarios/me.
    Todos os campos são opcionais, atualiza apenas o que for enviado.
    """
    nome: str | None = Field(None, description=DESC_NOME, json_schema_extra={"example": EXAMPLE_NOME})
    renda_mensal: str | None = Field(None, description="Renda mensal do usuário", json_schema_extra={"example": "1000.00"})

class TokenResponse(BaseModel):
    """
    Schema de saída — o que a API retorna sobre o token.
    Usado no POST /auth/login.

    Retorna o token de acesso e o tipo do token.
    """
    access_token: str = Field(..., description=DESC_TOKEN_ACESSO, json_schema_extra={"example": EXAMPLE_TOKEN})
    refresh_token: str = Field(..., description=DESC_TOKEN_REFRESH, json_schema_extra={"example": EXAMPLE_TOKEN})
    token_type: str = Field(..., description=DESC_TOKEN_TIPO, json_schema_extra={"example": "bearer"})

class TokenRefreshRequest(BaseModel):
    """
    Schema de entrada para refresh de token — o que o cliente envia no refresh
    Usado no POST /auth/refresh.
    """
    refresh_token: str = Field(..., description=DESC_TOKEN_REFRESH, json_schema_extra={"example": EXAMPLE_TOKEN})


# @file Fim do arquivo schemas/usuario.py
