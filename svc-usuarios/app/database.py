"""
@file: svc-usuarios/app/database.py
@description: Configuração da conexão com o banco de dados PlanetScale via SQLAlchemy.
              Define o engine, session factory e a classe Base para os models.

@author: Tina de Almeida
@date: Abril 2026
@version: 1.0.0
"""

import os
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Configuração de Logging
logger = logging.getLogger(__name__)

# Lê a URL de conexão do arquivo .env
# Formato: mysql+pymysql://usuario:senha@HOST/db_usuarios?ssl_ca=...
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("Variável DATABASE_URL não encontrada no arquivo .env")

# Cria o engine de conexão com o banco de dados
# pool_pre_ping= True -> verifica se a conexão está ativa antes de usar (importante pra PlanetScale)
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
    pool_recycle=1800,
    echo=False
)

# Cria a session factory - cada requisição abre e fecha uma session
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
    Garante que a conexão seja fechada corretamente após cada requisição, mesmo em caso de erro.

    @yields:
        db (SessionLocal): Session de banco de dados
    """
    db = SessionLocal()
    try:
        yield db
        logger.debug("Session de banco de dados fechada com sucesso")
    except Exception as e:
        logger.error(f"Erro ao fechar session de banco de dados: {e}", exc_info=True)
        db.rollback()
        raise e
    finally:
        db.close()

# @file Fim do arquivo database.py
