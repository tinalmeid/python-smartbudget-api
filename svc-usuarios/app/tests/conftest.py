"""
@file svc-usuarios/app/tests/conftest.py
@description: Fixtures compartilhadas para os testes do svc-usuarios.
              Configura banco de dados SQLite em memória e cliente HTTP para simular requisições sem depender de serviços externos.

@author: Tina de Almeida
@date: Abril de 2026
@version: 1.0.0
"""

import os
from dotenv import load_dotenv
load_dotenv()

# Sobrescrever variáveis de ambiente para testes
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["SECRET_KEY"] = "chave-secreta-para-testes-unitarios"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app

# --- Banco SQL em memória (apenas para testes) ---
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

from app import database
database.engine = engine
database.SessionLocal = TestingSessionLocal

# Banco de dados de teste
@pytest.fixture(scope="function")
def db():
    """
    Fixture que cria um banco SQLite em memória para cada teste.

    Cria todas as tabelas antes do teste e apaga depois.
    Garante que cada teste começa com banco limpo.

    Yields:
        Session: Sessão de banco de dados para uso nos testes.
    """
    Base.metadata.create_all(bind=engine)
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()

# Cliente HTTP de teste
@pytest.fixture(scope="function")
def client(db):
    """
    Fixture que cria um cliente HTTP para cada teste com banco isolado.

    Substitui a dependência get_db do FastAPI pelo banco de dados em memória.
    Permite simular requisições HTTP sem depender de serviços externos.

    Yields:
        TestClient: Cliente HTTP para uso nos testes.
    """
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

# Fixture com dados válidos para criação de usuário
@pytest.fixture
def usuario_dados():
    """
    Fixture com dados válidos para criação de usuário.

    Retorna:
        dict: Payload de usuário válido.
    """
    return {
        "email": "tina@smartbuget.com",
        "senha": "Senha@2026",
        "nome": "Tina Smartbudget"
    }

# Fixture com dados para o PATCH
@pytest.fixture
def usuario_update_dados():
    """
    Fixture com dados válidos para atualização de usuário.
    Usado no PATCH /usuarios/me

    Retorna:
        dict: Payload de usuário válido.
    """
    return {
        "nome": "Tina Smartbudget Atualizado",
        "renda_mensal": 5000.00
    }

# @file Fim do arquivo svc-usuarios/app/tests/conftest.py
