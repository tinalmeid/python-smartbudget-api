"""
@module: svc-orcamento.app.services.orcamento_service
@file: orcamento_service.py
@description: Regras de negócio para orçamentos financeiros.
              Responsável por criar, listar e deletar orçamentos,
              garantindo isolamento entre usuários.
@author: Tina de Almeida
@date: Maio 2026
@version: 1.0.0
"""

import logging
from decimal import Decimal
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import extract, func

from app.models.categoria import Categoria
from app.models.orcamento import Orcamento
from app.models.transacao import Transacao
from app.schemas.orcamento import OrcamentoCreate

logger = logging.getLogger(__name__)


class OrcamentoService:
    """
    Gerencia as regras de negócio de orçamentos financeiros.

    Métodos:
    criar_orcamento: Cria um novo orçamento associado a um usuário e categoria.
    calcular_resumo: Calcula o gasto real vs limite para um orçamento no mês informado.
    _calcular_gasto: Calcula o gasto total de uma categoria em um mês específico.(Privado)
    _validar_categoria: Verifica se a categoria existe.(Privado)
    _validar_duplicidade: Verifica se já existe um orçamento para a mesma categoria e mês.(Privado)
    """

    def criar_orcamento(
            self,
            db: Session,
            dados: OrcamentoCreate,
            usuario_id: int
    ) -> Orcamento:
        """
        Define um limite mensal por categoria para o usuário autenticado.

        Args:
            db: Sessão do banco de dados.
            dados: Dados validados para criação do orçamento.
            usuario_id: ID do usuário proprietário do orçamento autenticado via JWT.

        Returns:
            Orcamento: O orçamento criado.

        Raises:
            HTTPException 404: Se a categoria não existir.
            HTTPException 409: Se já existir um orçamento para a mesma categoria e mês.
        """

        self._validar_categoria(db, dados.categoria_id)
        self._validar_duplicidade(
            db, usuario_id, dados.categoria_id, dados.mes_ano)

        orcamento = Orcamento(
            usuario_id=usuario_id,
            categoria_id=dados.categoria_id,
            limite=dados.limite,
            mes_ano=dados.mes_ano,
        )

        db.add(orcamento)
        db.commit()
        db.refresh(orcamento)

        logger.info("Orcamento criado: id=%s usuario=%s mes=%s",
                    orcamento.id, usuario_id, dados.mes_ano)
        return orcamento

    def calcular_resumo(
            self,
            db: Session,
            usuario_id: int,
            mes_ano: str
    ) -> list[dict]:
        """
        Calcula o gasto real vs limite para um orçamento no mês informado.

        Args:
            db: Sessão do banco de dados.
            usuario_id: ID do usuário proprietário do orçamento.
            mes_ano: Mês e ano de orçamento (formato YYYY-MM).

        Returns:
            list[dict]: Lista com categoria, limite, gasto real e saldo.
        """

        ano, mes = mes_ano.split("-")

        orcamentos = (
            db.query(Orcamento)
            .filter_by(
                usuario_id=usuario_id,
                mes_ano=mes_ano
            ).all()
        )

        resumo = []
        for orcamento in orcamentos:
            gasto = self._calcular_gasto(
                db, usuario_id, orcamento.categoria_id, int(ano), int(mes))
            saldo = orcamento.limite - gasto

            resumo.append({
                "categoria_id": orcamento.categoria_id,
                "categoria_nome": orcamento.categoria.nome,
                "limite": orcamento.limite,
                "gasto_real": gasto,
                "saldo": saldo,
                "percentual_usado": round((gasto / orcamento.limite) * 100, 2) if orcamento.limite > 0 else None
            })

        return resumo

    def verificar_alerta(
            self,
            db: Session,
            usuario_id: int,
            categoria_id: int,
            mes_ano: str
    ) -> Optional[dict]:
        """
        Verifica se o gasto de uma categoria atingiu o percentual de alerta definido no orçamento do mês.

        Args:
            db: Sessão do banco de dados.
            usuario_id: ID do usuário proprietário do orçamento.
            categoria_id: ID da categoria para verificar o alerta.
            mes_ano: Mês e ano do orçamento (formato YYYY-MM).
        Returns:
            Optional[dict]: Dados do alerta (categoria_id, percentual_usado) se o percentual foia atingido,
            ou None se não houver orçamento para a categoria/mês ou se o percentual não tiver sido atingido.
        """
        orcamento = (
            db.query(Orcamento)
            .filter_by(
                usuario_id=usuario_id,
                categoria_id=categoria_id,
                mes_ano=mes_ano
            )
            .first()
        )

        if not orcamento:
            return None

        ano, mes = mes_ano.split("-")
        gasto = self._calcular_gasto(
            db, usuario_id, categoria_id, int(ano), int(mes))

        if orcamento.limite <= 0:
            return None

        percentual_usado = round((gasto / orcamento.limite) * 100, 2)

        if percentual_usado < orcamento.alerta_em:
            return None

        return {
            "categoria_id": categoria_id,
            "percentual_usado": percentual_usado
        }

    def _calcular_gasto(
            self,
            db: Session,
            usuario_id: int,
            categoria_id: int,
            ano: int,
            mes: int
    ) -> Decimal:
        """
        Calcula o total gasto em uma categoria no mês

        Args:
            db: Sessão do banco de dados.
            usuario_id: ID do usuário proprietário do orçamento.
            categoria_id: ID da categoria para calcular o gasto.
            ano: Ano do mês para calcular o gasto.
            mes: Mês para calcular o gasto.

        Returns:
            Decimal: Total gasto na categoria no mês.
        """

        resultado = (
            db.query(func.coalesce(func.sum(Transacao.valor), 0))
            .filter(
                Transacao.usuario_id == usuario_id,
                Transacao.categoria_id == categoria_id,
                extract('year', Transacao.data_transacao) == ano,
                extract('month', Transacao.data_transacao) == mes
            )
            .scalar()
        )

        return resultado or Decimal(0)

    def _validar_categoria(self, db: Session, categoria_id: int) -> Categoria:
        """
        Valida se a categoria existe no banco de dados.

        Args:
         db: Sessão do banco de dados.
         categoria_id: ID da categoria a validar.

        Returns:
         Categoria: A categoria validada.

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

    def _validar_duplicidade(
            self,
            db: Session,
            usuario_id: int,
            categoria_id: int,
            mes_ano: str
    ) -> None:
        """
        Verifica se já existe um orçamento para a mesma categoria e mês.

        Args:
         db: Sessão do banco de dados.
         usuario_id: ID do usuário proprietário do orçamento.
         categoria_id: ID da categoria do orçamento.
         mes_ano: Mês e ano do orçamento (formato YYYY-MM).

        Raises:
         HTTPException 409: Se já existir um orçamento para a mesma categoria e mês.
        """

        existente = (
            db.query(Orcamento)
            .filter_by(
                usuario_id=usuario_id,
                categoria_id=categoria_id,
                mes_ano=mes_ano
            )
            .first()
        )

        if existente:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Orçamento para esta categoria e mês já existe",
            )

# @file Fim do arquivo svc-orcamento/app/services/orcamento_service.py
