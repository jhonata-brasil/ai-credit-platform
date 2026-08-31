from __future__ import annotations

from datetime import datetime

import httpx

from backend.models.schemas import Empresa

RECEITA_URL = "https://www.receitaws.com.br/v1/cnpj/{cnpj}"
BRASILAPI_URL = "https://brasilapi.com.br/api/cnpj/v1/{cnpj}"


def format_cnpj(cnpj: str) -> str:
    d = "".join(ch for ch in cnpj if ch.isdigit())
    return f"{d[:2]}.{d[2:5]}.{d[5:8]}/{d[8:12]}-{d[12:]}"


def _parse_capital(raw: str | float | int | None) -> float:
    if raw is None:
        return 0.0
    if isinstance(raw, (int, float)):
        return float(raw)
    text = str(raw).replace(".", "").replace(",", ".")
    try:
        return float(text)
    except ValueError:
        return 0.0


def _anos_atividade(abertura: str | None) -> float:
    if not abertura:
        return 0.0
    for fmt in ("%d/%m/%Y", "%Y-%m-%d"):
        try:
            dt = datetime.strptime(abertura, fmt)
            return max(0.0, (datetime.now() - dt).days / 365.25)
        except ValueError:
            continue
    return 0.0


def _from_receita(data: dict, digits: str) -> Empresa:
    if data.get("status") == "ERROR":
        raise ValueError(data.get("message") or "CNPJ não encontrado na ReceitaWS")
    atividade = data.get("atividade_principal") or [{}]
    principal = atividade[0] if atividade else {}
    endereco_parts = [
        data.get("logradouro"),
        data.get("numero"),
        data.get("complemento"),
        data.get("bairro"),
    ]
    endereco = ", ".join(p for p in endereco_parts if p)
    return Empresa(
        razao_social=data.get("nome") or "",
        nome_fantasia=data.get("fantasia") or None,
        cnpj=format_cnpj(digits),
        situacao=(data.get("situacao") or "").upper(),
        porte=data.get("porte"),
        capital_social=_parse_capital(data.get("capital_social")),
        cnae=principal.get("code"),
        cnae_descricao=principal.get("text"),
        endereco=endereco or None,
        cidade=data.get("municipio"),
        uf=data.get("uf"),
        cep=data.get("cep"),
        telefone=data.get("telefone") or None,
        email=data.get("email") or None,
        abertura=data.get("abertura"),
        anos_atividade=round(_anos_atividade(data.get("abertura")), 1),
    )


def _from_brasilapi(data: dict, digits: str) -> Empresa:
    endereco_parts = [
        data.get("descricao_tipo_de_logradouro"),
        data.get("logradouro"),
        data.get("numero"),
        data.get("complemento"),
        data.get("bairro"),
    ]
    endereco = " ".join(str(p) for p in endereco_parts if p)
    abertura = data.get("data_inicio_atividade")
    return Empresa(
        razao_social=data.get("razao_social") or "",
        nome_fantasia=data.get("nome_fantasia") or None,
        cnpj=format_cnpj(digits),
        situacao=(data.get("descricao_situacao_cadastral") or "").upper(),
        porte=data.get("porte") or data.get("descricao_porte"),
        capital_social=_parse_capital(data.get("capital_social")),
        cnae=str(data.get("cnae_fiscal") or "") or None,
        cnae_descricao=data.get("cnae_fiscal_descricao"),
        endereco=endereco or None,
        cidade=data.get("municipio"),
        uf=data.get("uf"),
        cep=data.get("cep"),
        telefone=data.get("ddd_telefone_1") or None,
        email=data.get("email") or None,
        abertura=abertura,
        anos_atividade=round(_anos_atividade(abertura), 1),
    )


def consultar_cnpj(cnpj: str) -> Empresa:
    digits = "".join(ch for ch in cnpj if ch.isdigit())
    errors: list[str] = []
    import os

    verify = os.environ.get("SSL_CERT_FILE") or os.environ.get("REQUESTS_CA_BUNDLE") or True
    with httpx.Client(timeout=20.0, follow_redirects=True, verify=verify) as client:
        try:
            response = client.get(RECEITA_URL.format(cnpj=digits))
            response.raise_for_status()
            return _from_receita(response.json(), digits)
        except Exception as exc:
            errors.append(f"ReceitaWS: {exc}")
        try:
            response = client.get(BRASILAPI_URL.format(cnpj=digits))
            response.raise_for_status()
            return _from_brasilapi(response.json(), digits)
        except Exception as exc:
            errors.append(f"BrasilAPI: {exc}")
    raise ValueError("Não foi possível consultar o CNPJ. " + " | ".join(errors))
