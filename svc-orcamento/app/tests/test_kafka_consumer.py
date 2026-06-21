"""
@file: svc-orcamento/app/tests/test_kafka_consumer.py
@description: Testes unitários para o KafkaConsumerService com mock do Kafka e do cache.
@author: Tina de Almeida
@date: Maio 2026
@version: 1.0.0
"""
# pylint: disable=protected-access
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.services.kafka_consumer_service import KafkaConsumerService


class TestKafkaConsumerService:
    """Testes para o KafkaConsumerService."""

    @pytest.mark.asyncio
    async def test_start_sem_bootstrap_servers(self):
        """Deve manter o consumer desabilitado se KAFKA_BOOTSTRAP_SERVERS não estiver configurado."""
        mock_cache = MagicMock()
        service = KafkaConsumerService(mock_cache)

        with patch.dict("os.environ", {"KAFKA_BOOTSTRAP_SERVERS": ""}):
            await service.start()

        assert service._consumer is None

    @pytest.mark.asyncio
    async def test_processar_evento_invalida_cache(self):
        """Deve invalidar o cache do usuário e mês corretos ao processar o evento."""
        mock_cache = MagicMock()
        mock_cache.montar_chave.return_value = "resumo:1:2026-05"
        mock_cache.delete = AsyncMock()

        service = KafkaConsumerService(mock_cache)

        payload = {
            "user_id": 1,
            "valor": "50.00",
            "categoria": 1,
            "data_transacao": "2026-05-15",
        }

        await service._processar_evento(payload)

        mock_cache.montar_chave.assert_called_once_with(1, "2026-05")
        mock_cache.delete.assert_called_once_with("resumo:1:2026-05")

    @pytest.mark.asyncio
    async def test_processar_evento_payload_invalido(self):
        """Não deve lançar exceção nem invalidar cache se o payload estiver mal formado."""
        mock_cache = MagicMock()
        mock_cache.delete = AsyncMock()

        service = KafkaConsumerService(mock_cache)

        payload = {"user_id": 1}  # falta data_transacao

        await service._processar_evento(payload)

        mock_cache.delete.assert_not_called()

    @pytest.mark.asyncio
    async def test_stop_sem_consumer(self):
        """Não deve lançar exceção se o consumer não estiver disponível."""
        mock_cache = MagicMock()
        service = KafkaConsumerService(mock_cache)

        await service.stop()

    @pytest.mark.asyncio
    async def test_stop_com_consumer(self):
        """Deve encerrar o consumer ao parar o serviço."""
        mock_cache = MagicMock()
        service = KafkaConsumerService(mock_cache)

        mock_consumer = AsyncMock()
        service._consumer = mock_consumer

        await service.stop()

        mock_consumer.stop.assert_called_once()

# @file Fim do arquivo svc-orcamento/app/tests/test_kafka_consumer.py
