// Extrai a ATUAÇÃO (poses-chave, impactos, congelamento) de todos os efeitos do PixelFX original para JSON:
// é dado, não código — vira a biblioteca de movimentos do esqueleto (ADR-016).
// Uso: node extrair_atos.mjs <saida.json>
import { writeFileSync } from "node:fs";
import { allIds, loadEffect } from "../../vendor/pixelfx/tools/lib/fxlib.mjs";
import { actTiming } from "../../vendor/pixelfx/src/core/act.js";

const out = { origem: "https://github.com/patch-gg/pixelfx @ a841596 (MIT)", unidades: "px do boneco de 38 px (o esqueleto multiplica pela escala)", atos: {} };
for (const id of allIds()) {
  const fx = await loadEffect(id);
  const a = fx.mod.act;
  if (!a) continue;
  const tm = actTiming(fx.mod);
  out.atos[id] = {
    nome: fx.meta.name, desc: fx.meta.desc, duracao: fx.meta.duration, loop: !!fx.meta.loop,
    chaves: (a.poses ?? []).map(([t, pose, how]) => (how ? [t, pose, how] : [t, pose])),
    impactos: (a.hits ?? []).map((h) => ({ t: h.t, congela: h.stop ?? 0, tremor: h.shake ?? 0, amp: h.amp ?? 0, empurra: h.push ?? 0, pele: h.skin ?? null })),
    preparacao: tm.windup, recuperacao: tm.recovery, no_corpo: !!a.onBody,
  };
}
writeFileSync(process.argv[2], JSON.stringify(out, null, 1));
console.log(Object.keys(out.atos).length, "atos");
