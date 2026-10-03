"""Inventory local research data without publishing or modifying it."""

import argparse
import hashlib
import json
import os
from pathlib import Path

from legal_rag.preflight import missing_inputs


def inventory(root: Path) -> dict:
    """Return stable paths, sizes and SHA-256 digests for files beneath root."""
    if not root.is_dir():
        raise ValueError(f"Data directory does not exist: {root}")
    files = []
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.is_symlink():
            continue
        digest = hashlib.sha256()
        with path.open("rb") as stream:
            for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(chunk)
        files.append({"path": path.relative_to(root).as_posix(),
                      "bytes": path.stat().st_size, "sha256": digest.hexdigest()})
    return {"schema_version": 1, "files": files}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["inventory", "verify", "doctor"])
    parser.add_argument("--data-root", type=Path,
                        default=Path(os.environ.get("LEGAL_RAG_DATA_ROOT", "data")))
    parser.add_argument("--manifest", type=Path)
    args = parser.parse_args()
    if args.command == "doctor":
        missing = missing_inputs(args.data_root)
        if missing:
            print("Baseline inputs missing:")
            for name in missing:
                print(f"  {name}")
            raise SystemExit(2)
        print("Required baseline files exist; contents and corpus identity still need validation.")
        return
    if args.manifest is None:
        parser.error("--manifest is required for inventory and verify")
    current = inventory(args.data_root)
    if args.command == "inventory":
        args.manifest.parent.mkdir(parents=True, exist_ok=True)
        args.manifest.write_text(json.dumps(current, indent=2) + "\n", encoding="utf-8")
        print(f"Recorded {len(current['files'])} files in {args.manifest}")
    else:
        expected = json.loads(args.manifest.read_text(encoding="utf-8"))
        if current != expected:
            raise SystemExit("Data differs from manifest (files, sizes or hashes).")
        print(f"Verified {len(current['files'])} files")


if __name__ == "__main__":
    main()
