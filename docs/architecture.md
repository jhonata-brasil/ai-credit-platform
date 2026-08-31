# Arquitetura

Usuário acessa o site → FastAPI → orquestração de agentes → consulta ReceitaWS → análise de crédito → RAG → proposta JSON/PDF.

## Fluxo

Input cliente → Consulta CNPJ → Análise de crédito → Busca RAG → Geração da proposta → Validação → Saída.

## Agentes

- Consultor CNPJ
- Analista de crédito
- RAG Retriever
- Gerador de proposta
- Revisor

O site em `frontend/` é a interface para outras pessoas usarem. Langflow fica como mapa visual do fluxo, não como tela pública.
