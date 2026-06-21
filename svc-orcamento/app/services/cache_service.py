"""
@file svc-orcamento/app/services/cache_service.py
@description Serviço de cache Redis para o endpoint de resumo mensal.
    Estratégia:
    - Chave:resumo: {usuario_id}:{mes}
    - TTL: 1 hora( 3600 segundos) - expira automaticamente mesmo sem invalidação manual,
        protegendo contra eventos Kafka perdidos.
    - Invalidação: o KafkaConsumerService apaga a chave ao processar o evento trasacao.criada,
        garantindo que o cache seja atualizado na próxima solicitação.
    - Fallback: se o Redis estiver indisponível, get/set/delete falham silenciosamente e
        o chamador deve consultar o banco de dados diretamente, garantindo resiliência.

@author: Tina de Almeida
@date: Junho 2026
@version: 1.0.0
"""

import logging
import os
from urllib.parse import urlparse

from aiocache import RedisCache
from aiocache.serializers import JsonSerializer
from aiocache.base import BaseCache

logger = logging.getLogger(__name__)

TTL_RESUMO_SEGUNDOS = 3600  # 1 hora


class CacheService:
    """Gerencia leitura, escrita e invalidação de cache no Redis para resumos mensais."""
    # pylint: disable=attribute-defined-outside-init

    def __init__(self) -> None:
        self._cache: BaseCache | None = None
        self._inicializar()

    def _inicializar(self) -> None:
        """
        Cria a conexão com o Redis a partir da Variável de Ambiente REDIS_URL.
        Se não estiver configurada ou falhar, o cache fica desabilitado
        e todas as operações caem no fallback para o banco de dados(sem retornar erro).
        """
        redis_url = os.getenv("REDIS_URL", "")

        if not redis_url:
            logger.warning("REDIS_URL não configurado — cache desabilitado.")
            return

        try:
            parsed = urlparse(redis_url)
            db = int(parsed.path.lstrip("/") or 0)

            self._cache = RedisCache(
                endpoint=parsed.hostname,
                port=parsed.port or 6379,
                db=db,
                serializer=JsonSerializer(),
            )
        except Exception as e:  # pylint: disable=broad-except
            logger.exception("Erro ao configurar cache Redis: %s", e)
            self._cache = None

    @staticmethod
    def montar_chave(usuarios_id: int, mes: str) -> str:
        """
        Gera a chave de cache para um usuário e mês específicos.

        Args:
            usuarios_id (int): ID do usuário.
            mes (str): Mês no formato 'YYYY-MM'.

        Returns:
            str: Chave no formato "resumo:{usuarios_id}:{mes}".
        """
        return f"resumo:{usuarios_id}:{mes}"

    async def get(self, chave: str) -> list | None:
        """
        Recupera o valor do cache para a chave fornecida.

        Args:
            chave (str): Chave do cache.

        Returns:
            list | None: Valor armazenado, ou None se não existir ou se o
                Redis falhar — nesse caso o chamador deve consultar o banco.
        """
        if not self._cache:
            return None

        try:
            return await self._cache.get(chave)
        except Exception as e:  # pylint: disable=broad-except
            logger.warning(
                "Falha ao ler cache ( % s): fallback para o banco: % s", chave, e)
            return None

    async def set(self, chave: str, valor: list, ttl: int = TTL_RESUMO_SEGUNDOS) -> None:
        """
        Armazena um valor no cache com a chave e TTL especificados.

        Args:
            chave (str): Chave do cache.
            valor (list): Valor a ser armazenado - deve ser serializável como JSON.
            ttl (int, opcional): Tempo de vida em segundos. Padrão é 3600 (1 hora).
        """
        if not self._cache:
            return

        try:
            await self._cache.set(chave, valor, ttl=ttl)
        except Exception as e:  # pylint: disable=broad-except
            logger.warning(
                "Falha ao gravar cache (%s): %s", chave, e)

    async def delete(self, chave: str) -> None:
        """
        Remove a chave do cache, usada para invalidação após eventos de transação.

        Args:
            chave (str): Chave do cache a ser removida.
        """
        if not self._cache:
            return

        try:
            await self._cache.delete(chave)
        except Exception as e:  # pylint: disable=broad-except
            logger.warning(
                "Falha ao invalidar cache (%s): %s", chave, e)

# @file Fim do arquivo cache_service.py
