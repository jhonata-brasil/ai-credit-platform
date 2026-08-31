from __future__ import annotations

from backend.models.schemas import Analise, Empresa, Proposta


class AgenteRevisor:
    nome = "Revisor"

    def executar(self, empresa: Empresa, analise: Analise, proposta: Proposta) -> list[str]:
        erros: list[str] = []
        obrigatorios = {
            "razao_social": proposta.razao_social,
            "cnpj": proposta.cnpj,
        }
        for campo, valor in obrigatorios.items():
            if not valor:
                erros.append(f"Campo obrigatório ausente: {campo}")
        if analise.aprovado and proposta.valor_aprovado <= 0:
            erros.append("Proposta aprovada sem valor")
        if proposta.validade_dias < 60:
            erros.append("Validade abaixo do mínimo de 60 dias")
            proposta.validade_dias = 60
        if not empresa.razao_social:
            erros.append("Razão social não preenchida")
        return erros
