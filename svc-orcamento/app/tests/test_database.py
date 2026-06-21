"""
@file: svc-orcamento/app/tests/test_database.py
@description: Testes unitários para o comportamento de resiliência do banco
              de dados — verifica que falhas de conexão (OperationalError)
              são convertidas em HTTPException 503.
@author: Tina de Almeida
@date: Maio 2026
@version: 1.0.0
"""
from unittest.mock import patch

import pytest
from fastapi import HTTPException
from sqlalchemy.exc import OperationalError

from app.database import get_db


class TestBancoIndisponivel:
    """Testes para o comportamento do sistema quando o banco está indisponível."""

    def test_banco_indisponivel_levanta_503(self):
        """Deve converter OperationalError em HTTPException 503 ao criar a sessão."""
        with patch(
            "app.database.sessionlocal",
            side_effect=OperationalError(
                "statement", "params", "banco indisponível"),
        ):
            gerador = get_db()
            with pytest.raises(HTTPException) as exc_info:
                next(gerador)

        assert exc_info.value.status_code == 503

# @file Fim do arquivo svc-orcamento/app/tests/test_database.py
