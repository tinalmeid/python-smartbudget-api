"""
@file: svc-usuarios/app/database.py
@description: Configuração da conexão com o banco de dados via SQLAlchemy.
              Suporta PostgreSQL (produção/Neon) e SQLite (testes).
@author: Tina de Almeida
@date: Abril 2026
@version: 1.0.0
"""
import logging
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

logger = logging.getLogger(__name__)

# Lê a URL de conexão do arquivo .env
DATABASE_URL = os.getenv("DATABASE_URL", "")

if not DATABASE_URL:
    raise ValueError("Variável DATABASE_URL não encontrada no arquivo .env")

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
        pool_pre_ping=True,
        pool_size=5,
        max_overflow=10,
        pool_recycle=1800,
        echo=False
    )

# Cria a session factory — cada requisição abre e fecha uma session
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Cria a classe Base para os models
Base = declarative_base()


def get_db():
    """
    Dependency do FastAPI: Fornece uma session de banco por requisição.
    Garante que a conexão seja fechada corretamente após cada requisição,
    mesmo em caso de erro.

    Yields:
        Session: Session de banco de dados.
    """
    db = SessionLocal()
    try:
        yield db
        logger.debug("Session de banco de dados fechada com sucesso")
    except Exception as e:
        logger.error(f"Erro na session do banco: {e}", exc_info=True)
        db.rollback()
        raise
    finally:
        db.close()


# @file Fim do arquivo database.py
