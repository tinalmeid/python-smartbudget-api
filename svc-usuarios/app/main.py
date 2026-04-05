"""
@file svc-usuarios/app/main.py
@description: Ponto e entrada do svc-usuarios.
Inicializa o servidor FastAPI, configura middlewares e registra os outers de autenticação e perfil de usuário.

@author: Tina de Almeida
@date: Abril de 2026
@version: 1.0.0
"""

# Habilita o tracing do Datadog — deve ser chamado antes de qualquer outro import
try:
    from ddtrace import patch_all
    patch_all()
except ImportError:
    pass

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth, usuarios
import logging
import os
from dotenv import load_dotenv

# Carrega variáveis do .env
load_dotenv()

# Configura o logger para identificar o serviço
logger = logging.getLogger(__name__)

# Inicializa o servidor FastAPI
app = FastAPI(
    title="SmartBudget - svc-usuarios",
    description="API de autenticação e gerenciamento de perfis de usuário. "
                "Responsável por registro, login JWT e atualização de perfil.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Lê os origins permitidos do arquivo .env
# Em dev: http://localhost:3000
# Em prod: https://smartbudget.app.br (futuro)
ALLOWED_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:3000,http://localhost:8001,http://localhost:8002,http://localhost:8003,http://localhost:8004"
).split(",")

# Configura CORS — restringe origens, métodos e headers permitidos
# Em produção substituir ALLOWED_ORIGINS pelo domínio real
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=[
        "GET",
        "POST",
        "PUT",
        "PATCH",
        "DELETE",
    ],
    allow_headers=[
        "Authorization",
        "Content-Type",
        "X-Requested-With",
        "X-CSRFToken",
    ],
)

# Registra os routers
app.include_router(auth.router)
app.include_router(usuarios.router)

@app.get("/health", tags=["health"])
async def health_check() -> dict:
    """
    Verifica se o serviço está respondendo

    Returns:
        dict: Dicionário com o status do serviço com nome e versão
    """
    logger.info("Health check solicitado", extra={"service": "svc-usuarios", "version": "1.0.0"})
    return {"status": "ok", "service": "svc-usuarios", "version": "1.0.0"}

# @file Fim do arquivo svc-usuarios/app/main.py
