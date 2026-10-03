"""Notebook 07 multi-span scoring with explicit tokenizer injection.

Preserves whitespace trimming, window-prefix mapping and candidate-order budgets.
"""


def merge_intervals(intervals):
    merged = []
    for start, end in sorted((int(start), int(end)) for start, end in intervals):
        if start >= end:
            continue
        if not merged or start > merged[-1][1]:
            merged.append([start, end])
        else:
            merged[-1][1] = max(merged[-1][1], end)
    return merged


def trim_span_whitespace(text, start, end):
    while start < end and text[start].isspace():
        start += 1
    while end > start and text[end - 1].isspace():
        end -= 1
    return start, end


def locate_continuous_span(result, returned_text, document_text):
    if not returned_text:
        return None

    start_hint = result.node.start_char_idx
    if start_hint is not None:
        start_hint = int(start_hint)
        end_hint = start_hint + len(returned_text)
        if document_text[start_hint:end_hint] == returned_text:
            return start_hint, end_hint

    positions, position = [], document_text.find(returned_text)
    while position != -1:
        positions.append(position)
        position = document_text.find(returned_text, position + 1)

    if not positions:
        return None

    hint = start_hint if start_hint is not None else 0
    start = min(positions, key=lambda value: abs(value - hint))
    return start, start + len(returned_text)


def sentence_window_prefix_spans(result, prefix_characters):
    assert prefix_characters >= 0
    source_spans = [(int(start), int(end)) for start, end in result.node.metadata["source_spans"]]

    assert source_spans
    assert all(0 <= start < end for start, end in source_spans)
    assert source_spans == sorted(source_spans, key=lambda span: (span[0], span[1]))

    mapped_spans, window_cursor = [], 0
    for source_start, source_end in source_spans:
        segment_length = source_end - source_start
        covered = max(0, min(prefix_characters, window_cursor + segment_length) - window_cursor)

        if covered:
            mapped_spans.append((source_start, source_start + covered))

        window_cursor += segment_length + 1
        if window_cursor > prefix_characters:
            break

    return mapped_spans


def result_source_spans(result, document_text, returned_text=None):
    text = returned_text
    if text is None:
        text = result.node.get_content(metadata_mode="none")

    if result.node.metadata.get("span_representation") == "ordered_source_spans":
        return sentence_window_prefix_spans(result, len(text))

    span = locate_continuous_span(result, text, document_text)
    return [] if span is None else [span]


def score_retrieval(query_row, retrieved_nodes, document_text, k):
    gold_start, gold_end = trim_span_whitespace(
        document_text,
        int(query_row["evidence_start_char"]),
        int(query_row["evidence_end_char"]),
    )
    assert 0 <= gold_start < gold_end <= len(document_text)

    gold_doc_id = str(query_row["doc_id"])
    overlap_spans, first_overlap_rank, unlocated_results = [], None, 0

    for rank, result in enumerate(retrieved_nodes[:k], start=1):
        if str(result.node.metadata.get("doc_id")) != gold_doc_id:
            continue

        spans = result_source_spans(result, document_text)
        if not spans:
            unlocated_results += 1
            continue

        result_overlaps = []
        for start, end in spans:
            if start < gold_end and end > gold_start:
                result_overlaps.append((max(start, gold_start), min(end, gold_end)))

        if result_overlaps:
            overlap_spans.extend(result_overlaps)
            if first_overlap_rank is None:
                first_overlap_rank = rank

    merged_spans = merge_intervals(overlap_spans)
    covered_characters = sum(end - start for start, end in merged_spans)
    gold_characters = gold_end - gold_start
    coverage_ratio = min(covered_characters / gold_characters, 1.0)

    return {
        "complete_coverage": covered_characters >= gold_characters,
        "partial_overlap": covered_characters > 0,
        "coverage_ratio": coverage_ratio,
        "first_overlap_rank": first_overlap_rank,
        "reciprocal_rank": 0.0 if first_overlap_rank is None else 1.0 / first_overlap_rank,
        "unlocated_results": unlocated_results,
    }


def truncate_to_token_budget(text, token_budget, tokenizer):
    if token_budget <= 0 or not text:
        return "", 0

    encoded = tokenizer(
        text,
        add_special_tokens=False,
        truncation=False,
        return_offsets_mapping=True,
    )
    offsets = encoded["offset_mapping"]

    if len(offsets) <= token_budget:
        return text, len(offsets)

    character_end = offsets[token_budget - 1][1]
    return text[:character_end], token_budget


def score_budget_retrieval(
    query_row, retrieved_nodes, document_text, token_budget=1000, *, tokenizer
):
    assert token_budget > 0, "token_budget must be positive."
    gold_start, gold_end = trim_span_whitespace(
        document_text,
        int(query_row["evidence_start_char"]),
        int(query_row["evidence_end_char"]),
    )
    assert 0 <= gold_start < gold_end <= len(document_text)

    gold_doc_id = str(query_row["doc_id"])
    remaining_tokens = token_budget
    overlap_spans, first_overlap_rank = [], None
    included_results, unlocated_results = 0, 0

    for rank, result in enumerate(retrieved_nodes, start=1):
        if remaining_tokens <= 0:
            break

        returned_text = result.node.get_content(metadata_mode="none")
        assert returned_text, f"Empty retrieved node at rank {rank}"
        budgeted_text, used_tokens = truncate_to_token_budget(
            returned_text, remaining_tokens, tokenizer
        )
        remaining_tokens -= used_tokens
        included_results += 1

        if str(result.node.metadata.get("doc_id")) != gold_doc_id:
            continue

        spans = result_source_spans(result, document_text, budgeted_text)
        if not spans:
            unlocated_results += 1
            continue

        result_overlaps = []
        for start, end in spans:
            if start < gold_end and end > gold_start:
                result_overlaps.append((max(start, gold_start), min(end, gold_end)))

        if result_overlaps:
            overlap_spans.extend(result_overlaps)
            if first_overlap_rank is None:
                first_overlap_rank = rank

    merged_spans = merge_intervals(overlap_spans)
    covered_characters = sum(end - start for start, end in merged_spans)
    gold_characters = gold_end - gold_start
    coverage_ratio = min(covered_characters / gold_characters, 1.0)

    return {
        "budget_complete_coverage": covered_characters >= gold_characters,
        "budget_partial_overlap": covered_characters > 0,
        "budget_coverage_ratio": coverage_ratio,
        "budget_first_overlap_rank": first_overlap_rank,
        "budget_tokens_used": token_budget - remaining_tokens,
        "budget_results_used": included_results,
        "budget_unlocated_results": unlocated_results,
    }
