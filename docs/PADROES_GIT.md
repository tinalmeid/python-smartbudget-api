# 📘 Padrões de Git — python-smartbudget-api

Este documento define os padrões de versionamento e revisão de código do projeto.

## 1. Cheatsheet (Fluxo de Trabalho)

Siga esta ordem para cada task.

### Passo 1 — Atualize a main

```bash
git checkout main
git pull origin main
```

### Passo 2 — Crie a branch da task

Padrão: `ID-JIRA-tipo/nome-da-tarefa`

```bash
git checkout -b ARQ-453-chore/setup-repo-sonarcloud
git checkout -b ARQ-455-feat/svc-usuarios-jwt
git checkout -b ARQ-456-test/svc-usuarios-auth
```

### Passo 3 — Commit

Padrão de mensagem: `ARQ-ID tipo(escopo): descrição`

```bash
git status
git add .
git commit -m "ARQ-453 chore(setup): configura sonar-project.properties e pytest.ini"
```

### Passo 4 — Push

```bash
# Primeira vez na branch:
git push -u origin ARQ-453-chore/setup-repo-sonarcloud

# Próximas vezes:
git push
```

## 2. Tipos de Branch e Commit

| Tipo | Quando usar | Exemplo |
| --- | --- | --- |
| `chore` | Configuração, infra, CI/CD | `ARQ-453-chore/setup-repo-sonarcloud` |
| `feat` | Nova funcionalidade | `ARQ-455-feat/svc-usuarios-jwt` |
| `test` | Criação de testes | `ARQ-456-test/svc-usuarios-auth` |
| `fix` | Correção de bug | `ARQ-XXX-fix/corrige-token-expirado` |
| `refactor` | Melhoria sem mudar comportamento | `ARQ-XXX-refactor/extrai-service-layer` |
| `docs` | Apenas documentação | `ARQ-474-docs/readme-profissional` |

## 3. Auto Code Review (antes do PR)

- [ ] SOLID aplicado (ver `docs/SOLID.md`)
- [ ] Docstrings em todas as funções (ver `docs/PADROES_DE_DOCUMENTACAO.md`)
- [ ] Clean Code: sem print(), sem imports não usados, sem código morto (ver `docs/CLEAN_CODE.md`)
- [ ] Nenhuma credencial no código ou commit
- [ ] `pytest` passa com cobertura >= 80%
- [ ] SonarCloud Quality Gate verde

## 4. Padrão de Merge (Squash and Merge)

No GitHub, use sempre **Squash and Merge**.

**Título:**

```text
[ARQ-XXX] tipo(escopo): descrição curta
```

**Exemplos:**

```text
[ARQ-453] chore(setup): configura repositório monorepo e sonarcloud
[ARQ-455] feat(auth): implementa registro e login jwt no svc-usuarios
[ARQ-456] test(auth): testes unitários coverage 80% svc-usuarios
```

## 5. Limpeza Pós-Merge

```bash
git checkout main
git pull origin main
git branch -d ARQ-453-chore/setup-repo-sonarcloud
git checkout -b ARQ-454-chore/docker-compose-base
```

Configure o GitHub para apagar branches automaticamente:

```text
Settings > General > Pull Requests > Automatically delete head branches
```
