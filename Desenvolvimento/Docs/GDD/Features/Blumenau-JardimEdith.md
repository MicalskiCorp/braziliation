# Blumenau — Jardim de Edith e Side-Quest SQ-01

> **Tipo:** Feature — Área Segura + Side-Quest Colecionável + NPC Espectral
> **Status:** 📋 Planejado
> **Sistema(s) envolvido(s):** Exploração, Coleta/Inventário, Diálogo/NPC, Side-Quests
> **Prioridade:** Alta
> **Referência criativa:** [`Design/Criativo/Estados/SantaCatarina/cidades/Blumenau/index.md`](../../../../../Design/Criativo/Estados/SantaCatarina/cidades/Blumenau/index.md)

---

## Descrição

O Jardim de Edith é o único ponto místico de Die Unterwelt — enclave oculto e seguro dentro da cidade clerical. NPC Edith Gaertner (espectral) inicia a side-quest **SQ-01: Os Gatos de Edith** — coleta de 41 pingentes de gatos espectrais dispersos por toda Santa Catarina. Recompensa: relíquia **Guizo de Edith**. O jardim funciona como save point e ponto de descanso permanente.

---

## Mapa / Área

- **Tipo de espaço:** Área exterior oculta — clareira com vegetação fechada, enclave protegido
- **Acesso:** trilha estreita e escondida na vegetação, descoberta ao seguir um gato espectral
- **Posição:** Dentro de Blumenau, mas isolado visualmente — vegetação separa o jardim do ambiente clerical
- **Status de segurança:** Área protegida — o clero **não entra**. Nenhum inimigo patrolha aqui.

### Cenário do Jardim

```
[Abertura oculta na vegetação] ← gato espectral entra aqui
        ↓
[Trilha estreita]
        ↓
[Clareira — Jardim de Edith]
  ┌─────────────────────────────┐
  │  Árvore enorme com banco    │
  │  de raízes (fundo)          │
  │                             │
  │  Estátua de gato (centro)   │
  │                             │
  │  9 lápides de concreto      │
  │  (nomes gravados)           │
  │                             │
  │  Edith sentada na raiz      │
  │  + 9 gatos espectrais       │
  └─────────────────────────────┘
```

---

## NPC — Edith Gaertner *(espectral)*

- **Aparência:** Figura espectral melancólica, sentada na raiz da árvore enorme, chorando silenciosamente. Não ameaçadora.
- **Os 9 gatos presentes:** Pepito, Mirko, Bum, Peterle, Musch, Schnurr, Sittah, Putze e Mirl — sentados nas raízes e no chão ao redor dela
- **Backstory narrado por ela:** atriz, viajante, descendente do fundador — tudo abandonado por amor; preservou a memória da família; separou seus gatos pelo nome
- **Motivação:** os outros 41 gatos, sem lápide, perderam o vínculo e fugiram pelo estado

### Diálogos-Chave

> *"Eles não têm pedra que os segure. Andam perdidos pelo mundo lá fora. Se você os encontrar — você vai saber quando — traga-os de volta para mim."*

> *(Ao final do primeiro diálogo)*  
> *"Ao esmagar, hoje, uma aranha, perguntei-me se me era lícito matar a quem Deus dera, como a mim, parte igual nos dias desta vida."*

### Estados de Edith
- **Antes da quest:** chora silenciosamente; 9 gatos ao redor
- **Com pingentes parciais (1–40):** reconhece o esforço, comenta sobre alguns gatos pelo nome quando entregues
- **Com todos os 41 pingentes:** para de chorar, sorri — 41 gatos espectrais aparecem progressivamente na clareira

---

## Side-Quest SQ-01 — *Os Gatos de Edith*

### Gatilho
1. Jogador avista gato espectral entrando por abertura escondida na vegetação
2. Segue o vulto pela passagem estreita
3. Chega ao jardim e conversa com Edith
4. **Quest ativada** após o diálogo completo

### Mecânica de Coleta

**41 gatos espectrais** espalhados pelo mapa geral (Blumenau e demais cidades de SC):

| Aspecto | Detalhe |
|---------|---------|
| Detecção | Pressionar botão de ação em ponto específico do cenário → gato espectral aparece por instante e some |
| Recolha | Ao sumir, gato deixa cair um **pingente** — medalha pequena com o nome do gato gravado |
| Inventário | Jogador carrega pingentes no inventário (não pesam; não ocupam slot de equipamento) |
| Distribuição | Gatos estão em Blumenau e demais cidades de SC — coleta é progressiva ao longo da campanha |
| Indicação | Nenhum marcador no mapa — descoberta por exploração e atenção a movimentos espectrais |

### Resolução
- **Gatilho de conclusão:** retornar ao jardim com todos os 41 pingentes e entregar a Edith
- **Sequência cinematográfica:** pingentes somem → 41 gatos aparecem progressivamente no jardim → Edith sorri
- **Recompensa:** Edith entrega o **Guizo de Edith**

---

## Itens / Relíquias

| Item | Tipo | Como Obter | Efeito |
|------|------|-----------|--------|
| Pingentes de Gato (×41) | Colecionável (quest) | Exploração — interagir com pontos espalhados por SC | Necessários para resolver SQ-01 |
| Guizo de Edith | Relíquia passiva | Entregar os 41 pingentes a Edith | Suaviza presença hostil de espectros menores; denuncia segredos próximos com leve tilintar |

### Detalhe da Relíquia — Guizo de Edith
- **Tipo:** Passiva permanente equipada
- **Efeito 1 — Suavizar espectros:** espectros menores ficam menos agressivos ou ignorem o jogador em alguns contextos
- **Efeito 2 — Detecção de segredos:** tilintar suave e crescente quando o jogador se aproxima de segredos interativos (passagens ocultas, itens escondidos, NPCs enterrados)
- **Sinergia:** combina com a mecânica da Sineta de Túmulo (Igreja Luterana) — o Guizo amplia o alcance de detecção

### Os 9 Gatos com Lápide (presentes no jardim)
| Nome | Lápide | Estado |
|------|--------|--------|
| Pepito | Sim | Ancorado — presente desde o início |
| Mirko | Sim | Ancorado |
| Bum | Sim | Ancorado |
| Peterle | Sim | Ancorado |
| Musch | Sim | Ancorado |
| Schnurr | Sim | Ancorado |
| Sittah | Sim | Ancorado |
| Putze | Sim | Ancorado |
| Mirl | Sim | Ancorado |

---

## Função Narrativa

- **Contraponto ao Mausoléu:** o jardim de Edith é memória íntima, frágil e afetiva; o Mausoléu é memória oficial, petrificada e monumental
- **Contraste de ritmo:** do mármore seco do Mausoléu para a vegetação úmida do jardim — mudança intencional de tom e intenção
- **Enclave de humanidade:** único espaço de Die Unterwelt onde o clero não tem controle — lembrete de que há algo que o poder institucional não consegue capturar

---

## Dependências

| Feature / Sistema | Tipo | Arquivo |
|-------------------|------|---------|
| Sistema Hídrico de Blumenau | Usa — trilha de acesso pode ser afetada em cota de alerta/cheia | [Blumenau-SistemaHidrico.md](Blumenau-SistemaHidrico.md) |
| Mausoléu do Fundador | Lore cruzado — contraste narrativo direto | [Blumenau-MausoleumFundador.md](Blumenau-MausoleumFundador.md) |
| Igreja Luterana | Lore cruzado — Hermann pode mencionar o jardim como lugar seguro | [Blumenau-IgrejaLuterana.md](Blumenau-IgrejaLuterana.md) |
| Outras cidades de SC | Requer — 41 gatos distribuídos por SC (coordenar com features de outras cidades) | *(features futuras)* |

---

## Critérios de Aceitação

| # | Critério | Testável? |
|---|----------|-----------|
| 1 | Gato espectral visível perto da abertura na vegetação antes de descobrir o jardim | Sim |
| 2 | Jardim não contém inimigos em nenhuma circunstância | Sim |
| 3 | Jardim funciona como save point (trigger de save ao entrar) | Sim |
| 4 | Quest SQ-01 ativada após conversa completa com Edith | Sim |
| 5 | Pingentes são coletados via botão de ação em pontos específicos | Sim |
| 6 | Guizo de Edith concedido ao entregar os 41 pingentes | Sim |
| 7 | Efeito passivo do Guizo (tilintar perto de segredos) funcional | Sim |
| 8 | Sequência cinematográfica com 41 gatos aparecendo ao completar a quest | Sim |

---

## TODOs de Implementação

### `@GameplayEngineer`
| Tarefa | Prioridade |
|--------|-----------|
| Implementar sistema de coleta de pingentes com 41 pontos distribuíveis por mapa | Alta |
| Implementar estado de quest SQ-01 com contador de pingentes coletados | Alta |
| Implementar NPC Edith com estados e diálogos por progresso da quest | Alta |
| Implementar relíquia passiva Guizo de Edith (suavização de espectros + detecção) | Alta |
| Implementar aparição progressiva dos 41 gatos espectrais ao completar | Média |
| Implementar trigger de save point ao entrar no jardim | Média |

### `@UnityDeveloper`
| Tarefa | Prioridade |
|--------|-----------|
| Criar cena do Jardim de Edith (clareira, árvore, 9 lápides, estátua) | Alta |
| Criar visual e animação dos gatos espectrais (vulto etéreo, movimento) | Alta |
| Criar pingente 3D com nome gravado (reutilizável, nome parametrizado) | Média |

### `@SystemsDeveloper`
| Tarefa | Prioridade |
|--------|-----------|
| Modelo de dados: `SQ01State.cs` — lista de 41 slots de pingentes com estado coletado/não-coletado | Alta |
| Modelo de relíquia passiva com callback de detecção de proximidade | Média |

---

## Histórico

| Data | Alteração |
|------|-----------|
| 2026-05-17 | Criado — handoff do @GameCreative processado pelo @GameArchitect |
