"""Desenha um corpo resolvido em pixels: volumes com profundidade e o acabamento do Braziliation.

Baseado no desenho em pixel do `rig.js` do PixelFX (MIT) — a técnica do Dead Cells: um corpo
3D de volumes simples (esferas, cápsulas, elipsoides, caixas) presos aos ossos, num buffer de
profundidade, com tons chapados e uma linha de tinta. O acabamento foi generalizado para as
regras da style-bible:

- **tons por luz única**: normal · luz em 4 limiares → 4 degraus da RAMPA DO MATERIAL (paleta
  regional; nunca cor inventada), peças do lado de trás um degrau abaixo;
- **órfãos**: pixel de tom sem vizinho igual na mesma peça assume o tom dos vizinhos;
- **costura × tinta**: entre peças que se tocam, costura no tom mais escuro; quando uma passa na
  frente da outra (degrau de profundidade), tinta;
- **contorno seletivo** (`contorno="seletivo"`): tinta no lado da sombra, o tom mais escuro do
  material no lado iluminado — "outline não uniforme" da style-bible. `"uniforme"` = o original;
- **mapa de origem** (`src`): cada pixel sabe de qual pixel da pose de DESCANSO veio, pelo
  referencial do osso — é o que leva a pele desenhada uma vez para qualquer pose (`pele.py`).
"""
from __future__ import annotations

import math

from ..cor import hex
from .vetor import add, dot, mv, sub, tv, unit

LUZ = unit([-0.55, 0.72, 0.5])           # luz de cima à esquerda, um pouco à frente
LUZ_TELA = (-0.6, -0.8)                  # a mesma luz na tela (y para baixo), para o contorno seletivo
INK = hex("#0e0c14")
# rampas do manequim (as do boneco do PixelFX): aceso → escuro
RAMPAS_MANEQUIM = {
    "casca": ["#e4e6ec", "#b6b9c3", "#868995", "#5c5e6a"],
    "nucleo": ["#6e707c", "#4b4d58", "#34353f", "#34353f"],
    "metal": ["#e8edf6", "#a4afc6", "#68748f", "#3a3448"],
}


class Raster:
    """Grade de rascunho com profundidade. Pés em (OX, OY); coordenadas de mundo x→, y↑, z para quem olha."""

    def __init__(self, k=1.0):
        self.k = k
        self.BW, self.BH = int(140 * k) + 8, int(96 * k) + 8
        self.OX, self.OY = self.BW // 2, int(76 * k) + 4
        n = self.BW * self.BH
        self.Z = [0.0] * n
        self.Tone = [0.0] * n
        self.Part = [0] * n
        self.Mat = [None] * n
        self.Fr = [-1] * n
        self.Dim = [0] * n
        self.touched = []
        self.cur_frame = -1
        self.cur_dim = 0
        self.clip = True
        self.so_parte = 0

    # ---- primitivas
    def plot(self, i, z, tone, part, mat):
        if self.so_parte and part != self.so_parte:
            return
        if self.Part[i] == 0:
            self.touched.append(i)
        elif z <= self.Z[i]:
            return
        self.Z[i] = z
        self.Tone[i] = tone
        self.Part[i] = part
        self.Mat[i] = mat
        self.Fr[i] = self.cur_frame
        self.Dim[i] = self.cur_dim

    def _idx(self, wx, wy):
        x, y = self.OX + wx, self.OY - wy
        if x < 0 or y < 0 or x >= self.BW or y >= self.BH:
            return -1
        return y * self.BW + x

    def esfera(self, c, r, part, mat):
        corte = 1.5 * self.k if self.clip else -1e9
        for wy in range(math.floor(c[1] - r), math.ceil(c[1] + r) + 1):
            if wy < corte:
                continue
            dy = wy - c[1]
            for wx in range(math.floor(c[0] - r), math.ceil(c[0] + r) + 1):
                dx = wx - c[0]
                d2 = dx * dx + dy * dy
                if d2 > r * r:
                    continue
                i = self._idx(wx, wy)
                if i < 0:
                    continue
                dz = math.sqrt(r * r - d2)
                self.plot(i, c[2] + dz, dot([dx / r, dy / r, dz / r], LUZ), part, mat)

    def capsula(self, a, b, ra, rb, part, mat, bojo=0.0):
        """Cápsula (o `sweep` do original): esferas ao longo de a→b, raio de ra a rb, bojo no meio."""
        n = max(2, math.ceil(math.dist(a, b) / 0.4))
        for kk in range(n + 1):
            u = kk / n
            self.esfera(add(a, [(b[0] - a[0]) * u, (b[1] - a[1]) * u, (b[2] - a[2]) * u]),
                        ra + (rb - ra) * u + bojo * math.sin(u * math.pi), part, mat)

    def elipsoide(self, c, R, r, part, mat):
        """Elipsoide de raios r nos eixos do referencial R, vista ao longo de z."""
        big = max(r)
        D = [1 / (r[0] * r[0]), 1 / (r[1] * r[1]), 1 / (r[2] * r[2])]
        A = [0.0] * 9
        for i in range(3):
            for j in range(3):
                A[i * 3 + j] = R[i * 3] * D[0] * R[j * 3] + R[i * 3 + 1] * D[1] * R[j * 3 + 1] + R[i * 3 + 2] * D[2] * R[j * 3 + 2]
        corte = 1.5 * self.k if self.clip else -1e9
        for wy in range(math.floor(c[1] - big), math.ceil(c[1] + big) + 1):
            if wy < corte:
                continue
            for wx in range(math.floor(c[0] - big), math.ceil(c[0] + big) + 1):
                dx, dy = wx - c[0], wy - c[1]
                qa = A[8]
                qb = 2 * (A[2] * dx + A[5] * dy)
                qc = A[0] * dx * dx + 2 * A[1] * dx * dy + A[4] * dy * dy - 1
                disc = qb * qb - 4 * qa * qc
                if disc < 0:
                    continue
                i = self._idx(wx, wy)
                if i < 0:
                    continue
                dz = (-qb + math.sqrt(disc)) / (2 * qa)
                nrm = unit([A[0] * dx + A[1] * dy + A[2] * dz, A[3] * dx + A[4] * dy + A[5] * dz,
                            A[6] * dx + A[7] * dy + A[8] * dz])
                self.plot(i, c[2] + dz, dot(nrm, LUZ), part, mat)

    def caixa(self, c, R, h, part, mat):
        """Caixa orientada (placa, bloco de máquina): centro c, eixos de R, meias medidas h. Normal da face."""
        big = math.sqrt(h[0] ** 2 + h[1] ** 2 + h[2] ** 2)
        eixos = [[R[0], R[3], R[6]], [R[1], R[4], R[7]], [R[2], R[5], R[8]]]
        corte = 1.5 * self.k if self.clip else -1e9
        for wy in range(math.floor(c[1] - big), math.ceil(c[1] + big) + 1):
            if wy < corte:
                continue
            for wx in range(math.floor(c[0] - big), math.ceil(c[0] + big) + 1):
                o = [wx - c[0], wy - c[1], 0.0]
                tmin, tmax, nrm = -1e9, 1e9, None
                ok = True
                for e, he in zip(eixos, h):
                    oe, de = dot(o, e), e[2]  # o raio anda em +z (para quem olha): d = (0, 0, 1)
                    if abs(de) < 1e-9:
                        if abs(oe) > he:
                            ok = False
                            break
                        continue
                    t1, t2 = (-he - oe) / de, (he - oe) / de
                    lado = -1 if t1 > t2 else 1
                    if t1 > t2:
                        t1, t2 = t2, t1
                    # a face vista é a do t MAIOR (a mais próxima de quem olha, +z)
                    if t2 < tmax:
                        tmax = t2
                        nrm = [e[0] * lado, e[1] * lado, e[2] * lado]
                    tmin = max(tmin, t1)
                if not ok or tmin > tmax or nrm is None:
                    continue
                i = self._idx(wx, wy)
                if i < 0:
                    continue
                self.plot(i, c[2] + tmax, dot(nrm, LUZ), part, mat)

    # ---- acabamento
    def acabar(self, frames_pose, frames_descanso, nomes_frames, rampas, contorno="seletivo", tinta=INK,
               metais=("metal",)):
        k = self.k
        BW = self.BW
        R = {m: [hex(c) for c in cs] for m, cs in rampas.items()}
        tons = {}
        for i in self.touched:
            v = self.Tone[i]
            t = 0 if v > 0.8 else 1 if v > 0.42 else 2 if v > 0.08 else 3
            tons[i] = min(3, t + self.Dim[i])
        # pixel de tom isolado na própria peça assume o tom dos vizinhos (a regra "sem pixel órfão")
        for i in self.touched:
            if self.Mat[i] in metais:
                continue
            t = tons[i]
            votos = [0, 0, 0, 0]
            igual = False
            for d in (-1, 1, -BW, BW):
                j = i + d
                if self.Part[j] != self.Part[i] or j not in tons:
                    continue
                u = tons[j]
                votos[u] += 1
                if u == t:
                    igual = True
            if not igual and any(votos):
                tons[i] = votos.index(max(votos))
        cor = {i: R.get(self.Mat[i], R[next(iter(R))])[tons[i]] for i in self.touched}
        # entre peças: costura (tom mais escuro do material) se encostam, tinta se uma passa na frente
        marcas = {}
        for i in self.touched:
            for d in (1, BW):
                j = i + d
                if self.Part[j] == 0 or self.Part[j] == self.Part[i]:
                    continue
                longe = i if self.Z[i] < self.Z[j] else j
                dz = abs(self.Z[i] - self.Z[j])
                metal = self.Mat[i] in metais or self.Mat[j] in metais
                if self.Mat[longe] in metais and dz < 1 * k:
                    continue
                if metal or dz > 2.2 * k:
                    marcas[longe] = tinta
                elif longe not in marcas:
                    marcas[longe] = R.get(self.Mat[longe], R[next(iter(R))])[3]
        cor.update(marcas)
        # o contorno: anel de 1 px; seletivo = tinta na sombra, tom escuro do material na luz
        anel = {}
        for i in self.touched:
            for d in (-1, 1, -BW, BW):
                j = i + d
                if self.Part[j] == 0 and j not in anel:
                    anel[j] = (i, d)
        saida = {"xs": [], "ys": [], "color": [], "src": [], "tom": [], "mat": [], "parte": [], "ink": [],
                 "costura": [], "viz": []}

        def src_de(i):
            f = self.Fr[i]
            if f < 0 or frames_descanso is None:
                return None
            nome = nomes_frames[f]
            A, R0 = frames_pose[nome], frames_descanso[nome]
            wx, wy = (i % BW) - self.OX, self.OY - (i // BW)
            lp = tv(A["R"], sub([wx, wy, self.Z[i]], A["t"]))
            rp = add(R0["t"], mv(R0["R"], lp))
            return (round(rp[0]), -round(rp[1]))

        def empurra(i, c, s, tom, mat, parte, ink, costura=False, viz=0):
            saida["costura"].append(costura)
            saida["viz"].append(viz)
            saida["xs"].append((i % BW) - self.OX)
            saida["ys"].append((i // BW) - self.OY)
            saida["color"].append(c)
            saida["src"].append(s)
            saida["tom"].append(tom)
            saida["mat"].append(mat)
            saida["parte"].append(parte)
            saida["ink"].append(ink)

        for i in self.touched:
            empurra(i, cor[i], src_de(i), tons[i], self.Mat[i], self.Part[i], cor[i] == tinta,
                    i in marcas and cor[i] != tinta, self.Part[i])
        for j, (i, d) in anel.items():
            c = tinta
            if contorno == "seletivo":
                dx, dy = (1 if d == 1 else -1 if d == -1 else 0), (1 if d == BW else -1 if d == -BW else 0)
                if dx * LUZ_TELA[0] + dy * LUZ_TELA[1] > 0.3 and tons[i] <= 1 and self.Mat[i] not in metais:
                    c = R.get(self.Mat[i], R[next(iter(R))])[3]
            empurra(j, c, src_de(i), 3, self.Mat[i], 0, c == tinta, False, self.Part[i])
        for i in self.touched:
            self.Part[i] = 0
        self.touched = []
        return saida


def silhueta(bipede, pose, escala=None):
    """Os pixels (x, y) do corpo + contorno de uma pose — para comparar com o posed() original."""
    from .corpo import desenhar
    r = desenhar(bipede, pose, RAMPAS_MANEQUIM, contorno="uniforme", com_src=False)
    return list(zip(r["xs"], r["ys"]))
