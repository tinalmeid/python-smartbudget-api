"""
@module svc-orcamento.app.tests.conftest
@file conftest.py
@description Fixtures compartilhadas para os testes do svc-orcamento.
             Configura banco SQLite em memória e cliente HTTP isolado por teste.
             Usamos SQLite em memória para garantir testes rápidos e independentes, sem afetar dados reais.
@author: Tina de Almeida
@Date Maio 2026
@version 1.0.0
"""

# Para definir o escopo de uma fixture, use o parâmetro `scope` no decorador `@pytest.fixture`.
# O escopo determina com que frequência a fixture é criada e destruída durante a execução dos testes.
# Os valores possíveis para `scope` são:
# scope="function"  # cria uma nova fixture para CADA teste (padrão)
# scope="class"     # cria uma vez por classe de testes
# scope="module"    # cria uma vez por arquivo de testes
# scope="session"   # cria uma vez para todos os testes

from app import database
import os
from app.main import app
from app.database import Base, get_db
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from fastapi.testclient import TestClient
import pytest

# Sobrescreve variáveis antes de qualquer import do app para garantir que o ambiente de teste seja configurado corretamente
# Usa SQLite em memória para testes
os.environ['DATABASE_URL'] = 'sqlite:///:memory:'
# Chave secreta para testes
os.environ['SECRET_KEY'] = "chave-secreta-para-testes-unitarios"


# Configura o banco de dados SQLite em memória para testes
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

# Cria o engine do SQLAlchemy para o banco de dados em memória
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)

# Cria as tabelas no banco de dados em memória
testingsessionlocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine)


# Fixture para fornecer uma sessão de banco de dados para os testes
database.engine = engine
database.SessionLocal = testingsessionlocal


@pytest.fixture(scope="function")
def db():
    """Fixture que cria banco SQLite em memória para cada teste
    e garante que as tabelas sejam criadas.

    Yields:
        Session: Sessão de banco de dados para o teste.

    Teardown:
        Fecha a sessão e limpa o banco de dados após o teste.
    """

    # Remove schema para garantir compatibilidade com SQLite
    for table in Base.metadata.tables.values():
        table.schema = None

    # Cria as tabelas no banco de dados em memória
    Base.metadata.create_all(bind=engine)
    connection = engine.connect()
    transaction = connection.begin()
    session = testingsessionlocal(bind=connection)

    try:
        yield session  # Fornece a sessão para o teste
    finally:
        session.close()  # Fecha a sessão após o teste
        transaction.rollback()  # Reverte a transação para limpar o banco de dados
        connection.close()  # Fecha a conexão


@pytest.fixture(scope="function")
def client(db):
    """Fixture que fornece um cliente HTTP para os testes, usando o banco de dados em memória.

    Args:
        db (Session): Sessão de banco de dados fornecida pela fixture `db`.

    Yields:
        TestClient: Cliente HTTP para fazer requisições à API durante os testes.

    Teardown:
        N/A
    """

    # Sobrescreve a dependência get_db para usar a sessão de teste
    def override_get_db():
        yield db

    # Sobrescreve a dependência do banco de dados
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client  # Fornece o cliente HTTP para o teste
    app.dependency_overrides.clear()  # Limpa as dependências sobrescritas após o teste


@pytest.fixture
def categoria_dados():
    """Fixture que fornece dados de categoria para os testes.

    Yields:
        dict: Dados de categoria para uso nos testes.
    """
    return {
        "nome": "Alimentação",
        "tipo": "Variável"
    }


@pytest.fixture
def transacao_dados():
    """Fixture que fornece dados de transação para os testes.

    Yields:
        dict: Payload da transação para uso nos testes.
    """
    return {
        "categoria_id": 1,
        "valor": 50.00,
        "descricao": "Almoço no restaurante",
        "data": "2026-05-01",
    }


@pytest.fixture
def orcamento_dados():
    """Fixture que fornece dados de orçamento para os testes.

    Yields:
        dict: Payload do orçamento para uso nos testes.
    """
    return {
        "categoria_id": 1,
        "limite": 500.00,
        "mes_ano": "2026-05"
    }

# @file Fim do arquivo svc-orcamento/app/tests/conftest.py
