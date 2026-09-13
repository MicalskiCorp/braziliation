# Context Pack — Lote Sistema Hídrico (Blumenau)

## 1. Identificação

- Lote: props de sinalização do Sistema Hídrico de Die Unterwelt
- Rota: **programática (Opção A)** — specs JSON neste pack
- Região: Blumenau | Paleta: `blumenau.json` (aprovada 2026-07-11)
- Feature: `Docs/GDD/Features/Blumenau-SistemaHidrico.md`
- Data: 2026-07-11

## 2. Assets do lote

| Asset | Tamanho | Destino | Função |
|-------|---------|---------|--------|
| `prop_blumenau_marcador_pilar_{verde,amarelo,vermelho,preto}` | 16×16 | `Environments/Blumenau/Props/` | Marcador pintado nos pilares — 4 estados do rio (rotina/alerta/cheia/saturação) |
| `prop_blumenau_sino_alerta` (+ `_ring_sheet` 3f) | 16×16 | idem | Sino mecânico de alerta; badalada em 2 frames de balanço |
| `prop_blumenau_sirene_pneumatica` | 16×16 | idem | Sirene de longo alcance em poste |
| `prop_blumenau_sinalizador_torre` (+ `_aceso`) | 16×32 | idem | Farol de torre; estados apagado/aceso |

## 3. Direção

Materiais: madeira úmida (pilares), ferro escuro (sino/sirene/torre), latão (sino). Tinta dos marcadores mapeada na paleta: verde acinzentado (E), amarelo sujo (F), vermelho dessaturado (G), preto quente (1). Silhueta legível em 1x; nada limpo demais — escorrido de tinta nos marcadores.

## 4. Resultado

> **✅ ADR-004 — re-autoria concluída (2026-07-12):** todos os assets deste lote re-autorados para o grid 2× via `spec_redetail.py` (specs `*.2x.spec.json` = fonte atual; 1× = histórico); gates re-aprovados e entregas atualizadas.

- **Entregue 2026-07-12** — 9 specs → 9 PNGs + 1 sheet (`_ring_sheet` 48×16), todos APROVADOS no `palette_check` e no ciclo de crítica visual (contact sheet 8x + leitura contra fundo).
- Iterações: 1 (nenhum reprovado no ciclo).
- Destino: `Assets/Art/Environments/Blumenau/Props/`; cópias em `IA/Selected/`; registro em `Docs/Architecture/indices/assets.md`.
- Pendência de wiring: sino `_ring_sheet` será fatiado pelo `SheetAutoSlicer` na abertura do Unity; Animator via menu Braziliation (@UnityDeveloper).
