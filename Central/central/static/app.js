// Central do Braziliation — sem dependências. Toda ação é POST com o token da página (seguranca.py).
"use strict";
const TOKEN = document.querySelector('meta[name="central-token"]')?.content || "";

async function acao(url, dados) {
  const r = await fetch(url, { method: "POST", headers: { "X-Central-Token": TOKEN }, body: dados });
  try { return await r.json(); } catch { return { ok: false, erro: `resposta inválida (${r.status})` }; }
}

function mostrarErro(form, texto) {
  let alvo = form.querySelector(".erro-acao");
  if (!alvo) { alvo = document.createElement("div"); alvo.className = "erro-acao"; form.appendChild(alvo); }
  alvo.textContent = texto || "";
}

function mostrarTexto(texto) {
  const caixa = document.getElementById("saida-acao");
  if (caixa) { caixa.classList.remove("oculto"); caixa.querySelector("pre").textContent = texto; caixa.scrollIntoView(); }
  else alert(texto);
}

document.addEventListener("submit", async (ev) => {
  const form = ev.target;
  if (!form.matches("form[data-acao]")) return;
  ev.preventDefault();
  if (form.dataset.confirmar && !confirm(form.dataset.confirmar)) return;
  const dados = new FormData(form);
  if (ev.submitter && ev.submitter.name) dados.set(ev.submitter.name, ev.submitter.value);
  const botoes = form.querySelectorAll("button");
  botoes.forEach((b) => (b.disabled = true));
  mostrarErro(form, form.dataset.esperando || "");
  let j = await acao(form.action, dados);
  if (!j.ok && j.avisos && j.avisos.length) {
    if (confirm(j.avisos.join("\n\n") + "\n\nContinuar mesmo assim?")) {
      dados.set("confirmado", "1");
      j = await acao(form.action, dados);
    } else { botoes.forEach((b) => (b.disabled = false)); mostrarErro(form, ""); return; }
  }
  botoes.forEach((b) => (b.disabled = false));
  if (!j.ok) { mostrarErro(form, (j.erro || "falhou") + (j.saida ? "\n\n" + j.saida : "")); return; }
  mostrarErro(form, "");
  if (j.ir) { location.href = j.ir; return; }
  if (j.texto) { mostrarTexto(j.texto); return; }
  if ("limpar" in form.dataset) form.reset();
  if ("recarregar" in form.dataset) location.reload();
});

// ── fila: seleção e filtros ────────────────────────────────────────────────
function aplicarFiltros() {
  const filtros = [...document.querySelectorAll("[data-filtro]")].map((s) => [s.dataset.filtro, s.value]);
  document.querySelectorAll("tr[data-item]").forEach((tr) => {
    const visivel = filtros.every(([campo, valor]) => !valor || tr.dataset[campo] === valor);
    tr.classList.toggle("oculto", !visivel);
  });
}
document.querySelectorAll("[data-filtro]").forEach((s) => s.addEventListener("change", aplicarFiltros));
document.querySelector("[data-selecionar-visiveis]")?.addEventListener("change", (ev) => {
  document.querySelectorAll("tr[data-item]:not(.oculto) input[name=itens]:not(:disabled)")
    .forEach((c) => (c.checked = ev.target.checked));
  contarSelecao();
});
function contarSelecao() {
  const n = document.querySelectorAll("input[name=itens]:checked").length;
  const alvo = document.getElementById("n-selecionados");
  if (alvo) alvo.textContent = n;
}
document.addEventListener("change", (ev) => { if (ev.target.name === "itens") contarSelecao(); });

// ── painel e fila: atualização ao vivo ─────────────────────────────────────
const pagina = document.body.dataset.pagina;
if (pagina === "painel" || pagina === "fila" || pagina === "execucoes" || pagina === "saude") {
  let primeira = null;
  const fonte = new EventSource("/eventos");
  fonte.onmessage = (ev) => {
    if (primeira === null) { primeira = ev.data; return; }
    if (ev.data === primeira) return;
    const ocupado = document.querySelector("input[name=itens]:checked") ||
      (document.activeElement && ["TEXTAREA", "INPUT", "SELECT"].includes(document.activeElement.tagName));
    if (!ocupado) { location.reload(); return; }
    if (!document.querySelector(".banner")) {
      const b = document.createElement("div");
      b.className = "banner"; b.textContent = "Houve mudança — clique para atualizar";
      b.onclick = () => location.reload();
      document.body.appendChild(b);
    }
  };
}

// ── execução: chat ao vivo ─────────────────────────────────────────────────
const conversa = document.getElementById("conversa");
if (conversa) {
  const id = conversa.dataset.execucao;
  const estado = document.getElementById("estado");
  const fonte = new EventSource(`/execucao/${id}/eventos?desde=${conversa.dataset.proximo}`);
  const perto = () => window.innerHeight + window.scrollY >= document.body.scrollHeight - 160;
  fonte.onmessage = (ev) => {
    const d = JSON.parse(ev.data);
    const rolar = perto();
    conversa.insertAdjacentHTML("beforeend", d.html);
    if (rolar) window.scrollTo(0, document.body.scrollHeight);
  };
  fonte.addEventListener("estado", (ev) => {
    const d = JSON.parse(ev.data);
    if (estado) { estado.textContent = d.rotulo; estado.dataset.estado = d.estado; }
    const msg = document.getElementById("mensagem-estado");
    if (msg) msg.textContent = d.mensagem || "";
    document.querySelectorAll(".permissao[data-request]").forEach((card) => {
      if (!d.pendentes.includes(card.dataset.request)) card.querySelector(".acoes")?.remove();
    });
    document.querySelectorAll("[data-mostrar-em]").forEach((el) => {
      el.classList.toggle("oculto", !el.dataset.mostrarEm.split(" ").includes(d.estado));
    });
  });
  window.scrollTo(0, document.body.scrollHeight);
}

// ── validação: recarrega quando as checagens terminam ──────────────────────
const validacao = document.getElementById("validacao");
if (validacao) {
  let ultimo = null;
  const fonte = new EventSource(`/execucao/${validacao.dataset.execucao}/eventos?desde=${validacao.dataset.proximo}`);
  fonte.addEventListener("estado", (ev) => {
    if (ultimo === null) { ultimo = ev.data; return; }
    if (ev.data !== ultimo) {
      ultimo = ev.data;
      const digitando = document.activeElement && document.activeElement.tagName === "TEXTAREA";
      if (!digitando) location.reload();
    }
  });
  fonte.onmessage = () => {};
}
