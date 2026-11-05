// Paridade do ESQUELETO (ADR-016): juntas e silhueta de cada pose pelo rig.js ORIGINAL.
// Uso (quem chama é o paridade/esqueleto.py):  node esqueleto.mjs <poses.json>  → JSON no stdout
import { readFileSync } from "node:fs";
import { skeleton, posed } from "../../vendor/pixelfx/src/core/rig.js";
import { poseAt } from "../../vendor/pixelfx/src/core/act.js";

const { poses, trilhas } = JSON.parse(readFileSync(process.argv[2], "utf8"));
const out = { poses: [], trilhas: [] };
for (const pose of poses) {
  const s = skeleton(pose), r = posed(pose), px = [];
  for (let i = 0; i < r.n; i++) px.push([r.xs[i], r.ys[i]]);
  out.poses.push({ juntas: s.joints, pixels: px });
}
// interpolação de poses: amostra cada trilha em passos de 1/60 s
for (const tr of trilhas ?? []) {
  const amostras = [];
  for (let t = tr[0][0] - 0.1; t <= tr[tr.length - 1][0] + 0.1; t += 1 / 60) amostras.push(poseAt(tr, t));
  out.trilhas.push(amostras);
}
process.stdout.write(JSON.stringify(out));
