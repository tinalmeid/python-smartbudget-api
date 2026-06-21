"""
@module: svc-orcamento.app.database
@file: database.py
@description Configuração da conexão com o banco de dados via SQLAlchemy.
             Suporta PostgreSQL (produção/Neon) e SQLite (testes).
@author: Tina de Almeida
@date: Maio 2026
@version: 1.0.0
"""

import logging
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from fastapi import HTTPException, status
from sqlalchemy.exc import OperationalError

logger = logging.getLogger(__name__)

# Lê a URL de conexão do arquivo .env
DATABASE_URL = os.getenv("DATABASE_URL", "")

if not DATABASE_URL:
    DATABASE_URL = "sqlite:///:memory:"

# SQLite não suporta pool_size e max_overflow — usado nos testes
# PostgreSQL suporta — usado em desenvolvimento e produção
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
    )
else:
    engine = create_engine(
        DATABASE_URL,
        connect_args={"options": "-csearch_path=orcamento,public"},
        pool_pre_ping=True,
        pool_size=5,
        max_overflow=10,
        pool_recycle=1800,
        echo=False
    )

# Cria a session factory — cada requisição abre e fecha uma session
sessionlocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Cria a classe Base para os models
Base = declarative_base()


def get_db():
    """
    Dependency do FastAPI: Fornece uma session de banco por requisição.
    Garante que a conexão seja fechada corretamente após cada requisição.
    Se o banco estiver indisponível (OperationalError), converte em
    HTTPException 503 para o cliente, em vez de vazar um erro 500 genérico.

    Yields:
        Session: Session de banco de dados.

    Raises:
        HTTPException 503: Se o banco de dados estiver indisponível.
    """
    db = None
    try:
        db = sessionlocal()
        yield db
        logger.debug("Session de banco de dados fechada com sucesso")
    except OperationalError as e:
        logger.exception("Banco de dados indisponível: %s", e)
        if db:
            db.rollback()
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Serviço de banco de dados indisponível. Tente novamente em instantes.",
        ) from e
    except Exception as e:  # pylint: disable=broad-except
        logger.exception("Erro durante a operação com o banco de dados: %s", e)
        if db:
            db.rollback()
        raise
    finally:
        if db:
            db.close()

# @file Fim do arquivo svc-orcamento/app/database.py
