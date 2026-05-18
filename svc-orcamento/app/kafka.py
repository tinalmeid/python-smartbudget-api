"""
@module: app.kafka
@file: kafka.py
@description: Instância compartilhada do KafkaProducerService.
@author: Tina de Almeida
@date: Maio 2026
@version: 1.0.0
"""
from app.services.kafka_producer_service import KafkaProducerService

kafka_producer = KafkaProducerService()

# @file Fim do arquivo svc-orcamento/app/kafka.py
