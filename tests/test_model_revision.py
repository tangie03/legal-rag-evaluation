import pytest

from legal_rag.model_revision import resolve_revision


def test_revision_uses_cached_snapshot_and_preserves_requested_tag():
    calls = []
    commit = "a" * 40

    def download(**kwargs):
        calls.append(kwargs)
        return f"/cache/models--BAAI--bge-m3/snapshots/{commit}"

    assert resolve_revision(download, "BAAI/bge-m3", "release-tag") == commit
    assert calls == [
        {"repo_id": "BAAI/bge-m3", "revision": "release-tag", "allow_patterns": ["config.json"]}
    ]


def test_unknown_revision_fails_instead_of_recording_null():
    with pytest.raises(ValueError, match="immutable"):
        resolve_revision(lambda **kwargs: "/cache/unresolved", "BAAI/bge-m3", None)
