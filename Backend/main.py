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
def gerar_certificado_get(
    nome: str = "Nome do Aluno",
    curso: str = "Curso Exemplo",
    carga_horaria: int = 20,
    periodo: str = "01/01/2025 a 10/01/2025",
    local: str = "Jundiaí-SP",
    instrutor: str = "Instrutor Exemplo",
    assinatura: str = "CIJUN JUNDIAÍ"
):
    """
    Gera um certificado de exemplo via URL.
    Exemplo de uso:
      /certificado?nome=Alison&curso=IA&carga_horaria=20
    """

    pdf_content = pdf_bytes(lambda c: draw_certificado(
        c,
        nome=nome,
        curso=curso,
        carga_horaria=carga_horaria,
        periodo=periodo,
        local=local,
        instrutor=instrutor,
        assinatura=assinatura
    ))

    filename = f"certificado_{nome.lower().replace(' ', '_')}.pdf"
    return stream_pdf(pdf_content, filename)


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
    """Gera o certificado em PDF com base nos dados enviados pelo frontend."""
    pdf_content = pdf_bytes(lambda c: draw_certificado(
        c,
        nome=body.nome,
        curso=body.curso,
        carga_horaria=body.carga_horaria,
        periodo=body.periodo,
        local=body.local,
        instrutor=body.instrutor,
        assinatura=body.assinatura
    ))

    return stream_pdf(pdf_content, f"certificado_{body.nome.lower().replace(' ', '_')}.pdf")

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
    c.drawString(x_margin, y, f"Extrato No. {numero} do CUPOM FISCAL ELETRÔNICO ")
    y -= 10
    c.line(x_margin, y, largura - x_margin, y)
    y -= 10

    # Itens
    c.setFont("Helvetica-Bold", 8)
    c.drawString(x_margin, y, "  DESC")
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
    if data_str:
        c.drawString(x_margin, y, f"Data/Hora: {data_str}")
        y -= 12         

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

def draw_certificado(c, nome: str, curso: str, carga_horaria: int, periodo: str, local: str, instrutor: str, assinatura: str):
    # Fundo
    largura, altura = A4
    c.setFillColorRGB(0.96, 0.96, 0.96)
    c.rect(0, 0, largura, altura, fill=True, stroke=False)

    # Moldura decorativa
    c.setStrokeColorRGB(0.2, 0.5, 0.3)
    c.setLineWidth(5)
    c.rect(20, 20, largura - 40, altura - 40)

    # Título
    c.setFont("Helvetica-Bold", 28)
    c.setFillColorRGB(0.15, 0.4, 0.15)
    c.drawCentredString(largura / 2, altura - 100, "CERTIFICADO DE CONCLUSÃO")

    # Texto principal
    c.setFont("Helvetica", 13)
    c.setFillColor(colors.black)
    texto = (
        f"Certificamos que {nome}, concluiu com êxito o curso/evento '{curso}', "
        f"com carga horária total de {carga_horaria} horas, "
        f"realizado no período de {periodo}, na cidade de {local}."
    )
    text_obj = c.beginText(70, altura - 200)
    text_obj.setFont("Helvetica", 13)
    text_obj.setLeading(18)
    text_obj.textLines(texto)
    c.drawText(text_obj)

    # Assinatura e responsável
    c.setFont("Helvetica-Bold", 12)
    c.drawCentredString(largura / 2, 120, assinatura)
    c.setFont("Helvetica", 11)
    c.drawCentredString(largura / 2, 105, f"Instrutor(a): {instrutor}")

    # Rodapé institucional
    c.setFont("Helvetica-Oblique", 9)
    c.setFillColorRGB(0.4, 0.4, 0.4)
    c.drawCentredString(largura / 2, 50, "Emitido por CIJUN JUNDIAÍ • Sistema HelpTech Antunes © 2025")

    # Destaque nome (decorativo)
    c.setFont("Helvetica-Bold", 18)
    c.setFillColorRGB(0.1, 0.3, 0.1)
    c.drawCentredString(largura / 2, altura - 150, nome.upper())

    # QR Code (exemplo - opcional)
    from reportlab.graphics.barcode import qr
    from reportlab.graphics import renderPDF
    from reportlab.graphics.shapes import Drawing
    q = qr.QrCodeWidget(f"Verificado: {nome} | {curso}")
    bounds = q.getBounds()
    w, h = bounds[2] - bounds[0], bounds[3] - bounds[1]
    d = Drawing(50, 50, transform=[50 / w, 0, 0, 50 / h, 0, 0])
    d.add(q)
    renderPDF.draw(d, c, largura - 90, 60)
