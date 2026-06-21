"""
@file: svc-orcamento/app/services/kafka_consumer_service.py
@description: Consumer Kafka que escuta o tópico transacao.criada e invalida
              o cache de resumo correspondente ao usuário e mês da transação.

              Fluxo:
              1. POST /transacoes publica em transacao.criada (producer)
              2. Este consumer escuta esse tópico continuamente
              3. Ao receber o evento, monta a chave resumo:{user_id}:{mes}
              4. Invalida (apaga) essa chave do cache Redis
              5. Próxima consulta ao /resumo busca dados atualizados no banco

@author: Tina de Almeida
@date: Maio 2026
@version: 1.0.0
"""
import asyncio
import json
import logging
import os

from aiokafka import AIOKafkaConsumer

from app.services.cache_service import CacheService
from app.services.kafka_producer_service import TOPICO_TRANSACAO_CRIADA

logger = logging.getLogger(__name__)


class KafkaConsumerService:
    """Consome evento transacao.criada e invalida o cache de resumos mensais."""

    def __init__(self, cache_service: CacheService) -> None:
        self._cache_service = cache_service
        self._consumer: AIOKafkaConsumer | None = None
        self._task: asyncio.Task | None = None

    async def start(self) -> None:
        """
        Inicializa o consumer Kafka e inicia o loop de escuta em background.
        Se KAFKA_BOOTSRAP_SERVERS não estiver configurado, o consumer não
        é iniciado - comportamento idêntico ao producer, garantindo resiliência.
        """
        bootstrap_servers = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "")

        if not bootstrap_servers:
            logger.warning(
                "KAFKA_BOOTSTRAP_SERVERS não configurado - Kafka Consumer desabilitado.")
            return

        try:
            sasl_username = os.getenv("KAFKA_SASL_USERNAME", "")
            sasl_password = os.getenv("KAFKA_SASL_PASSWORD", "")

            if sasl_username and sasl_password:
                self._consumer = AIOKafkaConsumer(
                    TOPICO_TRANSACAO_CRIADA,
                    bootstrap_servers=bootstrap_servers,
                    security_protocol="SASL_SSL",
                    sasl_mechanism="PLAIN",
                    sasl_plain_username=sasl_username,
                    sasl_plain_password=sasl_password,
                    value_deserializer=lambda v: json.loads(v.decode("utf-8")),
                    group_id="svc-orcamento-cache-invalidation"
                )
            else:
                self._consumer = AIOKafkaConsumer(
                    TOPICO_TRANSACAO_CRIADA,
                    bootstrap_servers=bootstrap_servers,
                    value_deserializer=lambda v: json.loads(v.decode("utf-8")),
                    group_id="svc-orcamento-cache-invalidation"
                )

            await self._consumer.start()
            self._task = asyncio.create_task(self._consumir_eventos())
            logger.info("Kafka consumer iniciado com sucesso.")

        except Exception as e:  # pylint: disable=broad-except
            logger.exception("Erro ao iniciar Kafka consumer:  %s", e)
            self._consumer = None

    async def stop(self) -> None:
        """Encerra o consumer e cancela o loop de escuta em background."""
        if self._task:
            self._task.cancel()

        if self._consumer:
            await self._consumer.stop()
            logger.info("Kafka consumer encerrado")

    async def _consumir_eventos(self) -> None:
        """
        Loop principal que escuta mensagens do tópico transacao.criada
        e invalida o cache correspondente para cada uam recebida.
        """

        try:
            async for mensagem in self._consumer:
                await self._processar_evento(mensagem.value)
        except asyncio.CancelledError:
            logger.info("Loop de consumo Kafka cancelado.")
            raise
        except Exception as e:  # pylint: disable=broad-except
            logger.exception("Erro no loop de consumo Kafka: %s", e)

    async def _processar_evento(self, payload: dict) -> None:
        """
        Processa um evento transacao.criada, invalidando o cache do usuário e o mês correspondente.

        Args:
            payload (dict): Dado do evento, esperado conter user_id e data_transacao.
        """
        try:
            usuario_id = payload["user_id"]
            data_transacao = payload["data_transacao"]
            mes = data_transacao[:7]  # Extrai 'YYYY-MM' da data 'YYYY-MM-DD'

            chave_cache = self._cache_service.montar_chave(usuario_id, mes)
            await self._cache_service.delete(chave_cache)

        except (KeyError, TypeError) as e:
            logger.warning(
                "Evento mal formado, ignorando: %s — payload=%s", e, payload)

# @file Fim do arquivo svc-orcamento/app/services/kafka_consumer_service.py
