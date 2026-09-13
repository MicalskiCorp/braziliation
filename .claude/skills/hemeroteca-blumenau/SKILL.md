---
name: hemeroteca-blumenau
description: Pesquisa e localiza informações históricas de Blumenau nos PDFs OCR da revista "Blumenau em Cadernos" hospedados na Hemeroteca Digital de SC (CIASC), navegando os índices por década para achar a edição certa e depois lendo o PDF em busca do termo pedido. Use quando o usuário pedir para verificar/pesquisar algo sobre a história de Blumenau em fonte primária, mencionar "hemeroteca", "Blumenau em Cadernos" ou pedir uma edição específica por data/número.
context: fork
agent: historiador
---

# Skill: hemeroteca-blumenau

Fonte primária: **Hemeroteca Digital Catarinense (CIASC)**, acervo da revista histórico-cultural **"Blumenau em Cadernos"**. Todo o acervo está em `https://hemeroteca.ciasc.sc.gov.br/blumenau%20em%20cadernos/`, organizado em **páginas-índice por década** (HTML, cada uma lista os links das edições daquele período) e **PDFs OCR individuais** (um por edição).

> Esta skill serve para *localizar e ler fontes primárias*, não para decidir se uma referência folclórica existe (isso é o Modo 1 do Historiador). Use-a quando precisar checar um fato, data, nome ou evento específico de Blumenau contra o texto real de uma edição.
>
> **Roda num fork do `@Historiador`**: cada PDF tem 25-30 páginas de OCR, e ler isso na conversa principal a enche de texto que só serve para achar um trecho. O fork lê, e devolve só edição, trecho e fonte.

## Índices por década (fonte da verdade dos links)

| Período | URL do índice |
|---|---|
| 1957–1959 | `https://hemeroteca.ciasc.sc.gov.br/blumenau%20em%20cadernos/blumenaue%20cadernos50.html` |
| 1960–1969 | `https://hemeroteca.ciasc.sc.gov.br/blumenau%20em%20cadernos/blumenaue%20cadernos60.html` |
| 1970–1979 | `https://hemeroteca.ciasc.sc.gov.br/blumenau%20em%20cadernos/blumenaue%20cadernos70.html` |
| 1980–1989 | `https://hemeroteca.ciasc.sc.gov.br/blumenau%20em%20cadernos/blumenaue%20cadernos80.html` |
| 1990–1999 | `https://hemeroteca.ciasc.sc.gov.br/blumenau%20em%20cadernos/blumenaue%20cadernos90.html` |
| 2000–2009 | `https://hemeroteca.ciasc.sc.gov.br/blumenau%20em%20cadernos/blumenaue%20cadernos00.html` |
| 2010–2019 | `https://hemeroteca.ciasc.sc.gov.br/blumenau%20em%20cadernos/blumenaue%20cadernos10.html` |

Se a data pedida cair fora de 1957–2019, avisar o usuário que este índice não cobre o período antes de tentar adivinhar uma URL.

## Padrão observado nos PDFs (não confiável para adivinhar — só para reconhecer)

O nome do arquivo muda de esquema conforme a década, e o número embutido no arquivo **nem sempre é o número de edição** que o usuário conhece:

| Exemplo | Edição real | Observação |
|---|---|---|
| `1957/BLU1957002_dez.pdf` | Edição nº 2, dez/1957 | anos 1950 têm sufixo de mês abreviado (`_dez`) |
| `2001/BLU2001009.pdf` | Edição nº 09/10, set-out/2001 | sem sufixo de mês; número bate com a edição |
| `2010/BLU2010005.pdf` | Edição nº 51, mai-jun/2010 | número no arquivo (`005`) é a posição no ano, **não** o número global da edição (51) |

**Regra:** nunca montar a URL do PDF só pelo padrão acima. Sempre confirmar o link exato na página-índice da década (passo 2 do roteiro) — ela é a fonte da verdade, o padrão é só para reconhecer o que se está vendo.

## Roteiro

1. **Identificar a década-alvo** a partir do ano pedido pelo usuário e escolher o índice correspondente na tabela acima.
2. **WebFetch no índice da década** pedindo a lista de edições com seus links (ex.: prompt "listar todas as edições e URLs de PDF, com data/número de cada uma"). Isso evita adivinhar o nome de arquivo errado.
3. **Localizar a(s) edição(ões)-alvo** na lista retornada — por ano+mês ou por número de edição citado pelo usuário — e extrair a URL completa do PDF de cada uma.
4. **Baixar e ler cada PDF** seguindo exatamente o método da seção "Download e leitura (mecânica validada em produção)" abaixo — não tentar extrair o conteúdo direto da resposta do `WebFetch` sobre o PDF, ela quase sempre vem vazia por design da ferramenta.
5. **Reportar ao usuário**: edição (número + mês/ano), trecho relevante encontrado (ou "não encontrado nesta edição"), e a URL do PDF como fonte citável, seguindo o Protocolo de Fonte do Historiador:
   ```markdown
   > 📌 **Fonte:** Blumenau em Cadernos, edição {nº}, {mês/ano} — [PDF]({URL}) — acesso em DD/MM/AAAA
   ```
6. **Nunca inventar** conteúdo de uma edição que não foi de fato aberta e lida, nem confirmar leitura de uma edição cujo texto não chegou de fato a ser visto (ver alerta sobre leitura em lote abaixo). Se a busca não encontrar o termo na(s) edição(ões) verificada(s), dizer isso explicitamente — não presumir que "provavelmente está lá".
7. **Buscas amplas** ("em que década Blumenau em Cadernos menciona X?", "pesquise a década de 90") exigem varrer dezenas ou mais de cem edições — **sempre confirmar o escopo com o usuário antes de começar**, apresentando a contagem real de edições (buscada via passo 2, nunca estimada) e propondo um recorte sustentável (ex.: um ano por vez). Como referência de custo real observado: processar um único ano (~11-12 edições, leitura integral de cada uma) já consome uma fração muito grande do espaço de conversa disponível — tratar "década inteira" como 10 blocos de "um ano" separados, nunca como uma única leva.

## Download e leitura (mecânica validada em produção)

Os PDFs desta hemeroteca são digitalizações OCR pesadas (5-9 MB cada). Testes em produção mostraram um comportamento específico das ferramentas que **deve ser seguido à risca** para não desperdiçar chamadas nem arriscar alucinação:

1. **`WebFetch` direto no PDF quase sempre "falha" em extrair texto** — a resposta descreve o conteúdo como stream binário/`FlateDecode` ilegível. **Isso é esperado e não é motivo de alarme nem de nova tentativa**: o prompt enviado no `WebFetch` não importa muito (pode ser algo mínimo como "Extraia o texto deste PDF."), porque essa etapa não serve para ler o conteúdo — serve só para o passo 2.
2. **Mesmo "falhando", o `WebFetch` salva o binário localmente.** A resposta termina com uma linha do tipo `[Binary content (application/pdf, X MB) also saved to {caminho local}.pdf]`. **Sempre capturar esse caminho** — é ele que será lido de verdade no passo 3.
   - Exceção que quebra esse fallback: **arquivos acima de 10 MB fazem o `WebFetch` retornar erro `maxContentLength size of 10485760 exceeded` sem salvar nada localmente.** Não há caminho de recuperação dentro deste toolset (sem `Bash`/`curl` disponível, não há como forçar o download). Quando isso acontecer: **não tentar de novo esperando resultado diferente**, reportar ao usuário que aquela edição específica é inacessível por limitação técnica de tamanho, e seguir sem ela — nunca inventar o que "provavelmente" está no conteúdo não lido. Se o usuário puder fornecer o PDF por outro meio (ex.: caminho local), ler normalmente a partir dali.
3. **Ler o caminho local com `Read`, sem o parâmetro `pages`.** Usar `pages` aciona uma rota de renderização de página via `pdftoppm` (poppler), que tipicamente **não está instalado** neste ambiente e falha com `pdftoppm is not installed`. Chamar `Read` apenas com `file_path` (sem `pages`) extrai o texto diretamente e entrega o conteúdo completo, mesmo em PDFs de 25-30 páginas.
4. **Processar um arquivo por vez nesta etapa de leitura — nunca leitura em lote/paralela de múltiplos PDFs grandes.** Foi observado que, ao chamar `Read` em várias PDFs de uma vez, **apenas o conteúdo completo de um deles chega de fato ao modelo**; os demais retornam só a confirmação `PDF file read: {caminho} ({tamanho})`, sem o texto. Tratar essa confirmação como "arquivo ainda não lido de verdade" — nunca reportar achados (ou a ausência deles) de uma edição com base só nessa confirmação. É permitido `WebFetch` vários PDFs em paralelo (passo 1-2 funciona bem em lote, ele só baixa), mas o `Read` de cada um deve ser sequencial, um de cada vez, aguardando o texto completo aparecer antes de seguir para o próximo.
5. **Fluxo por edição, resumido:** `WebFetch` no PDF (prompt mínimo) → capturar caminho local salvo → `Read` no caminho local sem `pages` → só então analisar o texto retornado em busca do termo/tema pedido.

## Regras

- Sempre confirmar o link real no índice da década antes de tentar abrir um PDF — nunca extrapolar o padrão de nome de arquivo entre décadas.
- Resultado desta skill é fonte primária pesquisável — quando aprovado pelo usuário, o registro em `Design/Pesquisa/Estados/SantaCatarina/cidades/Blumenau/` segue o Modo 2 (Aprovar e Armazenar) do Historiador normalmente.
- Se o texto OCR estiver ilegível/corrompido em trechos, sinalizar isso ao usuário em vez de preencher a lacuna com suposição.
- Nunca declarar uma edição "lida" ou "sem achados" com base apenas na confirmação curta de tamanho do `Read` — só vale depois que o texto completo da edição foi de fato recebido e analisado.
- Edições acima de 10 MB são um limite técnico conhecido, não um erro pontual — reportar como tal na primeira ocorrência, sem repetir a tentativa.
