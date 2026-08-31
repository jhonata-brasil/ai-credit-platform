from __future__ import annotations

from backend.models.schemas import Analise, Empresa, ItemProposta, Proposta
from backend.services.receitaws import format_cnpj


def _taxa(risco: str) -> float:
    return {"baixo": 1.89, "medio": 2.49, "alto": 3.49}.get(risco, 2.49)


def _valor_aprovado(analise: Analise, valor_solicitado: float, faturamento_mensal: float) -> float:
    if not analise.aprovado:
        return 0.0
    teto = faturamento_mensal * 3 if faturamento_mensal else valor_solicitado
    base = min(valor_solicitado, teto)
    fator = 0.85 if analise.risco == "medio" else 1.0
    if analise.risco == "alto":
        fator = 0.5
    return round(base * fator, 2)


def montar_proposta(
    empresa: Empresa,
    analise: Analise,
    valor_solicitado: float,
    prazo: int,
    faturamento_mensal: float,
    contexto_rag: list[str],
    responsavel_legal: str | None,
    email_contato: str | None,
    telefone_contato: str | None,
    dados_bancarios: str | None,
) -> Proposta:
    aprovado = _valor_aprovado(analise, valor_solicitado, faturamento_mensal)
    taxa = _taxa(analise.risco)
    politica = " ".join(contexto_rag[:2]) if contexto_rag else "Política interna de crédito padrão."

    if analise.aprovado:
        texto = (
            f"Prezados,\n\nCom base na consulta cadastral da empresa {empresa.razao_social} "
            f"(CNPJ {empresa.cnpj}) e na política comercial vigente, apresentamos proposta de crédito "
            f"no valor de R$ {aprovado:,.2f}, com prazo de {prazo} meses e taxa de {taxa:.2f}% ao mês.\n\n"
            f"A análise considerou situação cadastral, tempo de abertura, capital social, CNAE e faturamento. "
            f"Score interno: {analise.score} (risco {analise.risco}).\n\n"
            f"Referência de política: {politica[:400]}\n\n"
            "Os valores incluem impostos e encargos. Esta proposta tem validade mínima de 60 dias."
        ).replace(",", "X").replace(".", ",").replace("X", ".")
        # The money formatting above is messy for the first number - let's do cleaner:
        texto = (
            f"Prezados,\n\nCom base na consulta cadastral da empresa {empresa.razao_social} "
            f"(CNPJ {empresa.cnpj}) e na política comercial vigente, apresentamos proposta de crédito "
            f"no valor aprovado de {aprovado:.2f} reais, prazo de {prazo} meses e taxa de {taxa:.2f}% a.m.\n\n"
            f"A análise considerou situação cadastral, tempo de abertura, capital social, CNAE e faturamento. "
            f"Score interno: {analise.score} (risco {analise.risco}).\n\n"
            f"Referência de política: {politica[:400]}\n\n"
            "Os valores incluem impostos e encargos. Esta proposta tem validade mínima de 60 dias."
        )
    else:
        texto = (
            f"Prezados,\n\nApós análise da empresa {empresa.razao_social} (CNPJ {empresa.cnpj}), "
            f"o crédito não foi aprovado nesta etapa. Motivo: {analise.motivo}\n\n"
            f"Score interno: {analise.score} (risco {analise.risco}). "
            "Uma nova avaliação poderá ser feita após regularização cadastral ou revisão do valor solicitado."
        )

    item_desc = (
        f"Linha de crédito empresarial — {prazo} meses — taxa {taxa:.2f}% a.m. "
        "Inclui impostos e encargos conforme política."
    )
    itens = [
        ItemProposta(
            item="1",
            descricao=item_desc,
            quantidade=1,
            valor_unitario=aprovado,
            valor_total=aprovado,
        )
    ]

    cidade = empresa.cidade
    if empresa.uf:
        cidade = f"{empresa.cidade}/{empresa.uf}" if empresa.cidade else empresa.uf

    return Proposta(
        razao_social=empresa.razao_social,
        nome_fantasia=empresa.nome_fantasia,
        cnpj=empresa.cnpj or format_cnpj(empresa.cnpj),
        endereco=empresa.endereco,
        cidade=cidade,
        cep=empresa.cep,
        telefone=telefone_contato or empresa.telefone,
        email=email_contato or empresa.email,
        responsavel_legal=responsavel_legal,
        dados_bancarios=dados_bancarios,
        itens=itens,
        valor_aprovado=aprovado,
        prazo=prazo,
        taxa=taxa,
        validade_dias=60,
        impostos_encargos="Valores brutos já consideram impostos e encargos da operação.",
        texto=texto,
    )
