#!/bin/bash
# Task Master Complexity Agent Runner

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AGENT_SCRIPT="$SCRIPT_DIR/task-complexity-agent.py"
CONFIG_FILE="$SCRIPT_DIR/complexity-agent-config.json"

echo "🤖 Running Task Master Complexity Analysis"
echo "==========================================="

# Check if we're in a Task Master project
if [ ! -d ".taskmaster" ]; then
    echo "❌ Not in a Task Master project directory"
    echo "   Run this from your project root directory"
    exit 1
fi

# Default mode: analysis only
if [ "$1" = "analyze" ] || [ -z "$1" ]; then
    echo "📊 Running complexity analysis..."
    python3 "$AGENT_SCRIPT" --config "$CONFIG_FILE" --verbose

# Auto-expand mode (dry run)
elif [ "$1" = "expand-dry" ]; then
    echo "🔍 Dry-run auto-expansion..."
    python3 "$AGENT_SCRIPT" --config "$CONFIG_FILE" --auto-expand --dry-run --verbose

# Auto-expand mode (real)
elif [ "$1" = "expand" ]; then
    echo "🚀 Auto-expanding complex tasks..."
    echo "⚠️  This will modify your Task Master tasks!"
    read -p "Continue? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        python3 "$AGENT_SCRIPT" --config "$CONFIG_FILE" --auto-expand --verbose
    else
        echo "Cancelled."
    fi

# Help
else
    echo "Usage: $0 [analyze|expand-dry|expand]"
    echo ""
    echo "Commands:"
    echo "  analyze    - Analyze task complexity (default)"
    echo "  expand-dry - Show what would be expanded (safe)"
    echo "  expand     - Actually expand complex tasks"
    echo ""
    echo "Examples:"
    echo "  $0                # Just analyze"
    echo "  $0 expand-dry     # See what would be expanded"
    echo "  $0 expand         # Expand tasks (with confirmation)"
fi