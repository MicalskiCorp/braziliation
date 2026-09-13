# Índice de Assets — Braziliation

> Assets principais referenciados por sistema. Atualizar conforme arte, prefabs, cenas e áudio evoluem.

## Pastas de Arte

| Categoria | Caminho | Uso |
|-----------|---------|-----|
| Personagens | `Assets/Art/Characters/` | Jogador, NPCs e figuras narrativas |
| Inimigos | `Assets/Art/Enemies/` | Criaturas, inimigos comuns e bosses |
| Ambientes — Blumenau | `Assets/Art/Environments/Blumenau/` | Tilesets, props, backgrounds e paletas de Blumenau |
| Ambiente legado | `Assets/Art/Environment/` | Pasta anterior; não usar para assets novos |
| Menu | `Assets/Art/Menu/` | Arte final de telas de menu |
| Props globais | `Assets/Art/Props/` | Objetos reutilizáveis entre regiões |
| UI | `Assets/Art/UI/` | Sprites de interface |
| VFX | `Assets/Art/VFX/` | Efeitos visuais em spritesheet |
| Terceiros | `Assets/Art/ThirdParty/` | Assets de terceiros (placeholder), um subdiretório por pacote + licença e `SOURCES.txt`; créditos em [`CREDITS.md`](../../../CREDITS.md) |

## Prefabs

| Categoria | Caminho | Uso |
|-----------|---------|-----|
| Player | `Assets/Prefabs/Player/` | Prefab do jogador e variantes |
| Enemies | `Assets/Prefabs/Enemies/` | Inimigos e bosses |
| Interactables | `Assets/Prefabs/Interactables/` | Totens, portas, alavancas, receptáculos e coletáveis |
| UI | `Assets/Prefabs/UI/` | HUD, menus e widgets reutilizáveis |
| World | `Assets/Prefabs/World/` | Checkpoints, hazards e blocos reutilizáveis de cenário |

## ScriptableObjects

| Categoria | Caminho | Uso |
|-----------|---------|-----|
| Combat | `Assets/ScriptableObjects/Combat/` | Dados de armas, dano e combate |
| Enemies | `Assets/ScriptableObjects/Enemies/` | Stats e configurações de inimigos |
| Items | `Assets/ScriptableObjects/Items/` | Itens, relíquias, componentes e materiais |
| Levels | `Assets/ScriptableObjects/Levels/` | Configurações por fase/região |
| Palettes | `Assets/ScriptableObjects/Palettes/` | Paletas e referências técnicas de cor |

## Cenas

| Cena/Pasta | Caminho | Descrição |
|------------|---------|-----------|
| Bootstrap | `Assets/Scenes/Bootstrap/` | Inicialização global e serviços |
| Levels | `Assets/Scenes/Levels/` | Fases jogáveis |
| Menus | `Assets/Scenes/Menus/` | Menu principal e telas auxiliares |
| Sandbox | `Assets/Scenes/Sandbox/` | Protótipos e testes |
| DemoGameplay | `Assets/Scenes/DemoGameplay.unity` | Cena jogável atual de demonstração |
| SampleScene | `Assets/Scenes/SampleScene.unity` | Cena padrão/legado |

## Backlog por Asset (fluxo concept art → sprite)

> Rastreia um asset através das 5 etapas descritas em [`pipeline-sprites-programaticos.md`](../../../../Design/GuiasDeArte/pipeline-sprites-programaticos.md#fluxo-completo-da-ideia-ao-sprite-5-etapas). Origem da linha: Passo 1 concluído em `Design/Criativo/TODO.md` (seção "Concept Art Pendente"). Ao completar o Passo 5, mover a linha para "Assets Registrados" abaixo e remover daqui.

| Asset | Ideia (P1) | Concept Art (P2) | Especificação (P3) | Spec JSON (P4) | Sprite (P5) |
|-------|:---:|:---:|:---:|:---:|:---:|
| *(nenhum em andamento)* | | | | | |

Legenda de status por célula: ❌ não iniciado · 🔨 em andamento · ⏸ aguardando aprovação do usuário · ✅ concluído.

## Assets Registrados

> **ADR-004 — re-autoria concluída (2026-07-12):** todos os assets pré-migração foram **re-autorados** para o grid 640×360/32 PPU via `spec_redetail.py` (EPX + textura de material) com crítica visual e gates re-aprovados — não são mais upscale cru. Tamanhos na tabela = originais 1×; no disco estão 2× re-detalhados. Fontes atuais: specs `*.2x.spec.json` nos context packs. Tilesets regenerados com detail pass (`gen_tileset --scale 2`). Frames do menu convertidos ×2 (640×360).

| Asset | Caminho | Fonte | Paleta | Observação |
|-------|---------|-------|--------|------------|
| `prop_blumenau_floodgate_lever.png` | `Assets/Art/Environments/Blumenau/Props/` | Spec JSON em `Design/ArteFonte/IA/ContextPacks/exemplo-prop-comporta-blumenau/` | Blumenau (proposta-inicial) | Prop 32×32 do sistema hídrico; gerado via pipeline programático (2 iterações) |
| `prop_blumenau_floodgate_lever_activate_sheet.png` | `Assets/Art/Environments/Blumenau/Props/` | Specs `_f2`/`_f3` no mesmo context pack | Blumenau (proposta-inicial) | Sheet 96×32, 3 frames de acionamento; requer Sprite Mode Multiple + slicing 32×32 (wiring pendente) |
| `frame_001.png`–`frame_008.png` | `Assets/Art/Menu/Background/Frames/` | — | — | Sequência de 8 frames do fundo animado do menu principal; wiring em `Assets/Editor/Menu/MenuBackgroundSetupEditor.cs` |
| `prop_blumenau_marcador_pilar_{verde,amarelo,vermelho,preto}.png` | `Assets/Art/Environments/Blumenau/Props/` | Specs em `ContextPacks/lote-sistema-hidrico-blumenau/` | Blumenau (aprovada) | 16×16 — 4 estados do rio (rotina/alerta/cheia/saturação) |
| `prop_blumenau_sino_alerta.png` + `_ring_sheet.png` | idem | idem | Blumenau (aprovada) | 16×16 idle + sheet 48×16 (3 frames de badalada) |
| `prop_blumenau_sirene_pneumatica.png` | idem | idem | Blumenau (aprovada) | 16×16 — sirene de alerta em poste |
| `prop_blumenau_sinalizador_torre.png` + `_aceso.png` | idem | idem | Blumenau (aprovada) | 16×32 — farol de torre, estados apagado/aceso |
| `prop_blumenau_lapide_gato.png` | idem | Specs em `ContextPacks/lote-jardim-edith/` | Blumenau (aprovada) | 16×16 — base das 9 lápides nomeadas (SQ-01) |
| `prop_blumenau_estatua_gato.png` | idem | idem | Blumenau (aprovada) | 16×32 — estátua do Jardim de Edith |
| `ui_item_pingente_gato.png` | `Assets/Art/UI/` | idem | Blumenau (aprovada) | 16×16 — item de coleta da SQ-01 (41×) |
| `enm_automato_idle_sheet.png` | `Assets/Art/Enemies/` | Specs em `ContextPacks/enm-automato-abandonado/` | Blumenau (aprovada) | 96×32, 3 frames idle — placeholder do Autômato Abandonado (candidato a inimigo básico da demo) |
| `env_blumenau_{enxaimel,metal,agua}_tileset.png` | `Assets/Art/Environments/Blumenau/Tilesets/` | `gen_tileset.py` seed 42 (manifests em `IA/Outputs/`) | Blumenau (aprovada) | Tiles 16×16 procedurais: enxaimel 4 tipos, metal 3, água/lama 3 × 4 variações |

## Assets de Terceiros (placeholder)

> Arte **não própria**, usada para destravar o desenvolvimento de mecânicas enquanto o pipeline
> próprio produz a arte final. Não segue a paleta de Blumenau nem a style-bible e **não é arte
> definitiva**. Créditos obrigatórios em [`CREDITS.md`](../../../CREDITS.md); procedência arquivo
> a arquivo em `Assets/Art/ThirdParty/Gothicvania/SOURCES.txt`.
>
> Reprodutível por `Design/ArteFonte/Ferramentas/prepare_thirdparty_gothicvania.py` (baixa,
> prepara e reinstala com os mesmos GUIDs). Preparo: upscale ×2 nearest (ADR-004: 32 PPU,
> 1 tile = 32px) + recorte por bbox de união por animação.

| Asset | Caminho | Origem | Licença | Uso |
|-------|---------|--------|---------|-----|
| `chr_placeholder_heroi_idle.png` | `Assets/Art/ThirdParty/Gothicvania/Resources/Demo/` | Gothicvania Patreon's Collection (ansimuz) | CC0 | Sprite do `Player_Demo` — 58×82 (1,81 × 2,56 un), pivot centro-inferior |
| `enm_placeholder_cao_idle.png` | idem | idem | CC0 | Sprite do `Enemy_Demo` — 84×48 (2,62 × 1,50 un), pivot centro-inferior |
| `env_placeholder_chao_tile.png` | idem | idem | CC0 | Tile do `Ground_Demo` — 32×64 (1 × 2 un), pivot no topo, FullRect (exigido pelo `drawMode` Tiled) |
| `env_placeholder_fundo_castelo.png` | idem | idem | CC0 | Fundo estático do `Background_Demo` — 960×608 (30 × 19 un) |
| `chr_placeholder_heroi_{idle,run}_sheet.png` | `Assets/Art/ThirdParty/Gothicvania/Resources/Demo/Sheets/` | idem | CC0 | Sheets 4 e 12 frames, células quadradas, pivot centro-inferior — tocados pelo `SpriteSheetAnimator` |
| `enm_placeholder_cao_{idle,walk}_sheet.png` | idem | idem | CC0 | Sheets 6 e 12 frames, idem |
| `env_placeholder_castelo_tileset.png` | `Assets/Art/ThirdParty/Gothicvania/Environments/` | idem | CC0 | Tileset completo 1664×480 (grid 32×32 após ×2) — para blockout de nível via Tilemap |

## Arte Conceitual e Fontes

| Categoria | Caminho | Uso |
|-----------|---------|-----|
| Conceitos | `Design/ArteConceitual/` | Referências visuais, exploração de estilo e composições |
| Fontes | `Design/ArteFonte/` | Arquivos editáveis, estudos de IA/Aseprite e material de treinamento autorizado |
| Guias | `Design/GuiasDeArte/` | Regras de escala, paleta, animação e pipeline de IA |

---

> `Assets/Sprites/` é legado. Novos sprites devem entrar em `Assets/Art/`.
