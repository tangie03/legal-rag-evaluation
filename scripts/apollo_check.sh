#!/usr/bin/env bash
set -euo pipefail

# Run on an Apollo compute node after activating the appropriate environment.
: "${LEGAL_RAG_DATA_ROOT:?Set LEGAL_RAG_DATA_ROOT to the private dataset directory}"
python -m pip install -e '.[dev]'
python -m pytest -q
python -m legal_rag.cli inventory --data-root "$LEGAL_RAG_DATA_ROOT" --manifest runs/apollo-data-manifest.json
echo "Inventory saved under runs/ (ignored by Git)."
