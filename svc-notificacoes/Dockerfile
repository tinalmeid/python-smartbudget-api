# @file svc-notificacoes/Dockerfile
# @description Imagem Docker do svc-notificacoes
# Baseada em Python 3.12-slim. Instala certificados SSL necessários para conexão com PlanetScale.
#
# @author Tina de Almeida
# @date Abril 2026
# @version 1.0.0

FROM python:3.12-slim

# @description Define o diretório de trabalho
WORKDIR /app

# @description Instala dependências necessárias para o funcionamento do container
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

# @description Copia os arquivos de dependências
COPY requirements.txt .

# @description Instala as dependências
RUN pip install --no-cache-dir -r requirements.txt

# @description Copia o código fonte
COPY . .

# @description Expõe a porta 8004 do svc-notificacoes
EXPOSE 8004

# @description Inicia o servidor FastAPI
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${APP_PORT:-8004}"]

# @file Fim do arquivo svc-notificacoes/Dockerfile
