// ==================== CONFIG BASE ====================
// Detecta backend local ou produção (Vercel)
const API_BASE =
  window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1"
    ? "http://127.0.0.1:8000" // local
    : "https://helptech-antunes-git-main-alisons-projects-f41ebd8c.vercel.app"; // produção

// ==================== FUNÇÃO DOWNLOAD ====================
async function download(endpoint, filename = "arquivo.pdf") {
  try {
    const res = await fetch(`${API_BASE}${endpoint}`, { mode: "cors" });
    if (!res.ok) throw new Error(`Erro ${res.status}`);
    const blob = await res.blob();
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    a.remove();
    setTimeout(() => URL.revokeObjectURL(url), 2000);
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
    const params = new URLSearchParams(new FormData(ev.target));
    await download(`/gerar-pdf?${params}`, "orcamento.pdf");
  };
}

// ==================== FORM NOTA FISCAL ====================
const formNF = document.querySelector("#formNF");
if (formNF) {
  formNF.onsubmit = async (ev) => {
    ev.preventDefault();
    const data = new FormData(ev.target);
    const params = new URLSearchParams();
    params.set("numero", data.get("numero"));
    params.set("cliente", data.get("cliente"));
    params.append("servicos", data.get("servico"));
    params.append("valores", data.get("valor"));
    await download(`/nota-fiscal?${params}`, `nota_${data.get("numero")}.pdf`);
  };
}

// ==================== FORM CONTRATO ====================
const formContrato = document.querySelector("#formContrato");
if (formContrato) {
  formContrato.onsubmit = async (ev) => {
    ev.preventDefault();
    const params = new URLSearchParams(new FormData(ev.target));
    await download(`/contrato?${params}`, "contrato.pdf");
  };
}

// ==================== FORM RECIBO ====================
const formRecibo = document.querySelector("#formRecibo");
if (formRecibo) {
  formRecibo.onsubmit = async (ev) => {
    ev.preventDefault();
    const params = new URLSearchParams(new FormData(ev.target));
    await download(`/recibo?${params}`, "recibo.pdf");
  };
}

// ==================== FORM CARTA ====================
const formCarta = document.querySelector("#formCarta");
if (formCarta) {
  formCarta.onsubmit = async (ev) => {
    ev.preventDefault();
    const params = new URLSearchParams(new FormData(ev.target));
    await download(`/carta?${params}`, "carta.pdf");
  };
}
