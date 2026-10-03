# Working on this project

Create a branch for each change. Keep implementation in `src/legal_rag`; use notebooks for exploration and reporting. Write descriptive names and explain scientific assumptions rather than narrating obvious code. Add a small test when a change can affect source alignment, metrics, selection rules or saved results.

Before committing:

```bash
python -m ruff format src tests
python -m ruff check src tests
python -m pytest -q
git diff --check
git status --short
```

Review the staged diff before a commit. Check that no corpus, secrets, model weights, local paths from a new machine or generated answers were accidentally staged. Never edit the historical notebooks simply to make their output match a fresh run. New experiments need new output folders and documented configurations.

The synthetic smoke workflow is a plumbing check. Evaluate BGE-M3 retrieval separately against archived outputs before reporting reproduced dissertation metrics. Record the source commit and any uncommitted changes in experiment manifests. On Apollo, use the site's documented compute-job procedure rather than launching heavy work on a login node.
