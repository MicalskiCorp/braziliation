// Central do Braziliation — sem dependências. Toda ação é POST com o token da página (seguranca.py).
"use strict";
const TOKEN = document.querySelector('meta[name="central-token"]')?.content || "";

// Ações desta aba ainda sem resposta: nada recarrega no meio de uma (2026-11-03: a validação recarregava
// durante o pre-commit e voltava com o botão Commitar habilitado — deu para clicar duas vezes).
let emVoo = 0;
// Depois de uma ação que falhou a página fica como está — a saída do erro não some num recarregamento.
let segurarRecarga = false;

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
  if (form.dataset.enviando) return;   // a primeira ação ainda não voltou (o servidor também recusa)
  if (form.dataset.confirmar && !confirm(form.dataset.confirmar)) return;
  const dados = new FormData(form);
  if (ev.submitter && ev.submitter.name) dados.set(ev.submitter.name, ev.submitter.value);
  const botoes = form.querySelectorAll("button");
  const travar = (sim) => {
    botoes.forEach((b) => (b.disabled = sim));
    if (sim) form.dataset.enviando = "1"; else delete form.dataset.enviando;
  };
  travar(true);
  mostrarErro(form, form.dataset.esperando || "");
  emVoo++;
  let j;
  try {
    j = await acao(form.action, dados);
    if (!j.ok && j.avisos && j.avisos.length) {
      if (!confirm(j.avisos.join("\n\n") + "\n\nContinuar mesmo assim?")) { travar(false); mostrarErro(form, ""); return; }
      dados.set("confirmado", "1");
      j = await acao(form.action, dados);
    }
  } catch {
    j = { ok: false, erro: "a Central não respondeu — ela pode estar reiniciando" };
  } finally {
    emVoo--;
  }
  if (!j.ok) {
    travar(false);
    segurarRecarga = true;
    mostrarErro(form, (j.erro || "falhou") + (j.saida ? "\n\n" + j.saida : ""));
    return;
  }
  mostrarErro(form, "");
  // Ação que troca de página fica travada até a troca: nada de segundo clique no caminho.
  if (j.ir) { location.href = j.ir; return; }
  if ("recarregar" in form.dataset) { location.reload(); return; }
  travar(false);
  if (j.texto) mostrarTexto(j.texto);
  if ("limpar" in form.dataset) form.reset();
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

// ── atualização ao vivo ────────────────────────────────────────────────────
// Consulta curta a cada 1,5 s (8 s com a aba escondida), não conexão aberta: o navegador aceita só 6
// conexões por endereço, e cada aba com EventSource segurava uma. E a página que volta pelo histórico
// vem do cache do navegador sem nada rodando — por isso o pageshow recarrega.
window.addEventListener("pageshow", (ev) => { if (ev.persisted) location.reload(); });

function vigiar(url, aoChegar) {
  let timer = null, rodando = false;
  async function passo() {
    if (rodando) return;
    rodando = true;
    clearTimeout(timer);
    try {
      const r = await fetch(url(), { cache: "no-store" });
      if (r.ok) await aoChegar(await r.json());
    } catch { /* Central reiniciando: tenta de novo no próximo passo */ }
    rodando = false;
    clearTimeout(timer);
    timer = setTimeout(passo, document.hidden ? 8000 : 1500);
  }
  document.addEventListener("visibilitychange", () => { if (!document.hidden) passo(); });
  passo();
}

function atualizarNav(d) {
  const b = document.getElementById("nav-badge");
  if (!b || d.atencao === undefined) return;
  const n = d.atencao || d.ativas;
  b.textContent = n;
  b.classList.toggle("cinza", !d.atencao);
  b.classList.toggle("oculto", !n);
}

function avisarMudanca() {
  if (document.querySelector(".banner")) return;
  const b = document.createElement("div");
  b.className = "banner"; b.textContent = "Houve mudança — clique para atualizar";
  b.onclick = () => location.reload();
  document.body.appendChild(b);
}

function podeRecarregar() {
  if (emVoo || segurarRecarga || document.querySelector("input[name=itens]:checked")) return false;
  const a = document.activeElement;
  if (a && (a.tagName === "TEXTAREA" || (a.tagName === "INPUT" && a.type === "text"))) return false;
  return ![...document.querySelectorAll("textarea, input[type=text]")].some((t) => t.value !== t.defaultValue);
}

function recarregarOuAvisar() {
  if (podeRecarregar()) location.reload(); else avisarMudanca();
}

// Troca cada [data-vivo] pela versão nova da mesma página, sem perder seleção, filtro nem o que se digita.
// Região em uso (foco, <details> aberto, ação em andamento) espera: devolve true para tentar de novo.
async function atualizarRegioes() {
  const r = await fetch(location.href, { cache: "no-store" });
  if (!r.ok) return true;
  const novo = new DOMParser().parseFromString(await r.text(), "text/html");
  const lista = (doc, sel, attr) => [...doc.querySelectorAll(sel)].map((el) => el.getAttribute(attr)).join("\n");
  if (lista(novo, "tr[data-id]", "data-id") !== lista(document, "tr[data-id]", "data-id") ||
      lista(novo, "[data-vivo]", "data-vivo") !== lista(document, "[data-vivo]", "data-vivo")) {
    recarregarOuAvisar();      // entrou ou saiu item: a estrutura mudou
    return false;
  }
  let restou = false;
  novo.querySelectorAll("[data-vivo]").forEach((el) => {
    const atual = document.querySelector(`[data-vivo="${CSS.escape(el.dataset.vivo)}"]`);
    if (!atual || (atual.innerHTML === el.innerHTML && atual.className === el.className)) return;
    if (atual.contains(document.activeElement) || atual.matches("details[open]") ||
        atual.querySelector("details[open], form[data-enviando]")) { restou = true; return; }
    atual.replaceWith(document.importNode(el, true));
  });
  novo.querySelectorAll("tr[data-id]").forEach((tr) => {
    const atual = document.querySelector(`tr[data-id="${CSS.escape(tr.dataset.id)}"]`);
    if (!atual) return;
    atual.className = tr.className;
    ["status", "prioridade", "responsavel"].forEach((k) => (atual.dataset[k] = tr.dataset[k] || ""));
    const cbNovo = tr.querySelector("input[name=itens]"), cb = atual.querySelector("input[name=itens]");
    if (cb && cbNovo) { cb.disabled = cbNovo.disabled; if (cb.disabled) cb.checked = false; }
  });
  aplicarFiltros();
  contarSelecao();
  return restou;
}

// Painel, fila, execuções, saúde: qualquer execução que muda de estado, ou TODO editado, atualiza as regiões.
const pagina = document.body.dataset.pagina;
if (["painel", "fila", "execucoes", "saude"].includes(pagina)) {
  let ultimo = null, restou = false;
  vigiar(() => "/vivo", async (d) => {
    atualizarNav(d);
    if (ultimo === null) { ultimo = d.v; return; }
    if (d.v === ultimo && !restou) return;
    if (emVoo) return;           // a consulta depois da resposta atualiza
    ultimo = d.v;
    restou = await atualizarRegioes();
  });
}

// ── execução: chat ao vivo ─────────────────────────────────────────────────
function aplicarEstado(d) {
  const estado = document.getElementById("estado");
  if (estado) { estado.textContent = d.rotulo; estado.dataset.estado = d.estado; }
  const msg = document.getElementById("mensagem-estado");
  if (msg) msg.textContent = d.mensagem || "";
  document.querySelectorAll(".permissao[data-request]").forEach((card) => {
    if (!d.pendentes.includes(card.dataset.request)) card.querySelector(".acoes")?.remove();
  });
  document.querySelectorAll("[data-mostrar-em]").forEach((el) => {
    if (el.dataset.enviando) return;
    el.classList.toggle("oculto", !el.dataset.mostrarEm.split(" ").includes(d.estado));
  });
}

const conversa = document.getElementById("conversa");
if (conversa) {
  const id = conversa.dataset.execucao;
  let proximo = Number(conversa.dataset.proximo) || 0, assinatura = null;
  const perto = () => window.innerHeight + window.scrollY >= document.body.scrollHeight - 160;
  vigiar(() => `/execucao/${id}/novidades?desde=${proximo}`, (d) => {
    atualizarNav(d);
    const rolar = perto();
    let chegou = false;
    for (const e of d.entradas) {
      if (e.i < proximo) continue;     // uma consulta atrasada não duplica a mensagem
      conversa.insertAdjacentHTML("beforeend", e.html);
      proximo = e.i + 1;
      chegou = true;
    }
    if (chegou && rolar) window.scrollTo(0, document.body.scrollHeight);
    if (d.assinatura !== assinatura) { assinatura = d.assinatura; aplicarEstado(d.estado); }
  });
  window.scrollTo(0, document.body.scrollHeight);
}

// ── validação: estado novo recarrega; checagens e mensagem se atualizam no lugar ───
const validacao = document.getElementById("validacao");
if (validacao) {
  const id = validacao.dataset.execucao;
  const estadoDaPagina = document.getElementById("estado")?.dataset.estado;
  let assinatura = null, restou = false;
  vigiar(() => `/execucao/${id}/novidades?desde=999999999`, async (d) => {
    atualizarNav(d);
    if (emVoo) return;           // a resposta da ação decide (navega ou mostra o erro)
    if (d.estado.estado !== estadoDaPagina) { recarregarOuAvisar(); return; }
    if (assinatura === null) { assinatura = d.assinatura; return; }
    if (d.assinatura === assinatura && !restou) return;
    assinatura = d.assinatura;
    restou = await atualizarRegioes();
  });
}
