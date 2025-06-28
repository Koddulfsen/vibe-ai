#!/bin/bash
#
# Claude Code Intelligent Filter - Installation Script
# ===================================================
#
# This script installs the Claude Code intelligent filter system globally
# so you can use it from any project directory.
#
# Usage: ./install.sh
#

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m' # No Color

# Banner
echo -e "${CYAN}"
echo "🚀 ================================================================"
echo "   CLAUDE CODE INTELLIGENT FILTER - INSTALLATION"
echo "   Enhance Claude Code with intelligent agent routing"
echo "================================================================${NC}"
echo

# Determine installation directory
INSTALL_DIR="$HOME/dev-tools/claude-code-filter"

echo -e "${BLUE}📋 Installation Plan:${NC}"
echo "   Install to: $INSTALL_DIR"
echo "   Add to PATH for convenient usage"
echo "   Create executable scripts"
echo

# Confirm installation
read -p "$(echo -e ${YELLOW}🤔 Proceed with installation? [Y/n]: ${NC})" choice
case "$choice" in 
  n|N|no|No ) echo "Installation cancelled."; exit 1;;
  * ) echo "Proceeding with installation...";;
esac

echo

# Create installation directory
echo -e "${BLUE}📁 Creating installation directory...${NC}"
mkdir -p "$INSTALL_DIR"

# Copy files
echo -e "${BLUE}📦 Copying files...${NC}"
cp claude_code_filter.py "$INSTALL_DIR/"
cp claude-code-wrapper.py "$INSTALL_DIR/"
cp claude-code-integration.py "$INSTALL_DIR/"
cp master-agent.py "$INSTALL_DIR/"

# Copy agents directory if it exists
if [ -d "agents" ]; then
    cp -r agents "$INSTALL_DIR/"
    echo "   ✅ Copied agents directory"
fi

# Copy config directory if it exists
if [ -d "config" ]; then
    cp -r config "$INSTALL_DIR/"
    echo "   ✅ Copied config directory"
fi

# Copy documentation
cp SETUP_GUIDE.md "$INSTALL_DIR/" 2>/dev/null || true
cp HOW_IT_WORKS.md "$INSTALL_DIR/" 2>/dev/null || true
cp workflow-examples.md "$INSTALL_DIR/" 2>/dev/null || true

echo "   ✅ Files copied successfully"

# Make scripts executable
echo -e "${BLUE}🔧 Making scripts executable...${NC}"
chmod +x "$INSTALL_DIR/claude_code_filter.py"
chmod +x "$INSTALL_DIR/claude-code-wrapper.py"
chmod +x "$INSTALL_DIR/claude-code-integration.py"
chmod +x "$INSTALL_DIR/master-agent.py"

# Create convenient aliases
echo -e "${BLUE}🔗 Creating convenient commands...${NC}"

# Create claude-filter command
cat > "$INSTALL_DIR/claude-filter" << 'EOF'
#!/bin/bash
python3 "$(dirname "$0")/claude_code_filter.py" "$@"
EOF
chmod +x "$INSTALL_DIR/claude-filter"

# Create claude-agents command  
cat > "$INSTALL_DIR/claude-agents" << 'EOF'
#!/bin/bash
python3 "$(dirname "$0")/master-agent.py" "$@"
EOF
chmod +x "$INSTALL_DIR/claude-agents"

# Create claude-wrapper command
cat > "$INSTALL_DIR/claude-wrapper" << 'EOF'
#!/bin/bash
python3 "$(dirname "$0")/claude-code-wrapper.py" "$@"
EOF
chmod +x "$INSTALL_DIR/claude-wrapper"

echo "   ✅ Created convenient commands: claude-filter, claude-agents, claude-wrapper"

# Check Python dependencies
echo -e "${BLUE}🐍 Checking Python dependencies...${NC}"
python3 -c "import sys, subprocess, os, pathlib, json, time, re" 2>/dev/null && echo "   ✅ Core Python modules available" || {
    echo "   ❌ Missing core Python modules"
    exit 1
}

# Check optional dependencies
python3 -c "import requests" 2>/dev/null && echo "   ✅ requests module available" || {
    echo "   ⚠️  requests module not found (optional, for GitHub integration)"
    echo "      Install with: pip install requests"
}

# PATH integration
echo -e "${BLUE}🛣️  Setting up PATH integration...${NC}"

SHELL_CONFIG=""
if [ -f "$HOME/.bashrc" ]; then
    SHELL_CONFIG="$HOME/.bashrc"
elif [ -f "$HOME/.zshrc" ]; then
    SHELL_CONFIG="$HOME/.zshrc"
elif [ -f "$HOME/.profile" ]; then
    SHELL_CONFIG="$HOME/.profile"
fi

if [ -n "$SHELL_CONFIG" ]; then
    # Check if already in PATH
    if grep -q "claude-code-filter" "$SHELL_CONFIG"; then
        echo "   ✅ PATH already configured in $SHELL_CONFIG"
    else
        echo "" >> "$SHELL_CONFIG"
        echo "# Claude Code Intelligent Filter" >> "$SHELL_CONFIG"
        echo "export PATH=\"\$PATH:$INSTALL_DIR\"" >> "$SHELL_CONFIG"
        echo "   ✅ Added to PATH in $SHELL_CONFIG"
        echo "   💡 Run 'source $SHELL_CONFIG' or restart your terminal"
    fi
else
    echo "   ⚠️  Could not detect shell config file"
    echo "      Manually add to your PATH: export PATH=\"\$PATH:$INSTALL_DIR\""
fi

# Create test script
echo -e "${BLUE}🧪 Creating test script...${NC}"
cat > "$INSTALL_DIR/test-installation.sh" << 'EOF'
#!/bin/bash
echo "🧪 Testing Claude Code Intelligent Filter Installation"
echo "======================================================"
echo

echo "📝 Test 1: Simple query"
python3 "$(dirname "$0")/claude_code_filter.py" "what is 2+2?"
echo

echo "📝 Test 2: Complex task"  
python3 "$(dirname "$0")/claude_code_filter.py" "implement complete authentication system"
echo

echo "📝 Test 3: System status"
python3 "$(dirname "$0")/master-agent.py" status 2>/dev/null || echo "   (Agent system needs setup)"
echo

echo "✅ Installation test complete!"
echo "💡 Try: claude-filter 'your prompt here'"
EOF
chmod +x "$INSTALL_DIR/test-installation.sh"

# Installation complete
echo
echo -e "${GREEN}🎉 INSTALLATION COMPLETE!${NC}"
echo "=" * 40
echo -e "${WHITE}📍 Installed to: ${GREEN}$INSTALL_DIR${NC}"
echo

echo -e "${WHITE}🚀 Quick Start:${NC}"
echo "   # Test the installation:"
echo "   $INSTALL_DIR/test-installation.sh"
echo
echo "   # Use from any project:"
echo "   cd ~/your-project"
echo "   claude-filter 'your prompt here'"
echo
echo "   # Or with full path:"
echo "   python3 $INSTALL_DIR/claude_code_filter.py 'your prompt'"
echo

echo -e "${WHITE}📚 Documentation:${NC}"
echo "   Setup Guide: $INSTALL_DIR/SETUP_GUIDE.md"
echo "   How It Works: $INSTALL_DIR/HOW_IT_WORKS.md"
echo "   Examples: $INSTALL_DIR/workflow-examples.md"
echo

echo -e "${WHITE}🔧 Next Steps:${NC}"
echo "   1. Restart your terminal (or run: source $SHELL_CONFIG)"
echo "   2. Test with: claude-filter 'implement user authentication'"
echo "   3. Use before complex Claude Code requests!"
echo

echo -e "${CYAN}Happy coding with enhanced Claude Code! 🎯${NC}"