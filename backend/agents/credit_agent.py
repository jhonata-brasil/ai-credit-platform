from __future__ import annotations

from backend.models.schemas import Analise, Empresa
from backend.services.credit import analisar_credito


class AgenteAnalistaCredito:
    nome = "Analista de Crédito"

    def executar(
        self,
        empresa: Empresa,
        valor_solicitado: float,
        prazo: int,
        faturamento_mensal: float,
    ) -> Analise:
        return analisar_credito(empresa, valor_solicitado, prazo, faturamento_mensal)
