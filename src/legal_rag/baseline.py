"""Validate recovered baseline inputs without loading models or calling APIs."""

import hashlib
import json
from pathlib import Path

from legal_rag.preflight import missing_inputs

EVALUATION_HASH = "7d74b8baa896be4a5be6a449b0e5eed070a0a67624609630f6c028abce099ded"


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()
            if line.strip()]


def corpus_fingerprint(paths: list[Path]) -> str:
    digest = hashlib.sha256()
    for path in sorted(paths):
        digest.update(path.name.encode("utf-8") + b"\0")
        digest.update(path.read_bytes() + b"\0")
    return digest.hexdigest()


def validate_baseline(root: Path) -> dict:
    missing = missing_inputs(root)
    if missing:
        raise ValueError("Missing inputs: " + ", ".join(missing))
    benchmark = root / "outputs/qa_benchmark"
    qa = read_jsonl(benchmark / "evaluation_qa_benchmark_2.3.5-final.jsonl")
    evidence = read_jsonl(benchmark / "evaluation_qa_evidence_2.3.5-final.jsonl")
    paths = list((root / "data/splits/eval").glob("*.txt"))
    fingerprint = corpus_fingerprint(paths)
    if fingerprint != EVALUATION_HASH:
        raise ValueError("Evaluation corpus differs from the historical fingerprint.")
    by_id = {record["evidence_id"]: record for record in evidence}
    if len(by_id) != len(evidence):
        raise ValueError("Duplicate evidence identifiers.")
    if len({record["qa_id"] for record in qa}) != len(qa):
        raise ValueError("Duplicate question identifiers.")
    document_ids = {path.stem for path in paths}
    units = read_jsonl(root / "data/parsed/eval_units.jsonl")
    provisions = read_jsonl(root / "data/parsed/eval_provisions.jsonl")
    parsed = {(row["unit_id"], row["doc_id"]):
              (row, "unit_text") for row in units}
    parsed.update({(row["provision_id"], row["doc_id"]):
                   (row, "provision_text") for row in provisions})
    absent_evidence_records = []
    for record in qa:
        key = (record["evidence_id"], record["doc_id"])
        if key not in parsed:
            raise ValueError(f"Question has invalid parser link: {record['qa_id']}")
        gold, text_key = parsed[key]
        source = (root / "data/splits/eval" / gold["cleaned_filename"]).read_text(
            encoding="utf-8")
        if (gold[text_key] != record["original_evidence_text"]
                or source[gold["start_char"]:gold["end_char"]].strip() != gold[text_key].strip()):
            raise ValueError(f"Gold text or source offsets differ: {record['qa_id']}")
        if record["evidence_id"] not in by_id:
            absent_evidence_records.append(record["qa_id"])
        if record["doc_id"] not in document_ids:
            raise ValueError(f"Question document missing: {record['doc_id']}")
        if not record["question"].strip() or not record["answer"].strip():
            raise ValueError(f"Question or answer is empty: {record['qa_id']}")
    frozen = json.loads((benchmark / "frozen_chunking_configurations_2.4.1.json")
                        .read_text(encoding="utf-8"))
    if {c["method"] for c in frozen["configurations"]} != {
        "sentence", "token", "sentence_window", "semantic", "hierarchical"
    }:
        raise ValueError("Frozen configurations do not cover the five expected methods.")
    return {"evaluation_corpus_sha256": fingerprint, "retrieval_documents": len(paths),
            "parsed_documents": len({row["doc_id"] for row in units}),
            "questions": len(qa), "gold_documents": len({row["doc_id"] for row in qa}),
            "evidence_records": len(evidence), "configuration_count": len(frozen["configurations"]),
            "questions_absent_from_evidence_export": absent_evidence_records,
            "scope": "Input integrity only; no generation or legal correctness assessment."}
