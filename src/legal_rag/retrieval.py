"""Bounded Sentence and Sentence Window BGE-M3 retrieval runs."""

import copy
import hashlib
import importlib.metadata
import json
import platform
import subprocess
import sys
from pathlib import Path

from legal_rag.baseline import corpus_fingerprint, read_jsonl, validate_baseline
from legal_rag.chunking import create_nodes
from legal_rag.scoring import score_budget_retrieval, score_retrieval


def run_retrieval(
    root: Path,
    output: Path,
    method: str,
    question_limit: int = 3,
    document_limit: int = 3,
    device: str = "cpu",
    revision: str | None = None,
):
    """Zero limits select the full corpus; small subsets are diagnostic only."""
    if sys.version_info >= (3, 13):
        raise ValueError(
            "Use a separate Python 3.12 environment for the historical retrieval dependencies."
        )
    if output.exists():
        raise ValueError(f"Output already exists: {output}")
    if method not in {"sentence", "sentence_window"}:
        raise ValueError("Only Sentence and Sentence Window have been migrated.")
    if question_limit < 0 or document_limit < 0:
        raise ValueError("Limits must be nonnegative; zero means all.")
    baseline = validate_baseline(root)
    folder = root / "outputs/qa_benchmark"
    frozen = json.loads((folder / "frozen_chunking_configurations_2.4.1.json").read_text())
    config = next(row for row in frozen["configurations"] if row["method"] == method)
    queries = read_jsonl(folder / "evaluation_qa_benchmark_2.3.5-final.jsonl")
    if question_limit:
        queries = queries[:question_limit]
    paths = sorted((root / "data/splits/eval").glob("*.txt"))
    gold_ids = {row["doc_id"] for row in queries}
    if document_limit:
        if document_limit < len(gold_ids):
            raise ValueError("Document limit must include all selected questions' gold documents.")
        required = [path for path in paths if path.stem in gold_ids]
        extras = [path for path in paths if path.stem not in gold_ids]
        paths = sorted(required + extras[: max(0, document_limit - len(required))])
    try:
        from llama_index.core import Document, VectorStoreIndex
        from llama_index.core.postprocessor import MetadataReplacementPostProcessor
        from llama_index.core.schema import QueryBundle
        from llama_index.embeddings.huggingface import HuggingFaceEmbedding
        from transformers import AutoTokenizer
    except ImportError as error:
        raise ValueError("Install with: python -m pip install -e '.[retrieval]'") from error
    documents = [
        Document(
            text=path.read_text(encoding="utf-8"),
            id_=path.stem,
            metadata={"doc_id": path.stem, "split": "eval", "cleaned_filename": path.name},
            excluded_embed_metadata_keys=["doc_id", "split", "cleaned_filename"],
            excluded_llm_metadata_keys=["doc_id", "split", "cleaned_filename"],
        )
        for path in paths
    ]
    texts = {path.stem: path.read_text(encoding="utf-8") for path in paths}
    lookup = {}
    for kind, identifier in [("units", "unit_id"), ("provisions", "provision_id")]:
        for row in read_jsonl(root / f"data/parsed/eval_{kind}.jsonl"):
            lookup[(row[identifier], row["doc_id"])] = row
    model_name = frozen["embedding_model"]
    revision_args = {"revision": revision} if revision else {}
    tokenizer = AutoTokenizer.from_pretrained(model_name, **revision_args)
    resolved_revision = tokenizer.init_kwargs.get("_commit_hash")
    if resolved_revision:
        revision_args = {"revision": resolved_revision}
    model = HuggingFaceEmbedding(
        model_name=model_name,
        max_length=8192,
        normalize=True,
        embed_batch_size=4,
        show_progress_bar=False,
        device=device,
        **revision_args,
    )
    nodes = create_nodes(method, config["parameters"], documents)
    for node in nodes:
        node.embedding = None
        node.excluded_embed_metadata_keys = list(node.metadata)
        node.excluded_llm_metadata_keys = list(node.metadata)
    index = VectorStoreIndex(nodes, embed_model=model, show_progress=False)
    retriever = index.as_retriever(similarity_top_k=min(50, len(nodes)))
    postprocessor = MetadataReplacementPostProcessor(target_metadata_key="window")
    records = []
    for query in queries:
        gold = lookup[(query["evidence_id"], query["doc_id"])]
        query = dict(
            query, evidence_start_char=gold["start_char"], evidence_end_char=gold["end_char"]
        )
        vector = model.get_query_embedding(query["question"])
        if len(vector) != 1024:
            raise ValueError("BGE-M3 vectors must have 1024 dimensions.")
        bundle = QueryBundle(query_str=query["question"], embedding=vector)
        results = retriever.retrieve(bundle)
        if method == "sentence_window":
            results = postprocessor.postprocess_nodes(copy.deepcopy(results), query_bundle=bundle)
        source = texts[query["doc_id"]]
        scores = {}
        for k in [1, 3, 5, 10]:
            fixed_results = index.as_retriever(similarity_top_k=min(k, len(nodes))).retrieve(bundle)
            if method == "sentence_window":
                fixed_results = postprocessor.postprocess_nodes(
                    copy.deepcopy(fixed_results), query_bundle=bundle
                )
            scores[str(k)] = score_retrieval(query, fixed_results, source, k)
        budget = score_budget_retrieval(query, results, source, tokenizer=tokenizer)
        if budget["budget_unlocated_results"] or any(
            x["unlocated_results"] for x in scores.values()
        ):
            raise ValueError(f"Unlocated source spans: {query['qa_id']}")
        records.append(
            {
                "qa_id": query["qa_id"],
                "method": method,
                "scores": scores,
                "budget": budget,
                "retrieved": [
                    {
                        "doc_id": result.node.metadata["doc_id"],
                        "score": result.score,
                        "text": result.node.get_content(metadata_mode="none"),
                        "start": result.node.start_char_idx,
                        "end": result.node.end_char_idx,
                        "source_spans": result.node.metadata.get("source_spans"),
                    }
                    for result in results
                ],
            }
        )
    git = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=False)
    dirty = subprocess.run(
        ["git", "status", "--porcelain"], capture_output=True, text=True, check=False
    )
    manifest = {
        "workflow": "frozen_retrieval",
        "configuration": config,
        "full_baseline_inputs": baseline,
        "input_file_sha256": {
            name: hashlib.sha256((folder / name).read_bytes()).hexdigest()
            for name in [
                "frozen_chunking_configurations_2.4.1.json",
                "evaluation_qa_benchmark_2.3.5-final.jsonl",
                "evaluation_qa_evidence_2.3.5-final.jsonl",
            ]
        },
        "selected_corpus_sha256": corpus_fingerprint(paths),
        "document_ids": [path.stem for path in paths],
        "question_ids": [q["qa_id"] for q in queries],
        "is_full_evaluation": len(paths) == 81 and len(queries) == 118,
        "indexed_nodes": len(nodes),
        "model": model_name,
        "requested_revision": revision,
        "tokenizer_revision": tokenizer.init_kwargs.get("_commit_hash"),
        "device": device,
        "python": platform.python_version(),
        "git_commit": git.stdout.strip() if git.returncode == 0 else None,
        "git_dirty": bool(dirty.stdout.strip()) if dirty.returncode == 0 else None,
        "versions": {
            name: importlib.metadata.version(name)
            for name in [
                "llama-index-core",
                "llama-index-embeddings-huggingface",
                "transformers",
                "sentence-transformers",
                "torch",
                "tiktoken",
                "nltk",
            ]
        },
        "context_budget": 1000,
        "candidate_k": 50,
        "complete_recall_at_5": sum(r["scores"]["5"]["complete_coverage"] for r in records)
        / len(records),
        "budget_complete_recall": sum(r["budget"]["budget_complete_coverage"] for r in records)
        / len(records),
        "historical_comparison": "Not established; software and model revision need reconciliation.",
    }
    output.mkdir(parents=True, exist_ok=False)
    (output / "retrieval.jsonl").write_text(
        "".join(json.dumps(row) + "\n" for row in records), encoding="utf-8"
    )
    (output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return manifest
