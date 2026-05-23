# Blumenau — Igreja Matriz do Centro

> **Tipo:** Feature — Área + Horror Social + Infiltração Política
> **Status:** 📋 Planejado
> **Sistema(s) envolvido(s):** Exploração, Diálogo/NPC, Sistema Hídrico
> **Prioridade:** Alta
> **Referência criativa:** [`Design/Criativo/Estados/SantaCatarina/cidades/Blumenau/index.md`](../../../../../Design/Criativo/Estados/SantaCatarina/cidades/Blumenau/index.md)

---

## Descrição

Sede do alto clero e centro ritual do poder religioso em Die Unterwelt. Área de missão política e infiltração, com catacumbas abaixo do altar contendo os sepultados privilegiados da elite — o horror social de *Podres de Ricos*: a morte como distinção de classe, arquivos de poder enterrados literalmente sob a pedra.

---

## Mapa / Área

- **Tipo de espaço:** Interior monumental (nave + altar + sacristia) + catacumbas subterrâneas + túneis de conexão
- **Posição:** Centro da cidade, posição dominante — visível de múltiplos pontos, símbolo de autoridade e vigilância
- **Conexões:**
  - Túneis conectam ao Teatro Carlos Gomes (mercado negro)
  - Túneis conectam ao *Unterwasser-Gang* (passagem subaquática rumo à Florianópolis)
  - Missões de Hermann Baumgarten terminam ou têm desdobramentos aqui

### Layout de Referência

```
[Praça Central / entrada]
        ↓
[Nave principal] → [Sacristia / sala do clero]
        ↓
[Altar] → [Acesso selado às catacumbas] (key item necessário)
        ↓
[Catacumbas — Nível 1: jazigos das famílias influentes]
        ↓
[Catacumbas — Nível 2: arquivo dos segredos / conexão túneis]
        ↓
[Cruzamento de túneis] → [Teatro Carlos Gomes] / [Unterwasser-Gang]
```

---

## Mecânicas Envolvidas

### Horror Social — *Podres de Ricos*
- **Contraste com o cemitério luterano:** o cemitério popular foi deslocado para fora do centro; na Matriz permaneceram apenas as sepulturas dos ricos e poderosos
- **Leitura gameplay:** o jogador percebe que quanto mais prestígio a família, mais fundo está enterrada — e quanto mais fundo vai, mais sombrios os segredos encontrados
- **Mecânica de investigação:** documentos, retratos adulterados, brasões e decretos de posse escondidos nos jazigos revelam reescrita da história da cidade

### Infiltração Política
- **Estrutura de facções:** o alto clero opera aqui como poder central — decisões, punições, decretos e alianças são administrados da Matriz
- **Mecânica de disfarce/infiltração:** o jogador pode tentar passar pelo interior sem confronto direto usando roupas de peregrino ou documentos roubados
- **Eventos de encontro:** cerimônias encenadas como rituais religiosos escondem julgamentos políticos e punições

### Catacumbas — Arquivo Enterrado
- **Segredos:** livros de linhagem, retratos alterados, decretos de posse e documentos reescritos após enchentes, censura e reorganizações de poder
- **Itens de lore:** cada jazigo privilegiado contém fragmento da história oficial adulterada — coletar todos revela a narrativa real da fundação
- **Perigo:** sacerdotes mortos-vivos reativados pelo éter das catacumbas patrulham os níveis mais profundos

### Conexão com o *Unterwasser-Gang*
- A saída do túnel rumo à Florianópolis tem entrada nos subterrâneos da Matriz
- Câmara do arquivo do alto clero — registros de "declarados mortos", lista de túneis, brasão duplicado (aparece também em Florianópolis)

---

## Personagens / NPCs

### Arcebispo Vogt *(boss político, não combate)*
- **Papel:** Líder do alto clero, antagonista político central de Blumenau
- **Local:** Sacristia — câmara privada acima das catacumbas
- **Mecânica:** NPC de negociação/confronto, não boss de combate direto — o jogador pode aliá-lo, confrontá-lo ou expô-lo via documentos das catacumbas
- **Alinhamento com o Teatro:** Vogt possui camarote no Teatro Carlos Gomes e usa o espaço para acordos privados

### Família Köhler *(facção aristocrata — interação múltipla)*
- Família sepultada nas catacumbas de Nível 1; membros vivos frequentam as cerimônias como poder paralelo ao clero
- Podem ser aliados ou inimigos dependendo das escolhas do jogador

### Sacerdotes Mortos-Vivos *(inimigos — catacumbas profundas)*
- **Tipo:** Variante clerical do `Figura Mutante com Partes Mecânicas`
- **Comportamento:** Patrulham em silêncio, reagem a luz e a documentos sendo abertos (alertados por mecanismo místico)

---

## Itens / Relíquias

| Item | Tipo | Como Obter | Efeito |
|------|------|-----------|--------|
| Chave das Catacumbas | Key Item | Roubada da sacristia ou recebida de Hermann via quest chain | Abre acesso selado sob o altar |
| Registro de Declarados Mortos | Lore / Key Item | Câmara do arquivo, Nível 2 | Revela lista completa; dá context para quest de Hermann |
| Brasão do Alto Clero | Key Item | Câmara do arquivo | Permite acesso a áreas seladas em Florianópolis |
| Relíquia: Cálice de Vogt | Relíquia *(opcional)* | Confrontar ou subornar Arcebispo Vogt | Abre diálogos especiais com figuras clericais em outras cidades |

---

## Dependências

| Feature / Sistema | Tipo | Arquivo |
|-------------------|------|---------|
| Igreja Luterana Matriz (Hermann) | Requer — quest chain de Hermann chega aqui | [Blumenau-IgrejaLuterana.md](Blumenau-IgrejaLuterana.md) |
| Teatro Carlos Gomes | Conecta — túneis subterrâneos | [Blumenau-TeatroCarlosGomes.md](Blumenau-TeatroCarlosGomes.md) |
| Sistema Hídrico de Blumenau | Usa — inundação das catacumbas em cota de cheia altera rotas internas | [Blumenau-SistemaHidrico.md](Blumenau-SistemaHidrico.md) |
| Mausoléu do Fundador | Lore cruzado — Matriz e Mausoléu formam dualidade de controle narrativo | [Blumenau-MausoleumFundador.md](Blumenau-MausoleumFundador.md) |

---

## Critérios de Aceitação

| # | Critério | Testável? |
|---|----------|-----------|
| 1 | Catacumbas acessíveis apenas com Chave correta (key item) | Sim |
| 2 | Documentos nos jazigos revelam progressivamente a história adulterada da cidade | Sim |
| 3 | Conexão de túnel funcional para Teatro Carlos Gomes | Sim |
| 4 | Câmara do arquivo contém o Registro de Declarados Mortos e Brasão do Alto Clero | Sim |
| 5 | Sacerdotes mortos-vivos patrulham catacumbas profundas e reagem a luz/documentos | Sim |
| 6 | Mecânica de disfarce/infiltração funciona na nave principal | Sim |

---

## TODOs de Implementação

### `@GameplayEngineer`
| Tarefa | Prioridade |
|--------|-----------|
| Implementar sistema de infiltração com disfarce/documentos roubados | Alta |
| Implementar NPC Arcebispo Vogt com árvore de diálogo (negociação/confronto/exposição) | Alta |
| Implementar sacerdotes mortos-vivos com trigger de alerta por luz e interação com documentos | Alta |
| Implementar câmara do arquivo com items de lore progressivos | Média |

### `@UnityDeveloper`
| Tarefa | Prioridade |
|--------|-----------|
| Criar cena da nave + altar + sacristia | Alta |
| Criar cenas das catacumbas (Nível 1 e Nível 2) com layout de jazigos | Alta |
| Conexão de túnel físico (collider/portal) para Teatro Carlos Gomes | Alta |

### `@SystemsDeveloper`
| Tarefa | Prioridade |
|--------|-----------|
| Modelo de dados da facção clerical com estados de aliança/confronto | Alta |
| Sistema de documentos de lore com estado "encontrado/não encontrado" por jazigo | Média |

---

## Histórico

| Data | Alteração |
|------|-----------|
| 2026-05-17 | Criado — handoff do @GameCreative processado pelo @GameArchitect |
