# Plataforma de crédito com IA

Site simples para analisar CNPJ, aplicar regras de crédito e gerar proposta comercial (JSON e PDF).

Outras pessoas usam pelo **endereço do site**. Não é necessário instalar nada no computador delas.

## Como publicar um link para outras pessoas (Render)

1. Crie uma conta em [https://render.com](https://render.com)
2. New → Web Service → conecte este repositório
3. Runtime: Docker (o `Dockerfile` já está na raiz)
4. Depois do deploy, o Render mostra um endereço do tipo `https://algo.onrender.com`

Esse é o link para enviar. Quem abrir vê o formulário e usa a análise.

A API gratuita da ReceitaWS tem limite de consultas por minuto. Se muitas pessoas usarem ao mesmo tempo, pode atrasar.

## Rodar no seu computador

```bash
cd ai-credit-platform
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export PYTHONPATH=.
uvicorn backend.api.main:app --reload --host 0.0.0.0 --port 8000
```

Abra [http://localhost:8000](http://localhost:8000).

Com Docker:

```bash
docker compose up --build
```

## Endpoint

`POST /api/v1/analyze-credit`

## O que o sistema faz

1. Consulta o CNPJ em `https://www.receitaws.com.br/v1/cnpj/{cnpj}`
2. Aplica análise de crédito (situação, tempo de abertura, capital, CNAE, faturamento, score)
3. Busca políticas internas em `docs/knowledge` (RAG)
4. Gera proposta com validade de 60 dias, impostos/encargos e PDF

Chave OpenAI é opcional. O fluxo já funciona sem ela, com regras e documentos internos.
