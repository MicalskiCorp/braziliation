# Mecânica: Sistema de Crafting — Receptáculos

> **Categoria:** Core Loop
> **Status:** 📋 Conceito
> **Agente de implementação:** `@GameplayEngineer` (mecânicas) · `@SystemsDeveloper` (modelos C#) · `@UnityDeveloper` (UI de crafting)
> **Mecânica relacionada:** [`Build.md`](Build.md) — o que os itens instalados fazem ao personagem

---

## Descrição para o Jogador

O jogador coleta componentes espalhados pelo mundo, leva-os até uma **mesa de crafting** nas cidades principais e combina dois de cada vez para criar itens. Esses itens são então instalados nos slots dos três receptáculos, definindo a build do personagem — as consequências dessa instalação estão documentadas em [`Build.md`](Build.md).

---

## Contexto do Mundo

Braziliation se passa em Santa Catarina, 500 anos após uma catástrofe nuclear. O evento despertou magia, lendas urbanas, criaturas folclóricas e manifestações sobrenaturais. O mundo combina ruínas industriais, flora fluorescente e símbolos místicos em três pilares visuais e culturais:

| Pilar | Estética |
|-------|----------|
| **Mecânico** | Máquinas enferrujadas, clockpunk, cobre oxidado, engrenagens, motores rústicos |
| **Biológico** | Flora e fauna mutadas, fungos bioluminescentes, raízes rompendo concreto, deformações corporais |
| **Místico** | Símbolos mágicos, runas bordadas, aura luminosa, relíquias ancestrais, lendas catarinenses |

---

## Filosofia do Sistema

O crafting é o eixo de progressão material do jogo. Coletar componentes, entender compatibilidades e instalar peças nos receptáculos é o processo — não o destino. O resultado dessa instalação (identidade visual, habilidades, acesso ao mundo) vive no sistema de **Build** ([`Build.md`](Build.md)).

---

## Componentes

Componentes são os materiais brutos do sistema de crafting. Não possuem efeito ao ser equipados diretamente — precisam ser combinados na mesa para gerar um item utilizável.

### Como obtê-los

| Fonte | Detalhe |
|-------|---------|
| Exploração | Encontrados em locais específicos do mapa (baús, ruínas, áreas secretas) |
| Compra com NPCs | Mercadores e artesãos nas cidades vendem componentes de tipos variados |
| Drop de monstros | Inimigos possuem chance percentual de dropar componentes ao serem derrotados |

> A definição de quais componentes existem, seus nomes, tipos e taxas de drop é um **TODO de design** — a ser detalhado no catálogo de itens.

---

## Visão Geral dos Receptáculos

Os três receptáculos são os contêineres físicos do crafting. Cada um possui slots de um tipo específico:

| Pilar | Receptáculo | Tipo de Slot |
|-------|-------------|-------------|
| Mecânico | Exoesqueleto dos Trilhos | Slots mecânicos |
| Místico | Capa das Lendas do Mar | Slots místicos |
| Biológico | Espinha de Fungo | Slots biológicos |

> Fichas detalhadas de cada receptáculo (habilidades, progressão visual, exploração) → [`Build.md`](Build.md)

---

## Regras de Crafting

| Regra | Detalhe |
|-------|---------|
| Combinação livre entre pilares | Componentes mecânicos, biológicos e místicos podem ser combinados |
| Slots por receptáculo | Cada receptáculo possui slots próprios — não compartilhados |
| Compatibilidade de slot | Cada slot aceita itens que contenham o tipo do receptáculo. Itens híbridos são compatíveis com todos os slots dos seus tipos — o efeito produzido varia conforme o tipo do slot receptor |
| Builds híbridas | Componentes de pilares diferentes gerão itens com tipagem híbrida |
| Sinergias ocultas | Certas combinações desbloqueiam efeitos únicos descobertos por experimentação |
| Progressão por exploração | O jogador descobre sinergias explorando e experimentando |

---

## Mesa de Crafting

A mesa de crafting é o ponto central de criação de itens, encontrada nas **cidades principais** do jogo. O jogador insere **sempre 2 entradas** (componentes ou itens já criados) — não é possível craftar com apenas 1. A mesa resolve o resultado conforme as tipagens envolvidas.

> A lore por trás da origem e funcionamento das mesas é um **TODO narrativo** — a ser detalhado futuramente pelo `@GameCreative`.

### Regras da Mesa

| Situação | Resultado |
|----------|-----------|
| 2 componentes do mesmo tipo (ex: Mecânico + Mecânico) | Item puro — tipagem única, efeito potencializado |
| 2 componentes de tipos diferentes (ex: Mecânico + Biológico) | Item híbrido — carrega os dois tipos |
| Item híbrido (2 tipos) + componente de 3º tipo | Item de 2 tipos — o 3º tipo é somado ao tipo do componente; qual dos dois tipos do híbrido acompanha é definido por **sorteio 50/50** no momento do craft |

### Tipagem do Item Gerado

O item resultante carrega **os tipos dos componentes usados**. Essa tipagem define em quais slots da build o item pode ser encaixado e qual efeito ele produz ao ser instalado:

| Tipagem do Item | Slots compatíveis | Efeito ao instalar |
|----------------|------------------|--------------------|
| Puro Mecânico | Slot Mecânico | Efeito mecânico completo |
| Puro Místico | Slot Místico | Efeito místico completo |
| Puro Biológico | Slot Biológico | Efeito biológico completo |
| Híbrido Mecânico × Biológico | Slot Mecânico **ou** Slot Biológico | Efeito varia conforme o slot onde é instalado |
| Híbrido Mecânico × Místico | Slot Mecânico **ou** Slot Místico | Efeito varia conforme o slot onde é instalado |
| Híbrido Biológico × Místico | Slot Biológico **ou** Slot Místico | Efeito varia conforme o slot onde é instalado |

> Sinergias e efeitos concretos de cada item instalado → [`Build.md`](Build.md)

---

> Expansão de slots (via NPCs) → [`Build.md — Expansão de Slots`](Build.md#expansão-de-slots)

---

## Exemplos de Combinações (lado INPUT)

> O *resultado* dessas combinações no personagem está documentado em [`Build.md — Sinergias Híbridas`](Build.md#sinergias-híbridas).

| Componentes combinados | Tipo de combinação |
|-----------------------|-------------------|
| [Componente Mecânico] + [Componente Biológico] | Híbrida: Mecânico × Biológico |
| [Componente Biológico] + [Componente Místico] | Híbrida: Biológico × Místico |
| [Componente Mecânico] + [Componente Místico] | Híbrida: Mecânico × Místico |

---

## Parâmetros de Balanceamento

| Parâmetro | Valor Atual | Faixa Aceitável | Notas |
|-----------|------------|----------------|-------|
| Slots iniciais por receptáculo | *(a definir)* | 2–4 | A definir no balanceamento |
| Slots máximos por receptáculo | *(a definir)* | 4–8 | Após todas as expansões |
| Número de expansões possíveis | *(a definir)* | 2–4 por receptáculo | — |
| Combinações híbridas únicas mapeadas | *(a definir)* | — | Ver design de itens |

---

## Interações com Outras Mecânicas

| Mecânica | Tipo de Interação |
|----------|-----------------|
| [Build do Personagem](Build.md) | Depende — crafting alimenta o sistema de build |
| Exploração de mundo | Depende — componentes são encontrados via exploração |
| Sistema de NPCs | Depende — expansão de slots requer interação com NPCs |
| Narrativa | Potencializa — itens carregam fragmentos de lore do mundo |
