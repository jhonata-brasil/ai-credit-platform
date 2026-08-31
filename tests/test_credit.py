from backend.services.credit import analisar_credito
from backend.models.schemas import Empresa


def test_empresa_inativa_reprovada():
    empresa = Empresa(
        razao_social="TESTE LTDA",
        cnpj="00.000.000/0001-00",
        situacao="BAIXADA",
        capital_social=100000,
        anos_atividade=5,
    )
    analise = analisar_credito(empresa, 10000, 12, 100000)
    assert analise.aprovado is False
