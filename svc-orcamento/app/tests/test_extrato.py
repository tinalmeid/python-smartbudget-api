"""
@module svc-orcamento.app.tests.test_extrato
@file: test_extrato.py
@description: Testes unitários para importação de extrato bancário via CSV.
@author: Tina de Almeida
@date: Maio 2026
@version: 1.0.0
"""
import os

import pytest
from fastapi import HTTPException

from app.models.categoria import Categoria
from app.services.extrato_service import ExtratoService


class TestExtratoService:
    """Testes para o parser e importador de extrato CSV."""

    def _cria_categoria(self, db) -> int:
        """Helper para criar categoria no banco."""
        categoria = Categoria(nome="Importado", tipo="variável")
        db.add(categoria)
        db.commit()
        db.refresh(categoria)
        return categoria.id

    def _ler_csv(self, nome: str) -> bytes:
        """Helper para ler arquivo CSV de teste."""
        caminho = os.path.join(os.path.dirname(__file__), nome)
        with open(caminho, "rb") as f:
            return f.read()

    def test_importar_extrato_sucesso(self, db):
        """Deve importar transações válidas e retornar erros das inválidas."""
        categoria_id = self._cria_categoria(db)
        conteudo = self._ler_csv("extrato_teste.csv")

        service = ExtratoService()
        resultado = service.importar_extrato(db, conteudo, 1, categoria_id)

        assert resultado["importadas"] == 7
        assert len(resultado["erros"]) == 2

    def test_arquivo_vazio(self, db):
        """Deve retornar erro 400 se arquivo estiver vazio."""
        categoria_id = self._cria_categoria(db)

        service = ExtratoService()
        with pytest.raises(ValueError, match="Arquivo sem dados."):
            service.importar_extrato(db, b"", 1, categoria_id)

    def test_colunas_faltando(self, db):
        """Deve retornar erro se colunas obrigatórias estiverem faltando."""
        categoria_id = self._cria_categoria(db)
        csv_invalido = b"data,valor\n2026-05-01,50.00"

        service = ExtratoService()
        with pytest.raises(ValueError, match="Colunas faltando"):
            service.importar_extrato(db, csv_invalido, 1, categoria_id)

    def test_arquivo_sem_dados(self, db):
        """Deve retornar erro se arquivo não tiver linhas de dados."""
        categoria_id = self._cria_categoria(db)
        csv_vazio = b"data,descricao,valor,tipo\n"

        service = ExtratoService()
        with pytest.raises(ValueError, match="Arquivo sem dados."):
            service.importar_extrato(db, csv_vazio, 1, categoria_id)

    def test_apenas_credito_ignorado(self, db):
        """Deve ignorar linhas com tipo=crédito."""
        categoria_id = self._cria_categoria(db)
        csv = b"data,descricao,valor,tipo\n2026-05-01,Salario,5000.00,credito\n"

        service = ExtratoService()
        resultado = service.importar_extrato(db, csv, 1, categoria_id)

        assert resultado["importadas"] == 0
        assert len(resultado["erros"]) == 0


class TestExtratoRouter:
    """Testes para o endpoint POST /v1/importar-extrato."""

    def _cria_categoria(self, db) -> int:
        """Helper para criar categoria no banco."""
        categoria = Categoria(nome="Importado", tipo="variável")
        db.add(categoria)
        db.commit()
        db.refresh(categoria)
        return categoria.id

    def test_upload_csv_sucesso(self, client, db):
        """Deve aceitar upload de CSV válido e retornar resultado."""
        categoria_id = self._cria_categoria(db)
        caminho = os.path.join(os.path.dirname(__file__), "extrato_teste.csv")

        with open(caminho, "rb") as f:
            response = client.post(
                f"/v1/importar-extrato?categoria_id={categoria_id}",
                files={"arquivo": ("extrato_teste.csv", f, "text/csv")},
            )

        assert response.status_code == 200
        assert response.json()["importadas"] == 7

    def test_upload_arquivo_nao_csv(self, client, db):
        """Deve retornar 400 se arquivo não for CSV."""
        categoria_id = self._cria_categoria(db)
        response = client.post(
            f"/v1/importar-extrato?categoria_id={categoria_id}",
            files={"arquivo": ("extrato.txt", b"conteudo", "text/plain")},
        )
        assert response.status_code == 400

    def test_upload_csv_vazio(self, client, db):
        """Deve retornar 400 se CSV estiver vazio."""
        categoria_id = self._cria_categoria(db)
        response = client.post(
            f"/v1/importar-extrato?categoria_id={categoria_id}",
            files={"arquivo": ("extrato.csv", b"", "text/csv")},
        )
        assert response.status_code == 400

# @file Fim do arquivo svc-orcamento/app/tests/test_extrato.py
