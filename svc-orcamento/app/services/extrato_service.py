"""
@module svc-orcamento.app.services.extrato_service
@file extrato_service.py
@description Serviço para importação de extratos bancários via CSV.
             Parseia o arquivo, valida as linhas e insere os dados na base de dados.
             Linhas inválidas são registradas em um log de erros para análise posterior.

             Formato esperado do CSV:
             - data: Data da transação (formato: YYYY-MM-DD)
             - descricao: Descrição do lançamento
             - valor: Valor da transação (positivo, decimal(10, 2) e aceita apenas credito)
            - tipo: tipo do lançamento (débito = importado | crédito = ignorado)

@author Tina Almeida
@date Maio 2026
@version 1.0.0
"""

import logging
from datetime import datetime
from decimal import Decimal, InvalidOperation
from io import BytesIO

import pandas as pd
from sqlalchemy.orm import Session

from app.models.transacao import Transacao

logger = logging.getLogger(__name__)

COLUNAS_ESPERADAS = {'data', 'descricao', 'valor', 'tipo'}


class ExtratoService:
    """
    Gerencia a importação de extratos bancários via CSV, validando os dados e inserindo transações na base de dados.
    """

    def importar_extrato(
            self,
            db: Session,
            conteudo: bytes,
            usuario_id: int,
            categoria_id: int
    ) -> dict:
        """
        Importa um extrato bancário a partir de um arquivo CSV.

        Args:
            db (Session): Sessão do banco de dados para operações de inserção.
            conteudo (bytes): Conteúdo do arquivo CSV a ser importado.
            usuario_id (int): ID do usuário autenticado das transações importadas.
            categoria_id (int): ID da categoria associada às transações importadas.

        Returns:
            dict: Resultado da importação contendo o número de transações importadas e detalhes de erros, se houver.

        Raises:
            ValueError: Se o arquivo CSV estiver em um formato inválido ou vazio.
        """
        df = self._parsear_csv(conteudo)
        return self._processar_linhas(db, df, usuario_id, categoria_id)

    def _parsear_csv(self, conteudo: bytes) -> pd.DataFrame:
        """
        Lê e valida o conteúdo do arquivo CSV e retorna um DataFrame.

        Args:
            conteudo (bytes): Conteúdo binário do arquivo CSV.

        Returns:
            pd.DataFrame: DataFrame contendo os dados do extrato.

        Raises:
            ValueError: Se o arquivo CSV estiver em colunas inválidas ou vazio.
        """
        if not conteudo:
            raise ValueError("Arquivo sem dados.")

        try:
            df = pd.read_csv(BytesIO(conteudo))
        except Exception as e:
            raise ValueError(f"Erro ao ler o arquivo CSV: {e}") from e

        if df.empty:
            raise ValueError("Arquivo sem dados.")

        colunas_faltando = COLUNAS_ESPERADAS - set(df.columns.str.lower())
        if colunas_faltando:
            raise ValueError(f"Colunas faltando: {colunas_faltando}")

        df.columns = df.columns.str.lower()
        return df

    def _processar_linhas(
        self,
        db: Session,
        df: pd.DataFrame,
        usuario_id: int,
        categoria_id: int
    ) -> dict:
        """
        Processa as linhas do DataFrame, validando e inserindo transações na base de dados.

        Args:
            db (Session): Sessão do banco de dados para operações de inserção.
            df (pd.DataFrame): DataFrame contendo os dados do extrato.
            usuario_id (int): ID do usuário autenticado das transações importadas.
            categoria_id (int): ID da categoria associada às transações importadas.

        Returns:
            dict: Resultado da importação contendo o número de transações importadas e detalhes de erros, se houver.
        """

        transacoes = []
        erros = []

        for i, row in df.iterrows():
            numero_linha = i + 2  # Considerando o cabeçalho

            if str(row.get("tipo", "")).strip().lower() != "débito":
                continue

            resultado = self._validar_linha(row, numero_linha)

            if resultado.get("erro"):
                erros.append(resultado)
                continue

            transacoes.append(Transacao(
                usuario_id=usuario_id,
                categoria_id=categoria_id,
                valor=resultado["valor"],
                data_transacao=resultado["data"],
                descricao=str(row.get("descricao", "")).strip()
            ))

        if transacoes:
            db.bulk_save_objects(transacoes)
            db.commit()

        logger.info("Importação de extrato concluída: %d transações importadas, %d erros encontrados.", len(
            transacoes), len(erros))

        return {
            "importadas": len(transacoes),
            "erros": erros
        }

    def _validar_linha(self, row: pd.Series, numero_linha: int) -> dict:
        """
        Valida os dados de uma linha do DataFrame(extrato).

        Args:
            row (pd.Series): Linha do DataFrame a ser validada.
            numero_linha (int): Número da linha no arquivo CSV para referência em mensagens de erro.

        Returns:
            dict: Resultado da validação contendo os dados validados ou detalhes de erros, se houver.
        """

        try:
            valor = Decimal(str(row.get("valor", "")).strip())
            if valor <= 0:
                return {"linha": numero_linha, "erro": "Valor deve ser maior que zero."}
        except (InvalidOperation, ValueError):
            return {"linha": numero_linha, "erro": "Valor inválido. Deve ser um número decimal."}

        try:
            data = datetime.strptime(
                str(row.get("data", "")).strip(), "%Y-%m-%d").date()
        except ValueError:
            return {"linha": numero_linha, "erro": "Data inválida. Formato esperado: YYYY-MM-DD."}

        return {"valor": valor, "data": data}

# @file Fim do arquivo csv-orcamento/app/services/extrato_service.py
