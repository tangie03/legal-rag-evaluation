from legal_rag.preflight import BASELINE_FILES, missing_inputs


def test_missing_data_reports_all_inputs_and_recovers_after_restore(tmp_path):
    assert missing_inputs(tmp_path) == list(BASELINE_FILES)
    for name in BASELINE_FILES:
        target = tmp_path / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("fixture", encoding="utf-8")
    assert missing_inputs(tmp_path) == []
