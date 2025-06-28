#!/bin/bash
# Intelligent Task Analysis Runner

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AGENT_SCRIPT="$SCRIPT_DIR/intelligent-task-agent.py"

echo "🤖 Intelligent Task Discovery Agent"
echo "==================================="

# Check if we're in a Task Master project
if [ ! -d ".taskmaster" ]; then
    echo "❌ Not in a Task Master project directory"
    echo "   Run this from your project root directory"
    exit 1
fi

# Default mode: analysis
if [ "$1" = "analyze" ] || [ -z "$1" ]; then
    echo "🔍 Running intelligent task analysis..."
    python3 "$AGENT_SCRIPT"

# Analyze specific tasks
elif [ "$1" = "task" ] && [ ! -z "$2" ]; then
    echo "🔍 Analyzing specific tasks: $2"
    python3 "$AGENT_SCRIPT" --tasks="$2"

# Execute expansion for specific tasks
elif [ "$1" = "expand" ] && [ ! -z "$2" ]; then
    echo "🚀 Expanding specific tasks: $2"
    echo "⚠️  This will create subtasks based on actual project analysis!"
    read -p "Continue? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        python3 "$AGENT_SCRIPT" --execute --tasks="$2"
    else
        echo "Cancelled."
    fi

# Execute expansion for all tasks
elif [ "$1" = "expand-all" ]; then
    echo "🚀 Expanding ALL tasks with intelligent analysis..."
    echo "⚠️  This will create subtasks based on actual project needs!"
    read -p "Continue? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        python3 "$AGENT_SCRIPT" --execute
    else
        echo "Cancelled."
    fi

# Help
else
    echo "Usage: $0 [analyze|task <ids>|expand <ids>|expand-all]"
    echo ""
    echo "Commands:"
    echo "  analyze        - Analyze all tasks (default, safe)"
    echo "  task <ids>     - Analyze specific tasks (e.g., 'task 1,2,3')"
    echo "  expand <ids>   - Create subtasks for specific tasks"
    echo "  expand-all     - Create subtasks for all tasks"
    echo ""
    echo "Examples:"
    echo "  $0                    # Analyze all tasks (safe)"
    echo "  $0 task 1,2          # Analyze just tasks 1 and 2"
    echo "  $0 expand 1           # Create subtasks for task 1"
    echo "  $0 expand-all         # Create subtasks for all tasks"
    echo ""
    echo "The agent will:"
    echo "  • Scan your actual codebase for missing files"
    echo "  • Check package.json for missing dependencies"
    echo "  • Find TODO comments in your code"
    echo "  • Identify implementation gaps"
    echo "  • Create relevant subtasks based on real needs"
fi