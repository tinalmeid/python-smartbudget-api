"""
@file: svc-usuarios/conftest.py
@description: Configuração do path para o pytest encontrar o módulo app.
@author: Tina de Almeida
@date: Abril 2026
@version: 1.0.0
"""
import sys
import os

# Adiciona o diretório svc-usuarios ao path do Python
sys.path.insert(0, os.path.dirname(__file__))

# @file Fim do arquivo svc-usuarios/conftest.py
