# 📖 Padrão de Documentação de Código

Este documento define as diretrizes obrigatórias de documentação para todos os projetos da nossa equipe, independentemente da linguagem de programação utilizada. A documentação clara e padronizada é essencial para a manutenibilidade, onboarding de novos membros e escalabilidade dos nossos sistemas.

## 📄 1. Documentação de Arquivo (Cabeçalho e Rodapé)

Todo arquivo de código-fonte que contenha lógica de negócio, rotas, modelos de dados ou configurações críticas deve conter um bloco de comentários no início (cabeçalho) e um marcador no final (rodapé). Isso garante a rastreabilidade da autoria e facilita a identificação rápida do propósito do arquivo.

### **Estrutura do Cabeçalho (Início do Arquivo)**

O bloco inicial deve conter as seguintes tags obrigatórias, utilizando a sintaxe de comentário em bloco da linguagem em questão:

* `@file`: Nome do arquivo com a extensão.

* `@description`: Resumo claro do objetivo, contexto e responsabilidade principal deste arquivo.

* `@author`: Nome da pessoa desenvolvedora ou da equipe/squad responsável pela criação.

* `@date`: Mês e ano da criação original.

* `@version`: Versão atual do arquivo (ex: 1.0.0).

Exemplo em linguagens com `/* */` (JavaScript, TypeScript, Java, C#, etc.):

```javascript
/**
 * @file processamento_metricas.js
 * @description Contém as funções de limpeza, agregação e cálculo de métricas de qualidade.
 * @author Seu Nome
 * @date Março 2026
 * @version 1.0.0
 */
```

Exemplo em linguagens com `""" """` ou `#` (Python, Ruby, etc.):

```python
"""
@file processamento_metricas.py
@description Contém as funções de limpeza, agregação e cálculo de métricas de qualidade.
@author Equipe de Engenharia / Seu Nome
@date Março 2026
@version 1.0.0
"""
```

Estrutura do Rodapé (Fim do Arquivo)
Para indicar o encerramento do escopo e garantir que o arquivo está completo (evitando problemas de merges truncados), a última linha útil do arquivo deve conter a tag `@file` como comentário simples.

```javascript
// @file Fim do arquivo processamento_metricas.js
```

```python
# @file Fim do arquivo processamento_metricas.py
```

## ⚙️ 2. Documentação de Funções, Métodos e Classes

Assim como nos arquivos, as funções e regras de negócio devem possuir um contrato claro. Utilize o padrão de tags reconhecido pelos geradores de documentação universais (JSDoc, JavaDoc, Doxygen, etc.).

Estrutura Obrigatória:

1. Resumo: O que a função faz (na primeira linha do bloco).

2. `@param` / `@arg`: Nome, tipo de dado (se a linguagem não for fortemente tipada) e a descrição dos parâmetros de entrada.

3. `@returns` / `@return`: Tipo e descrição do que a função devolve ao final da execução.

4. `@throws` / `@raises`: (Opcional) Erros ou exceções que a função levanta intencionalmente para serem tratados nas camadas superiores.

Exemplo Agnóstico (Padrão JSDoc / JavaDoc):

```javascript
/**
 * Calcula a taxa de retenção de usuários ativos com base nos logs de acesso.
 *
 * @param {Object/DataFrame} base_acessos - Estrutura de dados contendo o histórico de logins.
 * @param {number} periodo_dias - Janela de tempo em dias para o cálculo (padrão: 30).
 * @returns {number} A taxa de retenção percentual em formato decimal (ex: 0.85).
 * @throws {Error} Se a base de dados fornecida estiver vazia ou com colunas ausentes.
 */
function calcularTaxaRetencao(base_acessos, periodo_dias) {
    // Lógica implementada...
}
```
