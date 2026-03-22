# Limpo Código e Boas Práticas — python-smartbudget-api

> "Código é lido muito mais vezes do que é escrito."

## 1. Nomenclatura

Em Python seguimos snake_case.

| Tipo | Ruim | Bom | Por que |
| --- | --- | --- | --- |
| Variáveis | x, d, aux | dias_restantes, usuario_id | d pode ser dia, dinheiro ou distância |
| Funções | processar(), fazer() | calcular_gasto_mensal(), buscar_usuario_por_id() | O verbo deve dizer exatamente o que faz |
| Booleanos | flag, status | is_ativo, tem_permissao | Deve soar como pergunta de Sim/Não |
| Classes | dados, servico | TransacaoService, UsuarioRepository | Substantivo mais papel/camada |

## 2. Funções com Uma Responsabilidade (SRP)

```python
# Ruim: faz validação + cálculo + banco + e-mail tudo junto
def processar_transacao(dados):
    if dados["valor"] < 0:
        raise ValueError("Valor inválido")
    total = sum(...)
    db.save(...)
    email.send(...)

# Bom: cada função faz uma coisa só
def validar_transacao(dados: dict) -> None:
    if dados["valor"] < 0:
        raise ValueError("Valor não pode ser negativo")

def calcular_total_mensal(transacoes: list) -> float:
    return sum(t["valor"] for t in transacoes)

def salvar_transacao(transacao: Transacao, db: Session) -> Transacao:
    db.add(transacao)
    db.commit()
    return transacao
```

## 3. Tipagem — Obrigatória

```python
# Ruim: o que entra e o que sai?
def buscar_usuario(usuario_id):
    ...

# Bom: contrato claro
def buscar_usuario(usuario_id: str) -> Usuario | None:
    ...
```

> O FastAPI usa a tipagem para gerar o Swagger automaticamente.

## 4. Logs em vez de print()

```python
import logging
logger = logging.getLogger(__name__)

# Ruim
print("Usuário criado")
print("TESTE - valor:", valor)

# Bom — vai para o Datadog e Grafana
logger.info("Usuário criado", extra={"usuario_id": usuario_id})
logger.warning("Limite atingido", extra={"pct_usado": 85.3})
logger.error("Falha no banco", exc_info=True)
```

> NUNCA logue senhas, tokens JWT ou dados pessoais.

## 5. Constantes em vez de Números Mágicos

```python
# Ruim
if token_age > 900:
    raise ...
if gasto / limite > 0.8:
    publicar_alerta()

# Bom
ACCESS_TOKEN_EXPIRE_SECONDS = 900
LIMITE_ALERTA_PERCENTUAL = 0.8

if token_age > ACCESS_TOKEN_EXPIRE_SECONDS:
    raise ...
if gasto / limite > LIMITE_ALERTA_PERCENTUAL:
    publicar_alerta()
```

## 6. Tratamento de Erros

```python
# Ruim: captura tudo e esconde o problema
try:
    resultado = chamar_api()
except:
    pass

# Bom: específico, com log e resposta adequada
try:
    resultado = chamar_api()
except httpx.TimeoutException:
    logger.error("Timeout ao chamar svc-orcamento", exc_info=True)
    raise HTTPException(status_code=503, detail="Serviço indisponível")
```

## 7. Checklist Antes do `git add .`

- Remover todos os print() de debug
- Remover imports não usados
- Remover blocos de código comentado (o Git guarda o histórico)
- Confirmar que .env não está sendo adicionado
