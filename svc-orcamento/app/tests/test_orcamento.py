"""
@module svc-orcamento.app.tests.test_orcamento
@file test_orcamento.py
@description Testes unitários para transações, categorias e orçamentos da API de orçamento.
@author Tina Almeida
@date Maio 2026
@Version 1.0.0
"""

from app.models.categoria import Categoria


class TestCategoria:
    """Testes para criação e validação de categorias."""

    def test_criar_categoria_sucesso(self, client, categoria_dados):
        """Deve criar categoria e retornar status 201."""
        response = client.post("/v1/categorias/", json=categoria_dados)
        assert response.status_code == 201
        assert response.json()["nome"] == "Alimentação"

    def test_criar_categoria_nome_duplicado(self, client, categoria_dados):
        """Deve retornar erro 409 ao criar categoria com nome duplicado."""
        client.post("/v1/categorias/",
                    json=categoria_dados)  # Primeira criação
        response = client.post(
            "/v1/categorias/", json=categoria_dados)  # Segunda criação
        assert response.status_code == 409


class TestTransacao:
    """Testes para criação, listagem e deleção transações."""

    def _cria_categoria(self, db):
        """Helper para criar categoria no banco de dados."""
        categoria = Categoria(nome="Alimentação", tipo="variável")
        db.add(categoria)
        db.commit()
        db.refresh(categoria)
        return categoria.id

    def test_criar_transacao_sucesso(self, client, db, transacao_dados):
        """Deve criar transação e retornar status 201."""
        self._cria_categoria(db)
        response = client.post("/v1/transacoes/", json=transacao_dados)
        assert response.status_code == 201
        assert response.json()["valor"] == "50.00"

    def test_criar_transacao_categoria_inexistente(self, client, transacao_dados):
        """Deve retornar 404 se a categoria não existir."""
        response = client.post("/v1/transacoes/", json=transacao_dados)
        assert response.status_code == 404

    def test_criar_transacao_valor_zero(self, client, db):
        """Deve retornar 422 se o valor for zero."""
        self._cria_categoria(db)
        response = client.post("/v1/transacoes/", json={
            "categoria_id": 1,
            "valor": 0.00,
            "descricao": "Teste valor zero"
        })
        assert response.status_code == 422

    def test_listar_transacoes(self, client, db, transacao_dados):
        """Deve listar transações existentes."""
        self._cria_categoria(db)
        client.post("/v1/transacoes/", json=transacao_dados)
        response = client.get("/v1/transacoes/")
        assert response.status_code == 200
        assert len(response.json()) == 1

    def test_deletar_transacao_sucesso(self, client, db, transacao_dados):
        """Deve deletar transação e retornar status 204."""
        self._cria_categoria(db)
        post = client.post("/v1/transacoes/", json=transacao_dados)
        transacao_id = post.json()["id"]
        response = client.delete(f"/v1/transacoes/{transacao_id}")
        assert response.status_code == 204
        # Verifica que a transação foi realmente deletada
        response = client.get("/v1/transacoes/")
        assert response.status_code == 200
        assert len(response.json()) == 0

    def test_deletar_transacao_inexistente(self, client):
        """Deve retornar 404 ao tentar deletar transação inexistente."""
        response = client.delete("/v1/transacoes/999")
        assert response.status_code == 404


class TestOrcamento:
    """Testes para criação de orçamentos e resumo mensal."""

    def _cria_categoria(self, db):
        """Helper para criar categoria no banco de dados."""
        categoria = Categoria(nome="Alimentação", tipo="variável")
        db.add(categoria)
        db.commit()
        db.refresh(categoria)
        return categoria.id

    def test_criar_orcamento_sucesso(self, client, db, orcamento_dados):
        """Deve criar orçamento e retornar status 201."""
        self._cria_categoria(db)
        response = client.post("/v1/orcamentos", json=orcamento_dados)
        assert response.status_code == 201
        assert response.json()["limite"] == "500.00"

    def test_criar_orcamento_duplicado(self, client, db, orcamento_dados):
        """Deve retornar 409 ao criar orçamento duplicado."""
        self._cria_categoria(db)
        # Primeiro orçamento
        client.post("/v1/orcamentos", json=orcamento_dados)
        response = client.post(
            "/v1/orcamentos", json=orcamento_dados)  # Segundo orçamento
        assert response.status_code == 409

    def test_criar_orcamento_mes_invalido(self, client, db):
        """Deve retornar 402 se o mês for inválido."""
        self._cria_categoria(db)
        response = client.post("/v1/orcamentos", json={
            "categoria_id": 1,
            "valor": 500.00,
            "mes_ano": "2026-13"  # Mês inválido
        })
        assert response.status_code == 422

    def test_resumo_mensal(self, client, db, transacao_dados, orcamento_dados):
        """Deve retornar resumo mensal com gastos vs limite."""
        self._cria_categoria(db)
        # Cria transação
        client.post("/v1/transacoes/", json=transacao_dados)
        # Cria orçamento
        client.post("/v1/orcamentos/", json=orcamento_dados)
        # Solicita resumo mensal
        response = client.get("/v1/orcamentos/resumo?mes=2026-05")
        assert response.status_code == 200
        assert len(response.json()) == 1
        assert response.json()[0]["gasto_real"] == "50.00"

# @file Fim do arquivo svc-orcamento/app/tests/test_orcamento.py
