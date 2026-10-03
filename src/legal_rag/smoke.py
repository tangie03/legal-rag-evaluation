"""Small deterministic retrieval check using invented text and lexical scoring."""

import hashlib
import json
import platform
import re
import subprocess
from pathlib import Path

from legal_rag.metrics import evidence_coverage


def run_smoke(output: Path) -> dict:
    """Exercise retrieval and coverage output without private data or model downloads."""
    if output.exists():
        raise ValueError(f"Output already exists; choose a new run directory: {output}")
    documents = {
        "reporting": "A company must submit an annual emissions report. The deadline is 31 March.",
        "waste": "Waste handlers must retain disposal records for five years.",
    }
    question = "When is the deadline for the annual emissions report?"
    query_words = set(re.findall(r"\w+", question.lower()))
    chunks = []
    for doc_id, text in documents.items():
        for match in re.finditer(r"[^.!?]+[.!?]?", text):
            left = match.start() + len(match.group()) - len(match.group().lstrip())
            right = match.end()
            words = set(re.findall(r"\w+", text[left:right].lower()))
            chunks.append(
                {
                    "doc_id": doc_id,
                    "start": left,
                    "end": right,
                    "text": text[left:right],
                    "score": len(words & query_words),
                }
            )
    ranked = sorted(chunks, key=lambda row: (-row["score"], row["doc_id"], row["start"]))
    selected = ranked[:2]
    spans = [(row["start"], row["end"]) for row in selected if row["doc_id"] == "reporting"]
    coverage = evidence_coverage((0, len(documents["reporting"])), spans)
    # Ignore the one space between sentence spans, as it has no evidential content.
    complete = all(
        any(left <= i < right for left, right in spans)
        for i, char in enumerate(documents["reporting"])
        if not char.isspace()
    )
    try:
        commit = subprocess.run(
            ["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=True
        ).stdout.strip()
        dirty = bool(
            subprocess.run(
                ["git", "status", "--porcelain"], capture_output=True, text=True, check=True
            ).stdout.strip()
        )
    except (FileNotFoundError, subprocess.CalledProcessError):
        commit = None
        dirty = None
    report = {
        "workflow": "synthetic_lexical_smoke",
        "python": platform.python_version(),
        "git_commit": commit,
        "git_dirty": dirty,
        "configuration": {"backend": "word_overlap", "top_k": 2},
        "input_sha256": hashlib.sha256(json.dumps(documents, sort_keys=True).encode()).hexdigest(),
        "character_coverage": coverage,
        "complete_non_whitespace_evidence": complete,
        "notice": "Invented fixture; this is not a BGE-M3 baseline or legal answer.",
    }
    if not complete:
        raise ValueError("Synthetic retrieval did not recover the required evidence.")
    output.mkdir(parents=True, exist_ok=False)
    (output / "retrieved.jsonl").write_text(
        "".join(json.dumps(row) + "\n" for row in selected), encoding="utf-8"
    )
    (output / "manifest.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return report
