# Arquivos de Fonte — Imagens e Documentos Aprovados

Imagem ou documento que chegou pela captura de entrevistas (ADR-009) e foi **aprovado na
curadoria** do `@Historiador` mora aqui. É a única cópia versionada: o arquivo bruto
continua em `../../Entrevistas/_processado/`, fora do git.

> Gerenciado pela skill `processar-entrevistas`. Nada entra aqui sem aprovação explícita
> do responsável pelo projeto — e, se o material for de terceiro, sem consentimento
> confirmado para guardar e usar.

## Nomenclatura

`{estado-ou-tema}-{assunto-curto}-{AAAA-MM-DD}.{ext}` — a data é a da captura, não a do
documento retratado. Ex.: `sc-ata-sociedade-teatral-2026-09-21.jpg`.

## Registro

| # | Arquivo | Origem | Conteúdo | Usado em | Data de captura |
|---|---------|--------|----------|----------|-----------------|
| — | _(vazio)_ | | | | |

`Origem` = remetente do `meta.json` da captura. `Usado em` = arquivo de pesquisa que cita
este material (`Estados/…` ou `Temas/…`), ou `—` enquanto só arquivado.

## Limite de tamanho

Arquivo acima de ~5 MB **não** vem para cá: fica em `_processado/` e a pesquisa referencia
o caminho. O repo não tem regra LFS para `.jpg`/`.pdf`, e binário grande em blob comum
incha o histórico para sempre.
