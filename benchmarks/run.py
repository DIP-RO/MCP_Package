"""Benchmark: retrieval latency, storage latency, token reduction.

Run with: python -m benchmarks.run
"""

from __future__ import annotations

import os
import sys
import time
import tempfile
from pathlib import Path

# Add src to path for direct execution
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from contextmcp.config.settings import reset_settings, Settings
from contextmcp.core.memory import MemoryManager
from contextmcp.core.retrieval import Retriever
from contextmcp.core.token_budget import estimate_tokens
from contextmcp.storage.manager import StorageManager


def benchmark_storage_latency():
    """Measure storage write/read latency."""
    with tempfile.TemporaryDirectory() as tmpdir:
        os.environ["CONTEXTMCP_DATA_DIR"] = tmpdir
        reset_settings()

        sm = StorageManager()
        store = sm.get_store()
        store.upsert_project("bench", "bench", "/tmp/bench")
        mm = MemoryManager(store)

        # Write benchmark
        times = []
        for i in range(100):
            start = time.time()
            mm.save(
                content=f"Rule {i}: use pattern {i} for module {i}",
                scope="project",
                mem_type="project_rule",
                project_id="bench",
                deduplicate=False,
            )
            times.append((time.time() - start) * 1000)

        avg_write = sum(times) / len(times)
        print(f"Storage write latency (avg of 100): {avg_write:.2f}ms")

        # Read benchmark
        times = []
        for i in range(100):
            start = time.time()
            mm.list(project_id="bench", limit=10)
            times.append((time.time() - start) * 1000)

        avg_read = sum(times) / len(times)
        print(f"Storage read latency (avg of 100): {avg_read:.2f}ms")

        sm.close()
        return {"write_ms": avg_write, "read_ms": avg_read}


def benchmark_retrieval_latency():
    """Measure search retrieval latency."""
    with tempfile.TemporaryDirectory() as tmpdir:
        os.environ["CONTEXTMCP_DATA_DIR"] = tmpdir
        reset_settings()

        sm = StorageManager()
        store = sm.get_store()
        store.upsert_project("bench", "bench", "/tmp/bench")
        mm = MemoryManager(store)
        rv = Retriever(store)

        # Populate with 500 memories
        for i in range(500):
            mm.save(
                content=f"Rule {i}: use pattern {i} for module {i} with database access",
                scope="project",
                mem_type="project_rule",
                project_id="bench",
                deduplicate=False,
            )

        # Search benchmark
        queries = ["database access", "pattern module", "rule pattern", "database module"]
        times = []
        for q in queries:
            for _ in range(10):
                start = time.time()
                rv.search(q, project_id="bench", limit=5, token_budget=1000)
                times.append((time.time() - start) * 1000)

        avg = sum(times) / len(times)
        p95 = sorted(times)[int(len(times) * 0.95)]
        print(f"Retrieval latency (avg of {len(times)}): {avg:.2f}ms")
        print(f"Retrieval latency (p95): {p95:.2f}ms")

        sm.close()
        return {"avg_ms": avg, "p95_ms": p95}


def benchmark_token_reduction():
    """Measure token reduction from budget-aware retrieval."""
    with tempfile.TemporaryDirectory() as tmpdir:
        os.environ["CONTEXTMCP_DATA_DIR"] = tmpdir
        reset_settings()

        sm = StorageManager()
        store = sm.get_store()
        store.upsert_project("bench", "bench", "/tmp/bench")
        mm = MemoryManager(store)
        rv = Retriever(store)

        # Populate with memories of varying sizes
        for i in range(100):
            mm.save(
                content=f"Architecture rule {i}: " + "x" * (50 + i * 5),
                scope="project",
                mem_type="architecture",
                project_id="bench",
                deduplicate=False,
            )

        # Calculate raw token count
        all_memories = mm.list(project_id="bench", limit=10000)
        raw_tokens = sum(estimate_tokens(m["content"]) for m in all_memories)

        # Search with budget
        result = rv.search("architecture", project_id="bench", limit=10, token_budget=500)
        selected_tokens = result.estimated_tokens

        reduction = (1 - selected_tokens / raw_tokens) * 100 if raw_tokens > 0 else 0

        print(f"Raw context: {raw_tokens:,} tokens")
        print(f"Selected context: {selected_tokens:,} tokens")
        print(f"Token reduction: {reduction:.1f}%")

        sm.close()
        return {
            "raw_tokens": raw_tokens,
            "selected_tokens": selected_tokens,
            "reduction_pct": reduction,
        }


def main():
    print("=" * 50)
    print("ContextMCP Benchmarks")
    print("=" * 50)
    print()

    print("── Storage Latency ──")
    storage = benchmark_storage_latency()
    print()

    print("── Retrieval Latency ──")
    retrieval = benchmark_retrieval_latency()
    print()

    print("── Token Reduction ──")
    tokens = benchmark_token_reduction()
    print()

    print("=" * 50)
    print("Summary")
    print("=" * 50)
    print(f"Storage write: {storage['write_ms']:.2f}ms avg")
    print(f"Storage read: {storage['read_ms']:.2f}ms avg")
    print(f"Retrieval: {retrieval['avg_ms']:.2f}ms avg, {retrieval['p95_ms']:.2f}ms p95")
    print(f"Token reduction: {tokens['reduction_pct']:.1f}%")
    print()
    print("Note: These are real measurements on this machine.")
    print("Results vary by hardware, database size, and query complexity.")


if __name__ == "__main__":
    main()
