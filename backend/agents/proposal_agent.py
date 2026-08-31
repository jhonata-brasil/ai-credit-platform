from __future__ import annotations

from backend.models.schemas import Analise, Empresa, Proposta
from backend.services.proposal import montar_proposta


class AgenteGeradorProposta:
    nome = "Gerador de Proposta"

    def executar(
        self,
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
        return montar_proposta(
            empresa,
            analise,
            valor_solicitado,
            prazo,
            faturamento_mensal,
            contexto_rag,
            responsavel_legal,
            email_contato,
            telefone_contato,
            dados_bancarios,
        )
