# Token Optimization

ContextMCP's key differentiator is token-efficient context retrieval.

## Approach

1. **Never dump all memories** — only return relevant, ranked results
2. **Token budget API** — every search accepts `token_budget` parameter
3. **Structured compression** — facts over verbose explanations
4. **Deduplication** — no redundant memories

## Example

```python
# Search with 500 token budget
ctx_search(query="database transactions", token_budget=500)
```

Returns only the most relevant memories that fit within 500 estimated tokens.

## Benchmark Results

Real measurements (will vary by hardware):

```
Storage write: 0.07ms avg
Storage read: 0.05ms avg
Retrieval: 0.59ms avg, 0.87ms p95
Token reduction: 96.6%
```

## Token Estimation

Simple heuristic: ~4 characters per token.

This is labeled as `estimated_tokens` in all responses. ContextMCP does not pretend estimates are exact token counts from any specific model's tokenizer.
