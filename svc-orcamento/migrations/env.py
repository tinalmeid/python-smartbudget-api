"""
@module:svc-orcamento.migrations.env
@file: env.py
@description: Configuração do Alembic para migrations do svc-orcamento.
              Lê a DATABASE_URL do .env e usa os models para gerar migrations automáticas.
@author: Tina de Almeida
@date: Maio 2026
@version: 1.0.0
"""
# isort: skip_file

from app.models.transacao import Transacao  # pylint: disable=unused-import
from app.models.orcamento import Orcamento  # pylint: disable=unused-import
from app.models.categoria import Categoria  # pylint: disable=unused-import
from app.database import Base
from sqlalchemy import engine_from_config, pool
from alembic import context
import os
import sys
from logging.config import fileConfig

# PASSO 1 — adiciona svc-orcamento ao path para o Python encontrar o app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# PASSO 2 — carrega o .env antes de qualquer import do app
_env_path = os.path.join(os.path.dirname(
    os.path.abspath(__file__)), "..", ".env")
with open(_env_path) as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip())

# PASSO 3 — agora é seguro importar o app


config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

config.set_main_option("sqlalchemy.url", os.getenv(
    "DATABASE_URL", "").replace("%", "%%"))


def run_migrations_offline() -> None:
    """Roda migrations em modo offline (sem conexão com o banco)."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        include_name=lambda name, type_, parent_names: True if type_ == "schema" and name == "orcamento" else name is None,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Roda migrations em modo online (com conexão ao banco)."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            include_name=lambda name, type_, parent_names: True if type_ == "schema" and name == "orcamento" else name is None,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

# @file Fim do arquivo migrations/env.py
