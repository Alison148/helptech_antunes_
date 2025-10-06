from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from io import BytesIO

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.graphics.barcode import code128, qr
from reportlab.graphics import renderPDF
from reportlab.graphics.shapes import Drawing

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


# ========= MODELOS =========
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


# ========= GET =========
@app.get("/gerar-pdf")
def gerar_orcamento_get(
    cliente: str = "Cliente Teste",
    servicos: List[str] = Query(["Serviço X"]),
    valores: List[float] = Query([100.0]),
):
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


# ========= POST =========
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


# ========= Desenhos =========
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
        if y < 80:
            c.showPage()
            y = 800
            c.setFont("Helvetica", 12)
    c.setFont("Helvetica-Bold", 12)
    c.drawRightString(540, y - 6, f"Total: R$ {total:.2f}")

def draw_orcamento(c, cliente: str, pares: List[tuple]):
    draw_header(c, "Orçamento")
    c.setFont("Helvetica", 12)
    c.drawString(70, 760, f"Cliente: {cliente}")
    draw_list_items(c, start_y=730, pares=pares)


# ======= NOVO MODELO DE NOTA (CUPOM 80mm) =======
def draw_nota(c, numero: str, cliente: str, pares: List[tuple], data_str: Optional[str] = None):
    """Desenha uma nota fiscal no formato cupom térmico (80mm)."""
    largura = 80 * mm
    altura = 250 * mm
    x_margin = 6 * mm
    y = altura - 8 * mm

    c.setPageSize((largura, altura))

    # Cabeçalho
    c.setFont("Helvetica-Bold", 10)
    c.drawCentredString(largura / 2, y, "HELPTECH ANTUNES")
    y -= 10
    c.setFont("Helvetica", 8)
    c.drawCentredString(largura / 2, y, "Assistência Técnica e Serviços")
    y -= 9
    c.drawCentredString(largura / 2, y, "Rua Mariano Floripa Prudente 108 – Jundiaí/SP")
    y -= 9
    c.drawCentredString(largura / 2, y, "CNPJ 00.000.000/0001-00 | (11) 95780-5217")
    y -= 9
    c.line(x_margin, y, largura - x_margin, y)
    y -= 12

    c.setFont("Helvetica-Bold", 8)
    c.drawString(x_margin, y, f"Extrato No. {numero} do CUPOM FISCAL ELETRÔNICO - SAT")
    y -= 10
    c.line(x_margin, y, largura - x_margin, y)
    y -= 10

    # Itens
    c.setFont("Helvetica-Bold", 8)
    c.drawString(x_margin, y, "#  DESC")
    c.drawRightString(largura - x_margin, y, "VL ITEM R$")
    y -= 9
    c.line(x_margin, y, largura - x_margin, y)
    y -= 8

    total = 0
    c.setFont("Helvetica", 8)
    for i, (desc, val) in enumerate(pares, start=1):
        c.drawString(x_margin, y, f"{i:03d}  {desc[:20]}")
        c.drawRightString(largura - x_margin, y, f"{val:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
        total += val
        y -= 9

    c.line(x_margin, y, largura - x_margin, y)
    y -= 10

    # Totais
    c.drawString(x_margin, y, "Total bruto de itens")
    c.drawRightString(largura - x_margin, y, f"{total:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    y -= 9
    c.drawString(x_margin, y, "Total R$")
    c.setFont("Helvetica-Bold", 9)
    c.drawRightString(largura - x_margin, y, f"{total:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    y -= 12
    c.setFont("Helvetica", 8)
    c.drawString(x_margin, y, "Dinheiro")
    y -= 12

    # Observações
    c.line(x_margin, y, largura - x_margin, y)
    y -= 8
    c.setFont("Helvetica", 7)
    c.drawString(x_margin, y, "Comete crime quem sonega")
    y -= 9
    c.drawString(x_margin, y, "ICMS conforme LC 123/2006 - Simples Nacional.")
    y -= 9
    c.drawString(x_margin, y, "Documento emitido por ME e EPP optante.")
    y -= 9
    c.drawString(x_margin, y, "Valor aprox. dos tributos: R$ 14,61*")
    y -= 9
    c.drawString(x_margin, y, "Conforme Lei Fed. 12.741/2012 – Fonte IBPT")
    y -= 12

    # Código de barras
    barcode = code128.Code128(numero[:15], barHeight=8 * mm, barWidth=0.35)
    barcode.drawOn(c, x_margin, y - 8)
    y -= 16

    # QR Code
    qr_data = f"NF {numero} - Cliente: {cliente} - Total: R$ {total:.2f}"
    qr_code = qr.QrCodeWidget(qr_data)
    bounds = qr_code.getBounds()
    size = 28 * mm
    w, h = bounds[2] - bounds[0], bounds[3] - bounds[1]
    d = Drawing(size, size, transform=[size / w, 0, 0, size / h, 0, 0])
    d.add(qr_code)
    renderPDF.draw(d, c, largura / 2 - size / 2, y - size)
    y -= size + 6

    c.setFont("Helvetica", 7)
    c.drawCentredString(largura / 2, y, "Desenvolvido por: HelpTech Antunes")


def draw_contrato(c, cliente: str, descricao: str):
    draw_header(c, "Contrato de Prestação de Serviços")
    c.setFont("Helvetica", 12)
    c.drawString(70, 760, f"Cliente: {cliente}")
    text = c.beginText(70, 735)
    text.setFont("Helvetica", 12)
    text.textLines(["Descrição do serviço:", "", descricao])
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
    for line in mensagem.splitlines() or ["Mensagem vazia."]:
        text.textLine(line)
    c.drawText(text)

def draw_certificado(c, nome: str, curso: str):
    draw_header(c, "Certificado de Conclusão")
    c.setFont("Helvetica", 14)
    c.drawString(70, 760, f"Certificamos que {nome}")
    c.drawString(70, 740, f"concluiu o curso: {curso}")
