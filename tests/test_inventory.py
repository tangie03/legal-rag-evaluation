from legal_rag.cli import inventory


def test_inventory_is_stable_and_detects_changed_bytes(tmp_path):
    (tmp_path / "sub").mkdir()
    source = tmp_path / "sub" / "law.txt"
    source.write_text("first", encoding="utf-8")
    first = inventory(tmp_path)
    assert first["files"][0]["path"] == "sub/law.txt"
    assert inventory(tmp_path) == first
    source.write_text("later", encoding="utf-8")
    assert inventory(tmp_path) != first
