# Apollo recovery audit

The four supplied SHA-256 checksums matched their respective processed-data, notebook, critical-output and paper-recovery archives. No comparison checksum was supplied for the environment archive. Archives were inspected and extracted into separate folders; original uploaded archives were not changed.

The parsed units identify 283 development, 60 evaluation and 60 test documents. The split text directories contain 440, 81 and 76 files respectively. Uploaded Notebook 07 explicitly asserts 81 evaluation document objects. This differs from the dissertation description of a 60-document evaluation corpus; the relationship between parsed records, text files and the recorded corpus fingerprint must be checked before choosing a reproducible baseline. Do not remove extra files or silently select 60 documents.

The processed-data archive contains parsed units, provisions and source text. The following required Notebook 07 inputs were not found in the uploaded archives:

- `frozen_chunking_configurations_2.4.1.json`
- `evaluation_qa_benchmark_2.3.5-final.jsonl`
- `evaluation_qa_evidence_2.3.5-final.jsonl`

Development reproduction additionally needs `development_qa_generated_2.3.5-v3-direct-esg.jsonl` and `chunking_experiment_design_2.4.json`. Look for these in Apollo's `esg_rag_project/outputs/qa_benchmark` or the Mac submission package. Preserve original files and provenance; do not reconstruct gold labels from generated answers.

Apollo records Python 3.12.12. The requirements snapshot is evidence of the historical environment, not yet a validated cross-platform installation lock.

Run the missing-file check before retrieval:

```bash
python -m legal_rag.cli doctor --data-root /absolute/path/to/esg_rag_project
```

The checker reports every missing required file and exits with status 2. It works without the corpus, GPU or API key. Passing only establishes that expected paths exist, not that their content or corpus identity is valid. Unit tests use temporary fixtures and also run without the research data.
