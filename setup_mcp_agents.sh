#!/bin/bash
# Setup script to enable MCP mode for vibe.ai agents

echo "🚀 Setting up vibe.ai agents as MCP servers..."

# Create MCP wrapper scripts
mkdir -p ~/.vibe/mcp-agents

# Planning Agent
cat > ~/.vibe/mcp-agents/planning-agent.sh << 'EOF'
#!/bin/bash
python3 /home/koddulf/vibecode/tools/vibe.ai/mcp_wrapper.py \
  --agent planning \
  --agent-path /home/koddulf/vibecode/tools/vibe.ai/agents/planning-analysis-agent.py
EOF

# Execution Agent  
cat > ~/.vibe/mcp-agents/execution-agent.sh << 'EOF'
#!/bin/bash
python3 /home/koddulf/vibecode/tools/vibe.ai/mcp_wrapper.py \
  --agent execution \
  --agent-path /home/koddulf/vibecode/tools/vibe.ai/agents/universal-dev-agent.py
EOF

# Quality Agent
cat > ~/.vibe/mcp-agents/quality-agent.sh << 'EOF'
#!/bin/bash
python3 /home/koddulf/vibecode/tools/vibe.ai/mcp_wrapper.py \
  --agent quality \
  --agent-path /home/koddulf/vibecode/tools/vibe.ai/agents/quality-git-agent.py
EOF

# Make executable
chmod +x ~/.vibe/mcp-agents/*.sh

# Update MCP config
cat > ~/.claude/mcp.json << 'EOF'
{
  "mcpServers": {
    "vibe-planning": {
      "command": "bash",
      "args": ["~/.vibe/mcp-agents/planning-agent.sh"]
    },
    "vibe-execution": {
      "command": "bash", 
      "args": ["~/.vibe/mcp-agents/execution-agent.sh"]
    },
    "vibe-quality": {
      "command": "bash",
      "args": ["~/.vibe/mcp-agents/quality-agent.sh"]
    }
  }
}
EOF

echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Restart Claude Code"
echo "2. You'll see new tools available:"
echo "   - vibe-planning.analyze_project"
echo "   - vibe-execution.execute_task"
echo "   - vibe-quality.check_quality"
echo ""
echo "Example usage:"
echo '  "Use vibe-planning to analyze this project"'
echo '  "Use vibe-execution to implement the login feature"'