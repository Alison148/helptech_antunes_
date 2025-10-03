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
    allow_origins=["*"],  # Em produção, restringir para seu domínio
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"message": "API HelpTech Antunes rodando no Vercel 🚀"}

# ===== Função auxiliar =====
def criar_pdf(nome_arquivo: str, escrever):
    c = canvas.Canvas(nome_arquivo, pagesize=A4)
    escrever(c)
    c.save()
    return nome_arquivo

# ===== ORÇAMENTO =====
@app.get("/gerar-pdf")
def gerar_orcamento(
    cliente: str = "Cliente Teste",
    servicos: list[str] = Query(["Serviço X"]),
    valores: list[float] = Query([100.0])
):
    pdf = criar_pdf("orcamento.pdf", lambda c: (
        c.setFont("Helvetica-Bold", 14),
        c.drawString(100, 800, "Orçamento"),
        c.setFont("Helvetica", 12),
        c.drawString(100, 780, f"Cliente: {cliente}"),
        [c.drawString(100, 750 - i*20, f"- {s} : R$ {v:.2f}") for i, (s,v) in enumerate(zip(servicos,valores))]
    ))
    return FileResponse(pdf, media_type="application/pdf", filename=pdf)

# ===== NOTA FISCAL =====
@app.get("/nota-fiscal")
def rota_nota(
    numero: str = "0001",
    cliente: str = "Cliente Teste",
    servicos: list[str] = Query(["Serviço X"]),
    valores: list[float] = Query([100.0])
):
    pdf = criar_pdf(f"nota_{numero}.pdf", lambda c: (
        c.setFont("Helvetica-Bold", 14),
        c.drawString(100, 800, f"Nota Fiscal Nº {numero}"),
        c.setFont("Helvetica", 12),
        c.drawString(100, 780, f"Cliente: {cliente}"),
        c.drawString(100, 760, f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}"),
        [c.drawString(100, 730 - i*20, f"- {s} : R$ {v:.2f}") for i, (s,v) in enumerate(zip(servicos,valores))]
    ))
    return FileResponse(pdf, media_type="application/pdf", filename=pdf)

# ===== CONTRATO =====
@app.get("/contrato")
def gerar_contrato(cliente: str = "Cliente Teste", descricao: str = "Serviço contratado"):
    pdf = criar_pdf("contrato.pdf", lambda c: (
        c.setFont("Helvetica-Bold", 14),
        c.drawString(100, 800, "Contrato de Prestação de Serviços"),
        c.setFont("Helvetica", 12),
        c.drawString(100, 770, f"Cliente: {cliente}"),
        c.drawString(100, 750, f"Descrição: {descricao}"),
        c.drawString(100, 720, f"Data: {datetime.now().strftime('%d/%m/%Y')}")
    ))
    return FileResponse(pdf, media_type="application/pdf", filename=pdf)

# ===== RECIBO =====
@app.get("/recibo")
def gerar_recibo(cliente: str = "Cliente Teste", valor: float = 100.0):
    pdf = criar_pdf("recibo.pdf", lambda c: (
        c.setFont("Helvetica-Bold", 14),
        c.drawString(100, 800, "Recibo"),
        c.setFont("Helvetica", 12),
        c.drawString(100, 770, f"Recebemos de: {cliente}"),
        c.drawString(100, 750, f"Valor: R$ {valor:.2f}"),
        c.drawString(100, 730, f"Data: {datetime.now().strftime('%d/%m/%Y')}")
    ))
    return FileResponse(pdf, media_type="application/pdf", filename=pdf)

# ===== CARTA =====
@app.get("/carta")
def gerar_carta(destinatario: str = "Destinatário", mensagem: str = "Mensagem padrão"):
    pdf = criar_pdf("carta.pdf", lambda c: (
        c.setFont("Helvetica-Bold", 14),
        c.drawString(100, 800, "Carta"),
        c.setFont("Helvetica", 12),
        c.drawString(100, 770, f"Para: {destinatario}"),
        c.drawString(100, 740, f"Mensagem: {mensagem}"),
        c.drawString(100, 710, f"Data: {datetime.now().strftime('%d/%m/%Y')}")
    ))
    return FileResponse(pdf, media_type="application/pdf", filename=pdf)
# ===== CERTIFICADO =====
@app.get("/certificado")    
def gerar_certificado(nome: str = "Nome do Aluno", curso: str = "Curso Exemplo"):
    pdf = criar_pdf("certificado.pdf", lambda c: (
        c.setFont("Helvetica-Bold", 16),
        c.drawString(100, 800, "Certificado de Conclusão"),
        c.setFont("Helvetica", 12),
        c.drawString(100, 770, f"Certificamos que {nome}"),
        c.drawString(100, 750, f"concluiu o curso: {curso}"),
        c.drawString(100, 720, f"Data: {datetime.now().strftime('%d/%m/%Y')}")
    ))
    return FileResponse(pdf, media_type="application/pdf", filename=pdf)

