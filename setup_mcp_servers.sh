#!/bin/bash
# Setup script for vibe.ai MCP servers

echo "🚀 vibe.ai MCP Setup Script"
echo "=========================="
echo ""

# Check for required tools
echo "Checking requirements..."

if ! command -v node &> /dev/null; then
    echo "❌ Node.js is required but not installed"
    echo "   Install from: https://nodejs.org/"
    exit 1
else
    echo "✅ Node.js found"
fi

if ! command -v npm &> /dev/null; then
    echo "❌ npm is required but not installed"
    exit 1
else
    echo "✅ npm found"
fi

# Create MCP directory
MCP_DIR="$HOME/.cursor/mcp"
echo ""
echo "Creating MCP directory at: $MCP_DIR"
mkdir -p "$MCP_DIR"

# Check environment variables
echo ""
echo "Checking environment variables..."

check_env_var() {
    if [ -z "${!1}" ]; then
        echo "❌ $1 is not set"
        return 1
    else
        echo "✅ $1 is set"
        return 0
    fi
}

ENV_VARS_OK=true
check_env_var "ANTHROPIC_API_KEY" || ENV_VARS_OK=false
check_env_var "BRAVE_API_KEY" || ENV_VARS_OK=false
check_env_var "PERPLEXITY_API_KEY" || echo "   (Optional but recommended)"

if [ "$ENV_VARS_OK" = false ]; then
    echo ""
    echo "⚠️  Missing required environment variables!"
    echo "Add these to your ~/.bashrc or ~/.zshrc:"
    echo ""
    echo "export ANTHROPIC_API_KEY='your-key-here'"
    echo "export BRAVE_API_KEY='your-key-here'"
    echo "export PERPLEXITY_API_KEY='your-key-here'  # Optional"
fi

# Install MCP servers
echo ""
echo "Installing MCP servers..."

install_mcp_server() {
    echo ""
    echo "Installing $1..."
    if npm list -g "$1" &> /dev/null; then
        echo "✅ $1 already installed"
    else
        npm install -g "$1"
        if [ $? -eq 0 ]; then
            echo "✅ $1 installed successfully"
        else
            echo "❌ Failed to install $1"
        fi
    fi
}

# Install TaskMaster
install_mcp_server "taskmaster-ai"

# Install Brave Search MCP
install_mcp_server "@modelcontextprotocol/server-brave-search"

# Install Memory MCP
install_mcp_server "@modelcontextprotocol/server-memory"

# Install Git MCP
install_mcp_server "@modelcontextprotocol/server-git"

# Create MCP configuration
echo ""
echo "Creating MCP configuration..."

MCP_CONFIG="$HOME/.cursor/mcp.json"

cat > "$MCP_CONFIG" << 'EOF'
{
  "mcpServers": {
    "taskmaster-ai": {
      "command": "npx",
      "args": ["-y", "taskmaster-ai"],
      "env": {
        "ANTHROPIC_API_KEY": "${ANTHROPIC_API_KEY}",
        "PERPLEXITY_API_KEY": "${PERPLEXITY_API_KEY}",
        "OPENAI_API_KEY": "${OPENAI_API_KEY}",
        "GOOGLE_API_KEY": "${GOOGLE_API_KEY}"
      }
    },
    "brave-search": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-brave-search"],
      "env": {
        "BRAVE_API_KEY": "${BRAVE_API_KEY}"
      }
    },
    "memory": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-memory"],
      "env": {}
    },
    "git": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-git"],
      "env": {}
    }
  }
}
EOF

echo "✅ MCP configuration created at: $MCP_CONFIG"

# Create .env.example
echo ""
echo "Creating .env.example..."

cat > .env.example << 'EOF'
# Required API Keys for vibe.ai
ANTHROPIC_API_KEY=your-anthropic-api-key-here
BRAVE_API_KEY=your-brave-search-api-key-here

# Optional but recommended
PERPLEXITY_API_KEY=your-perplexity-api-key-here
OPENAI_API_KEY=your-openai-api-key-here
GOOGLE_API_KEY=your-google-api-key-here
EOF

echo "✅ Created .env.example"

# Summary
echo ""
echo "======================================"
echo "✨ Setup Complete!"
echo "======================================"
echo ""
echo "Next steps:"
echo "1. Set your API keys in environment variables"
echo "2. Restart Claude Code to load MCP servers"
echo "3. Run: python3 vibe_perfect.py --check-status"
echo ""
echo "To get API keys:"
echo "- Anthropic: https://console.anthropic.com/"
echo "- Brave Search: https://brave.com/search/api/"
echo "- Perplexity: https://www.perplexity.ai/api"
echo ""
echo "Happy building with vibe.ai! 🚀"