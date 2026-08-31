from __future__ import annotations

from backend.models.schemas import Empresa
from backend.services.receitaws import consultar_cnpj


class AgenteConsultorCNPJ:
    nome = "Consultor CNPJ"

    def executar(self, cnpj: str) -> Empresa:
        return consultar_cnpj(cnpj)
