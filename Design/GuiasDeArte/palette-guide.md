# Guia de Paletas

## Regra Geral

Cada sprite deve usar uma paleta curta, com cerca de 12 a 32 cores úteis (ADR-004 — densidade Blasphemous-like pede rampas mais longas que o limite original do projeto, de 16 cores). A paleta pode ter variações por região, mas precisa respeitar os materiais e o contraste do jogo.

> **Base + rampas:** uma paleta regional tem 16 cores **base** (keys `1`-`9`, `A`-`G`) e até 16 cores **de rampa** (keys `H`-`Y`, sem `I` e `O`, que se confundem com `1` e `0` nas specs) que fecham rampas de 4 degraus por material — o que o `rig.json` do esqueleto pede (ADR-016). Cor nova de rampa entra com o motivo, e as rampas por nome ficam no bloco `"rampas"` do JSON.

## Paleta Base Sugerida

| Função | Direção |
|--------|---------|
| Sombras | Azul petróleo, roxo acinzentado ou marrom frio |
| Metal escuro | Grafite, ferro azulado, preto quente |
| Metal quente | Latão velho, cobre queimado, dourado sujo |
| Madeira | Marrom frio, ocre escuro, bege gasto apenas como luz |
| Água/lama | Verde acinzentado, marrom frio, amarelo sujo pontual |
| Luz | Amarelo pálido, âmbar, verde místico controlado |
| Sangue/alerta | Vermelho escuro e pouco saturado |

## Blumenau — Clockpunk/Hídrico

> **Paleta aprovada (2026-07-11), estendida para 32 em 2026-11-05:** valores oficiais em `Design/ArteConceitual/Paletas/blumenau.json` (machine-readable, usada pelas ferramentas do pipeline programático) e `Design/ArteFonte/Aseprite/blumenau.gpl` (Aseprite/GIMP). Folha visual das rampas: [`blumenau-rampas.svg`](../ArteConceitual/Paletas/blumenau-rampas.svg).

### Rampas de Blumenau

Ordem **aceso → escuro**, a do `"rampas"` do `rig.json`. O `--rampa` do `pxfx` e as `LIGAS`/`BASE_RAMPS` do `montagem_base.py` pedem **escuro → claro** — inverter ao copiar.

| Rampa | Keys | Uso |
|-------|------|-----|
| `ferro` | `5 H 4 3` | metal frio; `J` é o especular, `2` e `1` a sombra |
| `esmalte` | `J 5 H 4` | louça de ágata, prata, Edith |
| `latao` | `K 8 7 6` | bronze do autômato, latão clockpunk |
| `cobre` | `T M 9 L` | cobre; `T` (pele clara) faz o brilho |
| `chama` | `K W 9 L` | chama e lampião — **só fonte de luz** |
| `vinho` | `P G N 1` | teatro, batina do clero, sangue |
| `musgo` | `R E Q 2` | loden, folhagem, água parada |
| `espectral` | `X R E Q` | brilho do Jardim de Edith — **pouca área** |
| `madeira` | `D C B A` | madeira (a base já tinha os 4 degraus) |
| `pele_clara` | `S T U V` | pele — uma cadeia `S T U V A` serve às duas |
| `pele_escura` | `T U V A` | pele, um degrau abaixo |
| `sombra_fria` | `4 Y 2 1` | sombra noturna, o roxo acinzentado da paleta base sugerida |

Saturação sob controle: `W` (âmbar) e `X` (espectral) são as únicas cores vivas — acento, nunca área grande.

| Camada | Direção |
|--------|---------|
| Centro clerical | Pedra fria, latão controlado, vitrais escuros, sombra profunda |
| Teatro | Vermelho vinho gasto, madeira escura, dourado envelhecido, poeira |
| Rio/cheia | Água barrenta, lama seca, marcas de umidade, metal oxidado |
| Jardim de Edith | Verde musgo, cinza azulado, brilho espectral pequeno e suave |
| Morro do Zendron | Terra úmida, concreto quebrado, vegetação abafada, céu pesado |

## Lages — Campos Gelados / Rio Caveiras

> **Rascunho (2026-07-24):** valores propostos em `Design/ArteConceitual/Paletas/lages.json` (`status: proposta-inicial`). Ainda sem paleta Aseprite `.gpl` equivalente — criar ao aprovar. Punk Genre e estética de monstros da cidade seguem `{TODO}` em `Design/Criativo/Estados/SantaCatarina/cidades/Lages/index.md`; revisar a paleta se a definição desses campos mudar a direção visual.

| Camada | Direção |
|--------|---------|
| Banhado/Rio Caveiras | Água turva, névoa fria, lama escura, vegetação de pântano abafada |
| Maquinário abandonado | Ferrugem em vez de latão polido — Lages é mais isolado e hostil que o clockpunk de Blumenau |
| Fauna/criaturas | Tons frios e dessaturados, pouco brilho — reforçar mistério (Minhocão) |

## Regras de Consistência

- Não crie paleta nova sem registrar o motivo.
- Use uma cor de acento por asset importante.
- Personagens e inimigos precisam destacar do fundo por valor.
- Cenários podem ter mais textura, mas menos contraste que entidades interativas.
- Paletas aprovadas devem ser salvas em `Design/ArteFonte/Aseprite/` e referenciadas em `Design/ArteConceitual/Paletas/`.
