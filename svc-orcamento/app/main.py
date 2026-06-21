"""
@module: svc-orcamento.app.main
@file: main.py
@description: Ponto e entrada do svc-orcamento.
Inicializa o servidor FastAPI, configura middlewares de CORS e registra os routers de transações, categorias e orçamentos mensais.

@author: Tina de Almeida
@date: Abril de 2026
@version: 1.0.1
"""

# Habilita o tracing do Datadog — deve ser chamado antes de qualquer outro import
try:
    from ddtrace import patch_all
    patch_all()
except ImportError:
    pass

# Stdlib (bibliotecas nativas do Python)
import os
import logging

# Third-party (libs instaladas)
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI

# Local imports (módulos do projeto)
from app.routers import transacoes, categorias, extrato, orcamentos
from app.kafka import kafka_producer
from app.kafka_consumer import kafka_consumer

# Configura o logger para identificar o serviço
logger = logging.getLogger(__name__)


# Gerencia o ciclo de vida da aplicação, iniciando e parando o KafkaProducer


@asynccontextmanager
async def lifespan(_: FastAPI):
    """Gerencia o ciclo de vida da aplicação."""
    await kafka_producer.start()
    await kafka_consumer.start()
    yield
    await kafka_producer.stop()
    await kafka_consumer.stop()

# Inicializa o servidor FastAPI
app = FastAPI(
    title="SmartBudget - svc-orcamento",
    description="API de gerenciamento financeiro pessoal. "
    "Responsável por transações, categorias, limites mensais e importação de extrato CSV.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,  # ← adiciona esta linha
)

# Lê os origins permitidos do arquivo .env
# Em dev: http://localhost:3000
# Em prod: https://smartbudget.app.br (futuro)
ALLOWED_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:3000,http://localhost:8001,http://localhost:8002,http://localhost:8003,http://localhost:8004"  # NOSONAR
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
app.include_router(transacoes.router)
app.include_router(categorias.router)
app.include_router(orcamentos.router)
app.include_router(extrato.router)


@app.get("/health", tags=["health"])
async def health_check() -> dict:
    """
    Verifica se o serviço está respondendo

    Returns:
        dict: Dicionário com o status do serviço com nome e versão
    """
    logger.info("Health check solicitado", extra={
                "service": "svc-orcamento", "version": "1.0.0"})
    return {"status": "ok", "service": "svc-orcamento", "version": "1.0.0"}

# @file Fim do arquivo svc-orcamento/app/main.py
