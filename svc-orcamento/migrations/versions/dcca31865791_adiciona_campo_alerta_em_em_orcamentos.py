"""adiciona campo alerta_em em orcamentos

Revision ID: dcca31865791
Revises: 254493daf071
Create Date: 2026-06-21 18:52:26.055416

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


revision: str = 'dcca31865791'
down_revision: Union[str, None] = '254493daf071'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Adiciona a coluna alerta_em na tabela orcamentos."""
    op.add_column("orcamentos",
                  sa.Column("alerta_em", sa.Integer(),
                            nullable=False, server_default="80"),
                  schema="orcamento")


def downgrade() -> None:
    """Remove a coluna alerta_em da tabela orcamentos."""
    op.drop_column("orcamentos", "alerta_em", schema="orcamento")
