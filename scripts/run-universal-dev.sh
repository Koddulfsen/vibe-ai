#!/bin/bash
# Universal Development Execution Agent Runner

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AGENT_SCRIPT="$SCRIPT_DIR/universal-dev-agent.py"

echo "🤖 Universal Development Execution Agent"
echo "======================================="

# Check if we're in a Task Master project
if [ ! -d ".taskmaster" ]; then
    echo "❌ Not in a Task Master project directory"
    echo "   Run this from your project root directory"
    exit 1
fi

# Default mode: single task execution
if [ "$1" = "single" ] || [ -z "$1" ]; then
    echo "🔍 Executing next available task..."
    python3 "$AGENT_SCRIPT" --single

# Continuous execution mode
elif [ "$1" = "auto" ]; then
    MAX_TASKS=${2:-10}
    echo "🚀 Starting continuous execution (max $MAX_TASKS tasks)..."
    echo "⚠️  This will automatically execute multiple tasks!"
    read -p "Continue? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        python3 "$AGENT_SCRIPT" --max-tasks="$MAX_TASKS"
    else
        echo "Cancelled."
    fi

# Custom project directory
elif [ "$1" = "project" ] && [ ! -z "$2" ]; then
    echo "🔍 Executing in project: $2"
    python3 "$AGENT_SCRIPT" --project="$2" --single

# Status check
elif [ "$1" = "status" ]; then
    echo "📊 Checking agent execution status..."
    if [ -f ".taskmaster/agent_state.json" ]; then
        echo "Agent state file found:"
        cat .taskmaster/agent_state.json | python3 -m json.tool
    else
        echo "No agent state file found."
    fi

# Help
else
    echo "Usage: $0 [single|auto [max_tasks]|project <dir>|status]"
    echo ""
    echo "Commands:"
    echo "  single              - Execute next available task (default, safe)"
    echo "  auto [max_tasks]    - Continuous execution (default: 10 tasks)"
    echo "  project <dir>       - Execute task in specific project directory"
    echo "  status              - Show agent execution status"
    echo ""
    echo "Examples:"
    echo "  $0                  # Execute next task (safe)"
    echo "  $0 single           # Same as above"
    echo "  $0 auto 5           # Execute up to 5 tasks automatically"
    echo "  $0 project ../other  # Execute task in different project"
    echo "  $0 status           # Check execution history"
    echo ""
    echo "The agent will:"
    echo "  • Auto-detect project type (React, Python, etc.)"
    echo "  • Intelligently interpret task descriptions"
    echo "  • Execute appropriate commands (npm install, file creation, etc.)"
    echo "  • Validate task completion"
    echo "  • Update Task Master status automatically"
    echo "  • Work with any Task Master project universally"
fi