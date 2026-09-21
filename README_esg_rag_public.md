# Legal RAG Evaluation

A research project on **retrieval-augmented generation (RAG) for legal question answering**, covering document preprocessing, chunking, retrieval evaluation, multi-passage retrieval, and answer-generation evaluation.

This public repository is a **lightweight research-code version** of the dissertation project. It contains the nine main Jupyter notebooks and this README; the underlying legal corpus, large intermediate files, model checkpoints, vector indexes, and execution caches are not included.

## Project workflow

The notebooks follow the research pipeline in order:

| # | Notebook | Purpose |
|---|---|---|
| 01 | `01_preprocessing.ipynb` | Source-document preprocessing |
| 02 | `02_split_chunk.ipynb` | Data splitting and initial chunk preparation |
| 03 | `03_article_parsing.ipynb` | Legal-article structure parsing |
| 04 | `04_qa_benchmark.ipynb` | QA benchmark construction |
| 05 | `05_chunking_development.ipynb` | Chunking-method development |
| 06 | `06_development_analysis_and_selection.ipynb` | Development-set analysis and frozen configuration selection |
| 07 | `07_single_passage_evaluation.ipynb` | Single-passage retrieval evaluation and computational-cost analysis |
| 08 | `08_multi_passage_challenge.ipynb` | Multi-passage retrieval evaluation |
| 09 | `09_answer_generation_evaluation.ipynb` | Answer generation and evaluation |

## Research focus

The project examines how different retrieval and chunking choices affect downstream performance in a legal RAG pipeline.

The workflow includes:

- legal document preprocessing and structural parsing;
- chunking-method development and configuration selection;
- single- and multi-passage retrieval evaluation;
- QA benchmark construction;
- answer generation using language models;
- answer-quality evaluation and comparison of retrieval/model configurations.

## Reported results

The dissertation's paper-aligned results include the following headline answer-quality measurements for the sentence-window configuration:

| Model | Exact | At least partially correct |
|---|---:|---:|
| Qwen3-4B | 59.3% | 78.0% |
| Qwen3-8B | 66.9% | 82.2% |

These figures correspond to the restored paper-aligned execution record described in the dissertation project materials.

## Important note about Notebook 09

Notebook 09 was rerun after the dissertation had been written, which changed several derived answer-quality metrics. The version included in the original project package was restored from the executed notebook checkpoint so that its reported results match the dissertation's headline values.

For future visual revisions, the project also contains a safeguarded version of Notebook 09 whose default mode does not regenerate answers or overwrite the historical evaluation run. That safeguarded notebook is **not included in this lightweight public repository**.

## Repository scope

The full dissertation package contains additional material that is intentionally not included here, including:

- raw legal documents and source metadata;
- processed datasets and annotations;
- selected retrieval and answer-generation outputs;
- statistical-analysis outputs and figures;
- environment records;
- large vector indexes and embedding caches;
- model checkpoints and transient execution caches.

The original project documentation notes that large regenerable intermediate files were excluded from the submission package to avoid including approximately 32 GB of non-critical files.

## Reproducibility

The notebooks were developed across macOS and the Apollo computing environment. Some notebooks contain paths or assumptions tied to those original execution environments and may require adaptation before they can be run on another machine.

The full research package also recorded Python/Conda environment information and checksum manifests, but those supporting files are not part of this lightweight public repository.

API credentials are not included.

## Tech stack

- Python
- Jupyter Notebook
- Retrieval-Augmented Generation (RAG)
- Large Language Models (LLMs)
- Legal document processing
- Information retrieval
- Question answering
- Evaluation and statistical analysis

## Repository structure

```text
legal-rag-evaluation/
├── README.md
└── notebooks/
    ├── 01_preprocessing.ipynb
    ├── 02_split_chunk.ipynb
    ├── 03_article_parsing.ipynb
    ├── 04_qa_benchmark.ipynb
    ├── 05_chunking_development.ipynb
    ├── 06_development_analysis_and_selection.ipynb
    ├── 07_single_passage_evaluation.ipynb
    ├── 08_multi_passage_challenge.ipynb
    └── 09_answer_generation_evaluation.ipynb
```

## Citation

This repository contains research code associated with a dissertation on legal retrieval-augmented generation. Please cite the associated dissertation if you use the methodology, notebooks, or reported results in academic work.
