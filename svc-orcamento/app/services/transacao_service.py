"""
@module: svc-orcamento.app.services.transacao_service
@file: transacao_service.py
@description: Regras de negócio para transações financeiras.
              Responsável por criar, listar e deletar transações,
              garantindo isolamento entre usuários.
@author: Tina de Almeida
@date: Maio 2026
@version: 1.0.0
"""

import logging
from datetime import date
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.categoria import Categoria
from app.models.transacao import Transacao
from app.schemas.transacao import TransacaoCreate

logger = logging.getLogger(__name__)


class TransacaoService:
    """
    Gerencia as regras de negócio de transações financeiras.

    Métodos:
    criar_transacao: Cria uma nova transação associada a um usuário e categoria.
    listar_transacoes: Lista transações de um usuário, com filtros opcionais.
    deletar_transacao: Deleta uma transação, garantindo que o usuário seja o proprietário.
    _validar_categoria: Verifica se a categoria existe e pertence ao usuário.(Privado)
    """

    def criar_transacao(
            self,
            db: Session,
            dados: TransacaoCreate,
            usuario_id: int
    ) -> Transacao:
        """
        Cria uma nova transação associada a um usuário e categoria.

        Args:
            db: Sessão do banco de dados.
            dados: Dados para criação da transação.
            usuario_id: ID do usuário proprietário da transação autenticado via JWT.

        Returns:
            Transacao: A transação criada.

        Raises:
            HTTPException 404: Se a categoria não existir.
        """

        self._validar_categoria(db, dados.categoria_id)

        transacao = Transacao(
            usuario_id=usuario_id,
            categoria_id=dados.categoria_id,
            valor=dados.valor,
            descricao=dados.descricao,
            data_transacao=dados.data_transacao or date.today()
        )

        db.add(transacao)
        db.commit()
        db.refresh(transacao)

        logger.info("Transação criada: id=%s, usuário=%s",
                    transacao.id, usuario_id)
        return transacao

    def listar_transacoes(
            self,
            db: Session,
            usuario_id: int,
            mes: Optional[str] = None,
            categoria: Optional[int] = None,
            pagina: int = 1,
            tamanho_pagina: int = 20
    ) -> list[Transacao]:
        """
        Lista transações de um usuário, com filtros opcionais.

        Args:
            db: Sessão do banco de dados.
            usuario_id: ID do usuário proprietário das transações autenticado via JWT.
            mes: Filtro opcional para mês e ano (formato YYYY-MM).
            categoria: Filtro opcional para categoria (ID).
            pagina: Número da página para paginação (padrão 1).
            tamanho_pagina: Quantidade de itens por página (padrão 20).

        Returns
            list[Transacao]: Lista de transações que atendem aos critérios de filtro.
        """

        query = db.query(Transacao).filter(Transacao.usuario_id == usuario_id)

        if mes:
            ano, num_mes = mes.split("-")
            query = query.filter(
                db.func.extract("year", Transacao.data_transacao) == int(ano),
                db.func.extract(
                    "month", Transacao.data_transacao) == int(num_mes),
            )

        if categoria:
            query = query.join(Categoria).filter(Categoria.nome == categoria)

        offset = (pagina - 1) * tamanho_pagina
        return query.offset(offset).limit(tamanho_pagina).all()

    def deletar_transacao(
            self,
            db: Session,
            transacao_id: int,
            usuario_id: int
    ) -> None:
        """
        Deleta uma transação verificando se pertence ao usuário autenticado.

        Args:
            db: Session do banco de dados.
            transacao_id: ID da transação a deletar.
            usuario_id: ID do usuário autenticado.

        Raises:
            HTTPException 404: Se a transação não existir.
            HTTPException 403: Se a transação não pertencer ao usuário.
        """

        transacao = db.query(Transacao).filter(
            Transacao.id == transacao_id).first()

        if not transacao:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Transação não encontrada",
            )

        if transacao.usuario_id != usuario_id:
            logger.warning(
                "Tentativa de deletar transacao de outro usuario: transacao=%s usuario=%s",
                transacao_id,
                usuario_id,
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Sem permissão para deletar esta transação",
            )

        db.delete(transacao)
        db.commit()

        logger.info("Transacao deletada: id=%s usuario=%s",
                    transacao_id, usuario_id)

    def _validar_categoria(self, db: Session, categoria_id: int) -> Categoria:
        """
        Valida se a categoria existe no banco.

        Args:
            db: Session do banco de dados.
            categoria_id: ID da categoria a validar.

        Returns:
            Categoria: Categoria encontrada.

        Raises:
            HTTPException 404: Se a categoria não existir.
        """

        categoria = db.query(Categoria).filter(
            Categoria.id == categoria_id).first()

        if not categoria:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Categoria não encontrada",
            )
        return categoria


# @file Final do arquivo svc-orcamento/app/services/transacao_service.py
