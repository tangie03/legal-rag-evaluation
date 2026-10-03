import json

import pytest

from legal_rag.metrics import evidence_coverage
from legal_rag.smoke import run_smoke


def test_overlapping_evidence_is_counted_once_and_clipped():
    assert evidence_coverage((10, 20), [(0, 14), (12, 18), (16, 30)]) == 1
    assert evidence_coverage((10, 20), [(12, 16), (14, 18)]) == 0.6
    assert evidence_coverage((10, 20), [(30, 40)]) == 0


def test_smoke_runs_without_corpus_and_preserves_existing_results(tmp_path):
    output = tmp_path / "run"
    report = run_smoke(output)
    assert report["complete_non_whitespace_evidence"]
    stored = json.loads((output / "manifest.json").read_text())
    assert stored == report
    before = (output / "retrieved.jsonl").read_bytes()
    with pytest.raises(ValueError, match="already exists"):
        run_smoke(output)
    assert (output / "retrieved.jsonl").read_bytes() == before
