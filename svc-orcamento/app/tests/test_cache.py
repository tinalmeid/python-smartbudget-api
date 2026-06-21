"""
@file svc-orcamento/app/tests/test_cache.py
@description Testes unitários para o CacheService, com mock do Redis
    para validar a lógica de cache sem depender de um servidor real.

@author Tina de Almeida
@date Junho 2026
@version 1.0.0
"""

from unittest.mock import AsyncMock, patch

import pytest

from app.services.cache_service import CacheService

# pylint: disable=protected-access


class TestCacheService:
    """Testes para o CacheService."""

    def test_inicializar_sem_redis_url(self):
        """Deve manter o cache desabilitado se REDIS_URL não estiver configurado."""
        with patch.dict("os.environ", {"REDIS_URL": ""}):
            service = CacheService()

            assert service._cache is None

    def test_montar_cache(self):
        """Deve montar a chave no formato resumo:{user_id}:{mes}."""
        chave = CacheService.montar_chave(1, "2026-05")

        assert chave == "resumo:1:2026-05"

    @pytest.mark.asyncio
    async def test_get_sem_cache(self):
        """Deve retornar None se o cache não estiver disponível."""
        service = CacheService()
        service._cache = None

        resultado = await service.get("resumo:1:2026-05")

        assert resultado is None

    @pytest.mark.asyncio
    async def test_get_com_cache(self):
        """Deve retornar o valor armazenado quando o cache estiver disponível."""
        service = CacheService()
        mock_cache = AsyncMock()
        mock_cache.get.return_value = [
            {"categoria_id": 1, "gasto_real": "50.00"}]
        service._cache = mock_cache

        resultado = await service.get("resumo:1:2026-05")

        assert resultado == [{"categoria_id": 1, "gasto_real": "50.00"}]
        mock_cache.get.assert_awaited_once_with("resumo:1:2026-05")

    @pytest.mark.asyncio
    async def test_get_falha_redis_retorna_none(self):
        """Deve retornar None se o Redis falhar - fallback para o banco de dados."""
        service = CacheService()
        mock_cache = AsyncMock()
        mock_cache.get.side_effect = Exception("Redis Indisponível")
        service._cache = mock_cache

        resultado = await service.get("resumo:1:2026-05")

        assert resultado is None

    @pytest.mark.asyncio
    async def test_set_sem_cache(self):
        """Não deve lançar exceção se o cache não estiver disponível."""
        service = CacheService()
        service._cache = None

        await service.set("resumo:1:2026-05", [{"categoria_id": 1, "gasto_real": "50.00"}])

    @pytest.mark.asyncio
    async def test_set_com_cache(self):
        """Deve gravar o valor no cache com TTL informado."""
        service = CacheService()
        mock_cache = AsyncMock()
        service._cache = mock_cache

        await service.set("resumo:1:2026-05", [{"categoria_id": 1, "gasto_real": "50.00"}], ttl=3600)

        mock_cache.set.assert_called_once_with(
            "resumo:1:2026-05", [{"categoria_id": 1, "gasto_real": "50.00"}], ttl=3600
        )

    @pytest.mark.asyncio
    async def test_delete_sem_cache(self):
        """Não deve lançar exceção se o cache não estiver disponível."""
        service = CacheService()
        service._cache = None

        await service.delete("resumo:1:2026-05")

    @pytest.mark.asyncio
    async def test_delete_com_cache(self):
        """Deve deletar a chave do cache quando disponível."""
        service = CacheService()
        mock_cache = AsyncMock()
        service._cache = mock_cache

        await service.delete("resumo:1:2026-05")

        mock_cache.delete.assert_awaited_once_with("resumo:1:2026-05")

# @file Fim do arquivo svc-orcamento/app/tests/test_cache.py
