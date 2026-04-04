"""
@file svc-orcamento/app/main.py
@description: Ponto e entrada do svc-orcamento.
Inicializa o servidor FastAPI, configura middlewares de CORS e registra os routers de transações, categorias e orçamentos mensais.

@author: Tina de Almeida
@date: Abril de 2026
@version: 1.0.0
"""

# Habilita o tracing do Datadog — deve ser chamado antes de qualquer outro import
from ddtrace import patch_all
patch_all()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
import os

# Configura o logger para identificar o serviço
logger = logging.getLogger(__name__)

# Inicializa o servidor FastAPI
app = FastAPI(
    title="SmartBudget - svc-orcamento",
    description="API de gerenciamento financeiro pessoal. "
            "Responsável por transações, categorias, limites mensais e importação de extrato CSV.",
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

@app.get("/health", tags=["health"])
async def health_check() -> dict:
    """
    Verifica se o serviço está respondendo

    Returns:
        dict: Dicionário com o status do serviço com nome e versão
    """
    logger.info("Health check solicitado", extra={"service": "svc-orcamento", "version": "1.0.0"})
    return {"status": "ok", "service": "svc-orcamento", "version": "1.0.0"}

# @file Fim do arquivo svc-orcamento/app/main.py
