"""
@file svc-orcamento/app/kafka_consumer.py
@description Instância compartilhada do KafkaConsumerService,
    criada no startup da aplicação e injetada onde necessário.

@author Tina de Almeida
@date Junho 2026
@version 1.0.0
"""
from app.cache import cache_service
from app.services.kafka_consumer_service import KafkaConsumerService

kafka_consumer = KafkaConsumerService(cache_service)

# @file Fim do arquivo svc-orcamento/app/kafka_consumer.py
