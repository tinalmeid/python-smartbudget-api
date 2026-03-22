# 📊 Guia de Criação de Dashboards Grafana

**Autora:** Cristina de Almeida

**Data:** Março 2026

**Versão:** 1.0.0

## 🗂️ Estrutura de Arquivos por Projeto

Cada projeto deve ter seus dashboards versionados no repositório:

```text
meu-projeto/
└── grafana/
    ├── dashboard-prometheus.json  ← métricas
    ├── dashboard-loki.json        ← logs
    └── README.md                  ← documenta as métricas do projeto
```

## 📐 Anatomia de um Dashboard

Um dashboard Grafana é um arquivo JSON com esta estrutura:

```text
Dashboard
├── Metadados (title, uid, tags, refresh)
├── __inputs (datasources que serão configurados no import)
└── panels[] (lista de painéis)
    └── Painel
        ├── id, title, description
        ├── type (stat, timeseries, gauge, logs, barchart)
        ├── gridPos (posição e tamanho: h=altura, w=largura, x=coluna, y=linha)
        ├── fieldConfig (unidades, thresholds, cores)
        ├── options (configurações visuais)
        └── targets[] (queries — uma por linha de dados)
            └── Target
                ├── datasource (prometheus ou loki)
                ├── expr (a query PromQL ou LogQL)
                └── legendFormat (label na legenda)
```

**Regra de gridPos:** O Grafana usa uma grade de 24 colunas.

- `w: 6` = ocupa 1/4 da tela
- `w: 12` = ocupa metade da tela
- `w: 24` = ocupa a tela toda
- `h: 4` = painel pequeno (número/stat)
- `h: 8` = painel médio (gráfico)

## 🔵 FERRAMENTA 1: PROMETHEUS

### O que é

Prometheus armazena **métricas numéricas** ao longo do tempo.
Cada métrica tem um nome e labels (filtros).

Exemplo de dado armazenado:

```bash
cdd_pipeline_success{branch="main", project="meu-projeto"} 1
```

### Linguagem: PromQL

PromQL é a linguagem de consulta do Prometheus. Exemplos do mais simples ao mais complexo:

| Query | O que faz |
| --- | --- |
| `nome_da_metrica` | Retorna o valor atual |
| `nome_da_metrica{label="valor"}` | Filtra por label |
| `avg_over_time(metrica[$__range])` | Média no período selecionado |
| `count_over_time(metrica[1d])` | Conta ocorrências no dia |
| `sum(metrica) by (label)` | Soma agrupada por label |
| `rate(metrica[5m])` | Taxa de variação por segundo |

`$__range` é uma variável especial do Grafana que representa o período selecionado no seletor de tempo.

### Tipos de Painéis para Métricas

| Tipo | Quando usar | Exemplo |
| --- | --- | --- |
| `stat` | Um único número em destaque | Status atual, total de builds |
| `gauge` | Percentual com zona de alerta | Taxa de sucesso % |
| `timeseries` | Evolução ao longo do tempo | Duração dos builds |
| `barchart` | Comparação por período | Builds por dia |
| `table` | Múltiplos valores lado a lado | Tabela de erros |

### Thresholds (Limites de Cor)

```json
"thresholds": {
  "mode": "absolute",
  "steps": [
    { "color": "red",    "value": null },  ← abaixo deste valor = vermelho
    { "color": "yellow", "value": 70 },    ← acima de 70 = amarelo
    { "color": "green",  "value": 90 }     ← acima de 90 = verde
  ]
}
```

### Unidades Comuns

| Código | Significado |
| --- | --- |
| `s` | Segundos |
| `ms` | Milissegundos |
| `percent` | Porcentagem (0-100) |
| `percentunit` | Porcentagem (0-1) |
| `short` | Número simples |
| `bytes` | Bytes |
| `reqps` | Requisições por segundo |

### Passo a Passo para Novo Projeto

```text
1. Identificar as métricas do projeto
   └── O que faz sentido monitorar?
       ex: api.tempo_resposta, pipeline.duracao, modelo.acuracia

2. Definir os nomes seguindo snake_case
   └── prefixo_categoria_nome
       ex: cdd_pipeline_success, cdd_api_tempo_resposta

3. Copiar prometheus-dashboard-template.json
   └── renomear para dashboard-prometheus-NOME_PROJETO.json

4. Substituir todos os ✏️ no JSON:
   ├── NOME_DO_PROJETO → nome real do projeto
   ├── TITULO_DO_PAINEL → nome descritivo do painel
   ├── NOME_DA_METRICA → nome exato da métrica no Prometheus
   ├── VALOR_ALERTA → número que dispara alerta amarelo
   ├── VALOR_OK → número que indica verde
   └── UNIDADE → código da unidade (s, percent, short...)

5. Importar no Grafana e validar
6. Salvar o JSON no repositório
```

## 🟡 FERRAMENTA 2: LOKI

### Definição

Loki armazena **logs de texto** com labels para filtrar.
Cada log tem: timestamp, labels e mensagem.

Exemplo de dado armazenado:

```bash
timestamp: 2026-03-17T18:00:00Z
labels: {job="azure-pipeline", nivel="info", branch="main"}
mensagem: "[SUCCESS] Pipeline concluído em 58s | Build=24"
```

### Linguagem: LogQL

LogQL é a linguagem do Loki. Exemplos:

| Query | O que faz |
| --- | --- |
| `{job="nome"}` | Todos os logs do job |
| `{job="nome", nivel="error"}` | Filtra por label |
| `{job="nome"} \|= "ERROR"` | Filtra por texto na mensagem |
| `{job="nome"} \| json` | Parseia mensagens JSON |
| `count_over_time({job="nome"}[5m])` | Conta logs em 5 min |
| `sum by (nivel) (count_over_time({job="nome"}[5m]))` | Agrupa por label |

### Tipos de Painéis para Logs

| Tipo | Quando usar |
| --- | --- |
| `logs` | Visualizar as mensagens em tempo real |
| `timeseries` | Volume de logs ao longo do tempo |
| `stat` | Contar total de erros |
| `table` | Listar logs estruturados |

### Labels Padrão Recomendados

Sempre envie estes labels nos logs para facilitar os filtros:

```bash
job     = nome do serviço/pipeline
nivel   = info | warning | error
env     = dev | test | prod
projeto = nome do projeto
branch  = branch do git (se aplicável)
```

### Passo a Passo se Novo Projeto

```text
1. Definir os labels do projeto
   └── Quais filtros vou precisar no Grafana?
       ex: job, nivel, etapa, servico

2. Garantir que o código envia esses labels
   └── No loki_client.py, passar os labels corretos

3. Copiar loki-dashboard-template.json
   └── renomear para dashboard-loki-NOME_PROJETO.json

4. Substituir todos os ✏️ no JSON:
   ├── NOME_DO_PROJETO → nome real
   └── NOME_DO_JOB → valor exato do label job= enviado no código

5. Importar no Grafana e validar
6. Salvar no repositório
```

## 🟣 FERRAMENTA 3: DATADOG

### Descrição

Datadog é um serviço pago com interface rica. As métricas são enviadas via API HTTP.
Não usa Grafana — tem seu próprio dashboard.

### Como criar um Dashboard no Datadog

```text
Datadog → Dashboards → New Dashboard
└── Add Widget
    ├── Timeseries → métrica ao longo do tempo
    ├── Query Value → número em destaque
    ├── Top List → ranking
    └── Log Stream → logs em tempo real
```

### Linguagem: DQL (Datadog Query Language)

```bash
# Valor atual da métrica
avg:cdd.pipeline.success{*}

# Filtrar por tag
avg:cdd.pipeline.duration_seconds{project:meu-projeto}

# Agrupar por tag
avg:cdd.pipeline.duration_seconds{*} by {project}
```

### Passo a Passo quando Novo Projeto

```text
1. Definir as métricas e tags
   └── prefixo.categoria.nome
       ex: cdd.pipeline.success, cdd.api.tempo_resposta

2. Garantir que o código envia as tags corretas
   └── No datadog_client.py, passar as tags do projeto

3. No Datadog → Dashboards → New Dashboard
   └── Criar painel por painel usando a interface visual

4. Exportar o JSON do dashboard
   └── Dashboard → Settings → JSON → copiar

5. Salvar no repositório como grafana/datadog-dashboard.json
```

## 📋 Checklist para Novo Projeto

```text
□ Identificar métricas relevantes do projeto
□ Definir nomes das métricas (snake_case, prefixo consistente)
□ Definir labels/tags para filtrar no dashboard
□ Criar pasta grafana/ no repositório
□ Copiar templates e substituir os ✏️
□ Importar no Grafana e validar que os dados chegam
□ Criar pasta no Grafana com o nome do projeto
□ Salvar JSONs no repositório
□ Documentar as métricas no grafana/README.md
```

## 💡 Boas Práticas

1. **Nome de métricas:** sempre `snake_case`, com prefixo do projeto
   - ✅ `cdd_pipeline_success`
   - ❌ `Pipeline-Success`, `pipelineSuccess`

2. **Labels:** use labels que você realmente vai filtrar
   - ✅ `{branch="main", env="prod"}`
   - ❌ labels demais aumentam a cardinalidade e custam caro

3. **Dashboards por camada:**
   - `overview` → visão executiva (taxa de sucesso, total)
   - `operacional` → status em tempo real, alertas
   - `debug` → logs detalhados, traces

4. **Versionar no Git:** o JSON do dashboard é código — commit junto com o projeto

5. **UID único:** o campo `uid` do dashboard precisa ser único por Grafana
   - Use o padrão: `nome-do-projeto-ferramenta`
   - ex: `pyfinance-prometheus`, `test-pipeline-loki`

## Como Utilizar os templates

GUIA_DASHBOARDS_GRAFANA.md — o guia completo com a teoria de cada ferramenta, PromQL, LogQL, tipos de painéis, unidades, boas práticas e o checklist para novos projetos.

prometheus-dashboard-template.json — JSON base com dois painéis (stat + timeseries).
Todos os campos que precisa editar estão marcados com ✏️ para não ter dúvida do que mudar.

loki-dashboard-template.json — JSON base com três painéis (logs em tempo real, logs de erro e volume por nível). Mesmo padrão de ✏️.

1. Copiar o template JSON para grafana/ no novo repositório
2. Substituir todos os ✏️ pelos valores do projeto
3. Importar no Grafana
4. Consultar o guia quando tiver dúvida de PromQL ou LogQL
