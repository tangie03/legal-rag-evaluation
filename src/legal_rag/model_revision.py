"""Resolve a model snapshot before loading weights or tokenizers."""

import re
from pathlib import Path


def resolve_revision(snapshot_download, model_name: str, requested: str | None) -> str:
    """Use the Hub snapshot identifier rather than private tokenizer attributes."""
    snapshot = Path(
        snapshot_download(
            repo_id=model_name, revision=requested or "main", allow_patterns=["config.json"]
        )
    )
    revision = snapshot.name
    if snapshot.parent.name != "snapshots" or re.fullmatch(r"[0-9a-f]{40}", revision) is None:
        raise ValueError("Could not resolve an immutable Hugging Face model revision.")
    return revision
