from __future__ import annotations

import json
import os
from datetime import datetime, timedelta
from pathlib import Path

from backend.models.schemas import Empresa

TTL_DAYS = 7
_MEMORY: dict[str, dict] = {}


def _digits(cnpj: str) -> str:
    return "".join(ch for ch in cnpj if ch.isdigit())


def _cache_dir() -> Path:
    if os.environ.get("VERCEL"):
        return Path("/tmp/cnpj-cache")
    return Path("data/cnpj-cache")


def _path(cnpj: str) -> Path:
    return _cache_dir() / f"{_digits(cnpj)}.json"


def _fresh(payload: dict) -> bool:
    saved = payload.get("saved_at")
    if not saved:
        return False
    try:
        dt = datetime.fromisoformat(saved)
    except ValueError:
        return False
    return datetime.now() - dt < timedelta(days=TTL_DAYS)


def ler_cnpj(cnpj: str) -> Empresa | None:
    key = _digits(cnpj)
    payload = _MEMORY.get(key)
    if payload and _fresh(payload):
        return Empresa.model_validate(payload["empresa"])
    path = _path(key)
    if not path.exists():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    if not _fresh(payload):
        return None
    _MEMORY[key] = payload
    return Empresa.model_validate(payload["empresa"])


def gravar_cnpj(empresa: Empresa) -> None:
    key = _digits(empresa.cnpj)
    payload = {
        "saved_at": datetime.now().isoformat(),
        "empresa": empresa.model_dump(),
    }
    _MEMORY[key] = payload
    folder = _cache_dir()
    try:
        folder.mkdir(parents=True, exist_ok=True)
        _path(key).write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    except OSError:
        pass
