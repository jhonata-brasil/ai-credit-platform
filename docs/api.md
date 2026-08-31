# API

## POST /api/v1/analyze-credit

```json
{
  "cnpj": "11378117000120",
  "valor_solicitado": 150000,
  "prazo": 24,
  "faturamento_mensal": 500000
}
```

## GET /api/v1/propostas/{arquivo}.pdf

Download da proposta gerada.

## GET /health

Checagem do serviço.
