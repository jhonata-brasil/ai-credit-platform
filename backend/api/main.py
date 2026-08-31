from __future__ import annotations

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from backend.models.schemas import AnalyzeCreditRequest, AnalyzeCreditResponse
from backend.services.pdf import gerar_pdf
from backend.workflows.credit_workflow import CreditWorkflow, WorkflowState

app = FastAPI(
    title="Plataforma de Crédito IA",
    description="Consulta CNPJ, análise de crédito, RAG e proposta comercial.",
    version="1.0.0",
)

workflow = CreditWorkflow()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/v1/analyze-credit", response_model=AnalyzeCreditResponse)
def analyze_credit(payload: AnalyzeCreditRequest) -> AnalyzeCreditResponse:
    try:
        state = workflow.run(
            WorkflowState(
                cnpj=payload.cnpj,
                valor_solicitado=payload.valor_solicitado,
                prazo=payload.prazo,
                faturamento_mensal=payload.faturamento_mensal,
                responsavel_legal=payload.responsavel_legal,
                email_contato=payload.email_contato,
                telefone_contato=payload.telefone_contato,
                dados_bancarios=payload.dados_bancarios,
            )
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Falha ao consultar dados: {exc}") from exc

    if not state.empresa or not state.analise or not state.proposta:
        raise HTTPException(status_code=500, detail="Fluxo incompleto")

    pdf_name = f"proposta-{payload.cnpj}.pdf"
    gerar_pdf(state.proposta, pdf_name)

    return AnalyzeCreditResponse(
        empresa=state.empresa,
        analise=state.analise,
        proposta=state.proposta,
        contexto_rag=state.contexto_rag or [],
        pdf_url=f"/api/v1/propostas/{pdf_name}",
    )


@app.get("/api/v1/propostas/{filename}")
def download_pdf(filename: str) -> FileResponse:
    from pathlib import Path

    path = Path("data/propostas") / filename
    if not path.exists():
        raise HTTPException(status_code=404, detail="PDF não encontrado")
    return FileResponse(path, media_type="application/pdf", filename=filename)


app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")
