# Context Pack — Autômato Abandonado (placeholder de inimigo)

> **✅ ADR-011 — re-autoria davinciana concluída (2026-10-05):** o asset foi **redesenhado**,
> não migrado. Saiu a versão frontal simétrica de 32×32/3 frames; entrou um autômato de
> relojoaria em **96×96 @ 48 PPU**, vista lateral, montado por catálogo de peças
> (`montagem.py`). Duas dimensões de variação: **armamento** (lança, escudo-engrenagem,
> sucata) e **liga** (bronze, prata, ferro), esta última pensada como grau de dificuldade —
> só a rampa do metal muda, a silhueta não. O idle de 6 frames é o **maquinismo girando**:
> cada roda avança um período de simetria por ciclo, rodas que engrenam giram em sentidos
> opostos, e a brasa da lente respira. Sem bob: é máquina rígida.
> Caminho percorrido até aqui: 32×32 frontal → lateral em latão (recusada por "fofa") →
> releitura gótica com manto (recusada por não ser davinciana) → esta. As duas recusadas
> ficam registradas em `enm_automato.alt-latao.spec.json` e no histórico do git.
>
> _Histórico:_ **ADR-004 — re-autoria concluída (2026-07-12):** specs 2× (`*.2x.spec.json` via `spec_redetail.py`) são a fonte atual; sheet re-autorado 192×64 (frames 64×64) entregue. Specs 1× = histórico.

## 1. Identificação

- Asset: `enm_automato_idle_sheet` (32×32, 3 frames)
- Rota: **programática (Opção A)** — placeholder; versão final poderá passar pela rota C (difusão) + pixel pass
- Região: Blumenau | Paleta: `blumenau.json` (aprovada 2026-07-11)
- Referência criativa: `Design/Criativo/Estados/SantaCatarina/cidades/Blumenau/index.md` → Monstros
- Data: 2026-07-11

## 2. Brief

"Máquina autônoma sem programação ativa, reage por reflexo a movimento. Corpo todo de metal trabalhado, estilo Da Vinci." Torso de latão arredondado com engrenagem exposta no peito, cabeça cilíndrica com olho de vidro (lente), braços e pernas de hastes de ferro finas. Idle: oscilação sutil de 1px + tique da engrenagem do peito.

> **Nota de design:** o inimigo básico da demo segue como decisão pendente no TODO — este placeholder permite `@GameplayEngineer` implementar AI/estados sem esperar arte final.

## 3. Restrições

32×32, side-view, pivot base central, ~12-16 cores, silhueta de ameaça legível em 1x, sem sci-fi moderno.

## 4. Resultado

- **Entregue 2026-07-12** — `enm_automato_idle_sheet.png` (96×32, 3 frames: engrenagem do peito tica um dente por frame + lente varia o brilho). APROVADO no `palette_check` e no mock 320×180 (silhueta de ameaça clara, latão destaca do fundo por valor).
- Iterações: 2 — a engrenagem do peito lia como painel quadrado; anel de cobre arredondado na iteração 2.
- Destino: `Assets/Art/Enemies/`; cópia em `IA/Selected/`; registro no índice.
- Pendências: decisão de design "inimigo básico da demo" continua aberta no TODO (este asset destrava a implementação de AI/estados como placeholder); animações de patrol/attack quando o design definir o comportamento.
