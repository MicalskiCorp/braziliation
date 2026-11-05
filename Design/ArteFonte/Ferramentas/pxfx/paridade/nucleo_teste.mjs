// Cenário de paridade do NÚCLEO (ADR-016): um "efeito" que exercita toda a API do PixelFX — os 12 tipos de
// partícula, detritos, luzes, fogueiras, todas as formas do pintor, texto, máscara, raios. O gêmeo em Python é
// nucleo_teste.py; o paridade.py renderiza os dois e compara pixel a pixel. Mexeu num, mexa no outro igual.
import {
  Particles, Bits, Lights, Blazes, P, PF, B, Rng, sparkle, flare, band, crystal, bolt, forks, star, ngon,
  cycle, stream, burst, fly, PAL, WHITE, hex, fit, at, mix, ease, tileFbm, loopNoise, stockActor,
} from "../../vendor/pixelfx/src/core/index.js";

export const meta = {
  name: "Núcleo", size: [200, 150], origin: [100, 120], duration: 2, loop: false, fps: 20, bg: "dark",
  options: { palette: PAL.ice, seed: 3 },
};

export function create(o) {
  const R = new Rng(o.seed), floor = () => 0;
  const blazes = { add: () => {} };
  const ps = new Particles({ rng: R, ground: floor, haze: "#9bdcff", onLand: (x, y) => blazes.add(x, y, 1.2, 1) });
  const real = new Blazes(ps);
  blazes.add = (x, y, l, pw) => real.add(x, y, l, pw);
  const bits = new Bits({ ground: floor }), lights = new Lights(), C = fit(o.palette, 8);
  lights.add(0, -20, 40, C[5], 0.8, 1.2);
  const kinds = [P.SPARK, P.MOTE, P.STREAK, P.FLAKE, P.VAPOUR, P.DUST, P.STAR, P.EMBER, P.SMOKE, P.FIRE, P.BRAND, P.GRIT];
  for (let i = 0; i < 48; i++) {
    const k = kinds[i % kinds.length], a = R.range(0, Math.PI * 2), sp = R.range(40, 200);
    const flag = k === P.FIRE ? PF.SMOKES | (i % 2 ? PF.BIG : 0) : i % 5 === 0 ? PF.BACK : 0;
    ps.spawn(k, R.range(-20, 20), -R.range(5, 40), Math.cos(a) * sp, Math.sin(a) * sp - 60, R.range(0.3, 1.5),
      k === P.FIRE || k === P.SMOKE ? 0 : C[R.int(2, 7)], R.range(0.5, 3), i % 7 === 0 ? 0.2 : 0, flag);
  }
  for (let i = 0; i < 9; i++)
    bits.add({ kind: i % 3, x: R.range(-15, 15), y: -R.range(10, 30), vx: R.range(-90, 90), vy: -R.range(80, 220),
      a: R.range(0, 6), va: R.range(-20, 20), s: R.range(1.5, 4), c: C[R.int(3, 7)], bounce: 0.4, life: R.range(0.8, 1.8) });
  let t = 0;
  return {
    update(dt) { t += dt; ps.update(dt); bits.update(dt); lights.update(dt); real.update(dt); },
    drawBack(p) { ps.draw(p, "back"); real.drawBack(p); band(p, 0, 0, 30 + t * 10, 0.16, 3, 0.9, PAL.ice, (g) => Math.sin(g) < 0); },
    draw(p) {
      const u = Math.min(1, t / 2);
      p.shade(-95, -110, -60, -80, (x, y, out) => { out.c = at(C, (x + 95) / 35); out.a = 0.3 + 0.7 * ((y + 110) / 30); out.k = 0.1; });
      p.beam(-90, -70, -50, -40, 5, (uu, v) => (v < 0.5 ? C[7] : C[4]), (uu) => 1 - uu * 0.5);
      p.circle(-40, -95, 8 * (1 - u) + 1, (d) => at(C, 1 - d));
      p.ellipse(40, -95, 14, 6, C[3], 0.7);
      p.ring(70, -95, 12, 3, (v) => at(C, v));
      p.arc(0, -60, 30, (uu) => 6 * Math.sin(uu * Math.PI), -2.5, -0.6 + u * 0.5, (uu, v) => mix(C[2], WHITE, v), 1);
      p.poly(star(-70, -20, 4, 9, 5, t), C[6]);
      p.tri(60, -20, 80, -40, 90, -10, C[5], 0.6);
      p.polyline(ngon(85, -70, 9, 6, t), C[7]);
      p.polyline(bolt(new Rng(7), -90, -5, -40, -50), WHITE);
      for (const f of forks(new Rng(9), bolt(new Rng(8), 40, -5, 90, -50), { count: 2, len: 14 })) p.polyline(f, C[6]);
      p.glowLine(-90, -5, -40, -50, 5, C[5], 0.4);
      p.glowRing(0, -20, 20 + t * 15, 5, C[6], 0.5);
      p.text("NUCLEO 01", -96, -116, C[7], { font: "big", outline: C[0], shadow: C[1] });
      p.text(`T${Math.round(t * 100)}`, 96, -116, WHITE, { align: "right" });
      const actor = stockActor(2);
      p.outline(actor.mask, 40 + actor.x, actor.y, C[6], 0.8);
      p.mask(actor.mask, 40 + actor.x, actor.y, (mx, my) => at(C, my / actor.h), 0.5);
      crystal(p, -20, 0, 18 * u + 2, 6, 2, PAL.ice, { glint: u });
      crystal(p, -8, 0, 12, 5, -1, PAL.ice, { white: t < 0.2 });
      sparkle(p, 20, -30, 6 * (1 - u), C[6], C[4], 0.6);
      flare(p, -30, -40, 10 * (1 - u), 0.5, PAL.ice);
      cycle(t, 1, 6, 5, 0.8, (age, life, r) => { const [x, y] = fly(r.range(-60, 60), -10, r.range(-20, 20), -r.range(30, 60), age, 40, 1); p.dot(x, y, C[6], 1 - age / life); });
      stream(t, 0, 1.5, 8, 6, 0.6, (age, life, r) => p.px(-60 + age * 40, -60 - r.range(0, 20), C[5]));
      burst(5, 11, (r, i) => p.light(r.range(-50, 50), -r.range(60, 100), C[7], 0.5));
      for (let i = 0; i < 8; i++) p.dot(-60 + i * 3, -120 + tileFbm(i, t * 4, 8, 8, 2) * 4 + loopNoise(u, 1, 3) * 3, C[ease.outBack(u) > 0.5 ? 7 : 3], ease.inOutSine(i / 8));
      p.sprite(["..##..", ".#oo#.", "#oooo#", ".#oo#."], { "#": "#222034", o: hex("#ffe26b") }, 60, -100, { scale: 2, flip: true });
      bits.draw(p);
      ps.draw(p, "front");
      lights.draw(p);
    },
  };
}
