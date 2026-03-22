# 🧱 Princípios SOLID

Guia de referência dos princípios de arquitetura utilizados no projeto.

## 1. SRP - Single Responsibility Principle (Responsabilidade Única)

> *"Uma classe ou função deve ter um, e apenas um, motivo para mudar."*

### 💡 O Conceito (S)

Imagine um **Canivete Suíço** vs. um **Bisturi**.

* O canivete faz tudo (corta, abre vinho, lixa), mas não faz nada com excelência e é difícil de manusear.
* O bisturi faz apenas uma coisa (cortar), mas faz com precisão absoluta.

No código, queremos **Bisturis**. Cada função deve resolver apenas um problema pequeno.

### ❌ Como NÃO fazer (Violação do SRP)

Uma função "Faz Tudo". Se a regra de e-mail mudar, você mexe nela. Se o banco de dados mudar, você mexe nela também. Isso gera bugs.

```javascript
// Ruim: A função mistura Validação + Regra de Negócio + Infraestrutura em um lugar só.
function registrarHost(nome) {
    // 1. Validação
    if (nome == null || nome == "") {
        throw new Error("Nome não pode ser vazio");
    }

    // 2. Lógica de Negócio (Formatação de String)
    let nomeFinal = nome.trim().toLowerCase() + ".com";

    // 3. Infraestrutura (Comunicação com o Banco de Dados)
    Database.save(nomeFinal);
}
```

### ✅ Como FAZER (Aplicando SRP)

Quebramos a lógica em pequenas funções especialistas. O código fica limpo, fácil de testar (você pode testar a formatação sem precisar de um banco de dados falso) e as responsabilidades ficam claras.

```javascript
/**
 * Responsabilidade: Apenas manipular texto (Regra de Negócio Pura).
 */
function formatarHostname(nome) {
    return nome.trim().toLowerCase() + ".com";
}

/**
 * Responsabilidade: Apenas falar com o Banco de Dados (Infraestrutura).
 */
function salvarHostNoBanco(nomeFormatado) {
    Database.save(nomeFormatado);
}

/**
 * Responsabilidade: Orquestrar o processo (Controlador).
 * Ela não formata nem salva, apenas delega o trabalho para os especialistas.
 */
function registrarHost(nome) {
    if (nome == null || nome == "") {
        throw new Error("Nome não pode ser vazio");
    }

    let host = formatarHostname(nome);
    salvarHostNoBanco(host);
}
```

## 2. OCP - Open/Closed Principle (Princípio do Aberto/Fechado)

> *"Entidades de software (classes, módulos, funções) devem estar abertas para extensão, mas fechadas para modificação."*

### 💡 O Conceito (O)

Pense nas **Portas USB** do seu computador.

Se você quer adicionar um novo mouse, teclado ou webcam, você não precisa abrir a CPU com uma chave de fenda, cortar fios e soldar o novo equipamento na placa-mãe. Você simplesmente "pluga" o dispositivo na entrada USB.
O computador está **fechado para modificação** (você não altera a placa-mãe), mas **aberto para extensão** (você pode plugar infinitos dispositivos novos).

No código, queremos a mesma coisa: poder adicionar novos comportamentos sem ter que alterar (e correr o risco de quebrar) o código que já funciona em produção.

### ❌ Como NÃO fazer (Violação do OCP)

O maior sintoma de violação do OCP é aquele arquivo cheio de `if/else` ou `switch` intermináveis.

Imagine um serviço que exporta métricas de qualidade. Toda vez que a área de negócios pede um formato novo, o engenheiro tem que abrir a função principal e alterar o código, correndo o risco de quebrar a exportação dos formatos antigos.

```javascript
// Ruim: Se precisarmos exportar para 'pdf' ou 'parquet',
// teremos que alterar e recompilar essa mesma função.
function exportarMetricas(dados, formato) {
    if (formato === "csv") {
        // Lógica gigante para converter em CSV
        console.log("Exportando CSV...");
    }
    else if (formato === "json") {
        // Lógica gigante para converter em JSON
        console.log("Exportando JSON...");
    }
    else {
        throw new Error("Formato não suportado.");
    }
}
```

### ✅ Como FAZER (Aplicando OCP)

Nós usamos "Polimorfismo" (Interfaces ou Classes abstratas) ou um padrão de projeto como o Strategy.

Criamos um "contrato" (a nossa porta USB) e cada novo formato de exportação é um arquivo separado (o nosso pen-drive). O código principal nunca mais precisa ser tocado.

```javascript
/**
 * 1. Criamos a nossa "Porta USB" (A Interface/Contrato)
 * Todos os exportadores devem ter o método 'exportar'.
 */
class Exportador {
    exportar(dados) {
        throw new Error("Método precisa ser implementado");
    }
}

/**
 * 2. Criamos as extensões (Os "Pen-drives")
 * Se der erro no CSV, o JSON continua funcionando perfeitamente.
 */
class ExportadorCSV extends Exportador {
    exportar(dados) {
        // Lógica isolada para CSV
        console.log("Exportando dados para CSV...");
    }
}

class ExportadorJSON extends Exportador {
    exportar(dados) {
        // Lógica isolada para JSON
        console.log("Exportando dados para JSON...");
    }
}

/**
 * 3. O Controlador (Fechado para modificação!)
 * Esta função não precisa mais de if/else. Ela aceita qualquer "Exportador".
 * Se amanhã criarem o ExportadorParquet, essa função continuará intacta.
 */
function processarMétricas(dados, exportador) {
    // Ela confia cegamente que o exportador sabe o que fazer.
    exportador.exportar(dados);
}

// Uso:
processarMétricas(dadosDoBanco, new ExportadorCSV());
```

## 3. LSP - Liskov Substitution Principle (Princípio da Substituição de Liskov)

> *"Classes filhas (ou implementações) devem poder substituir suas classes pais (ou interfaces) sem quebrar o comportamento do sistema."*

### 💡 O Conceito (L)

Existe uma brincadeira clássica na engenharia de software: *"Se parece com um pato e grasna como um pato, mas precisa de pilhas para funcionar... você violou o Princípio de Liskov."*

Em outras palavras: se você cria uma regra dizendo que todo "Pássaro" pode voar, e amanhã você cria um "Pinguim" que herda de "Pássaro", o seu sistema vai quebrar quando tentar fazer o pinguim voar.

A regra de ouro é: **quem consome a classe não deve precisar saber qual é a classe específica que está rodando por baixo dos panos.**

### ❌ Como NÃO fazer (Violação do LSP)

Quando uma classe herda de outra (ou implementa uma interface), mas altera drasticamente o comportamento esperado, lançando erros do nada ou ignorando comandos.

```javascript
class Passaro {
    voar() {
        console.log("Batendo as asas e voando!");
    }
}

class Aguia extends Passaro {
    voar() {
        console.log("Voando alto nas montanhas!");
    }
}

// O problema começa aqui:
class Pinguim extends Passaro {
    voar() {
        // Pinguins não voam! O comportamento da classe pai foi quebrado.
        // Quem chamar passaro.voar() aqui vai receber uma quebra (Exception).
        throw new Error("Pinguins não sabem voar!");
    }
}

function iniciarMigracao(passaro) {
    // O sistema espera que TODOS os pássaros voem.
    // Se passar um Pinguim aqui, o sistema cai.
    passaro.voar();
}
```

### ✅ Como FAZER (Aplicando LSP)

O problema não estava no Pinguim, estava na nossa abstração original que assumiu que todo pássaro voa. A solução é refatorar as interfaces/classes para refletir a realidade sem forçar comportamentos irreais.

```javascript
/**
 * 1. Criamos abstrações mais precisas.
 */
class Passaro {
    comer() {
        console.log("Comendo...");
    }
}

// Separamos o comportamento de voar para quem realmente voa
class PassaroVoador extends Passaro {
    voar() {
        console.log("Batendo as asas...");
    }
}

// Separamos o comportamento de nadar
class PassaroNadador extends Passaro {
    nadar() {
        console.log("Nadando na água fria...");
    }
}

/**
 * 2. Agora as heranças fazem sentido e não mentem.
 */
class Aguia extends PassaroVoador {
    voar() {
        console.log("Voando alto nas montanhas!");
    }
}

class Pinguim extends PassaroNadador {
    nadar() {
        console.log("Nadando rápido como um torpedo!");
    }
}

function iniciarMigracaoPelosAres(passaroVoador) {
    // Agora o sistema tem garantia total:
    // Ele só aceita quem herda de PassaroVoador. O sistema nunca mais vai quebrar.
    passaroVoador.voar();
}
```

## ## 4. ISP - Interface Segregation Principle (Princípio da Segregação da Interface)

> *"Uma classe não deve ser forçada a implementar interfaces e métodos que ela não vai utilizar."*

### 💡 O Conceito (I)

Imagine um **Controle Remoto Universal** com 100 botões (configurar satélite, ajustar cor do LED, parear bluetooth). Se você der esse controle para uma pessoa que só quer ligar a TV e mudar de canal, 98 botões serão inúteis e só vão causar confusão.

No código, criar "Interfaces Gordas" (cheias de métodos) força as classes a implementarem funções vazias ou que lançam erros, sujando o código e violando a regra de que as coisas devem ser específicas.

A regra de ouro é: **É muito melhor ter várias interfaces pequenas e específicas do que uma única interface gigante e genérica.**

### ❌ Como NÃO fazer (Violação do ISP)

Imagine que você tem um contrato geral para interagir com o Banco de Dados. Ele obriga que todo mundo que assine esse contrato saiba ler, escrever e deletar dados.
Mas e se você tiver um robô (script) que gera relatórios de métricas e **só precisa ler** os dados? Ele será forçado a ter métodos perigosos (como deletar) sem necessidade.

```javascript
/**
 * Interface Gorda: Força todo mundo a implementar os 4 métodos.
 */
class RepositorioBancoDeDados {
    lerDados() { throw new Error("A implementar"); }
    salvarDados(dados) { throw new Error("A implementar"); }
    deletarDados(id) { throw new Error("A implementar"); }
}

/**
 * O robô de métricas é forçado a implementar 'salvar' e 'deletar',
 * mesmo sendo um script de leitura (Read-Only).
 */
class GeradorDeMetricas extends RepositorioBancoDeDados {
    lerDados() {
        console.log("Lendo dados de acessos...");
    }

    // Código inútil apenas para satisfazer o contrato da classe pai
    salvarDados(dados) {
        throw new Error("Eu não salvo dados, só leio!");
    }

    // Perigoso: E se alguém chamar isso por engano?
    deletarDados(id) {
        throw new Error("Eu não deleto dados, sou apenas de leitura!");
    }
}
```

### ✅ Como FAZER (Aplicando ISP)

Nós quebramos a interface gigante em interfaces menores, focadas por papel. Assim, as classes assinam apenas os contratos que realmente precisam cumprir.

```javascript
/**
 * 1. Interfaces Pequenas e Específicas (Segregadas)
 */
class LeitorDeDados {
    lerDados() { throw new Error("A implementar"); }
}

class EscritorDeDados {
    salvarDados(dados) { throw new Error("A implementar"); }
    deletarDados(id) { throw new Error("A implementar"); }
}

/**
 * 2. As implementações agora são limpas e assinam só o que precisam.
 */
class GeradorDeMetricas extends LeitorDeDados {
    // Fica limpo! Ele só precisa saber ler. Não tem métodos inúteis.
    lerDados() {
        console.log("Lendo dados de acessos de forma segura...");
    }
}

/**
 * Se uma classe precisar fazer os dois (ler e escrever),
 * ela simplesmente assina os dois contratos (Múltipla herança de interface).
 */
class APIUsuarios extends LeitorDeDados, EscritorDeDados {
    lerDados() { console.log("Lendo usuário..."); }
    salvarDados(dados) { console.log("Salvando usuário..."); }
    deletarDados(id) { console.log("Deletando usuário..."); }
}
```

## 5. DIP - Dependency Inversion Principle (Princípio da Inversão de Dependência)

> *"Módulos de alto nível não devem depender de módulos de baixo nível. Ambos devem depender de abstrações. Abstrações não devem depender de detalhes. Detalhes devem depender de abstrações."*

### 💡 O Conceito

Pense na **Tomada da sua casa**.

Quando você compra uma TV nova (Módulo de Alto Nível), você não liga os fios dela direto no poste da rua (Módulo de Baixo Nível). A TV não precisa saber se a energia vem de uma usina hidrelétrica, solar ou nuclear.
Ela apenas se conecta ao **padrão da tomada** (A Abstração). Se a cidade trocar a fonte de energia amanhã, a sua TV continua funcionando perfeitamente.

No código, **Inversão de Dependência** significa que as nossas regras de negócio (Alto Nível) não devem instanciar diretamente ferramentas de infraestrutura como Bancos de Dados ou APIs externas (Baixo Nível). Elas devem depender de "contratos" (Interfaces).

[Image of Dependency Inversion Principle UML diagram]

### ❌ Como NÃO fazer (Violação do DIP)

A classe de negócio cria a dependência de infraestrutura diretamente dentro dela. Ela fica "acoplada" (presa) àquela tecnologia específica.

```javascript
class RelatorioDeVendas {
    constructor() {
        // Ruim: O módulo de negócio está preso ao MySQL!
        // Se amanhã quisermos ler de um arquivo Parquet ou CSV,
        // teremos que alterar o coração da regra de negócio.
        this.bancoDeDados = new MySQLDatabase();
    }

    gerar() {
        let dados = this.bancoDeDados.buscarVendas();
        console.log("Gerando relatório com os dados:", dados);
    }
}
```

### ✅ Como FAZER (Aplicando DIP com Injeção de Dependência)

Nós criamos uma abstração (a "Tomada") e "injetamos" a dependência de fora para dentro (via construtor). O módulo de negócio confia na abstração e não sabe qual é o banco real.

```javascript
/**
 * 1. A Abstração (A Tomada)
 */
class FonteDeDadosInterface {
    buscarVendas() { throw new Error("A implementar"); }
}

/**
 * 2. Os Módulos de Baixo Nível (A Energia)
 * Eles se adaptam à tomada.
 */
class BancoMySQL extends FonteDeDadosInterface {
    buscarVendas() { return [{ id: 1, valor: 100 }]; }
}

class ArquivoCSV extends FonteDeDadosInterface {
    buscarVendas() { return [{ id: 2, valor: 250 }]; }
}

/**
 * 3. O Módulo de Alto Nível (A TV)
 * Ele só pede uma "FonteDeDados", não importa qual seja.
 */
class RelatorioDeVendas {
    // Recebemos a dependência de fora (Injeção de Dependência)
    constructor(fonteDeDados) {
        this.fonteDeDados = fonteDeDados;
    }

    gerar() {
        let dados = this.fonteDeDados.buscarVendas();
        console.log("Gerando relatório avançado com:", dados);
    }
}

// Uso na prática:
// Em produção usamos o banco MySQL
const relatorioProd = new RelatorioDeVendas(new BancoMySQL());

// Na equipe de Dados ou em Testes Unitários, passamos um CSV falso!
const relatorioDados = new RelatorioDeVendas(new ArquivoCSV());
```
