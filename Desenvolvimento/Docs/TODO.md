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
| Composição final dos itens híbridos (stats, nome e lore do resultado) — a compatibilidade de slot já está decidida no `Mechanics/Crafting.md` (híbrido entra no slot de qualquer um dos seus tipos) | [`Mechanics/Crafting.md`](Mechanics/Crafting.md) | Alta | ❌ |
| Política de seed do sorteio híbrido (determinístico × aleatório) | [`Sistemas/Crafting.md`](Architecture/Sistemas/Crafting.md) | Média | ❌ |
| Localização e quantidade de totens | [`Mechanics/Build.md`](Mechanics/Build.md) | Média | ❌ |
| Localização das benzedeiras (uma por região; a casa é o checkpoint?) e do ponto único do Monge João Maria — quando houver mapa | [DDR-001](GDD/Decisoes/DDR-001-benzedeira-npc.md) · [DDR-002](GDD/Decisoes/DDR-002-monge-joao-maria-papel.md) | Média | ❌ |

---

## Unity — validação no Editor e wiring

> Compilação e testes EditMode rodam sem abrir o Editor pela skill `unity-validar`. Os itens abaixo exigem o Editor aberto (ou o MCP `unity`).

| Item | Responsável | Prioridade | Status |
|------|-------------|-----------|--------|
| Conferir no Editor o padrão de `CanvasScaler` de 2026-11-09. **Menu:** rodar `Tools › Braziliation › Setup Main Menu UI` na `MainMenu.unity` para gravar o layout ×3 e o canvas 960×540 na cena; deve sair igual ao de antes. **HUD:** o `HUD_Demo` da `DemoGameplay.unity` deixou o Constant Pixel Size, então em 1080p fica 2× maior que antes. Se ficar grande, dividir por 2 as medidas do `CreateHud`/`EnsureHud` e da cena. O `EventSystem` novo da cena deve aparecer sem aviso | Usuário + `@UnityDeveloper` | Média | ❌ |
| Montar a tela de controles (ADR-017): prefab de `RebindView` com o `RebindRowView` de linha, um asset `ControlGlyphLibrary` (vazio até os glifos chegarem) e um botão "Controles" nas Opções do menu. Nas Opções, um seletor de glifo (Automático/Xbox/PlayStation/Switch) que muda `GameInput.GlyphStyle` e grava o `GameSettings`. Testar no Editor, de teclado e de controle: trocar, Esc cancela, 8 s sem input cancela, aviso de conflito, restaurar um e tudo, e o binding sobrevivendo a reiniciar o jogo. O código está pronto e compilado (`GameInput.Rebind.cs`, `GameInput.Devices.cs`, `RebindView.cs`) | `@UnityDeveloper` | Alta | ❌ |

---

## Gameplay

| Item | Responsável | Prioridade | Status |
|------|-------------|-----------|--------|
| Inventário completo: capacidade, categorias por pilar, persistência no save | `@SystemsDeveloper` + `@GameplayEngineer` | Média | ⏸ depende dos números de Crafting |
| Reação a dano (stagger) e percepção por linha de visão | `@GameplayEngineer` | Média | ❌ — ver [`Mechanics/InimigosIA.md`](Mechanics/InimigosIA.md) |
| Perfis de inimigo dos arquétipos de Blumenau (skill `novo-inimigo`) | `@GameCreative` + `@GameplayEngineer` | Média | ⏸ depende do inimigo base |
| Trocar o inimigo placeholder pelo `enm_automato_idle_sheet.png` — o código já trocou (`DemoSceneVisuals` aponta o autômato), falta a cena: o `Enemy_Demo` da `DemoGameplay.unity` ainda guarda sprite e sheets do cão do Gothicvania, e o `DemoSceneBootstrap` reaproveita o objeto. Trocar no próprio objeto, no Editor (sprite, `ResourcePath` dos clipes, collider); **não** usar `Braziliation > Demo > Create or Update Fixed Demo Scene`, que recria a cena do zero e apaga o que entrou nela depois | `@GameplayEngineer` | Média | ⏸ depende do inimigo base |
| Hit-stop, tremor e empurrão no `PlayerCombat`/`HealthComponent` lendo os `eventos` do JSON lateral do sheet (`congela`, `tremor`, `amp` — ADR-016); hoje o combate não tem nenhuma resposta de impacto. Lógica de tempo no core, MonoBehaviour só aplica | `@GameplayEngineer` | Média | ❌ — formato em [`animacao-por-esqueleto.md`](../../Design/GuiasDeArte/animacao-por-esqueleto.md) |
| Arte da porta da comporta hídrica de Blumenau (aberta e fechada) pela skill `novo-asset`, ligada no `_gateRenderer`/`_openSprite`/`_closedSprite` do `FloodgateController` e no `Prop_FloodgateGate.prefab`. Hoje a comporta funciona só pelo colisor, sem sprite próprio (só a alavanca tem arte). O estado global do rio já existe e trava a comporta em Cheia e Saturação (ficha [`Hydric.md`](Architecture/Sistemas/Hydric.md)) | `@SpriteArtist` + `@UnityDeveloper` | Média | ❌ |

---

## UI e arte

| Item | Responsável | Prioridade | Status |
|------|-------------|-----------|--------|
| pxfx onda 1 — combate: portar e reescalar impacts, melee, projectiles, explosions, spawn, status e o resto de fire (90 arquivos), com paridade OK na escala 1, `--escala 2.5` corrigida e aprovação pelo [`vfx-guide.md`](../../Design/GuiasDeArte/vfx-guide.md) (skill `vfx`); ruído de textura do `shade` por `p.noiseCell` (regra no `pxfx/index.md`) | `@SpriteArtist` | Média | 🔨 `fire/torch` portado — ver [`pxfx/index.md`](../../Design/ArteFonte/Ferramentas/pxfx/index.md) |
| pxfx onda 2 — mundo: water, weather, lightning, scifi, critters, nature, ice (89 arquivos) | `@SpriteArtist` | Baixa | ⏸ depois da onda 1 |
| pxfx onda 3 — sobrenatural: holy, shadow, arcane redesenhados para lendas e clero (37 arquivos) | `@SpriteArtist` | Baixa | ⏸ depois da onda 2 |
| pxfx onda 4 — interface: ui, pickups, transitions (36 arquivos); ao fechar, remover `Ferramentas/vendor/pixelfx/` (o aviso MIT fica) | `@SpriteArtist` | Baixa | ⏸ depois da onda 3 |
| Armas na mão do esqueleto: portar os `WEAPONS` do `rig.js` (espada, lança, martelo, pistola, lançador...) e a busca de cotovelo de quem segura — as atuações da biblioteca pedem arma | `@SpriteArtist` | Média | ❌ |
| Decidir a camada emissiva do VFX: o brilho aditivo e a fumaça translúcida do `pxfx` reprovam no `palette_check`; opções: máscara emissiva do sprite no URP 2D, exceção de paleta para VFX, ou exportar sem luz | Usuário (arte) | Média | ❌ — contexto no [`vfx-guide.md`](../../Design/GuiasDeArte/vfx-guide.md) |
| Afinar os modelos do esqueleto por criatura ao criar cada uma: proporções do quadrúpede (Lobisomem) e da serpente (Minhocão, Boitatá), taxa de órfãos da transferência de pele (1,5% no teste) | `@SpriteArtist` | Baixa | ⏸ junto com cada personagem |
| Tirar os placeholders CC0 do Gothicvania do projeto quando a arte própria os substituir: remover `Assets/Art/ThirdParty/Gothicvania/`, a entrada no `Desenvolvimento/CREDITS.md`, a seção de terceiros do [`indices/assets.md`](Architecture/indices/assets.md), a lista `Legado` do `PixelScale` (vira constante de 48) e o `TilesetAutoSlicer` (só atua em `ThirdParty/`). Bloqueios por asset: herói (3 arquivos) ← protagonista; chão e tileset do castelo (o `CastleBlockoutEditor` fixa os nomes de sprite do Gothicvania) ← aprovar as bordas do `gen_tileset.py --bordas` (mock em `Design/ArteFonte/IA/Testes/tilesets-bordas/`) e exportar a família escolhida; fundo ← ainda sem asset nem pendência; cão (3 arquivos) ← item do inimigo placeholder em Gameplay | `@SpriteArtist` + `@UnityDeveloper` | Baixa | ⏸ depende da premissa (protagonista) e do tile de borda |
| Ruleset WFC de Blumenau: prédios largos e linha d'água fixa. Redesenhar o exemplo não basta (teste de 2026-11-09 em [`IA/Testes/wfc-fachada-v2/`](../../Design/ArteFonte/IA/Testes/wfc-fachada-v2/)): escolher entre bordas de prédio, WFC por padrões N×N ou leiaute de prédios + WFC por fachada (recomendado), e prender a água numa linha (`water_row`). Opções em [`Tech/tech_debt.md`](Tech/tech_debt.md) | `@SpriteArtist` | Média | ⏸ decisão do responsável |
| `BuildProgressionView` com um `SpriteRenderer` por parte: `_rendererCapa` e `_rendererEspinha` ao lado do exoesqueleto, um `AplicarSprite` por renderer, e cada parte num filho do personagem com o mesmo pivô. Hoje os três arrays de estágio caem no mesmo renderer, e só o último aparece. No `pxfx`, cada parte é uma camada de pele sobre o mesmo rig e sai num sheet próprio, com os mesmos quadros e o mesmo JSON lateral do corpo. Assim as partes andam juntas sem gerar um sheet por combinação de estágios. Paga a dívida dos três arrays no mesmo renderer | `@UnityDeveloper` | Média | ⏸ depende dos estágios visuais em «Parâmetros numéricos de Build» e da arte do personagem em partes |
| Glifos de controle (ADR-017): um conjunto por família (teclado/mouse, Xbox, PlayStation, Switch) para as ações do map `Player` e da UI, no grid de 48 e na paleta, pela skill `novo-asset` (brief e context pack primeiro) | `@SpriteArtist` | Alta | ❌ |

---

## Ecossistema e processo

| Item | Responsável | Prioridade | Status |
|------|-------------|-----------|--------|
| Avaliar a janela de compactação do ADR-015 na página Tokens da Central depois de ~5 execuções com janela nas filas Unity, Gameplay e UI e arte: manter, ajustar ou voltar ao `auto`; e decidir se vale o passo seguinte por mod (esforço por requisição, saídas grandes encurtadas) | @TechLead | Média | ⏸ aguardando as ~5 execuções com janela — nenhuma nas filas Unity, Gameplay e UI e arte desde o ADR-015 (2026-11-04) |

---

## Sequência recomendada para a demo

1. `fechar-decisao`: premissa → inimigo base → arma inicial → números de Crafting e Build.
2. `novo-inimigo` para o inimigo base; trocar o placeholder.
3. Inventário real no save.
4. UI e arte pendentes.
5. Checklist final da demo com o loop completo (combate + progressão + feedback).
