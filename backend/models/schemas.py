from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, field_validator


class AnalyzeCreditRequest(BaseModel):
    cnpj: str = Field(..., examples=["11378117000120"])
    valor_solicitado: float = Field(..., gt=0)
    prazo: int = Field(..., ge=1, le=120, description="Prazo em meses")
    faturamento_mensal: float = Field(..., ge=0)
    responsavel_legal: str | None = None
    email_contato: str | None = None
    telefone_contato: str | None = None
    dados_bancarios: str | None = None

    @field_validator("cnpj")
    @classmethod
    def only_digits(cls, value: str) -> str:
        digits = "".join(ch for ch in value if ch.isdigit())
        if len(digits) != 14:
            raise ValueError("CNPJ deve ter 14 dígitos")
        return digits


class Empresa(BaseModel):
    razao_social: str
    nome_fantasia: str | None = None
    cnpj: str
    situacao: str
    porte: str | None = None
    capital_social: float = 0
    cnae: str | None = None
    cnae_descricao: str | None = None
    endereco: str | None = None
    cidade: str | None = None
    uf: str | None = None
    cep: str | None = None
    telefone: str | None = None
    email: str | None = None
    abertura: str | None = None
    anos_atividade: float = 0


class Analise(BaseModel):
    score: int
    risco: Literal["baixo", "medio", "alto"]
    aprovado: bool
    motivo: str
    criterios: list[str]


class ItemProposta(BaseModel):
    item: str
    descricao: str
    quantidade: int
    valor_unitario: float
    valor_total: float


class Proposta(BaseModel):
    razao_social: str
    nome_fantasia: str | None = None
    cnpj: str
    endereco: str | None = None
    cidade: str | None = None
    cep: str | None = None
    telefone: str | None = None
    email: str | None = None
    responsavel_legal: str | None = None
    dados_bancarios: str | None = None
    itens: list[ItemProposta]
    valor_aprovado: float
    prazo: int
    taxa: float
    validade_dias: int = 60
    impostos_encargos: str
    texto: str


class AnalyzeCreditResponse(BaseModel):
    empresa: Empresa
    analise: Analise
    proposta: Proposta | None = None
    contexto_rag: list[str] = []
    pdf_url: str | None = None
    cnpj_em_cache: bool = False
