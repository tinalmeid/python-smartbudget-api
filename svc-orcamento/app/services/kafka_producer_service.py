"""
@module svc-orcamento.app.services.kafka_producer_service
@file kafka_producer_service.py
@description Serviço de publicação de eventos no Kafka.
             Publica eventos de forma assíncrona (fire-and-forget) para garantir alta performance e baixa latência.
             Nos tópicos:
                - transacao.criada: publicado após transação registrada
                payload: {user_id: str, valor: int,
                    categoria: str, data_transacao: str}

                - orcamento.alerta: publicado quando gastos >= percentual de alerta
                payload: {user_id: str, categoria_id: str,
                    pct_usado: int/float}

                Falhas no kafka são logadas, mas não bloqueiam o fluxo principal da aplicação(retorno), garantindo resiliência.
@author Tina de Almeida
@date Maio 2026
@version 1.0.0
"""

import json
import logging
import os

from aiokafka import AIOKafkaProducer

logger = logging.getLogger(__name__)

TOPICO_TRANSACAO_CRIADA = "transacao.criada"
TOPICO_ORCAMENTO_ALERTA = "orcamento.alerta"


class KafkaProducerService:
    """
    Gerencia a conexão e publicação de eventos no Kafka.
    Inicializado no startup da aplicação e encerrado no shutdown.
    """

    def __init__(self) -> None:
        self._producer: AIOKafkaProducer | None = None

    async def start(self) -> None:
        """
        Inicializa o producer Kafka.
        Chamado no evento startup FastAPI.
        Se as variáveis de ambiente nã estiverem configuradas, o producer não é inicializado, e os eventos Kafka serão ignorados.
        """
        bootstrap_servers = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "")

        if not bootstrap_servers:
            logger.warning(
                "KAFKA_BOOTSTRAP_SERVERS não configurado - Eventos Kafka desabilitados.")
            return

        try:
            sasl_username = os.getenv("KAFKA_SASL_USERNAME", "")
            sasl_password = os.getenv("KAFKA_SASL_PASSWORD", "")

            if sasl_username and sasl_password:
                self._producer = AIOKafkaProducer(
                    bootstrap_servers=bootstrap_servers,
                    security_protocol="SASL_SSL",
                    sasl_mechanism="PLAIN",
                    sasl_plain_username=sasl_username,
                    sasl_plain_password=sasl_password,
                    value_serializer=lambda v: json.dumps(v).encode("utf-8")
                )
            else:
                if not bootstrap_servers:
                    return
                self._producer = AIOKafkaProducer(
                    bootstrap_servers=bootstrap_servers,
                    value_serializer=lambda v: json.dumps(v).encode("utf-8")
                )

            await self._producer.start()
            logger.info("Kafka producer iniciado com sucesso.")

        except Exception as e:  # pylint: disable=broad-except
            logger.exception("Erro ao iniciar Kafka producer: %s", e)
            self._producer = None

    async def stop(self) -> None:
        """
        Encerra o producer Kafka.
        Chamado no evento shutdown FastAPI.
        """
        if self._producer:
            await self._producer.stop()
            logger.info("Kafka producer encerrado com sucesso.")

    async def publicar_transacao_criada(
            self,
            usuario_id: int,
            valor: str,
            categoria_id: int,
            data_transacao: str,
    ) -> None:
        """
        Publica um evento de transação criada no tópico transacao.criada.
        Fire-and-forget — falhas são logadas sem propagar exceção.

        Args:
            usuario_id (int): ID do usuário que realizou a transação.
            valor (str): Valor da transação.
            categoria_id (int): ID da categoria da transação.
            data_transacao (str): Data da transação no formato YYYY-MM-DD.
        """
        payload = {
            "user_id": usuario_id,
            "valor": valor,
            "categoria": categoria_id,
            "data_transacao": data_transacao
        }
        await self._publicar(TOPICO_TRANSACAO_CRIADA, payload)

    async def publicar_orcamento_alerta(
            self,
            usuario_id: int,
            categoria_id: int,
            pct_usado: float,
    ) -> None:
        """
        Publica evento no tópico orçamento.alerta.
        Fire-and-forget — falhas são logadas sem propagar exceção.

        Args:
            usuario_id (int): ID do usuário.
            categoria_id (int): ID da categoria que atingiu o limite.
            pct_usado (float): Percentual do orçamento usado (0-100).
        """
        payload = {
            "user_id": str(usuario_id),
            "categoria": str(categoria_id),
            "pct_usado": pct_usado
        }
        await self._publicar(TOPICO_ORCAMENTO_ALERTA, payload)

    async def _publicar(self, topico: str, payload: dict) -> None:
        """
        Publica um payload em um tópico Kafka.
        Fire-and-forget — falhas são logadas sem propagar exceção.

        Args:
            topico (str): Nome do tópico Kafka.
            payload (dict): Dados a serem publicados.
        """
        if not self._producer:
            logger.debug(
                "Kafka producer não disponível — evento ignorado: %s", topico)
            return

        try:
            await self._producer.send_and_wait(topico, payload)
            logger.info("Evento publicado: topico=%s payload=%s",
                        topico, payload)
        except Exception as e:  # pylint: disable=broad-except
            logger.exception("Erro ao publicar evento no Kafka: %s", e)

# @file Fim do arquivo kafka_producer_service.py
