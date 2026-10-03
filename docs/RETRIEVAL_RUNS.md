# Migrated retrieval runs

Sentence and Sentence Window chunking and multi-span scoring have been extracted from the uploaded final Apollo Notebook 07. The migration preserves Sentence settings (512 tokens with 50 overlap), Sentence Window size 7, text-only embeddings, normalized BGE-M3 vectors, 50 budget candidates and the 1,000-token budget with tokenizer-offset truncation. Fixed-depth retrieval is run separately at depths 1, 3, 5 and 10, as in the notebook.

The default run selects three questions and up to three documents, including each selected question's gold document. Such a run checks operation, not representative accuracy: it removes most distractors. Output folders must be new. Retrieval runs do not generate answers or call a judge API.

## Install separately from lightweight development

Use Python 3.12 for the retrieval environment. A Python 3.13 install can select NumPy 1.26.4, which only supports Python 3.9 through 3.12, and attempt a failing source build. The lightweight package tests can still run under Python 3.13; they do not establish that embedding dependencies installed.

```bash
python -m pip install -e '.[retrieval]'
```

This adds the embedding dependencies. The first actual run downloads BGE-M3 and its tokenizer unless cached; it also needs the parser's sentence and token resources. The historical notebook requested core 0.14.23, while the uploaded environment snapshot lists core 0.14.24 and omits several embedding packages. Core and its Hugging Face integration are pinned to the notebook values in the retrieval extra; transitive model dependencies are not yet a complete historical environment lock. Actual installed versions and the resolved tokenizer revision are recorded. The model is requested at the same resolved revision as the tokenizer.

Use the existing Apollo model environment if it is available. A Mac run can use CPU but may take longer. Do not install over the old dissertation environment just to reconcile the conflicting snapshots; use a separate environment for new runs.

## Small run on the Mac

```bash
export LEGAL_RAG_DATA_ROOT="$HOME/legal-rag-data/esg_rag_project"
python -m legal_rag.cli retrieve --method sentence --device cpu --output runs/bge-sentence-001
python -m legal_rag.cli retrieve --method sentence_window --device cpu --output runs/bge-window-001
```

On an allocated Apollo GPU compute session, set `LEGAL_RAG_DATA_ROOT` to the private project root on Apollo and use `--device cuda`. No generation or judging credentials are needed.

For another run, use another output directory. Each successful run writes `retrieval.jsonl` and `manifest.json`, with source spans, token-budget scores, selected corpus fingerprint, model revision, package versions and source commit. This implementation rebuilds the index each time; restart-safe caches from the notebook have not been migrated yet. Historical latency and build-cost comparisons are not supported by this runner.

To select all documents and all questions, use `--document-limit 0 --question-limit 0`; first complete and inspect the small runs. A new full run is not evidence of historical result reproduction until its metrics and environment are compared with the archived output.

## Validation completed during extraction

The actual parsers generated 2,008 Sentence nodes and 24,693 Sentence Window nodes, matching archived counts, from the 81-document corpus and attached verified constituent source spans to every node. Replaying coverage from the two methods' 236 archived rows reproduced 1,180 fixed-depth and fixed-budget coverage values. Unit tests cover incorrect-document budgets, disjoint window spans, repeated text and truncation. An integration test uses the real parser and vector index with mock embeddings; it does not load BGE-M3.

No fresh BGE-M3 embedding or retrieval run has been completed in this workspace. The optional full model dependency install was not completed; GPU binaries were not needed to verify parsing or scoring. Run the small commands above on the Mac or Apollo to establish model compatibility before freezing a complete retrieval environment.
