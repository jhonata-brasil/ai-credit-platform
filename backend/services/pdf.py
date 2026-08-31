from __future__ import annotations

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from backend.models.schemas import Proposta

OUTPUT_DIR = Path("data/propostas")


def _money(value: float) -> str:
    return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def gerar_pdf(proposta: Proposta, filename: str) -> Path:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUTPUT_DIR / filename

    styles = getSampleStyleSheet()
    title = ParagraphStyle(
        "TitleBR",
        parent=styles["Title"],
        fontSize=16,
        textColor=colors.HexColor("#0F3D2E"),
        spaceAfter=12,
    )
    body = ParagraphStyle("BodyBR", parent=styles["Normal"], fontSize=10, leading=14)
    small = ParagraphStyle("SmallBR", parent=styles["Normal"], fontSize=8, textColor=colors.HexColor("#555555"))

    doc = SimpleDocTemplate(
        str(path),
        pagesize=A4,
        leftMargin=2 * cm,
        rightMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
    )

    story = [
        Paragraph("Proposta Comercial de Crédito", title),
        Paragraph("Validade mínima de 60 dias. Valores incluem impostos e encargos.", small),
        Spacer(1, 12),
        Paragraph(f"<b>Razão social:</b> {proposta.razao_social}", body),
        Paragraph(f"<b>Nome fantasia:</b> {proposta.nome_fantasia or '-'}", body),
        Paragraph(f"<b>CNPJ:</b> {proposta.cnpj}", body),
        Paragraph(f"<b>Endereço:</b> {proposta.endereco or '-'}", body),
        Paragraph(f"<b>Cidade:</b> {proposta.cidade or '-'}", body),
        Paragraph(f"<b>CEP:</b> {proposta.cep or '-'}", body),
        Paragraph(f"<b>Telefone:</b> {proposta.telefone or '-'}", body),
        Paragraph(f"<b>E-mail:</b> {proposta.email or '-'}", body),
        Paragraph(f"<b>Responsável legal:</b> {proposta.responsavel_legal or '-'}", body),
        Paragraph(f"<b>Dados bancários:</b> {proposta.dados_bancarios or 'A informar na contratação'}", body),
        Spacer(1, 14),
        Paragraph(proposta.texto.replace("\n", "<br/>"), body),
        Spacer(1, 14),
    ]

    rows = [["Item", "Descrição", "Qtd", "Valor unitário", "Valor total"]]
    for item in proposta.itens:
        rows.append(
            [
                item.item,
                item.descricao,
                str(item.quantidade),
                _money(item.valor_unitario),
                _money(item.valor_total),
            ]
        )
    table = Table(rows, colWidths=[2.5 * cm, 7 * cm, 2 * cm, 3.5 * cm, 3.5 * cm])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0F3D2E")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#CCCCCC")),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    story.extend(
        [
            table,
            Spacer(1, 14),
            Paragraph(f"<b>Prazo:</b> {proposta.prazo} meses", body),
            Paragraph(f"<b>Taxa:</b> {proposta.taxa:.2f}% a.m.", body),
            Paragraph(f"<b>Validade da proposta:</b> {proposta.validade_dias} dias", body),
            Paragraph(f"<b>Impostos e encargos:</b> {proposta.impostos_encargos}", body),
            Spacer(1, 24),
            Paragraph("________________________________", body),
            Paragraph("Assinatura do responsável legal", small),
        ]
    )
    doc.build(story)
    return path
