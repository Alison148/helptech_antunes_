from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from io import BytesIO

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

app = FastAPI(title="HelpTech Antunes PDF API", version="1.0.0")

# --- CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção: restringir para seu domínio
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ========= Helpers =========
def pdf_bytes(draw_fn) -> bytes:
    """Gera PDF em memória (BytesIO) e retorna bytes."""
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    draw_fn(c)
    c.save()
    buffer.seek(0)
    return buffer.read()

def stream_pdf(content: bytes, filename: str) -> StreamingResponse:
    """Retorna StreamingResponse com headers para download."""
    return StreamingResponse(
        BytesIO(content),
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )

# ========= Saúde / Home =========
@app.get("/")
def home():
    return {"message": "API HelpTech Antunes rodando no Vercel 🚀"}

@app.get("/health")
def health():
    return {"status": "ok", "time": datetime.now().isoformat()}


# ========= MODELOS (POST) =========
class Item(BaseModel):
    descricao: str = Field(..., example="Troca de Tela")
    valor: float = Field(..., example=199.90)

class OrcamentoBody(BaseModel):
    cliente: str = Field(..., example="João da Silva")
    itens: List[Item] = Field(default_factory=list)

class NotaFiscalBody(BaseModel):
    numero: str = Field(..., example="0001")
    cliente: str = Field(..., example="João da Silva")
    itens: List[Item] = Field(default_factory=list)
    data: Optional[str] = Field(None, example="2025-10-06 09:00")

class ContratoBody(BaseModel):
    cliente: str = Field(..., example="Cliente Teste")
    descricao: str = Field(..., example="Serviço contratado")

class ReciboBody(BaseModel):
    cliente: str = Field(..., example="Cliente Teste")
    valor: float = Field(..., example=100.0)

class CartaBody(BaseModel):
    destinatario: str = Field(..., example="Destinatário")
    mensagem: str = Field(..., example="Mensagem padrão")

class CertificadoBody(BaseModel):
    nome: str = Field(..., example="Nome do Aluno")
    curso: str = Field(..., example="Curso Exemplo")


# ========= GET (compatível com seu frontend atual) =========
@app.get("/gerar-pdf")
def gerar_orcamento_get(
    cliente: str = "Cliente Teste",
    servicos: List[str] = Query(["Serviço X"]),
    valores: List[float] = Query([100.0]),
):
    # normaliza pares serviço/valor
    pares = list(zip(servicos, valores))
    pdf = pdf_bytes(lambda c: draw_orcamento(c, cliente, pares))
    return stream_pdf(pdf, "orcamento.pdf")

@app.get("/nota-fiscal")
def rota_nota_get(
    numero: str = "0001",
    cliente: str = "Cliente Teste",
    servicos: List[str] = Query(["Serviço X"]),
    valores: List[float] = Query([100.0]),
):
    pares = list(zip(servicos, valores))
    pdf = pdf_bytes(lambda c: draw_nota(c, numero, cliente, pares))
    return stream_pdf(pdf, f"nota_{numero}.pdf")

@app.get("/contrato")
def gerar_contrato_get(cliente: str = "Cliente Teste", descricao: str = "Serviço contratado"):
    pdf = pdf_bytes(lambda c: draw_contrato(c, cliente, descricao))
    return stream_pdf(pdf, "contrato.pdf")

@app.get("/recibo")
def gerar_recibo_get(cliente: str = "Cliente Teste", valor: float = 100.0):
    pdf = pdf_bytes(lambda c: draw_recibo(c, cliente, valor))
    return stream_pdf(pdf, "recibo.pdf")

@app.get("/carta")
def gerar_carta_get(destinatario: str = "Destinatário", mensagem: str = "Mensagem padrão"):
    pdf = pdf_bytes(lambda c: draw_carta(c, destinatario, mensagem))
    return stream_pdf(pdf, "carta.pdf")

@app.get("/certificado")
def gerar_certificado_get(nome: str = "Nome do Aluno", curso: str = "Curso Exemplo"):
    pdf = pdf_bytes(lambda c: draw_certificado(c, nome, curso))
    return stream_pdf(pdf, "certificado.pdf")


# ========= POST (JSON) =========
@app.post("/orcamento")
def gerar_orcamento_post(body: OrcamentoBody):
    pares = [(i.descricao, i.valor) for i in body.itens]
    pdf = pdf_bytes(lambda c: draw_orcamento(c, body.cliente, pares))
    return stream_pdf(pdf, "orcamento.pdf")

@app.post("/nota-fiscal")
def gerar_nota_post(body: NotaFiscalBody):
    pares = [(i.descricao, i.valor) for i in body.itens]
    pdf = pdf_bytes(lambda c: draw_nota(
        c,
        body.numero,
        body.cliente,
        pares,
        body.data
    ))
    return stream_pdf(pdf, f"nota_{body.numero}.pdf")

@app.post("/contrato")
def gerar_contrato_post(body: ContratoBody):
    pdf = pdf_bytes(lambda c: draw_contrato(c, body.cliente, body.descricao))
    return stream_pdf(pdf, "contrato.pdf")

@app.post("/recibo")
def gerar_recibo_post(body: ReciboBody):
    pdf = pdf_bytes(lambda c: draw_recibo(c, body.cliente, body.valor))
    return stream_pdf(pdf, "recibo.pdf")

@app.post("/carta")
def gerar_carta_post(body: CartaBody):
    pdf = pdf_bytes(lambda c: draw_carta(c, body.destinatario, body.mensagem))
    return stream_pdf(pdf, "carta.pdf")

@app.post("/certificado")
def gerar_certificado_post(body: CertificadoBody):
    pdf = pdf_bytes(lambda c: draw_certificado(c, body.nome, body.curso))
    return stream_pdf(pdf, "certificado.pdf")


# ========= Desenho dos PDFs =========
def draw_header(c, titulo: str):
    c.setFont("Helvetica-Bold", 16)
    c.drawString(70, 800, titulo)
    c.setFont("Helvetica", 10)
    c.drawString(70, 785, f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}")

def draw_list_items(c, start_y: int, pares: List[tuple], col_x=70, gap=18):
    y = start_y
    total = 0.0
    c.setFont("Helvetica", 12)
    for idx, (desc, val) in enumerate(pares, start=1):
        c.drawString(col_x, y, f"{idx}. {desc}")
        c.drawRightString(540, y, f"R$ {val:.2f}")
        total += float(val)
        y -= gap
        if y < 80:  # quebra de página se necessário
            c.showPage()
            y = 800
            c.setFont("Helvetica", 12)
    # total
    c.setFont("Helvetica-Bold", 12)
    c.drawRightString(540, y - 6, f"Total: R$ {total:.2f}")

def draw_orcamento(c, cliente: str, pares: List[tuple]):
    draw_header(c, "Orçamento")
    c.setFont("Helvetica", 12)
    c.drawString(70, 760, f"Cliente: {cliente}")
    draw_list_items(c, start_y=730, pares=pares)

def draw_nota(c, numero: str, cliente: str, pares: List[tuple], data_str: Optional[str] = None):
    draw_header(c, f"Nota Fiscal Nº {numero}")
    c.setFont("Helvetica", 12)
    c.drawString(70, 760, f"Cliente: {cliente}")
    data_fmt = data_str or datetime.now().strftime('%d/%m/%Y %H:%M')
    c.drawString(70, 742, f"Data: {data_fmt}")
    draw_list_items(c, start_y=715, pares=pares)

def draw_contrato(c, cliente: str, descricao: str):
    draw_header(c, "Contrato de Prestação de Serviços")
    c.setFont("Helvetica", 12)
    c.drawString(70, 760, f"Cliente: {cliente}")
    text = c.beginText(70, 735)
    text.setFont("Helvetica", 12)
    text.textLines([
        "Descrição do serviço:",
        "",
        descricao
    ])
    c.drawText(text)

def draw_recibo(c, cliente: str, valor: float):
    draw_header(c, "Recibo")
    c.setFont("Helvetica", 12)
    c.drawString(70, 760, f"Recebemos de: {cliente}")
    c.drawString(70, 742, f"Valor: R$ {valor:.2f}")

def draw_carta(c, destinatario: str, mensagem: str):
    draw_header(c, "Carta")
    c.setFont("Helvetica", 12)
    c.drawString(70, 760, f"Para: {destinatario}")
    text = c.beginText(70, 735)
    text.setFont("Helvetica", 12)
    # quebra simples
    for line in mensagem.splitlines() or ["Mensagem vazia."]:
        text.textLine(line)
    c.drawText(text)

def draw_certificado(c, nome: str, curso: str):
    draw_header(c, "Certificado de Conclusão")
    c.setFont("Helvetica", 14)
    c.drawString(70, 760, f"Certificamos que {nome}")
    c.drawString(70, 740, f"concluiu o curso: {curso}")
