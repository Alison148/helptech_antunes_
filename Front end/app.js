// ==================== ATALHO ====================
const $ = (q, el = document) => el.querySelector(q);

// ==================== URL BASE ====================
// Detecta automaticamente backend (local ou produção)
const API_BASE =
  window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1"
    ? "http://127.0.0.1:8000"   // backend local
    : "https://seu-dominio-api.vercel.app"; // backend produção

// ==================== FUNÇÃO DOWNLOAD ====================
/**
 * Faz download de um arquivo PDF vindo da API
 * @param {string} endpoint - Caminho da API (ex: "/nota-fiscal?...") 
 * @param {string} filename - Nome sugerido para o arquivo
 */
async function download(endpoint, filename = "arquivo.pdf") {
  try {
    const res = await fetch(`${API_BASE}${endpoint}`, { mode: "cors" });
    if (!res.ok) throw new Error(`Erro ${res.status}: falha ao gerar PDF`);

    const blob = await res.blob();
    const objectUrl = URL.createObjectURL(blob);

    // tenta pegar o nome do arquivo do header
    const cd = res.headers.get("content-disposition");
    if (cd) {
      const match = cd.match(/filename="?([^"]+)"?/i);
      if (match) filename = match[1];
    }

    const a = document.createElement("a");
    a.href = objectUrl;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    a.remove();

    // libera depois de um tempo (para não cancelar antes)
    setTimeout(() => URL.revokeObjectURL(objectUrl), 2000);

  } catch (err) {
    alert("Download falhou: " + err.message);
    console.error("Download falhou:", err);
  }
}

// ==================== FORM ORÇAMENTO ====================
const formOrc = $("#formOrc");
if (formOrc) {
  formOrc.onsubmit = async (ev) => {
    ev.preventDefault();
    const params = new URLSearchParams(new FormData(ev.target));
    await download(`/gerar-pdf?${params.toString()}`, "orcamento.pdf");
  };
}

// ==================== FORM NOTA FISCAL ====================
const formNF = $("#formNF");
if (formNF) {
  formNF.onsubmit = async (ev) => {
    ev.preventDefault();
    const data = new FormData(ev.target);

    const params = new URLSearchParams();
    params.set("numero", data.get("numero"));
    params.set("cliente", data.get("cliente"));

    // suporta múltiplos serviços e valores
    const servicos = data.getAll("servico");
    const valores = data.getAll("valor");
    servicos.forEach(s => params.append("servicos", s));
    valores.forEach(v => params.append("valores", v));

    await download(`/nota-fiscal/?${params.toString()}`, `nota_${data.get("numero") || "fiscal"}.pdf`);
  };
}

// ==================== FORM CONTRATO ====================
const formContrato = $("#formContrato");
if (formContrato) {
  formContrato.onsubmit = async (ev) => {
    ev.preventDefault();
    const params = new URLSearchParams(new FormData(ev.target));
    await download(`/contrato?${params.toString()}`, "contrato.pdf");
  };
}

// ==================== FORM RECIBO ====================
const formRecibo = $("#formRecibo");
if (formRecibo) {
  formRecibo.onsubmit = async (ev) => {
    ev.preventDefault();
    const params = new URLSearchParams(new FormData(ev.target));
    await download(`/recibo?${params.toString()}`, "recibo.pdf");
  };
}

// ==================== FORM CARTA ====================
const formCarta = $("#formCarta");
if (formCarta) {
  formCarta.onsubmit = async (ev) => {
    ev.preventDefault();
    const params = new URLSearchParams(new FormData(ev.target));
    await download(`/carta?${params.toString()}`, "carta.pdf");
  };
}
