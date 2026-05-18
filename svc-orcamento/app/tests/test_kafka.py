"""
@module svc-orcamento.app.tests.test_kafka
@file: test_kafka.py
@description: Testes unitários para o KafkaProducerService com mock.
@author: Tina de Almeida
@date: Maio 2026
@version: 1.0.0
"""
from unittest.mock import AsyncMock, patch

import pytest

from app.services.kafka_producer_service import KafkaProducerService


class TestKafkaProducerService:
    """Testes para o KafkaProducerService."""

    @pytest.mark.asyncio
    async def test_start_sem_bootstrap_servers(self):
        """Deve ignorar inicialização se KAFKA_BOOTSTRAP_SERVERS não estiver configurado."""
        service = KafkaProducerService()

        with patch.dict("os.environ", {"KAFKA_BOOTSTRAP_SERVERS": ""}):
            await service.start()

        assert service._producer is None

    @pytest.mark.asyncio
    async def test_publicar_transacao_criada_sem_producer(self):
        """Deve ignorar publicação se producer não estiver disponível."""
        service = KafkaProducerService()
        service._producer = None

        # Não deve lançar exceção mesmo sem producer
        await service.publicar_transacao_criada(
            usuario_id=1,
            valor="50.00",
            categoria_id=1,
            data_transacao="2026-05-01",
        )

    @pytest.mark.asyncio
    async def test_publicar_transacao_criada_com_producer(self):
        """Deve publicar evento no tópico correto."""
        service = KafkaProducerService()
        mock_producer = AsyncMock()
        service._producer = mock_producer

        await service.publicar_transacao_criada(
            usuario_id=1,
            valor="50.00",
            categoria_id=1,
            data_transacao="2026-05-01",
        )

        mock_producer.send_and_wait.assert_called_once()
        args = mock_producer.send_and_wait.call_args[0]
        assert args[0] == "transacao.criada"
        assert args[1]["user_id"] == 1

    @pytest.mark.asyncio
    async def test_publicar_orcamento_alerta_com_producer(self):
        """Deve publicar alerta no tópico correto."""
        service = KafkaProducerService()
        mock_producer = AsyncMock()
        service._producer = mock_producer

        await service.publicar_orcamento_alerta(
            usuario_id=1,
            categoria_id=1,
            pct_usado=85.0,
        )

        mock_producer.send_and_wait.assert_called_once()
        args = mock_producer.send_and_wait.call_args[0]
        assert args[0] == "orcamento.alerta"
        assert abs(args[1]["pct_usado"] - 85.0) < 0.01

    @pytest.mark.asyncio
    async def test_publicar_falha_kafka_nao_propaga(self):
        """Deve logar erro mas não propagar exceção quando Kafka falhar."""
        service = KafkaProducerService()
        mock_producer = AsyncMock()
        mock_producer.send_and_wait.side_effect = Exception(
            "Kafka indisponível")
        service._producer = mock_producer

        # Não deve lançar exceção
        await service.publicar_transacao_criada(
            usuario_id=1,
            valor="50.00",
            categoria_id=1,
            data_transacao="2026-05-01",
        )

    @pytest.mark.asyncio
    async def test_stop_com_producer(self):
        """Deve encerrar o producer corretamente."""
        service = KafkaProducerService()
        mock_producer = AsyncMock()
        service._producer = mock_producer

        await service.stop()

        mock_producer.stop.assert_called_once()

# @file Fim do arquivo svc-orcamento/app/tests/test_kafka.py
