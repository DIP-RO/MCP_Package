"""CLI command implementations."""

from __future__ import annotations

import sys

from contextmcp.clients.detector import detect_clients, get_all_adapters
from contextmcp.config.settings import get_settings
from contextmcp.core.lifecycle import get_engine, reset_engine
from contextmcp.core.token_budget import estimate_tokens
from contextmcp.environment.detector import EnvironmentInfo
from contextmcp.environment.diagnostics import run_diagnostics
from contextmcp.project.indexer import Indexer
from contextmcp.storage.manager import StorageManager


def cmd_status() -> int:
    """Show Promem-MCP status."""
    try:
        engine = get_engine()
        info = engine.project_info
        project_id = engine.project_id
        store = engine.store

        memory_count = engine.memory.count(project_id)
        global_count = engine.memory.count(None)

        # Git status
        git_status = "Detected" if info.git_root else "Not detected"

        # Environment
        env = EnvironmentInfo()
        env_status = "Healthy" if env.virtual_env else "System Python"

        # Index stats
        indexer = Indexer(store, project_id, info.root)
        index_stats = indexer.get_stats()

        # Storage
        settings = get_settings()
        db_exists = settings.db_path.exists()
        db_size = settings.db_path.stat().st_size if db_exists else 0

        print("Promem-MCP")
        print("─" * 30)
        print()
        print("Project:")
        print(f"  {info.name}")
        print()
        print("Project ID:")
        print(f"  {project_id}")
        print()
        print("Storage:")
        print(f"  {'✓ Local' if db_exists else '✗ Not initialized'}")
        if db_exists:
            print(f"  {db_size / 1024:.1f} KB")
        print()
        print("Memory:")
        print(f"  {memory_count} project items")
        print(f"  {global_count} global items")
        print()
        print("Git:")
        print(f"  {'✓ ' + git_status if info.git_root else '✗ ' + git_status}")
        print()
        print("Environment:")
        print(f"  {'✓ ' + env_status}")
        print()
        print("Framework:")
        print(f"  {info.framework or 'Not detected'}")
        print()
        print("Language:")
        print(f"  {info.language or 'Not detected'}")
        print()
        print("Index:")
        print(f"  {index_stats['file_count']} files")
        print(f"  {index_stats['total_size_mb']} MB indexed")
        print()

        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def cmd_doctor() -> int:
    """Run diagnostics."""
    print("Promem-MCP Doctor")
    print("─" * 40)
    print()

    checks_passed = 0
    checks_failed = 0
    checks_warning = 0

    # Check 1: Storage
    settings = get_settings()
    try:
        settings.ensure_data_dir()
        print("✓ Storage directory created/accessible")
        checks_passed += 1
    except Exception as e:
        print(f"✗ Storage directory error: {e}")
        checks_failed += 1

    # Check 2: Database
    try:
        engine = get_engine()
        engine.store  # noqa: F841
        print(f"✓ Database initialized at {settings.db_path}")
        checks_passed += 1
    except Exception as e:
        print(f"✗ Database error: {e}")
        checks_failed += 1

    # Check 3: Project detection
    try:
        info = engine.project_info
        print(f"✓ Project detected: {info.name}")
        print(f"  Language: {info.language or 'unknown'}")
        print(f"  Framework: {info.framework or 'unknown'}")
        checks_passed += 1
    except Exception as e:
        print(f"✗ Project detection error: {e}")
        checks_failed += 1

    # Check 4: Git
    info = engine.project_info
    if info.git_root:
        print(f"✓ Git detected at {info.git_root}")
        checks_passed += 1
    else:
        print("⚠ No Git repository detected")
        checks_warning += 1

    # Check 5: Environment
    print()
    print("Environment diagnostics:")
    diag = run_diagnostics(info.root)
    for finding in diag["findings"]:
        status_icon = {"ok": "✓", "error": "✗", "warning": "⚠", "info": "ℹ"}.get(
            finding["status"], "?"
        )
        print(f"  {status_icon} {finding['check']}: {finding['detail']}")
        if finding["status"] == "ok":
            checks_passed += 1
        elif finding["status"] == "error":
            checks_failed += 1
        elif finding["status"] == "warning":
            checks_warning += 1

    # Check 6: Client support
    print()
    print("Client support:")
    detected = detect_clients()
    if detected:
        for adapter in detected:
            configured = adapter.is_configured()
            status = "✓ Configured" if configured else "⚠ Detected, not configured"
            print(f"  {adapter.display_name}: {status}")
            if not configured:
                print(f"    Run: promem config {adapter.name}")
            checks_passed += 1
    else:
        print("  ⚠ No supported AI clients detected")
        checks_warning += 1
        print("  Manual configuration required. See: promem config --help")

    print()
    print(f"Summary: {checks_passed} passed, {checks_warning} warnings, {checks_failed} errors")

    return 0 if checks_failed == 0 else 1


def cmd_stats() -> int:
    """Show usage statistics."""
    engine = get_engine()
    project_id = engine.project_id
    store = engine.store

    stats = store.get_stats_summary(project_id)
    memory_count = engine.memory.count(project_id)

    print("Promem-MCP Stats")
    print("─" * 30)
    print()
    print(f"Queries: {stats['queries']}")
    print(f"Average retrieval: {stats['avg_latency_ms']}ms")
    print()
    print(f"Memories: {memory_count}")
    print()

    # Estimate raw vs selected context
    all_memories = engine.memory.list_memories(project_id=project_id, limit=10000)
    raw_tokens = sum(estimate_tokens(m.get("content", "")) for m in all_memories)
    print("Estimated raw context:")
    print(f"  {raw_tokens:,} tokens")
    print()

    # Simulate a search to get selected context
    if all_memories:
        result = engine.retriever.search(
            query="project architecture",
            project_id=project_id,
            limit=5,
            token_budget=1000,
        )
        selected = result.estimated_tokens
        print("Selected context (last query):")
        print(f"  {selected:,} tokens")
        print()
        if raw_tokens > 0:
            reduction = (1 - selected / raw_tokens) * 100
            print("Estimated reduction:")
            print(f"  {reduction:.1f}%")
    else:
        print("No memories to calculate reduction.")

    return 0


def cmd_search(
    query: str,
    scope: str | None = None,
    limit: int = 5,
    token_budget: int = 1000,
) -> int:
    """Search context from CLI."""
    engine = get_engine()
    result = engine.retriever.search(
        query=query,
        project_id=engine.project_id,
        scope=scope,
        limit=limit,
        token_budget=token_budget,
    )
    print(result.to_compact_text())
    print()
    print(
        f"({result.total_found} found, {len(result.memories)} returned, "
        f"~{result.estimated_tokens} tokens, {result.latency_ms:.1f}ms)"
    )
    return 0


def cmd_memory_list(scope: str | None = None, limit: int = 20) -> int:
    """List memories."""
    engine = get_engine()
    memories = engine.memory.list_memories(project_id=engine.project_id, scope=scope, limit=limit)
    if not memories:
        print("No memories found.")
        return 0
    for m in memories:
        print(f"  [{m['type']}] {m['content'][:80]}...")
        print(f"    id: {m['id']}")
        print(f"    source: {m.get('source', 'unknown')}")
        print()
    return 0


def cmd_memory_search(query: str, limit: int = 10) -> int:
    """Search memories."""
    return cmd_search(query, limit=limit)


def cmd_memory_delete(memory_id: str) -> int:
    """Delete a memory."""
    engine = get_engine()
    success = engine.memory.delete(memory_id)
    if success:
        print(f"Deleted: {memory_id}")
        return 0
    print(f"Not found: {memory_id}")
    return 1


def cmd_decision(content: str, reason: str | None = None) -> int:
    """Save a technical decision."""
    engine = get_engine()
    mem = engine.memory.save_decision(
        decision=content,
        reason=reason,
        project_id=engine.project_id,
    )
    if mem is not None:
        print(f"Saved decision: {mem['id']}")
    else:
        print("Failed to save decision")
    return 0


def cmd_privacy() -> int:
    """Show privacy information."""
    print("Promem-MCP Privacy")
    print("─" * 30)
    print()
    print("Storage:")
    print("  Local only (project-local: .contextmcp/)")
    print()
    print("Network:")
    print("  No external requests")
    print()
    print("Project contents:")
    print("  Not uploaded")
    print()
    print("Secrets:")
    print("  Redacted")
    print()
    print("Global memory:")
    print("  Enabled")
    print()
    print("Project memory:")
    print("  Enabled")
    print()
    print("Data directory:")
    settings = get_settings()
    print(f"  {settings.data_dir}")
    print()
    print("No optional network features are enabled.")
    return 0


def cmd_reset(confirm: bool = False) -> int:
    """Reset all Promem-MCP data."""
    reset_engine()
    settings = get_settings()

    # Count what will be deleted
    sm = StorageManager(settings)
    store = sm.get_store()
    projects = store.get_all_projects()
    total_memories = store.count_memories(None)

    print("This will permanently delete Promem-MCP local memory.")
    print()
    print(f"Projects: {len(projects)}")
    print(f"Memory items: {total_memories}")
    print()

    if not confirm:
        response = input("Continue? [y/N] ")
        if response.lower() != "y":
            print("Cancelled.")
            return 0

    sm.reset()
    print("All Promem-MCP data has been deleted.")
    return 0


def cmd_config(client_name: str | None = None) -> int:
    """Configure MCP client integration."""
    if client_name:
        from contextmcp.clients.detector import get_adapter
        adapter = get_adapter(client_name)
        if adapter is None:
            print(f"Unknown client: {client_name}")
            print(f"Available: {', '.join(a.name for a in get_all_adapters())}")
            return 1

        result = adapter.write_config(backup=True)
        if result["success"]:
            print(f"✓ {adapter.display_name}: {result['message']}")
            print(f"  Config: {result.get('path', 'N/A')}")
            print()
            print("Restart the client for changes to take effect.")
        else:
            print(f"✗ {adapter.display_name}: {result.get('error', 'Failed')}")
            print()
            print("Manual configuration:")
            print(adapter.get_instructions())
        return 0

    # List all clients
    print("Promem-MCP Client Configuration")
    print("─" * 40)
    print()
    detected = detect_clients()
    if detected:
        print("Detected clients:")
        for adapter in detected:
            configured = adapter.is_configured()
            status = "✓ configured" if configured else "⚠ not configured"
            print(f"  {adapter.display_name} ({adapter.name}): {status}")
            if not configured:
                print(f"    Run: promem config {adapter.name}")
        print()
        print("Or configure all at once: promem config --all")
        print()
    else:
        print("No supported AI clients detected.")
        print()

    print("All supported clients:")
    for adapter in get_all_adapters():
        detected_status = "detected" if adapter.detect() else "not detected"
        print(f"  {adapter.display_name} ({adapter.name}): {detected_status}")
    print()
    print("Usage: promem config <client-name>")
    print("       promem config --all")
    return 0


def cmd_config_all() -> int:
    """Auto-configure all detected clients at once."""
    print("Promem-MCP — Auto-Configure All Detected Clients")
    print("─" * 50)
    print()
    detected = detect_clients()
    if not detected:
        print("No supported AI clients detected.")
        print("Use `promem config <client-name>` to configure a specific client.")
        return 0

    success_count = 0
    fail_count = 0
    already_configured = 0

    for adapter in detected:
        if adapter.is_configured():
            print(f"  ✓ {adapter.display_name}: already configured")
            already_configured += 1
            continue

        result = adapter.write_config(backup=True)
        if result["success"]:
            print(f"  ✓ {adapter.display_name}: {result['message']}")
            print(f"    Config: {result.get('path', 'N/A')}")
            success_count += 1
        else:
            print(f"  ✗ {adapter.display_name}: {result.get('error', 'Failed')}")
            print(f"    Manual: promem config {adapter.name}")
            fail_count += 1

    print()
    print(
        f"Summary: {success_count} configured, "
        f"{already_configured} already done, {fail_count} failed"
    )
    if success_count > 0 or already_configured > 0:
        print()
        print("Restart your AI clients for changes to take effect.")
    return 0


def cmd_repair() -> int:
    """Repair Promem-MCP data (rebuild index, repair DB)."""
    print("Promem-MCP Repair")
    print("─" * 30)
    print()

    engine = get_engine()
    store = engine.store
    project_id = engine.project_id
    info = engine.project_info

    # Rebuild file index
    print("Rebuilding file index...")
    indexer = Indexer(store, project_id, info.root)
    stats = indexer.index_incremental()
    print(f"  Indexed: {stats['indexed']}")
    print(f"  Skipped: {stats['skipped']}")
    print(f"  Removed: {stats['removed']}")
    print(f"  Time: {stats['elapsed_ms']}ms")
    print()

    # Vacuum database
    print("Optimizing database...")
    store.execute("VACUUM")
    print("  ✓ Done")
    print()

    print("Repair complete.")
    return 0
