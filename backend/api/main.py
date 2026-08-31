from __future__ import annotations

import os
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from backend.models.schemas import AnalyzeCreditRequest, AnalyzeCreditResponse
from backend.services.pdf import gerar_pdf
from backend.workflows.credit_workflow import CreditWorkflow, WorkflowState

ROOT = Path(__file__).resolve().parents[2]
PUBLIC_DIR = ROOT / "public"
FRONTEND_DIR = ROOT / "frontend"

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
    from backend.services.pdf import output_dir

    path = output_dir() / filename
    if not path.exists():
        raise HTTPException(status_code=404, detail="PDF não encontrado")
    return FileResponse(path, media_type="application/pdf", filename=filename)


def _static_dir() -> Path | None:
    for candidate in (PUBLIC_DIR, FRONTEND_DIR):
        if candidate.is_dir() and (candidate / "index.html").exists():
            return candidate
    return None


# On Vercel, files in public/ are served by the CDN. Mounting "/" crashes
# the function when the folder is not in the serverless bundle.
if not os.environ.get("VERCEL"):
    static_dir = _static_dir()
    if static_dir is not None:
        app.mount("/", StaticFiles(directory=str(static_dir), html=True), name="frontend")
