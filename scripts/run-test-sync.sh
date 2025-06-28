#!/bin/bash
# Testing & Synchronization Agent Runner

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AGENT_SCRIPT="$SCRIPT_DIR/test-sync-agent.py"

echo "🧪 Testing & Synchronization Agent"
echo "=================================="

# Check if we're in a Task Master project
if [ ! -d ".taskmaster" ]; then
    echo "❌ Not in a Task Master project directory"
    echo "   Run this from your project root directory"
    exit 1
fi

# Default mode: scan and sync
if [ "$1" = "scan" ] || [ -z "$1" ]; then
    echo "🔍 Scanning project state and syncing agents..."
    python3 "$AGENT_SCRIPT" --scan --sync

# Test specific subtask
elif [ "$1" = "test" ] && [ ! -z "$2" ]; then
    echo "🧪 Testing subtask: $2"
    python3 "$AGENT_SCRIPT" --test-subtask="$2"

# Status report
elif [ "$1" = "status" ]; then
    echo "📊 Generating status report..."
    python3 "$AGENT_SCRIPT" --status

# Sync agents only
elif [ "$1" = "sync" ]; then
    echo "🔄 Synchronizing all agents..."
    python3 "$AGENT_SCRIPT" --sync

# Watch mode - continuously monitor
elif [ "$1" = "watch" ]; then
    echo "👁️  Starting continuous monitoring..."
    echo "   Press Ctrl+C to stop"
    
    while true; do
        echo ""
        echo "$(date): Scanning and syncing..."
        python3 "$AGENT_SCRIPT" --scan --sync
        sleep 30  # Check every 30 seconds
    done

# Help
else
    echo "Usage: $0 [scan|test <subtask_id>|status|sync|watch]"
    echo ""
    echo "Commands:"
    echo "  scan               - Scan project state and sync agents (default)"
    echo "  test <subtask_id>  - Run tests for specific subtask"
    echo "  status             - Show comprehensive status report"
    echo "  sync               - Sync all agents with current state"
    echo "  watch              - Continuously monitor and sync (30s intervals)"
    echo ""
    echo "Examples:"
    echo "  $0                 # Scan and sync (safe)"
    echo "  $0 test 2.1        # Test subtask 2.1"
    echo "  $0 status          # Show status report"
    echo "  $0 watch           # Continuous monitoring"
    echo ""
    echo "The agent will:"
    echo "  • Run appropriate tests after each subtask"
    echo "  • Track project state (dependencies, files, tests)"
    echo "  • Sync all agents with current reality"
    echo "  • Enforce quality gates"
    echo "  • Prevent bad changes from propagating"
fi