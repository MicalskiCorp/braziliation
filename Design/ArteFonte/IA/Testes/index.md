# Testes — arte de primeiro teste, fora do fluxo de aprovação

> Criada em 2026-11-05 por decisão do usuário. Aqui fica a arte produzida como **exemplo e primeiro
> teste** de uma família ou de uma técnica — para comparar, aprender com o processo e servir de
> ponto de partida quando o asset for retomado. **Nada daqui é canônico:** não vai para `Selected/`,
> não é exportado para `Desenvolvimento/Assets/Art/` e não entra em `indices/assets.md`. O usuário
> volta a cada item, um a um; ao retomar, o asset nasce de novo pelo fluxo normal (brief → spec ou
> gerador → crítica → `Selected/`) e pode usar o que está aqui como referência.

| Diferença para as pastas vizinhas | |
|---|---|
| `Selected/` | escolhido no gate, a caminho do pixel pass ou do export |
| `Rejected/` | descartado no gate — registro do que **não** serviu |
| `Testes/` | **serviu como experimento**, mas ainda não é a versão de produção |

## Conteúdo

| Pasta | O que é | Origem |
|-------|---------|--------|
| [`tilesets-onda2/`](tilesets-onda2/) | 4 tilesets 48×48 (192×192, 4 tipos × 4 variações): `pedra_portuguesa` (túnel séc. XVIII — cantaria, abóbada, piso pé-de-moleque, musgo), `cemiterio` (terra, mato, cascalho, cova), `marmore` (placa, veio, cimalha, lascado), `periferia` (tábua encharcada, zinco, reboco com lama, entulho). Manifests com seed e o mock 960×540 em contexto | `gen_tileset.py <família> --seed 42` — as 4 famílias continuam no gerador; regerar dá o mesmo PNG. Ciclo de crítica (até 4 iterações no piso) documentado nas docstrings das funções. Execução da fila «UI e arte», 2026-11-04 |
| [`tilesets-bordas/`](tilesets-bordas/) | Primeiro teste do `--bordas` do `gen_tileset.py`: cemitério (terra), periferia (entulho), pedra portuguesa (piso) e mármore (placa), seed 42, com topo, quinas e laterais; `env_blumenau_bordas_mock.png` monta uma plataforma de cada | `gen_tileset.py <família> --seed 42 --bordas <tipo>`. Fila «Dívida técnica», 2026-11-09, para a aprovação do responsável antes de exportar alguma família para `Assets/` |
| [`wfc-fachada-v2/`](wfc-fachada-v2/) | Teste da correção sugerida para o ruleset WFC de Blumenau: o exemplo atual × um exemplo com prédios de 4 a 7 colunas (`blumenau-fachada-exemplo-v2.json`), `--learn`, seeds 7, 42 e 2026. Os prédios continuam de 1 a 3 colunas nos dois, e na seed 7 a água sobe até o topo nos dois | `gen_map_wfc.py rulesets/blumenau-fachada.json --learn <exemplo> --seed N -w 24 -H 12`. Fila «Dívida técnica», 2026-11-09: refuta a hipótese da dívida e leva a decisão ao responsável |
| [`pxfx-ruido-tela/`](pxfx-ruido-tela/) | `fire/torch` na escala 2,5, quadros 0, 20 e 40, ampliados ×5: à esquerda o ruído do enrolado sorteado por célula local (blocos de 2,5 px), à direita pelo `p.noiseCell` (um sorteio por pixel de tela) | Comparação gerada na fila «Dívida técnica», 2026-11-09, para a aprovação do helper de ruído do `pxfx` |
| [`comporta-pixel-pass/`](comporta-pixel-pass/) | A comporta com a engrenagem redesenhada — 10 dentes quadrados, 3 raios, cubo, girando junto com a alavanca — no lugar do "torrão" que o Scale3x deixou. Frame, sheet de acionamento, mock e as 3 specs 3x passadas | `pixel_pass_engrenagem.py` (nesta pasta, roda sobre as cópias das specs daqui). A comporta canônica — context pack `exemplo-prop-comporta-blumenau/`, `Selected/` e `Assets/` — continua com a roda antiga |

## O que ficou de aprendizado (vale ao retomar)

- **O Scale3x arredonda todo bloco de cor contra uma junta de outra cor.** Estraga mosaico de cubos
  (vira bolinha) e engrenagem de dente pequeno (vira lóbulo); ajuda pedra rolada. Desenhar no 16 já
  pensando no arredondamento.
- **Tile que cruza a borda tem de ser igual em todas as variações**, ou o mapa mostra costura.
- **Fundo × personagem:** em contexto, o reboco bege da periferia quase apaga o Autômato bronze
  (`D` contra `7`/`8`). Tiles usados como fundo vão precisar de uma convenção de valor.
- **Falta tile de borda** (topo de chão, quina) em todas as famílias — dívida em
  `Desenvolvimento/Docs/Tech/tech_debt.md`.
