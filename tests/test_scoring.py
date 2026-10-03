from types import SimpleNamespace

from legal_rag.scoring import score_budget_retrieval, score_retrieval, sentence_window_prefix_spans


class Node:
    def __init__(self, text, doc_id, start=0, spans=None):
        self.text = text
        self.start_char_idx = start
        self.metadata = {"doc_id": doc_id}
        if spans:
            self.metadata.update(source_spans=spans, span_representation="ordered_source_spans")

    def get_content(self, metadata_mode):
        return self.text


def result(text, doc_id="gold", start=0, spans=None):
    return SimpleNamespace(node=Node(text, doc_id, start, spans))


def character_tokenizer(text, **kwargs):
    # Deterministic fixture; production budgeting uses the actual BGE tokenizer.
    return {"offset_mapping": [(i, i + 1) for i in range(len(text))]}


def test_window_mapping_does_not_invent_evidence_between_disjoint_spans():
    window = result("abc xyz", spans=[[0, 3], [10, 13]])
    assert sentence_window_prefix_spans(window, 5) == [(0, 3), (10, 11)]
    query = {"doc_id": "gold", "evidence_start_char": 0, "evidence_end_char": 13}
    score = score_retrieval(query, [window], "abcDEFGHIJxyz", 1)
    assert score["coverage_ratio"] == 6 / 13
    assert not score["complete_coverage"]


def test_wrong_document_consumes_budget_and_truncation_maps_only_used_prefix():
    query = {"doc_id": "gold", "evidence_start_char": 0, "evidence_end_char": 6}
    results = [result("noise", "other"), result("abcdef")]
    score = score_budget_retrieval(query, results, "abcdef", 8, tokenizer=character_tokenizer)
    assert score["budget_coverage_ratio"] == 0.5
    assert score["budget_tokens_used"] == 8
    assert score["budget_first_overlap_rank"] == 2


def test_repeated_text_uses_source_hint_and_whitespace_is_trimmed():
    source = "rule then rule  "
    query = {"doc_id": "gold", "evidence_start_char": 10, "evidence_end_char": len(source)}
    score = score_retrieval(query, [result("rule", start=10)], source, 1)
    assert score["complete_coverage"]
