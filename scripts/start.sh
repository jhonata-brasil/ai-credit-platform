#!/usr/bin/env bash
set -euo pipefail
export PYTHONPATH=.
uvicorn backend.api.main:app --host 0.0.0.0 --port "${PORT:-8000}"
