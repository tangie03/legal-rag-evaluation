# Continuing the dissertation project

## Current boundary

This public repository contains nine historical notebooks, but no raw corpus, annotations, processed data, environment snapshots or vector indexes. The research pipeline cannot yet run end to end from this checkout. The notebook outputs are historical records; do not use Run All to regenerate the paper results.

The Mac notebooks reference `/Users/tanggiee/Desktop/RAG_AI/esg_rag_project` and `/Users/tanggiee/Desktop/RAG_AI/Documents`. Apollo notebooks reference `/data/home/zll/xh0862/esg_rag_project`. These are old machine-specific locations and should be replaced only after the full data package is inventoried.

## Recommended private data layout

Keep the full package outside Git. Set `LEGAL_RAG_DATA_ROOT` to its local path on each machine. A future data adapter will map its actual folders after inspection. Do not copy legal source documents, annotation tables, credentials, checkpoints, indexes, or historical answer outputs into this public repository.

## Initial setup

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
pytest -q
ruff check src tests
export LEGAL_RAG_DATA_ROOT=/absolute/path/to/private/full/package
legal-rag inventory --manifest runs/local-data-manifest.json
legal-rag verify --manifest runs/local-data-manifest.json
```

On Apollo, activate your Python environment and set `LEGAL_RAG_DATA_ROOT` to the Apollo copy before running `bash scripts/apollo_check.sh` from this repository. The script is scheduler-independent; submit it through your site's normal job workflow if compute jobs require a scheduler.

## Migration sequence

1. Obtain the `RAG_AI` folder or `F516607_data.tar.gz` (and its `.sha256` companion) from the Mac. On Apollo, the screenshot shows `esg_rag_project` and separate `apollo_processed_data_7d74b8baa8.tar.gz`, `apollo_final_notebooks.tar.gz`, `apollo_critical_outputs_7d74b8baa8.tar.gz`, `apollo_environment.tar.gz`, and `paper_frozen_results_recovery.tar.gz` archives, several with checksum companions. Preserve their original names and verify supplied checksums before extraction. The screenshots establish that these files exist on those machines, not that they are accessible from this checkout.
2. Compare its structure against the dissertation package's `00_data`, `01_code`, `02_outputs`, `03_environment` and `04_appendix` directories. Identify the safeguarded Notebook 09 and preserve `paper_frozen_results` unchanged.
3. Record manifests on Mac and Apollo and check that the intended inputs have matching hashes.
4. Extract preprocessing, parsing, retrieval and evaluation functions from the notebooks into `src/legal_rag/` incrementally, with small fixture-based tests. Add a configuration file and environment lock for each runnable stage.
5. Run one frozen baseline in a new `runs/<run-id>/` folder. Only then start new benchmark and retrieval experiments.

## Git practice

Use a branch per change and commit source, tests, configuration templates and documentation. `data/`, `artifacts/`, `runs/`, secrets and local environments are ignored. Review `git status` before every commit or push.
