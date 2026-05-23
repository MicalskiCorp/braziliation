# Blumenau — Igreja Luterana Matriz e Cemitério Histórico

> **Tipo:** Feature — Área + Linha de Quests
> **Status:** 📋 Planejado
> **Sistema(s) envolvido(s):** Diálogo/NPC, Exploração, Sistema Hídrico
> **Prioridade:** Alta
> **Referência criativa:** [`Design/Criativo/Estados/SantaCatarina/cidades/Blumenau/index.md`](../../../../../Design/Criativo/Estados/SantaCatarina/cidades/Blumenau/index.md)

---

## Descrição

Igreja Luterana Matriz no alto do morro, com cemitério histórico como área de dungeon. Ponto de entrada da linha de quests do NPC Hermann Baumgarten — jornalista fundador do *Blumenauer-Zeitung*, enterrado vivo por catalepsia e reanimado como testemunha undead do poder clerical.

---

## Mapa / Área

- **Tipo de espaço:** Área exterior a céu aberto + interior da igreja + dungeon subterrânea (cemitério com porões)
- **Ligações:** Rua das Palmeiras → entrada do cemitério → interior da igreja → túmulos → porão cripta
- **Posição no mapa:** Alto do morro — vista estratégica da cidade, visível de outros mapas como ponto de referência
- **Atmosfera:** Horror físico e íntimo — sepulturas expostas, terra remexida, caixões arranhados, ausência total de luz artificial

### Layout de Referência

```
[Rua das Palmeiras]
      ↓
[Portão do Cemitério] → [Área dos túmulos — dungeon exterior]
      ↓                          ↓
[Fachada da Igreja]    [Túmulo de Hermann ← batidas abafadas]
      ↓
[Interior — nave]
      ↓
[Cripta / porão]
```

---

## Mecânicas Envolvidas

### Gatilho de Descoberta — Batidas do Túmulo
- O jogador ouve sons abafados de batidas vindas da terra ao entrar no cemitério
- Quanto mais o jogador se aproxima do túmulo correto, mais nítidas e urgentes as batidas ficam
- **Sistema de áudio posicional:** intensidade do som escala com a proximidade do túmulo de Hermann

### Encontro com Hermann
- Ao interagir com o túmulo, caixão é aberto — Hermann emerge como NPC undead preservado de forma anormal
- Sua condição: segunda catalepsia durante o enterro verdadeiro → sepultado vivo → morto após → reanimado pela ecatombe
- Estado atual: testemunha, jornalista, memória viva da cidade que o clero tentou apagar

### Mecânica Clerical — "Confirmação de Morte"
- Lore sistêmico: o alto clero declara legalmente quem está morto — quem é declarado é enterrado, vivo ou não
- Hermann foi um dos primeiros a sofrer isso; suas missões revelam outros casos ao longo do jogo
- **Impacto no gameplay:** algumas missões de Hermann exigem encontrar outros "declarados mortos" espalhados pela cidade

### Exploração do Cemitério (Dungeon)
- Caixões que se movem por baixo da terra
- Cordas de sineta conectadas a mãos enterradas — ao tocar a corda, uma mão emerge
- Terra remexida indica possibilidade de escavar (ação contextual) para encontrar itens, cartas ou NPCs enterrados
- Risco: inimigos emergem de túmulos ao escavar o lugar errado

---

## Personagens / NPCs

### Hermann Baumgarten *(undead preservado)*
- **Papel:** NPC de quest principal, fonte de lore sobre o alto clero
- **Local:** Seu túmulo, cemitério histórico da Igreja Luterana
- **Personalidade:** Jornalista rigoroso, observador, movido pela necessidade de testemunhar e denunciar — mesmo morto
- **Linha de diálogo inicial:** Toca o caixão por dentro antes de emergir; primeiras palavras são datas e nomes — o que ele memorizou para não esquecer
- **Quest chain:** Missões de Hermann começam e se resolvem a partir deste mapa, mas seus desdobramentos conduzem ao centro clerical da cidade (Igreja Matriz)
- **Conexão narrativa:** Hermann conhecia Edith Gaertner — pode mencionar o Jardim de Edith como lugar seguro

### Cléricos Guardas *(inimigos patrulheiros)*
- **Tipo:** `Soldado Mercenário Clérico`
- **Comportamento:** Patrulham a área ao redor da igreja, reagem a sons (batidas do cemitério os alertam se o volume escalar demais)

---

## Itens / Relíquias

| Item | Tipo | Como Obter | Efeito |
|------|------|-----------|--------|
| Diário de Hermann — Vol. 1 | Lore / Key Item | Escavar área marcada no cemitério | Revela nomes de "declarados mortos" pelo clero |
| Chave da Cripta Luterana | Key Item | Recebida de Hermann após primeira conversa | Abre o porão da cripta sob a nave |
| Sineta de Túmulo | Consumível | Encontrado preso em mão enterrada | Soa ao usar — revela túmulos com NPCs vivos escondidos |

---

## Dependências

| Feature / Sistema | Tipo | Arquivo |
|-------------------|------|---------|
| Sistema Hídrico de Blumenau | Usa — cota de alerta bloqueia rota de acesso norte | [Blumenau-SistemaHidrico.md](Blumenau-SistemaHidrico.md) |
| Igreja Matriz do Centro | Estende — missões de Hermann terminam lá | [Blumenau-IgrejaMatriz.md](Blumenau-IgrejaMatriz.md) |
| Mausoléu do Fundador | Referência de lore — Hermann conhecia o fundador | [Blumenau-MausoleumFundador.md](Blumenau-MausoleumFundador.md) |
| Jardim de Edith | Referência de lore cruzada — Hermann/Edith | [Blumenau-JardimEdith.md](Blumenau-JardimEdith.md) |

---

## Critérios de Aceitação

| # | Critério | Testável? |
|---|----------|-----------|
| 1 | Jogador ouve batidas abafadas ao entrar no cemitério | Sim |
| 2 | Intensidade do áudio aumenta ao se aproximar do túmulo correto | Sim |
| 3 | Hermann emerge ao interagir com o túmulo correto | Sim |
| 4 | Mechânica de sineta revela túmulos com NPCs enterrados | Sim |
| 5 | Quest chain de Hermann referencia a Igreja Matriz como próximo destino | Sim |
| 6 | Cléricos patrulheiros reagem a sons de alta intensidade no cemitério | Sim |

---

## TODOs de Implementação

### `@GameplayEngineer`
| Tarefa | Prioridade |
|--------|-----------|
| Implementar sistema de áudio posicional para batidas do túmulo (escala com proximidade) | Alta |
| Implementar mecânica de escavação com risco de inimigo emergente | Alta |
| Implementar comportamento de NPC Hermann (undead, diálogos, quest chain) | Alta |
| Implementar cordas de sineta com trigger de mão emergente | Média |

### `@UnityDeveloper`
| Tarefa | Prioridade |
|--------|-----------|
| Criar cena da Igreja Luterana + cemitério exterior | Alta |
| Criar cena do interior da nave + cripta | Alta |
| Layout dos túmulos com marcadores de escavação e sinetas | Média |

### `@SystemsDeveloper`
| Tarefa | Prioridade |
|--------|-----------|
| Modelo de dados: NPC Hermann com estado de quest chain | Alta |
| Sistema de "declarados mortos" — lista de NPCs com estado enterrado/resgatado | Média |

---

## Histórico

| Data | Alteração |
|------|-----------|
| 2026-05-17 | Criado — handoff do @GameCreative processado pelo @GameArchitect |
