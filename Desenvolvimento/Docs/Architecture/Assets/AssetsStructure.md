# Estrutura de Assets — Braziliation

Este documento define a estrutura-alvo dentro de `Desenvolvimento/Assets/`. A organização privilegia leitura rápida no Unity, consistência de arte pixel art, modularidade de gameplay e trabalho assistido por IA.

> Importante: ao mover assets Unity existentes, prefira mover pelo Editor para preservar `.meta` e referências de cenas/prefabs.

---

## Layout Principal

```text
Assets/
├── Animations/
│   └── Menu/
├── Art/
│   ├── Characters/
│   ├── Enemies/
│   ├── Environments/
│   │   └── Blumenau/
│   │       ├── Backgrounds/
│   │       ├── Palettes/
│   │       ├── Props/
│   │       └── Tilesets/
│   ├── Menu/
│   ├── Props/
│   ├── ThirdParty/
│   ├── UI/
│   └── VFX/
├── Audio/
│   ├── Music/
│   └── SFX/
├── Editor/
│   ├── Art/
│   ├── Gameplay/
│   └── Menu/
├── Prefabs/
│   ├── Enemies/
│   ├── Interactables/
│   ├── Player/
│   ├── UI/
│   └── World/
├── Scenes/
│   ├── Bootstrap/
│   ├── Levels/
│   ├── Menus/
│   └── Sandbox/
├── ScriptableObjects/
│   ├── Combat/
│   ├── Enemies/
│   ├── Items/
│   ├── Levels/
│   └── Palettes/
├── Scripts/
│   ├── Build/
│   ├── Combat/
│   ├── Core/
│   ├── Crafting/
│   ├── Enemies/
│   ├── Gameplay/
│   ├── Player/
│   ├── UI/
│   ├── Utils/
│   └── World/
├── Settings/
└── Plugins/
```

---

## Regras por Pasta

### Animations/

Guarda Animation Clips e Animator Controllers organizados por contexto (`Menu/`, e por domínio conforme crescer: `Player/`, `Enemies/`). Spritesheets fonte das animações vivem em `Art/`; aqui ficam apenas os assets de animação do Unity.

### Art/

Guarda todo asset visual final importado no Unity: sprites, tilesets, backgrounds, UI, VFX e spritesheets. **Todo** asset visual entra aqui — as antigas `Assets/Sprites/`, `Assets/UI/` e `Assets/Tilemaps/` na raiz foram removidas em 2026-09-02 por estarem vazias.

- `Characters/`: jogador e NPCs.
- `Enemies/`: inimigos comuns, criaturas e bosses.
- `Environments/{Cidade}/`: assets por região/cidade. Use subpastas `Tilesets`, `Props`, `Backgrounds` e `Palettes`.
- `Menu/`: fundos e elementos visuais específicos de menu.
- `Props/`: props globais reutilizáveis entre regiões.
- `ThirdParty/`: arte **não própria** (ver regras abaixo).
- `UI/`: ícones, molduras, barras, botões e sprites de interface.
- `VFX/`: fumaça, faísca, vapor, impactos e feedbacks visuais.

#### Art/ThirdParty/ — arte de terceiros

Isolada em um único lugar para que a origem seja sempre rastreável e para que qualquer
pacote possa ser removido inteiro quando a arte própria o substituir. Um subdiretório por
pacote (`ThirdParty/{Pacote}/`), contendo obrigatoriamente:

- o **texto de licença original** do pacote, sem alteração;
- um `SOURCES.txt` com URL de origem, licença, procedência arquivo a arquivo e a lista de
  modificações aplicadas;
- entrada correspondente em [`CREDITS.md`](../../../CREDITS.md) (raiz do projeto Unity) e em
  [`indices/assets.md`](../indices/assets.md).

Regras:

- Só entram assets com licença compatível com uso comercial. Prefira CC0; CC-BY exige
  atribuição obrigatória. **Não** aceite CC-BY-NC nem "free for non-commercial".
- Assets de terceiros são **placeholder por padrão**: não seguem a paleta da região nem a
  style-bible, e não contam como entrega de arte no backlog.
- Antes de importar, adeque a densidade ao ADR-004 (32 PPU, 1 tile = 32px). Arte externa
  autorada em 16px normalmente precisa de upscale ×2 nearest para não ficar com metade do
  tamanho de pixel da arte própria na mesma tela.
- Se algum asset for referenciado por código em runtime, ele vive em uma subpasta
  `Resources/` **dentro** do pacote — assim o `SpriteImportPostprocessor` continua valendo
  (o caminho começa com `Assets/Art/`) e o pacote segue removível em bloco.

> Import automático: `Assets/Editor/Art/SpriteImportPostprocessor.cs` força 32 PPU, Filter Point, sem compressão e sem mipmap em toda textura que entrar em `Assets/Art/`. Spritesheets `*_sheet.png` são fatiados automaticamente pelo `SheetAutoSlicer.cs` (Multiple + grid quadrado + pivot bottom-center); o clip/controller é gerado via menu `Assets > Braziliation > Criar Animação do Spritesheet` (`SheetAnimationTool.cs`, saída em `Animations/World/`). Não configure import settings de sprite manualmente, salvo exceção documentada.

### Audio/

Guarda música e efeitos sonoros finais. Use `Music/` e `SFX/` quando o volume crescer.

### Editor/

Guarda ferramentas de editor (scripts que só rodam no Unity Editor). Organize por domínio:

- `Art/`: automação de import de arte (postprocessors, presets).
- `Gameplay/`: utilitários de edição de gameplay.
- `Menu/`: utilitários de edição de menus.

### Prefabs/

Guarda composições reutilizáveis de GameObjects. Prefabs devem viver aqui, não em `Art/`.

- `Player/`: prefab do jogador e variantes.
- `Enemies/`: inimigos e bosses.
- `Interactables/`: portas, totens, alavancas, receptáculos e coletáveis.
- `UI/`: telas, HUDs e widgets reutilizáveis.
- `World/`: hazards, checkpoints, blocos de cenário interativos e kits de level design.

### Scenes/

Organiza cenas por função.

- `Bootstrap/`: inicialização global, services e setup de runtime.
- `Menus/`: menu principal, opções, créditos.
- `Levels/`: fases jogáveis finais ou candidatas.
- `Sandbox/`: testes, protótipos e cenas descartáveis.

### ScriptableObjects/

Guarda dados de design versionáveis: stats, configurações de inimigos, itens, níveis e paletas. Use ScriptableObjects quando designers/IA precisarem ajustar dados sem alterar código.

### Scripts/

Guarda código Unity, organizado por **domínio de sistema** — ver ADR-005. Pastas atuais: `Core/` (infra transversal: service locator, layers, `GameInput`, interfaces), `Gameplay/` (MonoBehaviours de jogo), `Build/` e `Crafting/` (adaptadores Unity dos sistemas homônimos do core puro), `Enemies/` (ScriptableObjects de perfil) e `UI/`.

As pastas reservadas do ADR-003 (`Player/`, `Combat/`, `World/`, `Utils/`) foram removidas em 2026-09-02: ficaram vazias enquanto o código crescia por domínio, e o ADR-003 foi substituído pelo ADR-005. Script novo vai para a pasta do domínio, não do tipo de entidade.

### Settings/ e Plugins/

Pastas especiais ou existentes do Unity. Mantenha como estão, salvo decisão documentada em ADR.

### Pastas legadas e de terceiros

| Pasta | Status |
|-------|--------|
| `Assets/TextMesh Pro/` | Pacote de terceiros — não modificar |
| `Assets/Art/ThirdParty/` | Assets licenciados de terceiros — ver `CREDITS.md` |

> Removidas em 2026-09-02 por estarem vazias ou órfãs: `Assets/Sprites/`, `Assets/UI/` (raiz),
> `Assets/Tilemaps/`, `Assets/Art/Environment/` (singular, legado de `Environments/`) e
> `Assets/_Recovery/`. Não recriar.

---

## Convenções de Nome

Use nomes sem espaços e com prefixo funcional:

| Tipo | Exemplo |
|------|---------|
| Personagem | `chr_edith_idle_sheet.png` |
| Jogador | `chr_player_run_sheet.png` |
| Inimigo | `enm_automato_idle_sheet.png` |
| Tileset | `env_blumenau_clockpunk_tileset.png` |
| Prop | `prop_blumenau_gear_door.png` |
| UI | `ui_health_bar_frame.png` |
| VFX | `vfx_steam_puff_sheet.png` |
| Prefab | `Enemy_Automato.prefab` |
| ScriptableObject | `EnemyStats_Automato.asset` |

---

## Fluxo de Arte

1. Ideia e pesquisa vivem em `Design/Criativo/` e `Design/Pesquisa/`.
2. Conceitos e referências visuais vivem em `Design/ArteConceitual/`; paletas machine-readable em `Design/ArteConceitual/Paletas/*.json`.
3. Fontes editáveis, estudos e material de IA vivem em `Design/ArteFonte/`; specs e sprites programáticos seguem `Design/GuiasDeArte/pipeline-sprites-programaticos.md` usando as ferramentas de `Design/ArteFonte/Ferramentas/`.
4. Regras de estilo vivem em `Design/GuiasDeArte/`.
5. Assets finais exportados entram em `Desenvolvimento/Assets/Art/` (import settings aplicados automaticamente pelo `SpriteImportPostprocessor`).
6. Prefabs montados no Unity entram em `Desenvolvimento/Assets/Prefabs/`.
7. Assets relevantes devem ser registrados em `Docs/Architecture/indices/assets.md`.
