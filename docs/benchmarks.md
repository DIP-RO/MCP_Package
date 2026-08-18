# Benchmarks

## Running

```bash
python -m benchmarks.run
```

## What's Measured

1. **Storage write latency** — time to insert a memory
2. **Storage read latency** — time to list memories
3. **Retrieval latency** — FTS5 search + ranking + token budgeting
4. **Token reduction** — raw context vs. selected context

## Sample Results

```
Storage write: 0.07ms avg
Storage read: 0.05ms avg
Retrieval: 0.59ms avg, 0.87ms p95
Token reduction: 96.6%
```

These are real measurements. Results vary by hardware, database size, and query complexity.

## Reproducibility

The benchmark script (`benchmarks/run.py`):
- Creates a temporary directory for each run
- Populates 100-500 memories
- Runs 100 write/read iterations
- Runs 40 search iterations across 4 queries
- Measures token reduction with 100 memories

No results are fabricated. The script prints actual measurements from the machine it runs on.

## Baseline Comparison

To compare AI with raw context vs. ContextMCP selected context:

1. Count total tokens of all memories: `raw_tokens`
2. Run a search: `selected_tokens = result.estimated_tokens`
3. Reduction = `(1 - selected_tokens / raw_tokens) * 100`

ContextMCP does not claim model-quality improvements without a reproducible experiment.
