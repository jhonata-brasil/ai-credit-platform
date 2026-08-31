from __future__ import annotations

from dataclasses import dataclass

from backend.agents.cnpj_agent import AgenteConsultorCNPJ
from backend.agents.credit_agent import AgenteAnalistaCredito
from backend.agents.proposal_agent import AgenteGeradorProposta
from backend.agents.rag_agent import AgenteRAGRetriever
from backend.agents.reviewer_agent import AgenteRevisor
from backend.models.schemas import Analise, Empresa, Proposta


@dataclass
class WorkflowState:
    cnpj: str
    valor_solicitado: float
    prazo: int
    faturamento_mensal: float
    responsavel_legal: str | None = None
    email_contato: str | None = None
    telefone_contato: str | None = None
    dados_bancarios: str | None = None
    empresa: Empresa | None = None
    analise: Analise | None = None
    contexto_rag: list[str] | None = None
    proposta: Proposta | None = None
    revisao: list[str] | None = None
    cnpj_em_cache: bool = False


class CreditWorkflow:
    """Fluxo sequencial (LangGraph-style): CNPJ → crédito → RAG → proposta → revisão."""

    def __init__(self) -> None:
        self.cnpj_agent = AgenteConsultorCNPJ()
        self.credit_agent = AgenteAnalistaCredito()
        self.rag_agent = AgenteRAGRetriever()
        self.proposal_agent = AgenteGeradorProposta()
        self.reviewer = AgenteRevisor()

    def run(self, state: WorkflowState) -> WorkflowState:
        state.empresa, state.cnpj_em_cache = self.cnpj_agent.executar(state.cnpj)
        assert state.empresa is not None
        state.analise = self.credit_agent.executar(
            state.empresa,
            state.valor_solicitado,
            state.prazo,
            state.faturamento_mensal,
        )
        query = (
            f"política crédito CNAE {state.empresa.cnae} porte {state.empresa.porte} "
            f"proposta comercial validade impostos"
        )
        state.contexto_rag = self.rag_agent.executar(query)
        state.proposta = self.proposal_agent.executar(
            state.empresa,
            state.analise,
            state.valor_solicitado,
            state.prazo,
            state.faturamento_mensal,
            state.contexto_rag,
            state.responsavel_legal,
            state.email_contato,
            state.telefone_contato,
            state.dados_bancarios,
        )
        state.revisao = self.reviewer.executar(state.empresa, state.analise, state.proposta)
        return state
