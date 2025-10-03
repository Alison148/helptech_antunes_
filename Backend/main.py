from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.pdfbase.pdfmetrics import stringWidth
from datetime import datetime

app = FastAPI()

# --- CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # <- Aqui está liberando para qualquer origem
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Helpers ---
def brl(v: float) -> str:
    return f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def wrap_text(c: canvas.Canvas, text: str, max_width_mm: float, font_name="Helvetica", font_size=10):
    max_width = max_width_mm * mm
    words = text.split()
    lines, line = [], ""
    for w in words:
        test = (line + " " + w).strip()
        if stringWidth(test, font_name, font_size) <= max_width:
            line = test
        else:
            if line:
                lines.append(line)
            line = w
    if line:
        lines.append(line)
    return lines

def draw_header(c: canvas.Canvas):
    c.setFont("Helvetica-Bold", 16)
    c.drawString(30*mm, 280*mm, "HelpTech Antunes - Assistência Técnica")
    c.setFont("Helvetica", 10)
    c.drawString(30*mm, 274*mm, "CNPJ: 12.345.678/0001-99")
    c.drawString(30*mm, 268*mm, "Endereço: Av. Luís Pereira dos Santos, 556 - Jundiaí/SP")
    c.drawString(30*mm, 262*mm, "WhatsApp: (11) 95780-5217")

def draw_table_header(c: canvas.Canvas, top_y_mm: float = 215):
    c.setFont("Helvetica-Bold", 11)
    c.drawString(30*mm, top_y_mm*mm, "Serviço")
    c.drawString(120*mm, top_y_mm*mm, "Valor (R$)")
    c.line(30*mm, (top_y_mm-3)*mm, 180*mm, (top_y_mm-3)*mm)

@app.get("/")
def home():
    return {"message": "API HelpTech Antunes rodando com FastAPI + PDF"}

# Função principal para gerar PDF
def gerar_pdf_interno(
    numero: str,
    cliente: str,
    servicos: list[str],
    valores: list[float],
    garantia_dias: int
):
    if len(servicos) != len(valores):
        raise HTTPException(status_code=400, detail="Quantidade de serviços não bate com a de valores.")

    file_path = f"nota_fiscal_{numero}.pdf"
    c = canvas.Canvas(file_path, pagesize=A4)

    # Cabeçalho
    draw_header(c)
    c.setFont("Helvetica-Bold", 12)
    c.drawRightString(200*mm, 280*mm, f"NF Nº {numero}")
    c.setFont("Helvetica", 10)
    c.drawRightString(200*mm, 274*mm, f"Emissão: {datetime.now().strftime('%d/%m/%Y %H:%M')}")

    # Cliente
    c.setFont("Helvetica-Bold", 12)
    c.drawString(30*mm, 250*mm, "Dados do Cliente:")
    c.setFont("Helvetica", 11)
    c.drawString(30*mm, 242*mm, f"Nome: {cliente}")

    # Tabela
    c.setFont("Helvetica-Bold", 12)
    c.drawString(30*mm, 225*mm, "Descrição dos Serviços")
    draw_table_header(c, 215)

    y_mm = 205
    total = 0.0

    for servico, valor in zip(servicos, valores):
        c.drawString(30*mm, y_mm*mm, servico)
        c.drawRightString(180*mm, y_mm*mm, brl(valor))
        total += valor
        y_mm -= 8

    c.setFont("Helvetica-Bold", 12)
    c.drawString(120*mm, (y_mm-4)*mm, "Total:")
    c.drawRightString(180*mm, (y_mm-4)*mm, brl(total))

    c.save()

    return FileResponse(file_path, media_type="application/pdf", filename=file_path)

# Rota oficial
@app.get("/nota-fiscal/")
def gerar_nota(
    numero: str = "0001",
    cliente: str = "Cliente Teste",
    servicos: list[str] = Query(["Serviço X"]),
    valores: list[float] = Query([100.0]),
    garantia_dias: int = 90
):
    return gerar_pdf_interno(numero, cliente, servicos, valores, garantia_dias)

# Alias para compatibilidade
@app.get("/gerar-pdf")
def gerar_pdf(
    numero: str = "0001",
    cliente: str = "Cliente Teste",
    servicos: list[str] = Query(["Serviço X"]),
    valores: list[float] = Query([100.0]),
    garantia_dias: int = 90
):
    return gerar_pdf_interno(numero, cliente, servicos, valores, garantia_dias)
