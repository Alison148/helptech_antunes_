// ==================== CONFIG BASE ====================
// Detecta backend local ou produção (Vercel)
const API_BASE =
  window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1"
    ? "http://127.0.0.1:8000" // local
    : "https://helptech-antunes-git-main-alisons-projects-f41ebd8c.vercel.app"; // produção

// ==================== FUNÇÃO DOWNLOAD ====================
async function downloadBlob(url, options, filename = "arquivo.pdf") {
  try {
    const res = await fetch(url, options);
    if (!res.ok) throw new Error(`Erro ${res.status}`);
    const blob = await res.blob();
    const fileUrl = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = fileUrl;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    a.remove();
    setTimeout(() => URL.revokeObjectURL(fileUrl), 2000);
  } catch (err) {
    alert("Falha no download: " + err.message);
    console.error("Download falhou:", err);
  }
}

// ==================== FORM ORÇAMENTO ====================
const formOrc = document.querySelector("#formOrc");
if (formOrc) {
  formOrc.onsubmit = async (ev) => {
    ev.preventDefault();
    // coleta múltiplos serviços e valores (caso existam vários inputs)
    const cliente = formOrc.querySelector("[name='cliente']").value;
    const servicos = Array.from(formOrc.querySelectorAll("[name='servicos']"))
      .map((el) => el.value)
      .filter(Boolean);
    const valores = Array.from(formOrc.querySelectorAll("[name='valores']"))
      .map((el) => parseFloat(el.value || 0))
      .filter((v) => !isNaN(v));

    // envia via POST JSON
    const body = {
      cliente,
      itens: servicos.map((s, i) => ({ descricao: s, valor: valores[i] || 0 })),
    };

    await downloadBlob(`${API_BASE}/orcamento`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    }, "orcamento.pdf");
  };
}

// ==================== FORM NOTA FISCAL ====================
const formNF = document.querySelector("#formNF");
if (formNF) {
  formNF.onsubmit = async (ev) => {
    ev.preventDefault();
    const numero = formNF.querySelector("[name='numero']").value;
    const cliente = formNF.querySelector("[name='cliente']").value;
    const servicos = Array.from(formNF.querySelectorAll("[name='servico']"))
      .map((el) => el.value)
      .filter(Boolean);
    const valores = Array.from(formNF.querySelectorAll("[name='valor']"))
      .map((el) => parseFloat(el.value || 0))
      .filter((v) => !isNaN(v));

    const body = {
      numero,
      cliente,
      itens: servicos.map((s, i) => ({ descricao: s, valor: valores[i] || 0 })),
    };

    await downloadBlob(`${API_BASE}/nota-fiscal`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    }, `nota_${numero}.pdf`);
  };
}

// ==================== FORM CONTRATO ====================
const formContrato = document.querySelector("#formContrato");
if (formContrato) {
  formContrato.onsubmit = async (ev) => {
    ev.preventDefault();
    const params = new FormData(ev.target);
    const body = Object.fromEntries(params.entries());
    await downloadBlob(`${API_BASE}/contrato`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    }, "contrato.pdf");
  };
}

// ==================== FORM RECIBO ====================
const formRecibo = document.querySelector("#formRecibo");
if (formRecibo) {
  formRecibo.onsubmit = async (ev) => {
    ev.preventDefault();
    const params = new FormData(ev.target);
    const body = Object.fromEntries(params.entries());
    await downloadBlob(`${API_BASE}/recibo`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    }, "recibo.pdf");
  };
}

// ==================== FORM CARTA ====================
const formCarta = document.querySelector("#formCarta");
if (formCarta) {
  formCarta.onsubmit = async (ev) => {
    ev.preventDefault();
    const params = new FormData(ev.target);
    const body = Object.fromEntries(params.entries());
    await downloadBlob(`${API_BASE}/carta`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    }, "carta.pdf");
  };
}
