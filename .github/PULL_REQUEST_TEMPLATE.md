# Pull Request — python-smartbudget-api

**Task:** ARQ-XXX | Nome da Task
**Branch:** `ARQ-XXX-tipo/nome-da-tarefa`

## Contexto

Este PR implementa [descreva o que foi feito, ex: autenticação JWT no svc-usuarios com registro, login e refresh token].

## Tipo de Mudança

- [ ] Nova funcionalidade (`feat`)
- [ ] Correção de bug (`fix`)
- [ ] Refatoração (`refactor`)
- [ ] Testes (`test`)
- [ ] Configuração/Infra (`chore`)
- [ ] Documentação (`docs`)

## Escopo Técnico

- [ ] Código de negócio (routers, services, models)
- [ ] Testes unitários
- [ ] Configuração (Docker, CI/CD, env)
- [ ] Banco de dados (migrations, schemas)
- [ ] Documentação

## Qualidade e Evidências

**Cobertura de Testes:**

- [ ] >= 80% (padrão exigido pelo quality gate)
- [ ] Entre 60% e 80% (justificar abaixo)
- [ ] Abaixo de 60% (bloqueado — não abre PR)

## Print da Pipeline / Testes

> Cole aqui o output do pytest mostrando os testes passando e a cobertura,
> ou o link do run do GitHub Actions.

```text
pytest output aqui
```

> Recortar e colar no comentário do PR, antes de realizar o Squash Merge, confirmando todos os itens'
**Checklist obrigatório:**

Confirmação de execução local:
- [ ] `pytest` passa localmente com `--cov-fail-under=80`
- [ ] SonarCloud Quality Gate verde (sem new code smells)
- [ ] Docstrings em todas as funções novas ou alteradas
- [ ] SOLID aplicado (especialmente SRP — funções com uma responsabilidade)
- [ ] Sem `print()` de debug, sem imports não usados
- [ ] Nenhuma credencial ou secret no código
- [ ] `requirements.txt` atualizado (se instalou nova lib)
- [ ] `README.md` atualizado (se adicionou nova feature ou endpoint)
