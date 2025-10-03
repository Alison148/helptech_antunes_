from fastapi import FastAPI, Query
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from datetime import datetime

app = FastAPI()

# --- CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ajuste para ["https://seusite.vercel.app"] depois
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"message": "API HelpTech Antunes rodando no Vercel 🚀"}

# Função auxiliar para gerar PDF
def gerar_pdf(numero: str, cliente: str, servicos: list[str], valores: list[float]):
    file_path = f"nota_{numero}.pdf"
    c = canvas.Canvas(file_path, pagesize=A4)

    c.setFont("Helvetica-Bold", 14)
    c.drawString(100, 800, f"Nota Fiscal Nº {numero}")
    c.setFont("Helvetica", 12)
    c.drawString(100, 780, f"Cliente: {cliente}")
    c.drawString(100, 760, f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}")

    y = 730
    total = 0
    for serv, val in zip(servicos, valores):
        c.drawString(100, y, f"- {serv}  R$ {val:.2f}")
        y -= 20
        total += val

    c.setFont("Helvetica-Bold", 12)
    c.drawString(100, y-20, f"TOTAL: R$ {total:.2f}")

    c.save()
    return file_path

# Rota para gerar PDF
@app.get("/nota-fiscal")
def rota_nota(
    numero: str = "0001",
    cliente: str = "Cliente Teste",
    servicos: list[str] = Query(["Serviço X"]),
    valores: list[float] = Query([100.0])
):
    pdf = gerar_pdf(numero, cliente, servicos, valores)
    return FileResponse(pdf, media_type="application/pdf", filename=pdf)
