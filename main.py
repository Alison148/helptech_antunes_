from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import FileResponse
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.pdfbase.pdfmetrics import stringWidth
import os
from datetime import datetime

app = FastAPI()

def brl(v: float) -> str:
    return f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def wrap_text(c: canvas.Canvas, text: str, max_width_mm: float, font_name="Helvetica", font_size=10):
    """Quebra uma string em linhas que caibam na largura dada (em mm)."""
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
    # --- Cabeçalho da empresa ---
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

@app.get("/nota-fiscal/")
def gerar_nota(
    numero: str = "0001",
    cliente: str = "Cliente Teste",
    servicos: list[str] = Query(["Serviço X", "Serviço Y"]),
    valores: list[float] = Query([100.0, 200.0]),
    garantia_dias: int = 90,  # prazo parametrizável
):
    if len(servicos) != len(valores):
        raise HTTPException(status_code=400, detail="Quantidade de serviços não bate com a de valores.")

    file_path = f"nota_fiscal_{numero}.pdf"
    c = canvas.Canvas(file_path, pagesize=A4)

    # Margens e áreas úteis
    left_x = 30
    right_x = 180
    bottom_margin_mm = 30
    line_step_mm = 8

    # Cabeçalho e NF
    draw_header(c)
    c.setFont("Helvetica-Bold", 12)
    c.drawRightString(200*mm, 280*mm, f"NF Nº {numero}")
    c.setFont("Helvetica", 10)
    c.drawRightString(200*mm, 274*mm, f"Emissão: {datetime.now().strftime('%d/%m/%Y %H:%M')}")

    # Dados do cliente
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

    def new_page_with_table():
        nonlocal y_mm
        c.showPage()
        draw_header(c)
        c.setFont("Helvetica-Bold", 12)
        c.drawString(30*mm, 225*mm, "Descrição dos Serviços (continuação)")
        draw_table_header(c, 215)
        y_mm = 205

    c.setFont("Helvetica", 11)
    for servico, valor in zip(servicos, valores):
        # Quebra página se necessário
        if y_mm <= bottom_margin_mm + 40:  # reserva para total/rodapés
            new_page_with_table()

        c.drawString(30*mm, y_mm*mm, servico)
        c.drawRightString(180*mm, y_mm*mm, f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
        total += valor
        y_mm -= line_step_mm

    # Total
    if y_mm <= bottom_margin_mm + 30:
        new_page_with_table()
    c.setFont("Helvetica-Bold", 12)
    c.drawString(120*mm, (y_mm-4)*mm, "Total:")
    c.drawRightString(180*mm, (y_mm-4)*mm, brl(total))
    y_mm -= 14

    # Bloco de Garantia
    garantia_texto = (
        f"Garantia: {garantia_dias} dias a contar da data de retirada/entrega, "
        "abrangendo exclusivamente o serviço/peça substituída. Perde a validade em caso de violação de lacres, "
        "quedas, umidade/oxidação, mau uso, softwares não licenciados ou intervenção de terceiros. "
        "A garantia não cobre dados, acessórios, carcaças, displays com trincas ou danos decorrentes de agentes externos."
    )

    base_legal = (
        "Base legal (CDC – Lei 8.078/1990): Art. 26, II – 90 dias para reclamar de vícios aparentes em produtos/serviços "
        "duráveis; Arts. 18 e 20 – responsabilidade por vícios e direito à reexecução do serviço, abatimento proporcional "
        "ou restituição, conforme o caso."
    )

    obs_legal = (
        "Este documento não é NF-e; uso interno para orçamento/serviço. A eventual emissão fiscal ocorrerá em sistema próprio."
    )

    def draw_paragraph(title: str, text: str):
        nonlocal y_mm
        # Quebra página se faltar espaço
        needed_lines = len(wrap_text(c, text, max_width_mm=(right_x-left_x)))
        needed_height = 6 + needed_lines*5  # estimativa
        if y_mm <= bottom_margin_mm + needed_height:
            c.showPage()
            draw_header(c)
            y_mm = 240

        c.setFont("Helvetica-Bold", 11)
        c.drawString(30*mm, y_mm*mm, title)
        y_mm -= 6
        c.setFont("Helvetica", 10)
        lines = wrap_text(c, text, max_width_mm=(right_x-left_x))
        for ln in lines:
            c.drawString(30*mm, y_mm*mm, ln)
            y_mm -= 5
        y_mm -= 2

    draw_paragraph("GARANTIA", garantia_texto)
    draw_paragraph("BASE LEGAL (CDC)", base_legal)
    draw_paragraph("OBSERVAÇÃO", obs_legal)

    # Assinatura
    if y_mm <= bottom_margin_mm + 20:
        c.showPage()
        draw_header(c)
        y_mm = 240

    c.setFont("Helvetica", 10)
    c.drawString(30*mm, (y_mm-2)*mm, "Assinatura do Cliente: ____________________________    Data: ____/____/______")

    # Rodapé
    c.setFont("Helvetica-Oblique", 9)
    c.drawString(30*mm, 20*mm, "Documento gerado automaticamente pelo sistema HelpTech Antunes")

    c.showPage()
    c.save()

    return FileResponse(file_path, media_type="application/pdf", filename=file_path)
