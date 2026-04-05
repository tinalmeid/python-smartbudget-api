"""
@file: svc-usuarios/services/auth_service.py
@description: Serviço de autenticação JWT do svc-usuarios.
              Contém as regras de negócio de registro, login, geração e validação de tokens JWT.

@author: Tina de Almeida
@date: Abril 2026
@version: 1.0.0
"""

import logging
import os
import uuid
from datetime import datetime, timedelta

from jose import jwt, JWTError
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.models.usuario import Usuario
from app.schemas.usuario import UsuarioCreate

# Configuração de Logging
logger = logging.getLogger(__name__)

# --- Configuração JWT ---
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", 7))

if not SECRET_KEY:
    raise ValueError("Variável SECRET_KEY não encontrada no arquivo .env")

# --- Configuração bcrypt ---
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ==============================================================================
# FUNÇÕES DE SENHA
# ==============================================================================

def criar_hash_senha(senha: str) -> str:
    """
    Gera hash da senha usando bcrypt

    Args:
        senha: Senha em texto puro informada pelo usuário

    Returns:
        str: Hash bcrypt da senha
    """
    return pwd_context.hash(senha)

def verificar_senha(senha: str, hash_senha: str) -> bool:
    """
    Verifica se a senha informada pelo usuário corresponde ao hash armazenado

    Args:
        senha: Senha em texto puro informada pelo usuário
        hash_senha: Hash bcrypt da senha armazenado no banco de dados

    Returns:
        bool: True se a senha estiver correta, False caso contrário
    """
    return pwd_context.verify(senha, hash_senha)

# ==============================================================================
# FUNÇÕES DE TOKEN JWT
# ==============================================================================

def criar_access_token(dados: dict) -> str:
    """
    Gerar o access token JWT com expiração de 15 minutos

    Args:
        dados: Dicionário com os dados do usuário (user_id, email)

    Returns:
        str: Token JWT de acesso assinado
    """
    payload = dados.copy()
    expiracao = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload.update({"exp": expiracao, "type": "access"})
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    logger.info("Access token gerado", extra={"user_id": dados.get("user_id")})
    return token

def criar_refresh_token(dados: dict) -> str:
    """
    Gerar o refresh token JWT com expiração de 7 dias

    Args:
        dados: Dicionário com os dados do usuário (user_id, email)

    Returns:
        str: Refresh Token JWT assinado
    """
    payload = dados.copy()
    expiracao = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    payload.update({"exp": expiracao, "type": "refresh"})
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    logger.info("Refresh token gerado", extra={"user_id": dados.get("user_id")})
    return token

def verificar_token(token: str, tipo: str = "access") -> dict:
    """
    Valida e decodifica um token JWT.

    Args:
        token: Token JWT recebido na requisição.
        tipo: Tipo do token esperado — 'access' ou 'refresh'.

    Returns:
        dict: Payload decodificado do token.

    Raises:
        JWTError: Se o token for inválido, expirado ou do tipo errado.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != tipo:
            raise JWTError("Tipo de token inválido")
        return payload
    except JWTError as e:
        logger.warning("Token inválido", extra={"erro": str(e)})
        raise

# ==============================================================================
# FUNÇÕES DE USUÁRIO
# ==============================================================================

def buscar_por_email(email: str, db: Session) -> Usuario | None:
    """
    Busca um usuário pelo e-mail no banco de dados.

    Args:
        email: E-mail do usuário a ser buscado.
        db: Session ativa do SQLAlchemy.

    Returns:
        Usuario | None: Usuário encontrado ou None se não existir.
    """
    return db.query(Usuario).filter(Usuario.email == email).first()

def criar_usuario(dados: UsuarioCreate, db: Session) -> Usuario:
    """
    Cria um novo usuário no banco de dados.

    Args:
        dados: Dados do usuário validados pelo schema UsuarioCreate.
        db: Session ativa do SQLAlchemy.

    Returns:
        Usuario: Usuário criado com sucesso.

    Raises:
        ValueError: Se o e-mail já estiver cadastrado.
    """
    if buscar_por_email(dados.email, db):
        logger.warning("Tentativa de cadastro com e-mail duplicado",
                      extra={"email": dados.email})
        raise ValueError("E-mail já cadastrado")

    usuario = Usuario(
        id=str(uuid.uuid4()),
        email=dados.email,
        senha_hash=criar_hash_senha(dados.senha),
        nome=dados.nome,
    )

    db.add(usuario)
    db.commit()
    db.refresh(usuario)

    logger.info("Usuário criado com sucesso",
               extra={"usuario_id": usuario.id})
    return usuario

def autenticar_usuario(email: str, senha: str, db: Session) -> Usuario:
    """
    Autentica o usuário verificando e-mail e senha.

    Args:
        email: E-mail informado no login.
        senha: Senha em texto puro informada no login.
        db: Session ativa do SQLAlchemy.

    Returns:
        Usuario: Usuário autenticado com sucesso.

    Raises:
        ValueError: Se o e-mail não existir ou a senha for inválida.
    """
    usuario = buscar_por_email(email, db)

    if not usuario:
        logger.warning("Tentativa de login com e-mail inexistente",
                      extra={"email": email})
        raise ValueError("E-mail ou senha inválidos")

    if not verificar_senha(senha, usuario.senha_hash):
        logger.warning("Tentativa de login com senha inválida",
                      extra={"usuario_id": usuario.id})
        raise ValueError("E-mail ou senha inválidos")

    if not usuario.ativo:
        logger.warning("Tentativa de login em conta inativa",
                      extra={"usuario_id": usuario.id})
        raise ValueError("Conta inativa — entre em contato com o suporte")

    logger.info("Login realizado com sucesso",
               extra={"usuario_id": usuario.id})
    return usuario


# @file Fim do arquivo services/auth_service.py
