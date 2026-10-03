"""Sentence chunking extracted from the final Apollo Notebook 07."""

from collections import defaultdict
from itertools import pairwise


def attach_window_provenance(nodes, window_size, document_text_by_id):
    nodes_by_document = defaultdict(list)
    for node in nodes:
        nodes_by_document[str(node.metadata["doc_id"])].append(node)

    gap_windows = 0
    for doc_id, document_nodes in nodes_by_document.items():
        document_nodes.sort(key=lambda node: node.start_char_idx)
        document_text = document_text_by_id[doc_id]

        for position, anchor in enumerate(document_nodes):
            left, right = (
                max(0, position - window_size),
                min(len(document_nodes), position + window_size + 1),
            )
            neighbours = document_nodes[left:right]
            sentence_texts = [str(node.metadata["original_sentence"]) for node in neighbours]
            reconstructed_window = " ".join(sentence_texts)
            assert reconstructed_window == str(anchor.metadata["window"])

            segments, cursor = [], 0
            for number, (node, sentence_text) in enumerate(zip(neighbours, sentence_texts)):
                assert document_text[node.start_char_idx : node.end_char_idx] == sentence_text
                segments.append(
                    {
                        "window_start": cursor,
                        "window_end": cursor + len(sentence_text),
                        "source_start": int(node.start_char_idx),
                        "source_end": int(node.end_char_idx),
                    }
                )
                cursor += len(sentence_text) + (number < len(neighbours) - 1)

            source_spans = [
                [segment["source_start"], segment["source_end"]] for segment in segments
            ]
            has_gap = any(document_text[a[1] : b[0]].strip() for a, b in pairwise(source_spans))
            anchor.metadata.update(
                {
                    "source_spans": source_spans,
                    "window_segments": segments,
                    "span_representation": "ordered_source_spans",
                    "has_non_whitespace_gap": bool(has_gap),
                }
            )
            gap_windows += int(has_gap)

    return gap_windows


def create_nodes(method, parameters, documents):
    # Import only when chunking is requested; basic checks stay dependency-free.
    from llama_index.core.node_parser import SentenceSplitter, SentenceWindowNodeParser

    if method == "sentence":
        return SentenceSplitter(**parameters).get_nodes_from_documents(documents)
    if method == "sentence_window":
        parser = SentenceWindowNodeParser.from_defaults(
            window_size=parameters["window_size"],
            window_metadata_key="window",
            original_text_metadata_key="original_sentence",
        )
        nodes = parser.get_nodes_from_documents(documents)
        attach_window_provenance(
            nodes, parameters["window_size"], {str(doc.doc_id): doc.text for doc in documents}
        )
        return nodes
    raise ValueError(f"Method not migrated yet: {method}")
