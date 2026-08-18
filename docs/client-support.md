# Client Support

## Supported Clients

| Client | Auto-config | Config File | Key |
|--------|------------|-------------|-----|
| Claude Code | `contextmcp config claude-code` | `~/.claude.json` | `mcpServers` |
| Claude Desktop | `contextmcp config claude-desktop` | `claude_desktop_config.json` | `mcpServers` |
| Cursor | `contextmcp config cursor` | `.cursor/mcp.json` or `~/.cursor/mcp.json` | `mcpServers` |
| VS Code / Copilot | `contextmcp config vscode` | `.vscode/mcp.json` | `servers` |
| OpenCode | `contextmcp config opencode` | `opencode.json` or `~/.config/opencode/opencode.json` | `mcp` |
| Gemini CLI | `contextmcp config gemini-cli` | `~/.gemini/settings.json` | `mcpServers` |
| Windsurf | `contextmcp config windsurf` | `~/.codeium/mcp_config.json` | `mcpServers` |
| Cline | `contextmcp config cline` | `~/.cline/mcp.json` | `mcpServers` |
| Roo Code | `contextmcp config roo-code` | `roo_mcp_settings.json` | `mcpServers` |
| Amazon Q | `contextmcp config amazon-q` | `~/.amazonq/mcp.json` | `mcpServers` |
| ZCode (GLM/Zhipu) | `contextmcp config zcode` | `.zcode/config.json` | `mcpServers` |
| Tabnine | `contextmcp config tabnine` | `~/.tabnine/mcp.json` | `mcpServers` |

**Important:** VS Code uses `"servers"` key, NOT `"mcpServers"`. OpenCode uses `"mcp"` root key with array-format `command`. These are the most common configuration mistakes.

## Configuration Process

1. Run `contextmcp config` to see all detected clients
2. Run `contextmcp config <client-name>` to auto-configure
3. Restart the client

## Manual Configuration

If auto-config isn't desired, add this to your client's config file:

```json
{
  "mcpServers": {
    "contextmcp": {
      "command": "contextmcp",
      "args": []
    }
  }
}
```

For VS Code, use `"servers"` instead of `"mcpServers"` and add `"type": "stdio"`.

For OpenCode, use `"mcp"` root key with array command:
```json
{
  "mcp": {
    "contextmcp": {
      "type": "local",
      "command": ["contextmcp"],
      "enabled": true
    }
  }
}
```

## No True Zero-Config

No MCP client supports automatic server discovery. A config file entry is always required. ContextMCP minimizes this to a single command.

## CLI Alternatives

Some clients also support CLI-based registration:

```bash
# Claude Code
claude mcp add contextmcp -- contextmcp

# Cursor (via UI)
# Settings > MCP > Add Server
```
