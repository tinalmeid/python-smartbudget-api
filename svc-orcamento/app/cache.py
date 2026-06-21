"""
@file svc-orcamento/app/cache.py
@description: Instância compartilhada do serviço de cache Redis para resumos mensais.
    Fornece uma interface única para operações de cache, garantindo que a configuração e a conexão
    sejam gerenciadas centralmente. O cache é utilizado para armazenar resumos financeiros mensais,
    melhorando a performance e reduzindo a carga no banco de dados para consultas frequentes.
    A estratégia de cache inclui:
        - Chave: resumo:{usuario_id}:{mes}
        - TTL: 1 hora (3600 segundos) para expiração automática, protegendo contra dados desatualizados
        mesmo se a invalidação manual falhar.

@author: Tina de Almeida
@date: Junho 2026
@version: 1.0.0
"""

from app.services.cache_service import CacheService

cache_service = CacheService()

# @file Fim do arquivo svc-orcamento/app/cache.py
