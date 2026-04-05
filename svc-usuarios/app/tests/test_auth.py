"""
@file svc-usuarios/app/tests/test_auth.py
@description: Testes unitários de autenticação do svc-usuarios.
              Cobre cenários válidos e inválidos de registro, login e geração de tokens JWT.
@author: Tina de Almeida
@date: Abril de 2026
@version: 1.0.0
"""

import pytest
from jose import JWTError

from app.services import auth_service

# =====================================================================
# TESTES DE SENHA
# =====================================================================
class TestSenha:
    """
    Testes das funções de hash e verificação de senha.
    """
    def test_criar_hash_diferente_da_senha_original(self):
        """
        Verifica que o hash gerado é diferente da senha original.
        A senha nunca deve ser armazenada em texto puro.
        """
        senha = "Senha@2026"
        hash_gerado = auth_service.criar_hash_senha(senha)
        assert hash_gerado != senha

    def test_verificar_senha_correta(self):
        """
        Verifica que a senha original bate com o hash gerado.
        """

        senha = "Senha@2026"
        hash_gerado = auth_service.criar_hash_senha(senha)
        assert auth_service.verificar_senha(senha, hash_gerado) is True

    def test_verificar_senha_incorreta(self):
        """
        Verifica que a senha original não bate com o hash gerado.
        """

        senha = "Senha@2026"
        senha_incorreta = "SenhaErrada@2026"
        hash_gerado = auth_service.criar_hash_senha(senha)
        assert auth_service.verificar_senha(senha_incorreta, hash_gerado) is False

class TestToken:
    """
    Testes das funções de geração e verificação de tokens JWT.
    """
    def test_criar_access_token_valido(self):
        """
        Verifica que o access token é gerado e decodificado corretamente.
        """
        dados_usuario = {
            "user_id": 123,
            "email": "tina@smartbudget.com",
            "nome": "Tina Smartbudget"
        }
        token = auth_service.criar_access_token(dados_usuario)
        payload = auth_service.verificar_token(token, tipo="access")
        assert payload["user_id"] == 123
        assert payload["email"] == "tina@smartbudget.com"
        assert payload["nome"] == "Tina Smartbudget"
        assert payload["tipo"] == "access"

    def test_criar_refresh_token_valido(self):
        """
        Verifica que o refresh token é gerado e decodificado corretamente.
        """
        dados_usuario = {
            "user_id": 123,
            "email": "tina@smartbudget.com",
            "nome": "Tina Smartbudget"
        }
        token = auth_service.criar_refresh_token(dados_usuario)
        payload = auth_service.verificar_token(token, tipo="refresh")
        assert payload["tipo"] == "refresh"

    def test_token_tipo_errado_rejeitado(self):
        """
        Verifica que usar refresh token no lugar de access token falha.
        Protege contra uso indevido dos tokens.
        """
        dados_usuario = {
            "user_id": 123,
            "email": "tina@smartbudget.com",
            "nome": "Tina Smartbudget"
        }
        token_refresh = auth_service.criar_refresh_token(dados_usuario)
        with pytest.raises(JWTError):
            auth_service.verificar_token(token_refresh, tipo="access")

    def test_token_adulterado_rejeitado(self):
        """
        Verifica que um token com assinatura adulterada é rejeitado.
        """
        with pytest.raises(JWTError):
            auth_service.verificar_token("token.adulterado.invalido")

class TestRegister:
    """ Testes do endpoint POST /auth/register.
    """
    def test_register_sucesso(self, client, usuario_dados):
        """
        Verifica que um novo usuário é criado com sucesso.
        Esperado: HTTP 201 com dados do usuário sem senha.
        """
        response = client.post("/auth/register", json=usuario_dados)
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == usuario_dados["email"]
        assert data["nome"] == usuario_dados["nome"]
        assert "senha" not in data
        assert "senha_hash" not in data

    def test_register_email_duplicado(self, client, usuario_dados):
        """
        Verifica que o registro de usuário com email duplicado falha.
        Esperado: HTTP 409 com mensagem de erro.
        """
        client.post("/auth/register", json=usuario_dados)
        response = client.post("/auth/register", json=usuario_dados)
        assert response.status_code == 409

    def test_register_senha_sem_maiusculas(self, client):
        """
        Verifica que o registro de usuário com senha sem maiúsculas falha.
        Esperado: HTTP 422 com mensagem de erro.
        """
        response = (
            client.post("/auth/register",json = {
                "email": "tina@smartbudget.com",
                "senha": "senha@2026",
                "nome": "Tina Smartbudget"
            })
        )
        assert response.status_code == 422

    def test_register_senha_sem_numero(self, client):
        """
        Verifica que o registro de usuário com senha sem número falha.
        Esperado: HTTP 422 com mensagem de erro.
        """
        response = (
            client.post("/auth/register",json = {
                "email": "tina@smartbudget.com",
                "senha": "Senha@abc",
                "nome": "Tina Smartbudget"
            })
        )
        assert response.status_code == 422

    def test_register_sem_caracter_especial(self, client):
        """
        Verifica que o registro de usuário com senha sem caractere especial falha.
        Esperado: HTTP 422 com mensagem de erro.
        """
        response = (
            client.post("/auth/register",json = {
                "email": "tina@smartbudget.com",
                "senha": "Senha2026",
                "nome": "Tina Smartbudget"
            })
        )
        assert response.status_code == 422

    def test_register_email_invalido(self, client):
        """
        Verifica que o registro de usuário com email inválido falha.
        Esperado: HTTP 422 com mensagem de erro.
        """
        response = (
            client.post("/auth/register",json = {
                "email": "email-invalido",
                "senha": "Senha@2026",
                "nome": "Tina Smartbudget"
            })
        )
        assert response.status_code == 422

class TestLogin:
    """ Testes do endpoint POST /auth/login. """
    def test_login_sucesso(self, client, usuario_dados):
        """
        Verifica que um novo usuário é criado com sucesso.
        E retorna os tokens de acesso e refresh.
        Esperado: HTTP 200 com dados do usuário sem senha.
        """
        client.post("/auth/register", json=usuario_dados)
        response = client.post("/auth/login", json={
            "email": usuario_dados["email"],
            "senha": usuario_dados["senha"]
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    def test_login_senha_incorreta(self, client, usuario_dados):
        """
        Verifica que o login com senha incorreta falha.
        Esperado: HTTP 401 com mensagem de erro.
        """
        client.post("/auth/register", json=usuario_dados)
        response = client.post("/auth/login", json={
            "email": usuario_dados["email"],
            "senha": "SenhaErrada@2026"
        })
        assert response.status_code == 401

    def test_login_email_nao_cadastrado(self, client, usuario_dados):
        """
        Verifica que o login com email não cadastrado falha.
        Esperado: HTTP 401 com mensagem de erro.
        """
        response = client.post("/auth/login", json={
            "email": "naoexiste@smartbudget.com",
            "senha": "Senha@2026"
        })
        assert response.status_code == 401

# @file Fim do arquivo svc-usuarios/app/tests/test_auth.py
