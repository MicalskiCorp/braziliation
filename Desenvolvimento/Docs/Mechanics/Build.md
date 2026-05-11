# Mecânica: Build do Personagem — Receptáculos e Identidade

> **Categoria:** Progressão | Core Loop
> **Status:** 📋 Conceito
> **Agente de implementação:** `@GameplayEngineer` (stats, habilidades, exploração) · `@UnityDeveloper` (progressão visual, UI de build)
> **Mecânica relacionada:** [`Crafting.md`](Crafting.md) — como os componentes são criados e instalados

---

## Descrição para o Jogador

O estado atual do personagem é definido pelo que está instalado nos três receptáculos. Cada combinação de componentes gera uma build única que altera aparência, habilidades, acesso a zonas do mundo e relações com NPCs e entidades — transformando o corpo do jogador em parte viva da narrativa.

---

## Filosofia de Build

Os receptáculos não são simples slots de equipamento. Eles representam a **evolução física, biológica e espiritual** do jogador dentro do mundo. A build não é apenas uma escolha de stats — é uma identidade dentro do Braziliation.

Cada peça instalada altera:
- aparência visual do personagem (progressão visual por receptáculo);
- habilidades ativas e passivas disponíveis;
- acesso a zonas e passagens específicas do mundo;
- relações narrativas com NPCs e entidades;
- comportamento do personagem no ambiente.

---

## Os Três Pilares de Build

| Pilar | Receptáculo | Foco de Build |
|-------|-------------|--------------|
| Mecânico | Exoesqueleto dos Trilhos | Força, defesa e utilidade industrial |
| Místico | Capa das Lendas do Mar | Magias, encantamentos e utilidade sobrenatural |
| Biológico | Espinha de Fungo | Habilidades corporais, resistências elementais e utilidade orgânica |

> Como os slots de cada receptáculo funcionam (tipos e compatibilidade) → [`Crafting.md`](Crafting.md)

---

## Expansão de Slots

O jogador encontra **materiais especiais escondidos no mapa** e os entrega a **NPCs específicos** para desbloquear novos slots na build. A expansão representa partes físicas reais do equipamento ou do organismo — não upgrades numéricos abstratos.

| Receptáculo | Material de Expansão | NPC Responsável |
|-------------|---------------------|-----------------|
| Exoesqueleto dos Trilhos | Placas metálicas antigas | Artesãos de Blumenau |
| Capa das Lendas do Mar | Carretéis antigos | Costureiras ritualísticas / Bruxas da Ilha da Magia |
| Espinha de Fungo | Fungos cristalizados | Alquimistas biológicos / Pesquisadores da mata |

### Troca de Itens nos Slots

O jogador pode substituir itens instalados nos slots **livremente**, sem custo. Para isso deve se dirigir a um **totem** localizado em pontos específicos do mapa. O item removido retorna ao inventário do jogador — nenhum item é perdido na troca.

> **TODO de design** — Localização exata dos totens no mapa a ser definida (quantidade, cidades, áreas).

---

## Receptáculos — Fichas de Build

### Exoesqueleto dos Trilhos

- **Pilar:** Mecânico
- **Origem:** entregue ao jogador ao chegar em Blumenau
- **Inspiração cultural:** história industrial e ferroviária de Blumenau e Joinville; trabalhadores que acreditavam que máquinas poderiam superar limitações humanas

**Descrição:** exoesqueleto metálico com estrutura clockpunk — cobre, aço envelhecido, engrenagens aparentes e sistemas ferroviários antigos.

**Habilidades e atributos desbloqueados por slots:**
- aumentos de atributos físicos;
- melhoria de locomoção;
- utilidades gameplay (Exemplo: Visão noturna para  revelar areas, etc...);
- leitura de mecanismos antigos;
- interação com máquinas esquecidas.

**Progressão visual:**
novas placas metálicas surgem → engrenagens ficam aparentes → tubos e pistões são adicionados → visual industrial e imponente.

---

### Capa das Lendas do Mar

- **Pilar:** Místico
- **Inspiração cultural:** bruxas da Ilha da Magia e tradições açorianas do litoral catarinense

**Descrição:** capa ritualística inspirada nas rendas açorianas de Florianópolis. Símbolos bordados funcionam como circuitos mágicos que canalizam energia sobrenatural.

**Habilidades e atributos desbloqueados por slots:**
- magias e feitiços ofensivos;
- encantamentos de resistência e proteção;
- bênçãos para aumentar atributos;
- magias em área;
- utilidades gameplay (Exemplo: Rastreamento de itens e caminhos ocultos).

**Progressão visual:**
novos bordados aparecem → símbolos luminosos se espalham → partes do tecido surgem e flutuam → aparência quase viva e espiritual.

---

### Espinha de Fungo

- **Pilar:** Biológico
- **Inspiração cultural:** Mata Atlântica catarinense, fungos bioluminescentes da região sul, simbiose natureza × sobrevivência

**Descrição:** estrutura simbiótica formada por fungos bioluminescentes das regiões contaminadas. Cresce ao redor da coluna do jogador, conecta-se ao sistema nervoso e reage ao ambiente.

**Habilidades e atributos desbloqueados por slots:**
- melhoria de atributos (Exemplo: regeneração, defesa);
- resistência a veneno e absorção elétrica;
- habilidades inspiradas na fauna local;
- utilidades gameplay (Exemplo: Respiração submersa, para possibilitar entrar em areas)

**Progressão visual:**
fungos crescem nas costas → raízes aparecem na pele → esporos luminosos surgem no ambiente → bioluminescência muda de intensidade conforme a build.

---

## Utilidade na Exploração por Pilar

Os receptáculos desbloqueiam acesso a zonas do mundo que não podem ser acessadas sem o pilar correto.

| Pilar | Capacidades de Exploração |
|-------|--------------------------|
| Mecânico | Abrir portas antigas · ativar máquinas · enxergar mecanismos escondidos · acessar áreas industriais |
| Místico | Ouvir entidades · revelar passagens ocultas · detectar relíquias · enxergar ilusões |
| Biológico | Respirar debaixo d'água · sobreviver em áreas tóxicas · detectar criaturas · acessar regiões contaminadas · encontrar passagens naturais escondidas |

---

## Sinergias Híbridas

Combinações de componentes de pilares diferentes geram efeitos únicos que não existem em builds puras.

> ⚠️ Os exemplos abaixo são **ilustrativos** — representam o padrão de resultado esperado para cada tipo de combinação híbrida, não itens definitivos do jogo.

| Componentes (INPUT) | Resultado na Build (OUTPUT) |
|--------------------|-----------------------------|
| [Componente Mecânico] + [Componente Biológico] | Prótese viva — ex: resistência física + regeneração biológica |
| [Componente Biológico] + [Componente Místico] | Mutação arcana — ex: percepção de entidades + rastros espirituais |
| [Componente Mecânico] + [Componente Místico] | Armadura encantada — ex: força física + proteção sobrenatural |

> Como essas combinações são construídas (inputs, receitas) → [`Crafting.md — Exemplos de Combinações`](Crafting.md#exemplos-de-combinações-lado-input)

---

## Objetivos do Sistema de Build

- transformar builds em identidade visual do jogador;
- criar experimentação entre magia, biologia e mecânica;
- permitir progressão orgânica e descoberta constante;
- fortalecer a imersão narrativa;
- valorizar a cultura catarinense;
- transformar o corpo do jogador em parte viva da narrativa.

---

## Parâmetros de Balanceamento

| Parâmetro | Valor Atual | Faixa Aceitável | Notas |
|-----------|------------|----------------|-------|
| Habilidades por receptáculo (máximo ativo) | *{TODO}* | — | Definir no balanceamento |
| Resistências elementais (escala) | *{TODO}* | — | — |
| Sinergias híbridas únicas mapeadas | *{TODO}* | — | Ver design de itens |
| Estágios de progressão visual por receptáculo | *{TODO}* | 3–5 estágios | — |

---

## Interações com Outras Mecânicas

| Mecânica | Tipo de Interação |
|----------|-----------------|
| [Crafting — Receptáculos](Crafting.md) | Depende — build é o estado resultante do crafting |
| Exploração de mundo | Potencializa — build define quais zonas são acessíveis |
| Combate | Potencializa — habilidades e resistências impactam combate diretamente |
| Sistema de NPCs | Potencializa — builds podem alterar diálogos e relações |
| Narrativa | Potencializa — aparência e habilidades refletem escolhas narrativas |
