# Tech Debt – Braziliation

Known technical debt, shortcuts, and follow-up work. Use this so agents and the developer don’t forget and so refactors are prioritized.

Format:
- **Item:** Short description
- **Where:** Path or system
- **Why:** Reason it exists or why it’s debt
- **Fix (optional):** Suggested direction

---

## Current items

> Consolidado em 2026-09-02 a partir da auditoria de estrutura. Antes desta data este
> arquivo dizia "None yet" enquanto ~30 itens de dívida viviam no `Docs/TODO.md` e 29
> `TODO` inline no código — o processo existia e não era usado. `TODO.md` é pendência de
> **trabalho planejado**; este arquivo é **atalho que foi tomado** e precisa ser pago.

### Alta

*(nenhum item Alta em aberto — o rebind foi pago em 2026-11-09; montar a tela no menu e os glifos seguem como pendências em `Docs/TODO.md`)*

### Média

- **Item:** `montagem_base.py` pinta contorno uniforme e sombreia por faixa horizontal
- **Where:** `Design/ArteFonte/Ferramentas/montagem_base.py` (`outline()`, `shade()`) — usado pelo Autômato e pelo Soldado Clérico
- **Why:** A style-bible pede "outline não uniforme" (escuro na sombra, sutil na luz), e o `outline()` pinta `"1"` em toda a borda; o `shade()` decide a banda só pela posição do pixel na linha, então topo e base de uma peça não diferem por luz. Achado na análise do PixelFX (ADR-016).
- **Fix:** não corrigir. Personagem novo nasce no `pxfx` (contorno seletivo, 4 tons por normal · luz), e prop segue pela spec de chars (ADR-016). Revisto pelo @TechLead em 2026-11-09: só os dois `montagem.py` (Autômato e Soldado Clérico) importam o `montagem_base`, e nenhum prop o usa. Quando o usuário refizer os dois personagens no `pxfx` (ADR-016), apagar o `montagem_base.py`, os dois `montagem.py` e a linha do `catalogo.md`. Isso paga também a parte do `montagem_base` na dívida das rampas antigas (Baixa).

- **Item:** Ruleset WFC de Blumenau é primeira versão — lâmina d'água serrilhada
- **Where:** `Design/ArteFonte/Ferramentas/rulesets/blumenau-fachada.json`
- **Why:** A adjacência escrita à mão deixa `agua`/`lama` variarem de altura livremente, então
  a superfície da água sobe e desce em degraus em vez de ser plana. O ruleset **derivado**
  (`--learn` a partir de `exemplos/blumenau-fachada-exemplo.json`) já sai com água plana, mas
  produz prédios estreitos demais — porque o exemplo desenhado é estreito.
- **Teste de 2026-11-09 (@TechLead):** redesenhar o exemplo **não resolve**. Com um exemplo de prédios de 4 a 7 colunas, o
  `--learn` segue gerando prédios de 1 a 3 (`Design/ArteFonte/IA/Testes/wfc-fachada-v2/`). A adjacência aprendida é binária
  (quem pode encostar em quem), e nenhum par impõe largura mínima: o WFC abre e fecha prédio em qualquer coluna. Achado junto:
  a água sai plana, mas em altura solta — na seed 7 ela sobe até o topo e o mapa vira só água e lama.
- **Fix:** decisão do responsável entre (a) tiles de borda de prédio (lateral esquerda e direita, como as bordas do
  `gen_tileset.py`), com o céu encostando só nelas — largura mínima 2, pouca garantia acima disso; (b) WFC por padrões N×N
  (modelo *overlapping*), que aprende largura e altura do exemplo — troca maior no `gen_map_wfc.py`; (c) duas etapas, com um
  leiaute de prédios (posição, largura, altura) sorteado por regra e o WFC só preenchendo cada fachada — o mais controlável
  para desenho de nível. Em qualquer opção, a linha d'água vira restrição de linha fixa no ruleset (`water_row`). Recomendação
  do @TechLead: (c). → `Docs/TODO.md` › UI e arte (`@SpriteArtist`).

- **Item:** `PlayerInventory` é uma lista sem capacidade, categorias nem persistência
- **Where:** `Assets/Scripts/Core/PlayerInventory.cs` (TODO inline)
- **Why:** stub para destravar crafting.
- **Fix:** → `Docs/TODO.md` › Gameplay, inventário completo (`@SystemsDeveloper` + `@GameplayEngineer`, ⏸ números de Crafting). Definir regras no GDD antes de implementar; inventário não entra no save hoje.

- **Item:** `BuildProgressionView` aplica os três arrays de estágio no mesmo `SpriteRenderer`
- **Where:** `Assets/Scripts/UI/BuildProgressionView.cs` (comentário no fim de `UpdateVisuals`)
- **Why:** exoesqueleto, capa e espinha têm arrays de sprite separados, mas são aplicados em
  sequência no único renderer do personagem — na prática o último `AplicarSprite` vence e os
  dois primeiros não aparecem. Funciona como placeholder enquanto o personagem é um sprite só.
- **Fix:** → `Docs/TODO.md` › UI e arte, `BuildProgressionView` com um renderer por parte (`@UnityDeveloper`, ⏸). Lá estão os
  renderers por parte e o sheet por parte no `pxfx`, sincronizado ao do corpo. Depende da decisão dos estágios visuais
  em «Parâmetros numéricos de Build» (`Docs/TODO.md` › Decisões de design) e da arte em partes.

### Baixa

- **Item:** Rampas de material anteriores à paleta de 32 continuam repetindo degrau ou emprestando cor de outro material
- **Where:** `Design/ArteFonte/Ferramentas/montagem_base.py` (`LIGAS` bronze `6·7·8·8` e prata `3·4·5·5`, `BASE_RAMPS` cobre `1·9·C·C`) · `ContextPacks/enm-soldado-clerico/montagem.py` (`esmalte` `2·4·5·D`, `clero` `1·G·9·C`, `loden` `1·2·E·E`, `meia` `2·C·D·D`) · mapas fixos de textura do `spec_redetail.py` e do `gen_tileset.py` (`claro`/`escuro`), que só conhecem as keys `1`-`G`
- **Why:** A paleta de Blumenau ganhou 16 cores de rampa em 2026-11-05 (keys `H`-`Y`, rampas por nome no bloco `"rampas"` do `blumenau.json`). Por decisão do usuário, as rampas antigas **não** foram trocadas: o Autômato e o Soldado Clérico estão aprovados, e regerar com rampa nova mudaria os PNGs entregues.
- **Fix:** Trocar pela rampa nomeada do `palette-guide.md` (invertida, porque o `montagem_base` pede escuro → claro) **só quando o asset for re-autorado** — e os dois personagens já vão ser refeitos no `pxfx` (item do `montagem_base` acima). Os mapas `claro`/`escuro` ganham as keys novas quando um tile ou spec de prop usar cor de rampa. Atenção também ao `pixelize.py`: ele quantiza para as 32 cores, então um concept sem gente pode cair em tom de pele — conferir no gate e, se acontecer, dar a ele um filtro por rampa.

---

*QA Engineer and Tech Lead can add items when reviewing code or after refactors. Remove or mark “Done” when addressed.*
