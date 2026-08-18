"""ContextMCP CLI entry point.

Running `contextmcp` with no arguments starts the MCP server over stdio.
This is how MCP hosts launch it as a subprocess — no `serve` command needed.
"""

from __future__ import annotations

import sys
from typing import Any

import click

from contextmcp import __version__


@click.group(invoke_without_command=True)
@click.version_option(__version__, prog_name="contextmcp")
@click.pass_context
def cli(ctx: click.Context) -> None:
    """ContextMCP — Persistent project context for AI coding agents.

    Running with no command starts the MCP server (stdio transport).
    """
    if ctx.invoked_subcommand is None:
        # No subcommand — start MCP server
        from contextmcp.mcp.server import run
        run()


@cli.command()
def status() -> None:
    """Show ContextMCP status."""
    sys.exit(_run_command("status"))


@cli.command()
def doctor() -> None:
    """Run diagnostics and health checks."""
    sys.exit(_run_command("doctor"))


@cli.command()
def stats() -> None:
    """Show usage statistics."""
    sys.exit(_run_command("stats"))


@cli.command()
@click.argument("query")
@click.option("--scope", "-s", default=None, help="Filter by scope")
@click.option("--limit", "-l", default=5, help="Max results")
@click.option("--token-budget", "-t", default=1000, help="Token budget")
def search(query: str, scope: str | None, limit: int, token_budget: int) -> None:
    """Search project context."""
    sys.exit(_run_command("search", query, scope, limit, token_budget))


@cli.group()
def memory() -> None:
    """Manage memories."""
    pass


@memory.command(name="list")
@click.option("--scope", "-s", default=None)
@click.option("--limit", "-l", default=20)
def memory_list(scope: str | None, limit: int) -> None:
    """List memories."""
    sys.exit(_run_command("memory_list", scope, limit))


@memory.command(name="search")
@click.argument("query")
@click.option("--limit", "-l", default=10)
def memory_search(query: str, limit: int) -> None:
    """Search memories."""
    sys.exit(_run_command("memory_search", query, limit))


@memory.command(name="delete")
@click.argument("memory_id")
def memory_delete(memory_id: str) -> None:
    """Delete a memory."""
    sys.exit(_run_command("memory_delete", memory_id))


@cli.command()
@click.argument("content")
@click.option("--reason", "-r", default=None, help="Reason for the decision")
def decision(content: str, reason: str | None) -> None:
    """Save a technical decision."""
    sys.exit(_run_command("decision", content, reason))


@cli.command()
def privacy() -> None:
    """Show privacy information."""
    sys.exit(_run_command("privacy"))


@cli.command()
@click.option("--yes", "-y", is_flag=True, help="Skip confirmation")
def reset(yes: bool) -> None:
    """Reset all ContextMCP data (requires confirmation)."""
    sys.exit(_run_command("reset", yes))


@cli.command()
@click.argument("client_name", required=False)
def config(client_name: str | None) -> None:
    """Configure MCP client integration."""
    sys.exit(_run_command("config", client_name))


@cli.command()
def repair() -> None:
    """Repair ContextMCP data (rebuild index, optimize DB)."""
    sys.exit(_run_command("repair"))


def _run_command(name: str, *args: Any) -> int:
    """Run a CLI command by name."""
    from contextmcp.cli import commands as cmds

    func_map: dict[str, Any] = {
        "status": cmds.cmd_status,
        "doctor": cmds.cmd_doctor,
        "stats": cmds.cmd_stats,
        "search": cmds.cmd_search,
        "memory_list": cmds.cmd_memory_list,
        "memory_search": cmds.cmd_memory_search,
        "memory_delete": cmds.cmd_memory_delete,
        "decision": cmds.cmd_decision,
        "privacy": cmds.cmd_privacy,
        "reset": cmds.cmd_reset,
        "config": cmds.cmd_config,
        "repair": cmds.cmd_repair,
    }

    func = func_map.get(name)
    if func is None:
        click.echo(f"Unknown command: {name}", err=True)
        return 1

    result = func(*args)
    return int(result) if result is not None else 0


def main() -> None:
    """Main entry point."""
    cli()


if __name__ == "__main__":
    main()
