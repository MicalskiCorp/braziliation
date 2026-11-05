// Paridade (ADR-016): renderiza um efeito com o PixelFX ORIGINAL (cópia fixa em vendor/) e grava os
// buffers crus — cor e luz de cada quadro, antes da composição — para o pxfx comparar pixel a pixel.
// Uso (quem chama é o paridade.py):  node dump.mjs <id> <pasta-saida> [fps] [seed] [opts-json]
import { writeFileSync, mkdirSync } from "node:fs";
import { join, resolve } from "node:path";
import { pathToFileURL } from "node:url";
import { loadEffect, renderFrames } from "../../vendor/pixelfx/tools/lib/fxlib.mjs";

const [id, out, fpsArg, seedArg, optsArg] = process.argv.slice(2);
// um id ("fire/torch") vem da cópia fixa; um caminho .mjs é um cenário nosso (ex.: nucleo_teste.mjs)
async function carrega(alvo) {
  if (!alvo.endsWith(".mjs")) return loadEffect(alvo);
  const mod = await import(pathToFileURL(resolve(alvo)).href);
  const meta = { fps: 30, bg: "dark", loop: false, duration: 1, tags: [], options: {}, ...mod.meta };
  return { id: alvo, mod: { ...mod, meta }, meta };
}
const fx = await carrega(id);
const r = renderFrames(fx, {
  fps: fpsArg && fpsArg !== "-" ? +fpsArg : undefined,
  seed: seedArg && seedArg !== "-" ? +seedArg : undefined,
  options: optsArg ? JSON.parse(optsArg) : undefined,
});
mkdirSync(out, { recursive: true });
const n = r.frames.length, sz = r.w * r.h, buf = new Uint32Array(n * sz * 2);
r.frames.forEach((f, i) => {
  buf.set(f.raw, i * sz * 2);
  buf.set(f.light, i * sz * 2 + sz);
});
writeFileSync(join(out, "frames.bin"), Buffer.from(buf.buffer));
writeFileSync(join(out, "meta.json"), JSON.stringify({ id, w: r.w, h: r.h, n, fps: r.fps }));
