import pytest

from legal_rag.baseline import corpus_fingerprint, validate_baseline


def test_fingerprint_tracks_names_and_bytes(tmp_path):
    first = tmp_path / "a.txt"
    second = tmp_path / "b.txt"
    first.write_bytes(b"rule")
    second.write_bytes(b"exception")
    original = corpus_fingerprint([first, second])
    assert corpus_fingerprint([second, first]) == original
    second.write_bytes(b"changed exception")
    assert corpus_fingerprint([first, second]) != original


def test_baseline_without_data_reports_missing_inputs(tmp_path):
    with pytest.raises(ValueError, match="Missing inputs"):
        validate_baseline(tmp_path)
