# Retrieval

## Pipeline

```
Query
  ↓
Normalize (lowercase, tokenize, sanitize)
  ↓
FTS5 Search (BM25 ranked)
  ↓
Filter (scope, project_id, not expired)
  ↓
Project Isolation (block cross-project)
  ↓
Rank (relevance × confidence × importance × recency × scope × source)
  ↓
Deduplicate (Jaccard similarity)
  ↓
Token Budget (fit to budget)
  ↓
Return (with provenance + estimated_tokens)
```

## Ranking Factors

| Factor | Weight | Description |
|--------|--------|-------------|
| FTS relevance | ×10 | BM25 score from SQLite FTS5 |
| Confidence | ×20 | How trustworthy the source is |
| Importance | ×15 | User/system assigned importance |
| Recency | ×10 | Exponential decay (90-day half-life) |
| Scope | +2-5 | Project > environment > global > git > session |
| Source type | +1-10 | User > observed > inferred > ai |

## Token Budgeting

Every search supports `token_budget` parameter. The retriever fits results into the budget, maximizing information value per token.

Token estimation: ~4 characters per token (labeled as `estimated_tokens`, never claimed as exact).

## Context Packs

Optional focused retrieval:
- `backend` — architecture, decisions, conventions, dependencies
- `frontend` — architecture, conventions, dependencies
- `database` — decisions, rules, conventions
- `testing` — conventions, rules, known issues
- `deployment` — environment facts, decisions
- `architecture` — architecture, decisions, rules
