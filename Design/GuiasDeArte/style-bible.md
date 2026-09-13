# Bíblia Visual — Braziliation

## Pilares

1. **Pixel art de alta densidade (Blasphemous-like, ADR-004):** leitura clara em 640x360, poucos pixels desperdiçados e formas reconhecíveis em tamanho real de jogo.
2. **Dieselpunk brasileiro:** metal pesado, ferrugem, vapor, óleo, engrenagens e improviso técnico com identidade brasileira local.
3. **Paleta restrita:** cada região tem paleta própria, mas todas compartilham contraste, saturação controlada e materiais recorrentes.
4. **Silhueta primeiro:** antes de detalhe, o sprite precisa ser reconhecível apenas pela forma.
5. **Mundo vivido:** nada deve parecer limpo demais; desgaste, remendo e adaptação fazem parte do estilo.

## Densidade Alvo (referência: Castlevania: SotN, Blasphemous)

> Adicionado 2026-07-24: "Blasphemous-like" no Pilar 1 nunca foi traduzido em regra checável, e nada entregue até hoje testou essa densidade de verdade (ver [[braziliation-pipeline-analise-gargalos]]). Isto aqui é o ponto de partida para calibrar, não um número final — revisar contra o primeiro sprite-âncora orgânico aprovado.

- **Canvas mínimo para personagens/criaturas legíveis nesse nível de detalhe: 48×64.** Abaixo disso (ex.: 32×32) não há pixels suficientes para sustentar bandas de sombra, dithering e material distinto ao mesmo tempo — reservar canvas pequeno para props/ícones, não para entidades orgânicas.
- **Mínimo 3-4 bandas de valor por material principal** (não 2 — sombra/luz direto demais lê como plano, não como volume): sombra profunda, sombra, meio-tom, luz. Metal e pele/couro precisam disso pra não ficar "achatados".
- **Dithering controlado nas transições entre bandas**, não gradiente suave (proibido pela regra de leitura já existente) nem degrau único brusco — um padrão de dithering consistente por material é o que dá o acabamento "pintado à mão" das referências.
- **Um único ponto de luz direcional por sprite**, com highlight concentrado (1-3px) nas quebras de forma que mais importam pra leitura da silhueta — não espalhar highlight por toda superfície.
- **Outline não uniforme**: mais escuro/grosso nas sombras de contato e mais sutil (ou ausente) nas bordas iluminadas — outline de espessura única em todo o contorno é o sintoma mais comum de "sprite plano".

Nenhuma dessas regras substitui a Regra de Leitura já existente (nada de microdetalhe que some no jogo) — a densidade vem de bandas de valor bem colocadas na silhueta certa, não de textura fina espalhada pelo sprite inteiro.

## Linguagem de Formas

| Tema | Formas |
|------|--------|
| Clero/elite | Verticais rígidas, arcos, simetria, ornamento controlado |
| Máquinas clockpunk | Círculos, engrenagens, braços articulados, eixos e polias |
| Periferia pós-enchente | Linhas quebradas, madeira torta, remendos, cabos e lama |
| Sobrenatural íntimo | Formas suaves, baixa saturação, brilho pequeno e localizado |

## Materiais Recorrentes

- Latão envelhecido
- Ferro escurecido
- Madeira úmida
- Concreto rachado
- Azulejo gasto
- Tecido pesado
- Água barrenta
- Vapor e fuligem

## Regras de Leitura

- O sprite precisa funcionar em zoom 1x.
- Evite microdetalhe que desaparece no jogo.
- Use highlights apenas nos pontos que guiam o olhar.
- Separe personagem, inimigo e cenário por contraste de valor, não por excesso de saturação.
- Sprites importantes podem ter outline ou sombra de contato mais forte; cenário deve competir menos.

## O Que Evitar

- Pixel art com aparência de imagem hi-res reduzida.
- Diesel/steampunk genérico sem traço brasileiro ou regional.
- Paletas com muitas cores próximas sem função clara.
- Gradientes suaves demais.
- Excesso de textura que prejudica colisão, plataforma e leitura de ameaça.
