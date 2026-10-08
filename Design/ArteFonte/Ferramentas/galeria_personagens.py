#!/usr/bin/env python3
"""Regenera todas as páginas de personagem e monta o hub da galeria.

Por que existe: a galeria do claude.ai **não tem pastas**. Os artefatos ficam
numa lista única por data de atualização, misturados com tudo que já foi
publicado. O agrupamento possível é por conteúdo, não por diretório — então o
projeto mantém um HUB: uma página só que lista todos os personagens, com capa,
status e link. É ela que se fixa na barra lateral, e é por ela que se navega.

A fonte única de quem está na galeria é `IA/Paginas/galeria.json`. Cada entrada
aponta para a spec do asset; o resto (título, status, histórico) vem do
`{asset}.pagina.json` que já existe no context pack.

O que este script faz, numa passada:
  1. regenera a página de cada personagem com `pagina_personagem.py`;
  2. monta o hub com a capa de cada um;
  3. imprime as URLs a republicar — a do hub e a de cada personagem.

Uso:
  py galeria_personagens.py                 # regenera tudo em IA/Paginas/
  py galeria_personagens.py --so-hub        # só o hub, sem refazer as páginas
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

from PIL import Image

from render_spec import load_palette

RAIZ = Path(__file__).resolve().parents[1]          # Design/ArteFonte
PAGINAS = RAIZ / "IA" / "Paginas"
REGISTRO = PAGINAS / "galeria.json"

MODELO = """<title>Personagens do Braziliation</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@600;700&family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans:wght@400;500;600&display=swap">
<style>
  :root {{
    --ground: #e8e3d9; --panel: #f6f3ec; --panel-2: #ded7c9; --line: #c6bda9;
    --ink: #1b1616; --ink-soft: #5c554a; --brass: #8a6b22; --brass-lit: #c9a558;
    --stage: #232c33; --floor: #3a3f44; --ok: #3f6b3a;
  }}
  @media (prefers-color-scheme: dark) {{
    :root:not([data-theme="light"]) {{
      --ground: #15191d; --panel: #1c2227; --panel-2: #232c33; --line: #333d45;
      --ink: #e9e3d6; --ink-soft: #97a0a8; --brass: #c9a558; --brass-lit: #e2c485;
      --stage: #1b1616; --floor: #2b3238; --ok: #7fb069;
    }}
  }}
  :root[data-theme="dark"] {{
    --ground: #15191d; --panel: #1c2227; --panel-2: #232c33; --line: #333d45;
    --ink: #e9e3d6; --ink-soft: #97a0a8; --brass: #c9a558; --brass-lit: #e2c485;
    --stage: #1b1616; --floor: #2b3238; --ok: #7fb069;
  }}
  body {{ background: var(--ground); color: var(--ink); font-family: "IBM Plex Sans", system-ui, sans-serif; font-size: 15px; line-height: 1.55; }}
  .wrap {{ max-width: 960px; margin: 0 auto; padding-inline: 16px; padding-block: 28px 56px; }}
  header {{ display: flex; flex-wrap: wrap; align-items: baseline; gap: 6px 14px; }}
  h1 {{ font-family: "Barlow Condensed", "Arial Narrow", sans-serif; font-weight: 700; font-size: clamp(32px, 6vw, 46px); text-transform: uppercase; margin: 0; }}
  .tag {{ font-family: "IBM Plex Mono", monospace; font-size: 11px; letter-spacing: .08em; text-transform: uppercase; color: var(--brass); border: 1px solid var(--line); padding: 2px 7px; border-radius: 2px; }}
  .sub {{ color: var(--ink-soft); max-width: 64ch; margin: 6px 0 24px; }}
  .galeria {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(230px, 1fr)); gap: 14px; }}
  .ficha {{ display: block; text-decoration: none; color: inherit; background: var(--panel); border: 1px solid var(--line); border-radius: 3px; overflow: hidden; }}
  .ficha:hover {{ border-color: var(--brass); }}
  .ficha .palco {{ background: var(--stage); position: relative; display: grid; place-items: center; padding: 14px 0 0; }}
  .ficha .palco::after {{ content: ""; position: absolute; inset: auto 0 0 0; height: 20%; background: var(--floor); }}
  .ficha canvas {{ position: relative; z-index: 1; image-rendering: pixelated; display: block; }}
  .ficha .corpo {{ padding: 11px 13px 13px; }}
  .ficha .nome {{ font-family: "Barlow Condensed", "Arial Narrow", sans-serif; font-weight: 700; text-transform: uppercase; font-size: 19px; letter-spacing: .02em; }}
  .ficha .resumo {{ color: var(--ink-soft); font-size: 13px; margin-top: 3px; }}
  .ficha .pe {{ display: flex; flex-wrap: wrap; gap: 6px; margin-top: 9px; align-items: center; }}
  .selo {{ font-family: "IBM Plex Mono", monospace; font-size: 10.5px; letter-spacing: .06em; text-transform: uppercase; border: 1px solid var(--line); border-radius: 2px; padding: 1px 6px; color: var(--ink-soft); }}
  .selo.ok {{ color: var(--ok); border-color: var(--ok); }}
  .selo.anim {{ color: var(--brass); border-color: var(--brass); }}
  h2 {{ font-family: "Barlow Condensed", "Arial Narrow", sans-serif; text-transform: uppercase; letter-spacing: .04em; font-size: 20px; margin: 32px 0 3px; }}
  .dica {{ color: var(--ink-soft); font-size: 13px; margin: 0 0 12px; }}
  ol {{ padding-left: 20px; color: var(--ink-soft); font-size: 14px; }}
  ol li {{ margin-bottom: 6px; }}
  footer {{ margin-top: 30px; padding-top: 14px; border-top: 1px solid var(--line); color: var(--ink-soft); font-size: 13px; }}
  code {{ font-family: "IBM Plex Mono", monospace; font-size: .92em; background: var(--panel-2); padding: 1px 5px; border-radius: 2px; }}
</style>

<div class="wrap">
  <header>
    <h1>Personagens do Braziliation</h1>
    <span class="tag">{n} personagens</span>
    <span class="tag">96×96 · 48 PPU</span>
  </header>
  <p class="sub">
    A galeria do claude.ai não tem pastas — os artefatos ficam numa lista única por data.
    Esta página é o agrupamento: a porta de entrada para a ficha de cada personagem, onde
    moram os sprites, as variantes, a animação rodando e o histórico do que mudou.
  </p>

  <div class="galeria" id="galeria"></div>

  <h2>Como isto se mantém</h2>
  <p class="dica">Para a galeria não desandar conforme o projeto cresce.</p>
  <ol>
    <li>A lista de quem está aqui vive em <code>Design/ArteFonte/IA/Paginas/galeria.json</code>, no repositório.</li>
    <li>Cada ficha é <strong>gerada da spec</strong> do asset — não tem como mostrar arte velha.</li>
    <li>A URL de cada personagem fica no <code>{{asset}}.pagina.json</code> do context pack, e é nela que se republica. Personagem nunca ganha página nova: ganha versão nova da mesma página.</li>
    <li>Mudou arte ou entrou animação? <code>py galeria_personagens.py</code> regenera tudo e diz o que republicar.</li>
  </ol>

  <footer>{rodape}</footer>
</div>

<script id="dados" type="application/json">{dados}</script>
<script>
  const D = JSON.parse(document.getElementById("dados").textContent);
  const host = document.getElementById("galeria");
  D.forEach(p => {{
    const a = document.createElement("a");
    a.className = "ficha"; a.href = p.url; a.target = "_blank"; a.rel = "noopener";
    const palco = document.createElement("div"); palco.className = "palco";
    const c = document.createElement("canvas");
    const escala = 2;
    c.width = p.largura * escala; c.height = p.altura * escala;
    palco.appendChild(c);
    const corpo = document.createElement("div"); corpo.className = "corpo";
    const selos = [`<span class="selo ${{p.status === "aprovado" ? "ok" : ""}}">${{p.status}}</span>`,
                   `<span class="selo">${{p.variantes}} variantes</span>`];
    if (p.animacoes) selos.push(`<span class="selo anim">${{p.animacoes}} animação(ões)</span>`);
    corpo.innerHTML = `<div class="nome">${{p.titulo}}</div><div class="resumo">${{p.resumo}}</div>` +
                      `<div class="pe">${{selos.join("")}}</div>`;
    a.append(palco, corpo); host.appendChild(a);
    const img = new Image();
    img.onload = () => {{
      const ctx = c.getContext("2d");
      ctx.imageSmoothingEnabled = false;
      ctx.drawImage(img, 0, 0, c.width, c.height);
    }};
    img.src = p.capa;
  }});
</script>
"""


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--so-hub", action="store_true", help="Não regenera as páginas, só o hub")
    args = ap.parse_args()

    registro = json.loads(REGISTRO.read_text(encoding="utf-8"))
    hub_dir = PAGINAS / "_hub"
    (hub_dir / "capas").mkdir(parents=True, exist_ok=True)

    dados, pendentes = [], []
    for entrada in registro["personagens"]:
        spec_path = (PAGINAS / entrada["spec"]).resolve()
        spec = json.loads(spec_path.read_text(encoding="utf-8"))
        meta_path = spec_path.with_name(spec_path.name.replace(".spec.json", ".pagina.json"))
        meta = json.loads(meta_path.read_text(encoding="utf-8")) if meta_path.exists() else {}
        destino = PAGINAS / entrada["asset"]

        if not args.so_hub:
            r = subprocess.run([sys.executable, str(Path(__file__).with_name("pagina_personagem.py")),
                                str(spec_path), "--saida", str(destino)],
                               capture_output=True, text=True, encoding="utf-8", errors="replace")
            if r.returncode != 0:
                sys.exit(f"ERRO ao gerar {entrada['asset']}:\n{r.stdout}{r.stderr}")
            # o console do Windows e cp1252: nao repasse bytes que ele nao sabe imprimir
            print(r.stdout.strip().encode('ascii', 'replace').decode('ascii'))

        # capa: o output escolhido no registro, renderizado para o hub
        palette = load_palette((spec_path.parent / spec["palette"]).resolve())
        largura, altura = spec["size"]
        rows = next(o["rows"] for o in spec["outputs"] if o["id"] == entrada["capa"])
        img = Image.new("RGBA", (largura, altura), (0, 0, 0, 0))
        px = img.load()
        for y, linha in enumerate(rows):
            for x, ch in enumerate(linha):
                if ch != ".":
                    px[x, y] = palette[ch]
        capa = f"capas/{entrada['asset']}.png"
        img.save(hub_dir / capa)

        em_anim = {fid for ids in spec.get("sheets", {}).values() for fid in ids}
        dados.append({
            "titulo": meta.get("titulo", entrada["asset"]),
            "resumo": (meta.get("resumo", "")[:150] + "…") if len(meta.get("resumo", "")) > 150 else meta.get("resumo", ""),
            "status": meta.get("status", "rascunho"),
            "url": meta.get("artefato", ""),
            "capa": capa, "largura": largura, "altura": altura,
            "variantes": len([o for o in spec["outputs"] if o["id"] not in em_anim]),
            "animacoes": len(spec.get("sheets", {})),
        })
        if not meta.get("artefato"):
            pendentes.append(entrada["asset"])

    html = MODELO.format(
        n=len(dados),
        dados=json.dumps(dados, ensure_ascii=False),
        rodape="Gerado por <code>galeria_personagens.py</code> a partir de "
               "<code>IA/Paginas/galeria.json</code>. As páginas e as capas ficam em "
               "<code>Design/ArteFonte/IA/Paginas/</code>, versionadas junto com o projeto — "
               "o que foi publicado está sempre reproduzível a partir do repositório.",
    )
    (hub_dir / "index.html").write_text(html, encoding="utf-8")
    print(f"\nOK: {hub_dir / 'index.html'} — {len(dados)} personagem(ns)")
    if registro.get("hub"):
        print(f"     republicar o hub em: {registro['hub']}")
    else:
        print("     primeiro publish do hub: guarde a URL em galeria.json no campo \"hub\"")
    for a in pendentes:
        print(f"     AVISO: {a} ainda não tem URL no campo \"artefato\" do .pagina.json")


if __name__ == "__main__":
    main()
