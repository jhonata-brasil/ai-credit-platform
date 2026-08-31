const form = document.getElementById("form");
const statusEl = document.getElementById("status");
const resultEl = document.getElementById("result");
const btn = document.getElementById("btn");

function money(value) {
  return Number(value).toLocaleString("pt-BR", { style: "currency", currency: "BRL" });
}

function badge(risco, aprovado) {
  if (!aprovado) return `<span class="badge bad">Recusado</span>`;
  if (risco === "baixo") return `<span class="badge ok">Risco baixo</span>`;
  if (risco === "medio") return `<span class="badge mid">Risco médio</span>`;
  return `<span class="badge bad">Risco alto</span>`;
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const data = Object.fromEntries(new FormData(form).entries());
  const payload = {
    cnpj: data.cnpj,
    valor_solicitado: Number(data.valor_solicitado),
    prazo: Number(data.prazo),
    faturamento_mensal: Number(data.faturamento_mensal),
    responsavel_legal: data.responsavel_legal || null,
    email_contato: data.email_contato || null,
    telefone_contato: data.telefone_contato || null,
    dados_bancarios: data.dados_bancarios || null,
  };

  btn.disabled = true;
  statusEl.hidden = false;
  statusEl.textContent = "Consultando CNPJ e gerando análise...";
  resultEl.hidden = true;

  try {
    const response = await fetch("/api/v1/analyze-credit", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const json = await response.json();
    if (!response.ok) {
      throw new Error(json.detail || "Não foi possível concluir a análise");
    }

    const e = json.empresa;
    const a = json.analise;
    const p = json.proposta;
    resultEl.hidden = false;
    resultEl.innerHTML = `
      <h2>${e.razao_social}</h2>
      <p>${badge(a.risco, a.aprovado)} &nbsp; Score ${a.score}</p>
      <p>${a.motivo}</p>
      <h3>Empresa</h3>
      <dl class="kvs">
        <dt>CNPJ</dt><dd>${e.cnpj}</dd>
        <dt>Fantasia</dt><dd>${e.nome_fantasia || "-"}</dd>
        <dt>Situação</dt><dd>${e.situacao}</dd>
        <dt>Porte</dt><dd>${e.porte || "-"}</dd>
        <dt>Capital social</dt><dd>${money(e.capital_social)}</dd>
        <dt>CNAE</dt><dd>${e.cnae || "-"} ${e.cnae_descricao || ""}</dd>
        <dt>Endereço</dt><dd>${e.endereco || "-"}</dd>
        <dt>Cidade</dt><dd>${e.cidade || "-"} ${e.uf || ""}</dd>
        <dt>Abertura</dt><dd>${e.abertura || "-"} (${e.anos_atividade} anos)</dd>
      </dl>
      <h3>Critérios</h3>
      <ul>${a.criterios.map((c) => `<li>${c}</li>`).join("")}</ul>
      ${p ? `
        <h3>Proposta</h3>
        <dl class="kvs">
          <dt>Valor aprovado</dt><dd>${money(p.valor_aprovado)}</dd>
          <dt>Prazo</dt><dd>${p.prazo} meses</dd>
          <dt>Taxa</dt><dd>${p.taxa.toFixed(2)}% a.m.</dd>
          <dt>Validade</dt><dd>${p.validade_dias} dias</dd>
        </dl>
        <div class="actions">
          <a href="${json.pdf_url}" target="_blank">Baixar PDF</a>
          <a href="#" id="json-link">Baixar JSON</a>
        </div>
      ` : ""}
    `;
    const jsonLink = document.getElementById("json-link");
    if (jsonLink) {
      jsonLink.addEventListener("click", (ev) => {
        ev.preventDefault();
        const blob = new Blob([JSON.stringify(json, null, 2)], { type: "application/json" });
        const url = URL.createObjectURL(blob);
        const aTag = document.createElement("a");
        aTag.href = url;
        aTag.download = `analise-${payload.cnpj}.json`;
        aTag.click();
      });
    }
    statusEl.textContent = "Análise concluída.";
  } catch (error) {
    statusEl.textContent = error.message;
  } finally {
    btn.disabled = false;
  }
});
