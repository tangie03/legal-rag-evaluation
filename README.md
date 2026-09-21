# Dissertation reproducibility package

This package contains the data, code, selected outputs and environment records for the dissertation's legal retrieval-augmented generation experiments.

## Important result-version notice

The authoritative results reported in the dissertation are the paper-aligned outputs under:

`02_outputs/answer_generation/paper_frozen_results/`

Notebook 09 was accidentally rerun on 15 September 2026 after the dissertation had been written. That rerun regenerated the reference-correction judgments and changed several derived answer-quality metrics. The previously saved Jupyter checkpoint retained the original executed outputs. Those checkpoint tables were recovered and checked against the dissertation's headline values, including:

- Sentence-window, Qwen3-4B: 59.3% exact and 78.0% at least partially correct;
- Sentence-window, Qwen3-8B: 66.9% exact and 82.2% at least partially correct.

The restored executed Notebook 09 in `01_code/notebooks/final/` is the historical record matching the dissertation. The safeguarded version in `01_code/notebooks/safe_rerun/` is intended for future visual revisions. Its default `paper_visuals` mode does not regenerate answers, call the judge API, rebuild correction judgments or overwrite the historical run.

The older row-level gold-corrected JSONL was overwritten during the accidental rerun and could not be recovered. The verified aggregate, omnibus, method-comparison and model-comparison outputs were recovered from the pre-rerun notebook checkpoint. Files from the later rerun are retained only as an audit trail and are not the source of the dissertation's reported metrics.

## Directory structure

```text
00_data/
  01_raw/             Original legal documents and source metadata
  02_annotations/     Development, evaluation and judge-calibration annotations
  03_processed/       Parsed, cleaned and split project data
  04_manifests/       File inventories, security-scan record and SHA-256 checksums
01_code/
  notebooks/final/    Nine notebooks in execution order
  notebooks/safe_rerun/
                       Safeguarded Notebook 09 for visual revisions
  scripts/             Standalone scripts, where applicable
  configuration/       Non-secret configuration files, where applicable
02_outputs/
  retrieval/           Selected single- and multi-passage retrieval results
  answer_generation/   Paper-frozen results and retained audit/source outputs
  statistical_analysis/
  tables/
  figures/
  qualitative_examples/
03_environment/        Mac and Apollo Python/Conda environment records
04_appendix/           Appendix-oriented supporting material
```

## Notebook order

1. `01_preprocessing.ipynb` — source-document preprocessing
2. `02_split_chunk.ipynb` — data splitting and initial chunk preparation
3. `03_article_parsing.ipynb` — legal-article structure parsing
4. `04_qa_benchmark.ipynb` — QA benchmark construction
5. `05_chunking_development.ipynb` — chunking-method development
6. `06_development_analysis_and_selection.ipynb` — development-set analysis and frozen configuration selection
7. `07_single_passage_evaluation.ipynb` — single-passage retrieval evaluation and computational-cost analysis
8. `08_multi_passage_challenge.ipynb` — multi-passage challenge evaluation
9. `09_answer_generation_evaluation.ipynb` — restored executed answer-generation and evaluation record matching the dissertation

Notebooks 01–04 and 06 were primarily developed on macOS. The final computational runs for Notebooks 05 and 07–09 were performed on the Apollo computing environment.

## Safe use of Notebook 09

For figure or primary-table revisions, use:

`01_code/notebooks/safe_rerun/09_answer_generation_evaluation_safe_visuals.ipynb`

Its default mode is `paper_visuals`. Running all cells in this mode loads the recovered paper-aligned summary, verifies the headline metrics and writes revised visuals to a new UTC-stamped `visual_revisions` directory.

A genuinely new generation/judging experiment requires all of the following:

- `NB09_EXECUTION_MODE=full_pipeline`
- `NB09_ALLOW_FULL_PIPELINE=CREATE_A_NEW_VERSIONED_RUN`
- a new `NB09_NEW_RUN_ID`

The historical corpus/run identifier cannot be reused as a new run identifier. API credentials are not included in this package.

## Data and output scope

The package includes the raw legal corpus, source metadata, core manual annotations, processed data and selected analysis outputs needed to inspect the dissertation workflow. Large regenerable vector indexes, embedding caches, model checkpoints and transient execution caches are excluded. This avoids including approximately 32 GB of non-critical intermediate files.

## Environments

The `03_environment/` directory contains separate records for macOS and Apollo:

- Python version;
- `pip freeze` package snapshot;
- Conda environment history.

Absolute paths in the notebooks reflect the original execution environments and may need to be adapted when the package is moved.

## Integrity and privacy

SHA-256 manifests are stored under `00_data/04_manifests/`. The submitted notebooks were scanned for complete Anthropic and OpenAI API keys; no complete API keys were detected. Literal key prefixes in input prompts and masked password-entry output are not credentials.

After making any final change, regenerate the relevant checksum manifest before creating the submission archive.
