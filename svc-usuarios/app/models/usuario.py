"""
@file: svc-usuarios/app/models/usuario.py
@description: Model SQLAlchemy do usuário.
              Define a estrutura da tabela 'usuarios' no banco de dados PlanetScale.

@author: Tina de Almeida
@date: Abril 2026
@version: 1.0.0
"""

import logging
import uuid
from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, String
from app.database import Base

# Configuração de Logging
logger = logging.getLogger(__name__)

class Usuario(Base):
    """
    Model da tabela 'usuarios' no banco de dados

    Armazena os dados de autenticação e perfil de usuários do sistema.
    A senha nunca é armazenada em texto plano, sempre em hash bcrypt.
    """
    __tablename__ = "usuarios"

    # --- Identificação ---
    id = Column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        comment="UUID gerado automaticamente"
    )

    # ---Autenticação ---
    email = Column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
        comment="Email único do usuário - usado para login"
    )
    senha_hash = Column(
        String(255),
        nullable=False,
        comment="Hash bcrypt da senha — nunca armazenar senha pura"
    )

    # --- Perfil ---
    nome = Column(
        String(100),
        nullable=True,
        comment="Nome completo do usuário"
    )
    renda_mensal = Column(
        String(20),
        nullable=True,
        comment="Renda mensal declarada pelo usuário"
    )

    # --- Status ---
    ativo = Column(
        Boolean,
        default=True,
        nullable=False,
        comment="Indica se a conta do usuário está ativa"
    )

    # --- Auditoria ---
    criado_em = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        comment="Data e hora de criação do registro"
    )
    atualizado_em = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
        comment="Data e hora da última atualização"
    )

# @file Fim do arquivo models/usuario.py
