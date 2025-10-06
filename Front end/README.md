HelpTech Antunes — Frontend Estático

Frontend 100% estático (HTML, CSS, JS puro) para gerar PDF de Orçamento e Nota Fiscal consumindo uma API (FastAPI).

🔧 Pré-requisitos

Qualquer servidor estático (VS Code Live Server, python -m http.server, serve, Nginx, etc.).

API rodando e acessível (por padrão em http://127.0.0.1:8000).

🚀 Como usar

Coloque a pasta frontend/ em um servidor estático (ou abra com o Live Server).

Abra index.html no navegador.

Defina a URL da API (campo no topo da página) — por padrão http://127.0.0.1:8000.

Preencha os formulários e clique em Gerar PDF. O arquivo baixa automaticamente.

🗂️ Estrutura de pastas
frontend/
├─ index.html          # UI com os formulários
├─ styles.css          # Estilos básicos (responsivo/print)
├─ script.js           # Chamada à API, montagem de URL e download
└─ config.js (opcional)# Persistir API_BASE no localStorage

config.js (opcional)
// Persiste a base da API entre recarregamentos
window.APP_CONFIG = {
  API_BASE: localStorage.getItem('API_BASE') || 'http://127.0.0.1:8000'
};

⚙️ Configuração da API (frontend)

No topo da página há um input para a Base URL da API.
Também é possível definir direto no código:

// script.js
const API_BASE = (window.APP_CONFIG?.API_BASE) || 'http://127.0.0.1:8000';
// dica: permitir ajuste pelo usuário e salvar:
function setApiBase(url){
  localStorage.setItem('API_BASE', url);
  location.reload();
}

📡 Endpoints esperados

Orçamento: GET /gerar-pdf

Nota Fiscal: GET /nota-fiscal/

Parâmetros (query string)
Orçamento (/gerar-pdf)

cliente: string

servicos: string[] (pode repetir)

valores: number[] (pode repetir; mesma ordem de servicos)

Exemplo:

/gerar-pdf?cliente=Alison%20Antunes
&servicos=Formata%C3%A7%C3%A3o&valores=150
&servicos=Troca%20de%20Tela&valores=280

Nota Fiscal (/nota-fiscal/)

numero: string

cliente: string

servico: string

valor: number

Exemplo:

/nota-fiscal/?numero=000123&cliente=Jo%C3%A3o%20Silva
&servico=Troca%20de%20conector&valor=199.9

🧩 Exemplo de chamada no frontend
// Monta URL com múltiplos serviços/valores
function buildURL(base, path, params){
  const url = new URL(path, base);
  Object.entries(params).forEach(([k, v]) => {
    if (Array.isArray(v)) v.forEach(item => url.searchParams.append(k, item));
    else url.searchParams.set(k, v);
  });
  return url.toString();
}

// Faz o download de um PDF retornado pela API
async function downloadPdf(url, fallbackName = "documento.pdf"){
  try {
    const res = await fetch(url, { mode: "cors" });
    if (!res.ok) throw new Error(`Erro ${res.status} ao gerar PDF`);
    const blob = await res.blob();

    // tenta usar o nome do header
    let filename = fallbackName;
    const cd = res.headers.get("content-disposition");
    const match = cd && cd.match(/filename="?([^"]+)"?/i);
    if (match) filename = match[1];

    const a = document.createElement("a");
    const objectUrl = URL.createObjectURL(blob);
    a.href = objectUrl;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(objectUrl);
  } catch (err) {
    alert(err.message || "Falha ao baixar PDF");
    console.error(err);
  }
}

🧪 Fluxos rápidos
Orçamento com vários serviços
const url = buildURL(API_BASE, "/gerar-pdf", {
  cliente: "Alison Antunes",
  servicos: ["Formatação", "Troca de Tela"],
  valores: [150, 280]
});
downloadPdf(url, "orcamento.pdf");

Nota fiscal simples
const url = buildURL(API_BASE, "/nota-fiscal/", {
  numero: "000123",
  cliente: "João da Silva",
  servico: "Troca de Conector",
  valor: 199.90
});
downloadPdf(url, "nota-fiscal.pdf");

🛡️ Requisitos da API (recomendado)

Retornar Content-Type: application/pdf.

Incluir Content-Disposition: attachment; filename="arquivo.pdf".

Habilitar CORS no backend (ex.: allow_origins=["*"] em dev).

Garantir que rotas GET aceitam parâmetros repetidos para arrays.

🐞 Erros comuns & soluções

CORS / bloqueio no navegador
Habilite CORS na API ou use a mesma origem (proxy/reverse-proxy).

404 na rota
Verifique nomes exatos: /gerar-pdf e /nota-fiscal/.

PDF baixa corrompido
Confirme Content-Type e se a resposta é realmente um PDF/byte-stream.

Nome do arquivo genérico
API deve enviar Content-Disposition com filename. O frontend já tenta ler.

📱 UX rápida

Campo visível para Base URL (salva em localStorage).

Validação simples (cliente/serviço/valor obrigatórios).

Máscara/locale BRL no valor (exibição).

✅ Checklist antes de publicar

 API acessível externamente (porta/host corretos).

 CORS habilitado para o domínio do frontend.

 Rotas respondendo com PDF e cabeçalhos adequados.

 Teste de múltiplos serviços/valores no orçamento.

 Ícones/logotipo da HelpTech aplicados no index.html.

📄 Licença

Uso interno HelpTech Antunes. Ajuste conforme sua necessidade.