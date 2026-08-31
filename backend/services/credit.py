from __future__ import annotations

from backend.models.schemas import Analise, Empresa

# CNAEs de maior risco (exemplos). Ajuste na política interna.
CNAES_RESTRITOS_PREFIXOS = (
    "9200",  # jogos de azar
    "6499",  # outras atividades financeiras
)

CNAES_PREFERENCIAIS_PREFIXOS = (
    "62",  # TI
    "47",  # comércio varejista
    "46",  # comércio atacadista
    "41",  # construção
    "10",  # alimentos
    "86",  # saúde
)


def analisar_credito(
    empresa: Empresa,
    valor_solicitado: float,
    prazo: int,
    faturamento_mensal: float,
) -> Analise:
    criterios: list[str] = []
    score = 40

    ativa = empresa.situacao == "ATIVA"
    if ativa:
        score += 20
        criterios.append("Empresa ativa na Receita Federal")
    else:
        criterios.append(f"Situação cadastral: {empresa.situacao or 'não informada'}")

    if empresa.anos_atividade >= 5:
        score += 15
        criterios.append(f"Tempo de abertura: {empresa.anos_atividade} anos")
    elif empresa.anos_atividade >= 2:
        score += 10
        criterios.append(f"Tempo de abertura: {empresa.anos_atividade} anos")
    elif empresa.anos_atividade >= 1:
        score += 5
        criterios.append(f"Tempo de abertura: {empresa.anos_atividade} anos (recente)")
    else:
        criterios.append("Empresa com menos de 1 ano de atividade")

    if empresa.capital_social >= valor_solicitado:
        score += 10
        criterios.append("Capital social cobre o valor solicitado")
    elif empresa.capital_social >= valor_solicitado * 0.3:
        score += 5
        criterios.append("Capital social parcial em relação ao crédito")
    else:
        criterios.append("Capital social baixo frente ao valor solicitado")

    faturamento_anual = faturamento_mensal * 12
    if faturamento_mensal <= 0:
        criterios.append("Faturamento não informado")
    elif valor_solicitado <= faturamento_mensal * 3:
        score += 15
        criterios.append("Valor solicitado compatível com o faturamento")
    elif valor_solicitado <= faturamento_anual * 0.4:
        score += 8
        criterios.append("Valor solicitado elevado, mas ainda dentro da política")
    else:
        score -= 10
        criterios.append("Valor solicitado acima da capacidade de pagamento")

    cnae = (empresa.cnae or "").replace(".", "").replace("-", "")
    if any(cnae.startswith(p) for p in CNAES_RESTRITOS_PREFIXOS):
        score -= 20
        criterios.append("CNAE em lista de restrição")
    elif any(cnae.startswith(p) for p in CNAES_PREFERENCIAIS_PREFIXOS):
        score += 8
        criterios.append("CNAE permitido / preferencial")
    else:
        criterios.append("CNAE permitido com análise padrão")

    if prazo <= 12:
        score += 5
    elif prazo > 36:
        score -= 5
        criterios.append("Prazo longo aumenta o risco")

    score = max(0, min(100, score))

    if score >= 75:
        risco = "baixo"
    elif score >= 55:
        risco = "medio"
    else:
        risco = "alto"

    aprovado = ativa and score >= 60
    if not ativa:
        motivo = "Crédito recusado: empresa não está ativa."
    elif not aprovado:
        motivo = "Crédito recusado: score abaixo da política mínima (60)."
    else:
        motivo = "Crédito aprovado conforme política interna e dados da empresa."

    return Analise(
        score=score,
        risco=risco,  # type: ignore[arg-type]
        aprovado=aprovado,
        motivo=motivo,
        criterios=criterios,
    )
