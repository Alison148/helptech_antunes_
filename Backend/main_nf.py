from fastapi import FastAPI
from fastapi.responses import FileResponse
from pydantic import BaseModel
from datetime import datetime
import pdfkit

app = FastAPI(title="HelpTech Antunes - API Nota Fiscal")

class NotaFiscal(BaseModel):
    numero: str
    cliente: str
    cpf_cnpj: str
    endereco: str
    servico: str
    valor: float
    observacoes: str | None = None

@app.post("/gerar-nota")
def gerar_nf(dados: NotaFiscal):
    html = f"""
    <html>
    <head>
        <meta charset='utf-8'>
        <style>
            body {{ font-family: Arial, sans-serif; }}
            .cabecalho {{ text-align: center; margin-bottom: 20px; }}
            table {{ width: 100%; border-collapse: collapse; }}
            th, td {{ border: 1px solid #000; padding: 8px; text-align: left; }}
        </style>
    </head>
    <body>
        <div class='cabecalho'>
            <h2>HELPTECH ANTUNES</h2>
            <p>CNPJ: 12.345.678/0001-99</p>
            <p>Avenida Luís Pereira dos Santos, 556 - Jundiaí/SP</p>
        </div>
        <h3>Nota Fiscal Nº {dados.numero}</h3>
        <p><b>Data:</b> {datetime.today().strftime('%d/%m/%Y')}</p>
        <p><b>Cliente:</b> {dados.cliente} - {dados.cpf_cnpj}</p>
        <p><b>Endereço:</b> {dados.endereco}</p>
        <hr>
        <table>
            <tr><th>Descrição</th><th>Valor (R$)</th></tr>
            <tr><td>{dados.servico}</td><td>{dados.valor:.2f}</td></tr>
        </table>
        <p><b>Total:</b> R$ {dados.valor:.2f}</p>
        <p><b>Observações:</b> {dados.observacoes or ''}</p>
    </body>
    </html>
    """

    caminho_pdf = "nota_fiscal.pdf"
    pdfkit.from_string(html, caminho_pdf)
    return FileResponse(caminho_pdf, media_type="application/pdf", filename="nota_fiscal.pdf")
