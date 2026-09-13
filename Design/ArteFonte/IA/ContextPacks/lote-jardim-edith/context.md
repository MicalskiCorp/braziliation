# Context Pack — Lote Jardim de Edith (Blumenau)

## 1. Identificação

- Lote: props do Cemitério dos Gatos / SQ-01 "Os Gatos de Edith"
- Rota: **programática (Opção A)** — specs JSON neste pack
- Região: Blumenau | Paleta: `blumenau.json` (aprovada 2026-07-11)
- Feature: `Docs/GDD/Features/Blumenau-JardimEdith.md`
- Data: 2026-07-11

## 2. Assets do lote

| Asset | Tamanho | Destino | Função |
|-------|---------|---------|--------|
| `prop_blumenau_lapide_gato` | 16×16 | `Environments/Blumenau/Props/` | Lápide de concreto com nome gravado (9 nomeadas usam a mesma base) |
| `prop_blumenau_estatua_gato` | 16×32 | idem | Estátua de gato do centro do jardim (como no local real) |
| `ui_item_pingente_gato` | 16×16 | `Art/UI/` | Pingente/medalha com nome do gato — item de coleta da SQ-01 (41×) |

## 3. Direção

Pedra/concreto gasto (tons frios 5/4/3), musgo verde acinzentado (E) — "verde musgo, cinza azulado, brilho espectral pequeno e suave" (palette-guide, camada Jardim de Edith). Toque espectral discreto: olhos/detalhe em E. Melancolia, não horror.

## 4. Resultado

> **✅ ADR-004 — re-autoria concluída (2026-07-12):** todos os assets deste lote re-autorados para o grid 2× via `spec_redetail.py` (specs `*.2x.spec.json` = fonte atual; 1× = histórico); gates re-aprovados e entregas atualizadas.

- **Entregue 2026-07-12** — 3 specs → 3 PNGs, todos APROVADOS no `palette_check` e no ciclo de crítica visual (estátua com olhos espectrais E lendo bem em 8x; lápide com gravação e musgo).
- Iterações: 1 no ciclo visual; 1 correção de spec pré-render no pingente (largura/espaços — pego pelo validador do `render_spec.py`).
- Destinos: lápide/estátua em `Assets/Art/Environments/Blumenau/Props/`; pingente em `Assets/Art/UI/`; cópias em `IA/Selected/`; registro no índice.
- Próximo passo natural: as 9 lápides nomeadas (variações da base com nomes: Pepito, Mirko, Bum, Peterle, Musch, Schnurr, Sittah, Putze, Mirl) — nomes gravados são ilegíveis em 16×16, tratar via tooltip/interação, não via pixel.
