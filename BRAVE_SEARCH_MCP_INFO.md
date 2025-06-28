# Brave Search MCP Information

## Current Status

The Brave Search MCP is **configured** in `~/.claude/mcp.json` but **not loaded** in the current Claude Code session.

## Configuration Found

```json
"brave-search": {
  "command": "npx",
  "args": ["-y", "@modelcontextprotocol/server-brave-search"],
  "env": {
    "BRAVE_API_KEY": "${BRAVE_API_KEY}"
  }
}
```

## Why It's Not Available

MCP servers need to be loaded when Claude Code starts. The Brave Search MCP is configured but requires:

1. **Environment Variable**: The `BRAVE_API_KEY` needs to be set before Claude Code starts
2. **Session Restart**: MCPs are loaded at startup, so adding new MCPs requires restarting Claude Code
3. **NPM Package**: The `@modelcontextprotocol/server-brave-search` package needs to be available

## How to Enable Brave Search MCP

1. **Set the API key in your shell profile** (`.bashrc` or `.zshrc`):
   ```bash
   export BRAVE_API_KEY="BSArXZ987KsjfuUmJRTvpXPjuYVP7-I"
   ```

2. **Restart Claude Code** to load the MCP with the API key

3. **Verify it's loaded** by looking for `mcp__brave_search__*` functions

## Alternative: Use Built-in WebSearch

The built-in `WebSearch` function is currently available and working, which provides web search capabilities without needing the Brave API.

## Integration with Deep Planner

The `deep_planner_agent.py` already has the Brave API key configured:
```python
self.brave_api_key = brave_api_key or os.getenv("BRAVE_API_KEY", "BSArXZ987KsjfuUmJRTvpXPjuYVP7-I")
```

So the Deep Planner can still use Brave Search directly via the API, even without the MCP.