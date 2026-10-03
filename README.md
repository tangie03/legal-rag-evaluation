# Legal RAG evaluation

A Python research package for continuing the Vietnamese ESG legal QA dissertation. Workflows validate recovered inputs, inventory private files and run a small synthetic retrieval check. Sentence and Sentence Window BGE-M3 retrieval have been extracted into an optional model workflow; see `docs/RETRIEVAL_RUNS.md` for installation and small-run commands. Fresh BGE-M3 results have not yet been reproduced. Historical notebooks are retained for comparison; answer generation still needs migration.

## Set up on Mac or Apollo

Use a separate environment for this repository. Python 3.10 or newer is required; the recovered Apollo environment used Python 3.12.12. The lightweight package has no runtime dependencies. Model dependencies will be installed separately when the historical retrieval workflow is migrated.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
python -m pytest -q
python -m ruff check src tests
```

To reproduce the development-tool versions tested with this change, install `requirements-dev.lock.txt` before installing the package with `python -m pip install -e . --no-deps`. This lock covers tests and linting, not historical model execution.

## Run without private data

```bash
python -m legal_rag.cli smoke --output runs/smoke-001
```

This command uses invented documents and deterministic word-overlap retrieval. It exercises retrieval, source-span coverage and result recording without internet, a GPU or API credentials. It writes `manifest.json` and `retrieved.jsonl`, and refuses to overwrite an existing run directory. Use a new directory for each new run. This check does not reproduce BGE-M3 results or generate legal answers.

## Validate the recovered corpus

Keep the private corpus outside Git. On the Mac setup used in this project:

```bash
export LEGAL_RAG_DATA_ROOT="$HOME/legal-rag-data/esg_rag_project"
python -m legal_rag.cli doctor
python -m legal_rag.cli validate
```

On Apollo, set the same variable to the actual project location there. `doctor` reports missing files. `validate` checks benchmark links, gold text, source offsets and the historical evaluation fingerprint. See `docs/APOLLO_RECOVERY.md` for the recovered corpus discrepancy and evidence-export exception. Inventory files with:

```bash
python -m legal_rag.cli inventory --manifest runs/input-manifest.json
python -m legal_rag.cli verify --manifest runs/input-manifest.json
```

## Project layout

| Path | Purpose |
| --- | --- |
| `src/legal_rag/` | Importable implementation and command-line interface |
| `tests/` | Small tests that do not need Apollo data or models |
| `configs/` | Experiment configuration guidance |
| `notebooks/` | Historical dissertation notebooks |
| `docs/` | Recovery audit and migration instructions |
| `scripts/` | Apollo environment check helper |
| `.github/workflows/` | Automated tests and linting after a GitHub push |
| `runs/` | Local generated results, ignored by Git |

Commit source, tests, configuration and documentation. Keep private datasets, credentials, caches, model checkpoints and generated results outside version control. Run tests and linting before committing. Record new experiment outputs in a fresh directory and preserve paper-aligned results.

## Next implementation milestone

Run the extracted Sentence and Sentence Window retrieval on a small subset with BGE-M3, reconcile model and environment versions, then compare a full run with the archived output. A successful synthetic smoke check or input validation does not establish model-result reproduction. Restart-safe model caches and answer generation are later migrations.
