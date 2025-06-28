#!/bin/bash
# Setup principled MCP agents for vibe.ai

echo "🚀 Setting up Ultrathink MCP Agents..."
echo "   Principles: ULTRATHINK | BE CONCISE | NO BLOAT"
echo ""

# Create MCP scripts directory
mkdir -p ~/.vibe/mcp-agents

# Create wrapper scripts for each agent
cat > ~/.vibe/mcp-agents/planning-agent.sh << 'EOF'
#!/bin/bash
cd /home/koddulf/vibecode/tools/vibe.ai
python3 principled_mcp_wrapper.py \
  --agent planning \
  --agent-path agents/planning-analysis-agent.py
EOF

cat > ~/.vibe/mcp-agents/execution-agent.sh << 'EOF'
#!/bin/bash
cd /home/koddulf/vibecode/tools/vibe.ai
python3 principled_mcp_wrapper.py \
  --agent execution \
  --agent-path agents/universal-dev-agent.py
EOF

cat > ~/.vibe/mcp-agents/quality-agent.sh << 'EOF'
#!/bin/bash
cd /home/koddulf/vibecode/tools/vibe.ai
python3 principled_mcp_wrapper.py \
  --agent quality \
  --agent-path agents/quality-git-agent.py
EOF

# Make executable
chmod +x ~/.vibe/mcp-agents/*.sh

# Create MCP configuration with all agents
cat > ~/.vibe/mcp_config.json << 'EOF'
{
  "mcpServers": {
    "vibe-planning": {
      "command": "bash",
      "args": ["${HOME}/.vibe/mcp-agents/planning-agent.sh"],
      "env": {}
    },
    "vibe-execution": {
      "command": "bash",
      "args": ["${HOME}/.vibe/mcp-agents/execution-agent.sh"],
      "env": {}
    },
    "vibe-quality": {
      "command": "bash",
      "args": ["${HOME}/.vibe/mcp-agents/quality-agent.sh"],
      "env": {}
    },
    "memory": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-memory"],
      "env": {}
    },
    "brave-search": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-brave-search"],
      "env": {
        "BRAVE_API_KEY": "${BRAVE_API_KEY}"
      }
    }
  }
}
EOF

# Create or update Claude config
CLAUDE_CONFIG_DIR="${HOME}/.claude"
CURSOR_CONFIG_DIR="${HOME}/.cursor"

# Function to update config
update_config() {
    local config_dir=$1
    local config_file="${config_dir}/mcp.json"
    
    if [ -d "$config_dir" ]; then
        echo "📝 Updating ${config_dir}/mcp.json..."
        
        # Backup existing config
        if [ -f "$config_file" ]; then
            cp "$config_file" "${config_file}.backup"
        fi
        
        # Copy new config
        cp ~/.vibe/mcp_config.json "$config_file"
    fi
}

# Update Claude and Cursor configs
update_config "$CLAUDE_CONFIG_DIR"
update_config "$CURSOR_CONFIG_DIR"

# Create a test script
cat > ~/.vibe/test_mcp_agents.py << 'EOF'
#!/usr/bin/env python3
"""Test principled MCP agents"""

import json
import subprocess
import time

def test_agent(agent_name):
    print(f"\n🧪 Testing {agent_name}...")
    
    # Test tools/list
    request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/list"
    }
    
    proc = subprocess.Popen(
        ["bash", f"{agent_name}.sh"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        cwd=f"{os.path.expanduser('~')}/.vibe/mcp-agents"
    )
    
    proc.stdin.write(json.dumps(request) + "\n")
    proc.stdin.flush()
    
    response = proc.stdout.readline()
    if response:
        data = json.loads(response)
        if "result" in data and "tools" in data["result"]:
            print(f"✅ {agent_name} has {len(data['result']['tools'])} tools")
            for tool in data["result"]["tools"]:
                print(f"   - {tool['name']}: {tool['description']}")
        else:
            print(f"❌ {agent_name} failed to list tools")
    
    proc.terminate()

if __name__ == "__main__":
    import os
    test_agent("planning-agent")
    test_agent("execution-agent")
    test_agent("quality-agent")
EOF

chmod +x ~/.vibe/test_mcp_agents.py

echo ""
echo "✅ Setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Restart Claude Code / Cursor"
echo "2. Available tools:"
echo "   • vibe-planning.analyze - Deep analysis, concise results"
echo "   • vibe-planning.plan - Create actionable plans"
echo "   • vibe-execution.execute - Execute tasks efficiently"
echo "   • vibe-execution.implement - Implement features"
echo "   • vibe-quality.check - Quality check with insights"
echo "   • vibe-quality.test - Run tests, report concisely"
echo ""
echo "💡 Example usage:"
echo '   "Use vibe-planning to analyze this project"'
echo '   "Use vibe-execution to implement the login feature"'
echo '   "Use vibe-quality to check code quality"'
echo ""
echo "🧪 Test agents: python3 ~/.vibe/test_mcp_agents.py"