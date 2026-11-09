# TODO — Pendências vivas (Desenvolvimento)

> Só o que está **aberto**. Item concluído sai daqui com a data e o commit; o histórico até 2026-09-13 está em [`TODO-arquivo.md`](TODO-arquivo.md).
> **Modelo reativo:** o `@GameArchitect` lê este arquivo no Passo 0. Handoffs do `@GameCreative` chegam na primeira seção e são processados manualmente pelo usuário.
> Status: ❌ não iniciado · 🔨 em andamento · ⏸ bloqueado/aguardando · ✅ concluído (e então arquivar).

---

## Handoffs do @GameCreative

| Feature/Sistema | Referência Criativa | Prioridade | Status |
|----------------|---------------------|-----------|--------|
| *(nenhum pendente — os 7 de Blumenau foram processados em 2026-05-17)* | | | |

---

## Decisões de design — bloqueiam a demo

> Fechar com a skill `fechar-decisao` (gera um DDR em `GDD/Decisoes/`). A premissa vem antes das outras.

| Decisão | Referência | Prioridade | Status |
|---------|-----------|-----------|--------|
| Premissa: pitch, contexto do mundo, protagonista | [`premissa.md`](../../Design/Criativo/Historia/premissa.md) | Alta | ❌ |
| Inimigo básico da demo (comportamento, vida, dano) — o Autômato Abandonado já tem sprite | [`Mechanics/InimigosIA.md`](Mechanics/InimigosIA.md) | Alta | ❌ |
| Arma inicial do jogador (tipo, dano base, animação) | [`GDD/`](GDD/) | Alta | ❌ |
| Parâmetros numéricos de Crafting (slots iniciais/máximos, expansões, combinações híbridas) | [`Mechanics/Crafting.md`](Mechanics/Crafting.md) | Alta | ❌ |
| Parâmetros numéricos de Build (habilidades por receptáculo, resistências, estágios visuais) | [`Mechanics/Build.md`](Mechanics/Build.md) | Alta | ❌ |
| IDs dos materiais especiais de expansão (Artesão/Costureira/Alquimista) | [`Mechanics/Build.md`](Mechanics/Build.md) | Alta | ❌ |
| Regras de compatibilidade e composição final dos itens híbridos | [`Sistemas/Crafting.md`](Architecture/Sistemas/Crafting.md) | Alta | ❌ |
| Política de seed do sorteio híbrido (determinístico × aleatório) | [`Sistemas/Crafting.md`](Architecture/Sistemas/Crafting.md) | Média | ❌ |
| Localização e quantidade de totens | [`Mechanics/Build.md`](Mechanics/Build.md) | Média | ❌ |
| Localização das benzedeiras (uma por região; a casa é o checkpoint?) e do ponto único do Monge João Maria — quando houver mapa | [DDR-001](GDD/Decisoes/DDR-001-benzedeira-npc.md) · [DDR-002](GDD/Decisoes/DDR-002-monge-joao-maria-papel.md) | Média | ❌ |

---

## Unity — validação no Editor e wiring

> Compilação e testes EditMode rodam sem abrir o Editor pela skill `unity-validar`. Os itens abaixo exigem o Editor aberto (ou o MCP `unity`).

| Item | Responsável | Prioridade | Status |
|------|-------------|-----------|--------|
| *(nenhum pendente — o blockout do castelo foi concluído em 2026-11-04)* | | | |

---

## Gameplay

| Item | Responsável | Prioridade | Status |
|------|-------------|-----------|--------|
| Inventário completo: capacidade, categorias por pilar, persistência no save | `@SystemsDeveloper` + `@GameplayEngineer` | Média | ⏸ depende dos números de Crafting |
| Reação a dano (stagger) e percepção por linha de visão | `@GameplayEngineer` | Média | ❌ — ver [`Mechanics/InimigosIA.md`](Mechanics/InimigosIA.md) |
| Perfis de inimigo dos arquétipos de Blumenau (skill `novo-inimigo`) | `@GameCreative` + `@GameplayEngineer` | Média | ⏸ depende do inimigo base |
| Trocar o inimigo placeholder pelo `enm_automato_idle_sheet.png` — o código já trocou (`DemoSceneVisuals` aponta o autômato), falta a cena: o `Enemy_Demo` da `DemoGameplay.unity` ainda guarda sprite e sheets do cão do Gothicvania, e o `DemoSceneBootstrap` reaproveita o objeto. Trocar no próprio objeto, no Editor (sprite, `ResourcePath` dos clipes, collider); **não** usar `Braziliation > Demo > Create or Update Fixed Demo Scene`, que recria a cena do zero e apaga o que entrou nela depois | `@GameplayEngineer` | Média | ⏸ depende do inimigo base |
| Hit-stop, tremor e empurrão no `PlayerCombat`/`HealthComponent` lendo os `eventos` do JSON lateral do sheet (`congela`, `tremor`, `amp` — ADR-016); hoje o combate não tem nenhuma resposta de impacto. Lógica de tempo no core, MonoBehaviour só aplica | `@GameplayEngineer` | Média | ❌ — formato em [`animacao-por-esqueleto.md`](../../Design/GuiasDeArte/animacao-por-esqueleto.md) |
| `HealthComponent` emite o estado inicial no `Start`, não no `Awake` — paga a dívida "`HealthComponent` dispara `OnHealthChanged` no `Awake`" ([`Tech/tech_debt.md`](Tech/tech_debt.md)). Decisão do @TechLead: no `Start`, todo `Awake`/`OnEnable` já rodou, então quem se inscreve ali recebe a emissão; quem se inscreve depois lê `CurrentHealth`/`MaxHealth` na hora da inscrição. Não criar `EmitCurrent()` sem caso real. Fechar com `unity-validar` e a entrada fora do `tech_debt.md` | `@GameplayEngineer` | Média | ❌ |
| Renomear o efeito híbrido `"PrótesisViva"` (espanhol) para `"ProteseViva"` no `HybridSynergyResolver`, no `HybridSynergyResolverTests` e na ficha [`Sistemas/Build.md`](Architecture/Sistemas/Build.md). Paga a dívida do nome em espanhol. O save de hoje não grava build nem híbridos, então **não** precisa de degrau `ISaveMigration`. Fazer antes do inventário entrar no save (primeiro item desta seção), porque depois passa a precisar. `dotnet test` verde | `@GameplayEngineer` | Média | ❌ |
| `BuildState.GetReceptacle(ReceptacleType)` no core (xUnit antes: tipo presente, tipo ausente → `null`), com o mesmo contrato do `ReceptacleController.GetReceptacle`. Depois, trocar as três leituras do `BuildProgressionView`, que passa a depender só do `BuildState` emitido pelo `PlayerBuildController` e perde o `ReceptacleController` e o `LogWarning` de fallback. Paga a dívida "`BuildProgressionView` lê `ExpansionLevel` pelo `ReceptacleController`". Linha na ficha `Build.md`, `dotnet test` e `unity-validar` verdes | `@GameplayEngineer` + `@UnityDeveloper` | Média | ❌ |
| Sistema hídrico global de Blumenau: `HydricState` (Rotina/Alerta/Cheia/Saturação) e `HydricStateManager` no core puro, como serviço comum registrado no `GameServiceLocator` e **não** como singleton estático (a feature diz "singleton", e a regra do core proíbe estado estático), com evento de mudança e `SetState` chamado pelos eventos de campanha (o jogador não controla o estado). O `FloodgateController` assina o evento e chama `SetLocked` em Cheia e Saturação. A arte da porta da comporta sai pela skill `novo-asset` e entra no `_gateRenderer`. Paga a dívida da comporta só aberta/fechada. Spec e TODOs em [`Blumenau-SistemaHidrico.md`](GDD/Features/Blumenau-SistemaHidrico.md) | `@SystemsDeveloper` + `@GameplayEngineer` | Média | ❌ |

---

## UI e arte

| Item | Responsável | Prioridade | Status |
|------|-------------|-----------|--------|
| Slots de save por `SaveLoadStatus`: pagar a dívida "UI de slots trata `Corrupt` e `FromNewerBuild` como slot vazio" ([`Tech/tech_debt.md`](Tech/tech_debt.md)) pelo contrato de [`Sistemas/UI.md`](Architecture/Sistemas/UI.md) › Estado do slot. **Core:** `SaveLoadResult.CanOverwrite` (lista positiva `Empty`/`Ok`/`Migrated`/`Corrupt`), com xUnit escrito antes: um `[Theory]` com os 6 status e um teste que quebra se surgir status novo. **UI:** `SaveSlotsView` passa a usar `LoadDetailed` e registra no log os status bloqueados; `SaveSlotEntryView.Bind` recebe `SaveLoadResult`, ganha `unavailableSlotIndicator`, `statusLabel` e os textos, e define `interactable` por `IsUsable`/`CanOverwrite`. Nenhuma cena para religar: o `SaveSlotsPanel` ainda não tem entradas. Para fechar: `dotnet test` e `unity-validar` verdes, `CanOverwrite` na ficha `SaveSystem.md`, a frase "A UI de slots ainda trata…" do ADR-007 atualizada e a entrada removida do `tech_debt.md` | `@UnityDeveloper` + `@SystemsDeveloper` | Alta | ❌ |
| pxfx onda 1 — combate: portar e reescalar impacts, melee, projectiles, explosions, spawn, status e o resto de fire (90 arquivos), com paridade OK na escala 1, `--escala 2.5` corrigida e aprovação pelo [`vfx-guide.md`](../../Design/GuiasDeArte/vfx-guide.md) (skill `vfx`) | `@SpriteArtist` | Média | 🔨 `fire/torch` portado — ver [`pxfx/index.md`](../../Design/ArteFonte/Ferramentas/pxfx/index.md) |
| pxfx onda 2 — mundo: water, weather, lightning, scifi, critters, nature, ice (89 arquivos) | `@SpriteArtist` | Baixa | ⏸ depois da onda 1 |
| pxfx onda 3 — sobrenatural: holy, shadow, arcane redesenhados para lendas e clero (37 arquivos) | `@SpriteArtist` | Baixa | ⏸ depois da onda 2 |
| pxfx onda 4 — interface: ui, pickups, transitions (36 arquivos); ao fechar, remover `Ferramentas/vendor/pixelfx/` (o aviso MIT fica) | `@SpriteArtist` | Baixa | ⏸ depois da onda 3 |
| Armas na mão do esqueleto: portar os `WEAPONS` do `rig.js` (espada, lança, martelo, pistola, lançador...) e a busca de cotovelo de quem segura — as atuações da biblioteca pedem arma | `@SpriteArtist` | Média | ❌ |
| Decidir a camada emissiva do VFX: o brilho aditivo e a fumaça translúcida do `pxfx` reprovam no `palette_check`; opções: máscara emissiva do sprite no URP 2D, exceção de paleta para VFX, ou exportar sem luz | Usuário (arte) | Média | ❌ — contexto no [`vfx-guide.md`](../../Design/GuiasDeArte/vfx-guide.md) |
| Afinar os modelos do esqueleto por criatura ao criar cada uma: proporções do quadrúpede (Lobisomem) e da serpente (Minhocão, Boitatá), taxa de órfãos da transferência de pele (1,5% no teste) | `@SpriteArtist` | Baixa | ⏸ junto com cada personagem |
| Tirar os placeholders CC0 do Gothicvania do projeto quando a arte própria os substituir: remover `Assets/Art/ThirdParty/Gothicvania/`, a entrada no `Desenvolvimento/CREDITS.md`, a seção de terceiros do [`indices/assets.md`](Architecture/indices/assets.md), a lista `Legado` do `PixelScale` (vira constante de 48) e o `TilesetAutoSlicer` (só atua em `ThirdParty/`). Bloqueios por asset: herói (3 arquivos) ← protagonista; chão e tileset do castelo (o `CastleBlockoutEditor` fixa os nomes de sprite do Gothicvania) ← tile de topo e quina do `gen_tileset.py` (`Tech/tech_debt.md`); fundo ← ainda sem asset nem pendência; cão (3 arquivos) ← item do inimigo placeholder em Gameplay | `@SpriteArtist` + `@UnityDeveloper` | Baixa | ⏸ depende da premissa (protagonista) e do tile de borda |
| Um padrão só de `CanvasScaler` (ADR-011): Scale With Screen Size, referência 960×540, Match 0.5, aplicado por um helper único em `Assets/Scripts/UI/` e usado por todo código que cria canvas. Hoje são três jeitos: o `DemoSceneBuilderEditor` (l. 182) e o `DemoSceneBootstrap` (l. 232) fazem `AddComponent<CanvasScaler>()` sem configurar, daí o 800×600 padrão do Unity no `HUD_Demo`; o `MainMenuUISetupEditor` usa 320×180, então multiplique por 3 as constantes de layout e corrija o comentário e o log da câmera (o `orthographicSize` 5,625 já está certo para 960×540 @ 48 PPU). Na mesma passada, pôr `EventSystem` + `InputSystemUIInputModule` na `DemoGameplay.unity` e no builder. Paga três dívidas: menu a 320×180, HUD a 800×600 e `DemoGameplay` sem `EventSystem` ([`Tech/tech_debt.md`](Tech/tech_debt.md)). Conferir menu e HUD em jogo; `unity-validar` | `@UnityDeveloper` | Média | ❌ |
| `gen_tileset.py` com modificador de borda genérico: `topo` (3 a 5 linhas de superfície, silhueta irregular e alfa acima), `quina_esq` e `quina_dir`, todos derivados do miolo de cada família para casar de cor, numa linha extra no sheet e no manifest. O `gen_map_wfc.py` ganha a adjacência "topo só encosta em ar por cima". Paga a dívida do tile só de miolo e destrava a saída dos placeholders do castelo (item acima) | `@SpriteArtist` | Média | ❌ |
| `comfy_batch.py` dirige o workflow que recebe: detectar o `class_type` do nó de encode (`TextEncodeZImageOmni` → campo `prompt`; `CLIPTextEncode` → `text`), steps/cfg 8 / 1.0 no destilado e o nome do modelo lido do próprio workflow em vez da constante, que hoje mente no `lotes.md`. Encode desconhecido → erro, nunca falha silenciosa. Se o A/B SDXL × Z-Image fechar abandonando o Z-Image, o script passa a recusar esse workflow. Paga a dívida do bench de modelo base | `@SpriteArtist` | Média | ❌ |
| Ruleset WFC de Blumenau: redesenhar `exemplos/blumenau-fachada-exemplo.json` com massas de prédio mais largas e variadas e passar o ruleset derivado (`--learn`, água plana) a padrão no lugar de `rulesets/blumenau-fachada.json`. O responsável aprova o desenho no mock antes da troca (é decisão de direção de arte). Paga a dívida da lâmina d'água serrilhada | `@SpriteArtist` | Média | ❌ |
| Dividir o [`pipeline-ia-sprites.md`](../../Design/GuiasDeArte/pipeline-ia-sprites.md) (~5,8 mil tokens, lido inteiro a cada sessão de arte) em um arquivo por rota, com o `index.md` de `GuiasDeArte/` listando cada um, e consertar os links para as âncoras que mudarem de arquivo (o ADR-014 aponta `#regra-legal-e-criativa`). Ao terminar, tirar a exceção dele do `TokenBudgetTests`. É o que resta da dívida "Dois documentos acima do teto" (a ficha de Blumenau foi dividida em 2026-11-09) | `@SpriteArtist` | Média | ❌ |
| Rebind e glifos (ADR-017), parte do core: `GameSettings.InputBindingOverrides` (string, o JSON opaco do `SaveBindingOverridesAsJson`, vazio por padrão) e `GameSettings.GlyphStyle` (`Auto`/`Xbox`/`PlayStation`/`Switch`, `Auto` por padrão) persistidos pelo `SettingsService`. O core não interpreta o JSON. xUnit antes: ida e volta, padrão vazio e arquivo de settings antigo sem os campos carregando o padrão. Linha na ficha [`Settings.md`](Architecture/Sistemas/Settings.md) | `@SystemsDeveloper` | Alta | ❌ |
| Rebind e glifos (ADR-017), parte Unity: o `GameInput` aplica os overrides do `GameSettings` no boot, antes da primeira leitura; conduz o rebind interativo (`PerformInteractiveRebinding`: Esc cancela, conflito de tecla avisado, mouse fora das ações de movimento); restaura o padrão por ação e no geral; e expõe a família do dispositivo ativo com evento de troca. Uma `RebindView` em `UI/` lista as ações do map `Player` e só chama o `GameInput`. Um seletor de glifo resolve o sprite pela família, ou pelo `GlyphStyle` quando não é `Auto`. Navegável por controle (`SetSelectedGameObject`). Paga a dívida Alta do rebind ([`Tech/tech_debt.md`](Tech/tech_debt.md)) junto com a parte do core e os glifos; `unity-validar` e linha nas fichas `Core.md` e `UI.md` | `@UnityDeveloper` | Alta | ⏸ depende da parte do core (campos do `GameSettings`) |
| Glifos de controle (ADR-017): um conjunto por família (teclado/mouse, Xbox, PlayStation, Switch) para as ações do map `Player` e da UI, no grid de 48 e na paleta, pela skill `novo-asset` (brief e context pack primeiro) | `@SpriteArtist` | Alta | ❌ |

---

## Ecossistema e processo

| Item | Responsável | Prioridade | Status |
|------|-------------|-----------|--------|
| Avaliar a janela de compactação do ADR-015 na página Tokens da Central depois de ~5 execuções com janela nas filas Unity, Gameplay e UI e arte: manter, ajustar ou voltar ao `auto`; e decidir se vale o passo seguinte por mod (esforço por requisição, saídas grandes encurtadas) | @TechLead | Média | ❌ Não iniciado |

---

## Sequência recomendada para a demo

1. `fechar-decisao`: premissa → inimigo base → arma inicial → números de Crafting e Build.
2. Play-teste no Editor (menu → demo) e wiring pendente da seção Unity.
3. `novo-inimigo` para o inimigo base; trocar o placeholder.
4. Inventário real no save.
5. UI e arte pendentes.
6. Checklist final da demo com o loop completo (combate + progressão + feedback).
