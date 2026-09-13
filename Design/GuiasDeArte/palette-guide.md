# Guia de Paletas

## Regra Geral

Cada sprite deve usar uma paleta curta, com cerca de 12 a 32 cores úteis (ADR-004 — densidade Blasphemous-like pede rampas mais longas que o limite original do projeto, de 16 cores). A paleta pode ter variações por região, mas precisa respeitar os materiais e o contraste do jogo.

> **Expansão pendente:** as paletas regionais JSON têm 16 cores base; rampas estendidas (tons intermediários por material) devem ser adicionadas ao JSON conforme a re-autoria dos assets exigir — sempre registrando o motivo.

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

> **Paleta aprovada (2026-07-11):** valores oficiais em `Design/ArteConceitual/Paletas/blumenau.json` (machine-readable, usada pelas ferramentas do pipeline programático) e `Design/ArteFonte/Aseprite/blumenau.gpl` (Aseprite/GIMP).

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
