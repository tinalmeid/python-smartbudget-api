"""
@module:svc-orcamento.conftest
@file: conftest.py
@description: Configuração do path para o pytest encontrar o módulo app.
@author: Tina de Almeida
@date: Maio 2026
@version: 1.0.0
"""

import sys
import os

# Adiciona o diretório raiz do projeto ao sys.path para que o pytest possa encontrar o módulo app
sys.path.insert(0, os.path.dirname(__file__))

# @file Fim do arquivo svc-orcamento/conftest.py
