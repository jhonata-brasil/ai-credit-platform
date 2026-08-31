from __future__ import annotations

from backend.models.schemas import Empresa
from backend.services.cnpj_cache import gravar_cnpj, ler_cnpj
from backend.services.receitaws import consultar_cnpj


class AgenteConsultorCNPJ:
    nome = "Consultor CNPJ"

    def executar(self, cnpj: str) -> tuple[Empresa, bool]:
        cached = ler_cnpj(cnpj)
        if cached is not None:
            return cached, True
        empresa = consultar_cnpj(cnpj)
        gravar_cnpj(empresa)
        return empresa, False
