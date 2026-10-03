"""Check baseline inputs before running expensive retrieval experiments."""

from pathlib import Path

BASELINE_FILES = (
    "data/parsed/eval_units.jsonl",
    "data/parsed/eval_provisions.jsonl",
    "outputs/qa_benchmark/frozen_chunking_configurations_2.4.1.json",
    "outputs/qa_benchmark/evaluation_qa_benchmark_2.3.5-final.jsonl",
    "outputs/qa_benchmark/evaluation_qa_evidence_2.3.5-final.jsonl",
)


def missing_inputs(project_root: Path) -> list[str]:
    """List absent Notebook 07 inputs without modifying the project."""
    return [name for name in BASELINE_FILES if not (project_root / name).is_file()]
