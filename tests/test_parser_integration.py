import pytest


def test_real_window_parser_and_vector_index_keep_source_provenance():
    pytest.importorskip("llama_index.core")
    from llama_index.core import Document, VectorStoreIndex
    from llama_index.core.embeddings import MockEmbedding
    from llama_index.core.postprocessor import MetadataReplacementPostProcessor
    from llama_index.core.schema import QueryBundle

    from legal_rag.chunking import create_nodes
    from legal_rag.scoring import result_source_spans

    source = "Companies must report emissions. Reports are due annually."
    document = Document(text=source, id_="fixture", metadata={"doc_id": "fixture"})
    nodes = create_nodes("sentence_window", {"window_size": 7}, [document])
    for node in nodes:
        node.excluded_embed_metadata_keys = list(node.metadata)
        node.excluded_llm_metadata_keys = list(node.metadata)
    model = MockEmbedding(embed_dim=1024)
    index = VectorStoreIndex(nodes, embed_model=model)
    results = index.as_retriever(similarity_top_k=1).retrieve(
        QueryBundle(query_str="report", embedding=model.get_query_embedding("report"))
    )
    results = MetadataReplacementPostProcessor(target_metadata_key="window").postprocess_nodes(
        results
    )
    assert results[0].node.metadata["doc_id"] == "fixture"
    spans = result_source_spans(results[0], source)
    assert all(source[left:right] for left, right in spans)
    assert len(spans) == 2
