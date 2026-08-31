from __future__ import annotations

from pathlib import Path

from langchain_text_splitters import RecursiveCharacterTextSplitter

KNOWLEDGE_DIR = Path(__file__).resolve().parents[2] / "docs" / "knowledge"


def _read_documents() -> list[tuple[str, str]]:
    docs: list[tuple[str, str]] = []
    if not KNOWLEDGE_DIR.exists():
        return docs
    for path in KNOWLEDGE_DIR.rglob("*"):
        if path.suffix.lower() not in {".md", ".txt", ".mdx"}:
            continue
        docs.append((path.name, path.read_text(encoding="utf-8")))
    return docs


def _chunks() -> list[str]:
    splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=150)
    pieces: list[str] = []
    for name, text in _read_documents():
        for chunk in splitter.split_text(text):
            pieces.append(f"[{name}] {chunk}")
    return pieces


def buscar_contexto(query: str, k: int = 4) -> list[str]:
    """Busca simples por relevância lexical (funciona sem chave OpenAI)."""
    chunks = _chunks()
    if not chunks:
        return []
    terms = [t.lower() for t in query.split() if len(t) > 3]
    scored: list[tuple[int, str]] = []
    for chunk in chunks:
        low = chunk.lower()
        score = sum(low.count(term) for t in terms for term in [t])
        scored.append((score, chunk))
    scored.sort(key=lambda x: x[0], reverse=True)
    selected = [c for s, c in scored if s > 0][:k]
    if not selected:
        selected = [c for _, c in scored[:k]]
    return selected
