# 💰 SmartBudget API — Plataforma de Planejamento Financeiro com IA

![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=tinalmeid_python-smartbudget-api&metric=alert_status)
![Coverage](https://sonarcloud.io/api/project_badges/measure?project=tinalmeid_python-smartbudget-api&metric=coverage)
![Duplicated Lines (%)](https://sonarcloud.io/api/project_badges/measure?project=tinalmeid_python-smartbudget-api&metric=duplicated_lines_density)
![Build Status](https://github.com/tinalmeid/python-smartbudget-api/actions/workflows/ci.yml/badge.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

## Desenvolvimento

![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=flat&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/API-FastAPI-009688?style=flat&logo=fastapi&logoColor=white)
![Pytest](https://img.shields.io/badge/Testes-Pytest-0A9EDC?style=flat&logo=pytest&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/ORM-SQLAlchemy-D71F00?style=flat)
![Prophet](https://img.shields.io/badge/ML-Prophet-FF6F00?style=flat)
![MLflow](https://img.shields.io/badge/MLOps-MLflow-0194E2?style=flat&logo=mlflow&logoColor=white)

## Infraestrutura

![Docker](https://img.shields.io/badge/Container-Docker-2496ED?style=flat&logo=docker&logoColor=white)
![AWS](https://img.shields.io/badge/Cloud-AWS-FF9900?style=flat&logo=amazonaws&logoColor=white)
![PlanetScale](https://img.shields.io/badge/BD-PlanetScale-000000?style=flat)
![Redis](https://img.shields.io/badge/Cache-Redis-DC382D?style=flat&logo=redis&logoColor=white)
![Kafka](https://img.shields.io/badge/Mensageria-Kafka-231F20?style=flat&logo=apachekafka&logoColor=white)

## Gestão & DevOps

![Jira](https://img.shields.io/badge/Gestão-Jira-0052CC?style=flat&logo=jira&logoColor=white)
![Azure DevOps](https://img.shields.io/badge/Gestão-Azure_DevOps-0078D7?style=flat&logo=azuredevops&logoColor=white)
![GitHub Actions](https://img.shields.io/badge/CI-GitHub_Actions-2088FF?style=flat&logo=githubactions&logoColor=white)
![SonarCloud](https://img.shields.io/badge/Quality-SonarCloud-F3702A?style=flat&logo=sonarcloud&logoColor=white)
![Clean Code](https://img.shields.io/badge/Prática-Clean_Code-green?style=flat)

## Observabilidade

![Datadog](https://img.shields.io/badge/APM-Datadog-632CA6?style=flat&logo=datadog&logoColor=white)
![Grafana](https://img.shields.io/badge/Dashboard-Grafana-F46800?style=flat&logo=grafana&logoColor=white)

---

> Sistema de microsserviços para controle e previsão de gastos pessoais.
> O usuário registra transações, define limites por categoria, e a IA prevê os gastos
> dos próximos meses — gerando alertas automáticos quando o limite está próximo.

## 🏗️ Arquitetura

```text
Cliente (Mobile/Web)
        │
        ▼
   nginx (API Gateway) — Rate Limit · SSL · Roteamento
        │
        ├──▶ svc-usuarios   :8001  — Autenticação JWT
        ├──▶ svc-orcamento  :8002  — Transações e metas
        ├──▶ svc-previsao   :8003  — Prophet + MLflow
        └──▶ svc-notificacoes :8004 — Alertas (Kafka consumer)
                │
                ▼
          Kafka (Confluent Cloud)
          Redis (Cache)
          PlanetScale MySQL (1 banco por serviço)
          AWS S3 (artefatos MLflow)
```

## 🚀 Como Rodar Localmente

### Pré-requisitos

- Python 3.12+
- Docker e Docker Compose
- Git

### 1. Clone o repositório

```bash
git clone https://github.com/tinalmeid/python-smartbudget-api.git
cd python-smartbudget-api
```

### 2. Configure as variáveis de ambiente

```bash
cp .env.example .env
# Edite o .env com seus valores reais
```

### 3. Suba os serviços

```bash
# Infraestrutura primeiro (Redis + Datadog)
docker compose up redis datadog-agent -d

# Depois os serviços (um por vez para verificar)
docker compose up svc-usuarios -d

# Verificar saúde
curl http://localhost:8001/health
# Esperado: {"status": "ok", "service": "svc-usuarios"}

# Todos de uma vez (depois que estiver tudo configurado)
docker compose up -d
```

### 4. Acesse a documentação automática (Swagger)

```text
http://localhost:8001/docs  — svc-usuarios
http://localhost:8002/docs  — svc-orcamento
http://localhost:8003/docs  — svc-previsao
http://localhost:8004/docs  — svc-notificacoes
```

## 🔑 Endpoints Principais

| Método | Endpoint | Serviço | Descrição |
| --- | --- | --- | --- |
| `POST` | `/v1/auth/register` | usuarios | Cria conta |
| `POST` | `/v1/auth/login` | usuarios | Login → JWT |
| `POST` | `/v1/transacoes` | orcamento | Registra gasto |
| `GET` | `/v1/resumo?mes=YYYY-MM` | orcamento | Gasto vs limite |
| `POST` | `/v1/prever-gasto` | previsao | Previsão Prophet |

## 🧪 Testes

```bash
# Todos os serviços
pytest

# Serviço específico
pytest svc-usuarios/app/tests/ -v

# Com relatório de cobertura
pytest --cov-report=term-missing
```

**Cobertura mínima exigida: 80%** — o pipeline bloqueia o merge se cair abaixo.

## 🌿 Padrões de Desenvolvimento

Consulte os guias em `docs/`:

| Arquivo | Conteúdo |
| --- | --- |
| `docs/PADROES_GIT.md` | Branches, commits, squash merge |
| `docs/PADROES_JIRA.md` | Estrutura de tasks |
| `docs/CLEAN_CODE.md` | Nomenclatura e boas práticas |
| `docs/SOLID.md` | Princípios SOLID com exemplos |
| `docs/PADROES_DE_DOCUMENTACAO.md` | Docstrings e cabeçalhos |
| `grafana/GUIA_DASHBOARDS_GRAFANA.md` | Grafana, Prometheus e Loki |

## 🗺️ Roadmap (Jira / Azure DevOps)

| ID | Task | Branch | Status |
| --- | --- | --- | --- |
| **ARQ-453** | 🏗️ Setup repositório e SonarCloud | `ARQ-453-chore/setup-repo-sonarcloud` | ✅ Concluído |
| **ARQ-454** | 🐳 Docker Compose base | `ARQ-454-chore/docker-compose-base` | ✅ Concluído |
| **ARQ-455** | 🔐 svc-usuarios — JWT | `ARQ-455-feat/svc-usuarios-jwt` | ✅ Concluído |
| **ARQ-456** | 🧪 Testes svc-usuarios | `ARQ-456-test/svc-usuarios-auth` | 📝 A Fazer |
| **ARQ-457** | ⚙️ GitHub Actions CI/CD | `ARQ-457-chore/github-actions-pipeline` | 📝 A Fazer |
| **ARQ-458** | 📊 Datadog APM | `ARQ-458-chore/datadog-apm-setup` | 📝 A Fazer |

> **Legenda:** ✅ Concluído | 🔄 Em Andamento | 📝 A Fazer

## 🔐 Variáveis de Ambiente

Todas as variáveis estão documentadas em `.env.example`. As mais importantes:

| Variável | Descrição | Exemplo |
| --- | --- | --- |
| `SECRET_KEY` | Chave JWT (gere com `secrets.token_hex(32)`) | `abc123...` |
| `DB_USUARIOS_URL` | URL PlanetScale do svc-usuarios | `mysql+pymysql://...` |
| `KAFKA_BOOTSTRAP_SERVERS` | Endereço Confluent Cloud | `pkc-xxx:9092` |
| `DATADOG_API_KEY` | API Key do Datadog | `dd_api_...` |
| `AWS_ACCESS_KEY_ID` | Credencial AWS para S3/ECR | `AKIA...` |

## 📄 Licença

Projeto educacional — desenvolvido por **Cristina de Almeida** como parte do plano de aprendizado em Arquitetura, DevOps, Observabilidade e Ciência de Dados.

👩🏽‍💻 [github.com/tinalmeid](https://github.com/tinalmeid)
