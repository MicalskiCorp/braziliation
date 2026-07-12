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
├── Tilemaps/
└── Plugins/
```

---

## Regras por Pasta

### Animations/

Guarda Animation Clips e Animator Controllers organizados por contexto (`Menu/`, e por domínio conforme crescer: `Player/`, `Enemies/`). Spritesheets fonte das animações vivem em `Art/`; aqui ficam apenas os assets de animação do Unity.

### Art/

Guarda todo asset visual final importado no Unity: sprites, tilesets, backgrounds, UI, VFX e spritesheets. `Assets/Sprites/` e `Assets/UI/` (raiz) ficam como legado e não devem receber assets novos; novos sprites entram em `Assets/Art/`.

- `Characters/`: jogador e NPCs.
- `Enemies/`: inimigos comuns, criaturas e bosses.
- `Environments/{Cidade}/`: assets por região/cidade. Use subpastas `Tilesets`, `Props`, `Backgrounds` e `Palettes`.
- `Environment/`: legado da estrutura anterior; novos assets por região devem ir para `Environments/`.
- `Menu/`: fundos e elementos visuais específicos de menu.
- `Props/`: props globais reutilizáveis entre regiões.
- `UI/`: ícones, molduras, barras, botões e sprites de interface.
- `VFX/`: fumaça, faísca, vapor, impactos e feedbacks visuais.

> Import automático: `Assets/Editor/Art/SpriteImportPostprocessor.cs` força 16 PPU, Filter Point, sem compressão e sem mipmap em toda textura que entrar em `Assets/Art/`. Spritesheets `*_sheet.png` são fatiados automaticamente pelo `SheetAutoSlicer.cs` (Multiple + grid quadrado + pivot bottom-center); o clip/controller é gerado via menu `Assets > Braziliation > Criar Animação do Spritesheet` (`SheetAnimationTool.cs`, saída em `Animations/World/`). Não configure import settings de sprite manualmente, salvo exceção documentada.

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

Guarda código Unity. A estrutura atual preserva `Core`, `Crafting`, `Gameplay` e `UI`, e já reserva `Player`, `Enemies`, `Combat`, `World` e `Utils` para novos scripts por domínio. `Build/` guarda scripts de build/CI que precisam viver dentro de Assets.

### Settings/, Plugins/, Tilemaps/

Pastas especiais ou existentes do Unity. Mantenha como estão, salvo decisão documentada em ADR.

### Pastas legadas e de terceiros

| Pasta | Status |
|-------|--------|
| `Assets/Sprites/` | Legado — não receber assets novos; migrar para `Art/` pelo Editor |
| `Assets/UI/` (raiz) | Legado — novos sprites de UI vão para `Art/UI/` |
| `Assets/_Recovery/` | Temporária do Unity — não versionar conteúdo novo nela |
| `Assets/TextMesh Pro/` | Pacote de terceiros — não modificar |

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
