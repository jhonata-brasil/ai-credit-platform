from __future__ import annotations

from backend.rag.pipeline import buscar_contexto


class AgenteRAGRetriever:
    nome = "RAG Retriever"

    def executar(self, query: str) -> list[str]:
        return buscar_contexto(query, k=4)
