#!/bin/bash
#
# Task Master Agent System Setup
# ==============================
# 
# Quick setup script for the Task Master Agent System

set -e  # Exit on any error

echo "🚀 Task Master Agent System Setup"
echo "================================="
echo

# Check Python version
echo "📋 Checking Python version..."
python3 --version || {
    echo "❌ Python 3 is required but not found"
    echo "Please install Python 3.8 or higher"
    exit 1
}

# Check if we're in the right directory
if [ ! -f "master-agent.py" ]; then
    echo "❌ master-agent.py not found"
    echo "Please run this script from the vibe.ai directory"
    exit 1
fi

# Make scripts executable
echo "🔧 Making scripts executable..."
chmod +x master-agent.py
find agents/ -name "*.py" -exec chmod +x {} \;
find scripts/ -name "*.sh" -exec chmod +x {} \;

# Optional: Install Python packages
echo "📦 Checking optional dependencies..."
if [ -f "requirements.txt" ]; then
    echo "Found requirements.txt. Install optional packages? (y/n)"
    read -r response
    if [[ "$response" =~ ^[Yy]$ ]]; then
        pip3 install -r requirements.txt
        echo "✅ Optional packages installed"
    else
        echo "⏭️  Skipping optional package installation"
    fi
fi

# Test the system
echo "🧪 Testing system..."
if ./master-agent.py status > /dev/null 2>&1; then
    echo "✅ System test passed"
else
    echo "⚠️  System test had issues, but setup is complete"
fi

# Create example config if it doesn't exist
echo "⚙️  Setting up configuration..."
if [ ! -f "config/master-config.json" ]; then
    cat > config/master-config.json << 'EOF'
{
    "system": {
        "name": "Task Master Agent System",
        "version": "1.0.0",
        "timeout": 300
    },
    "agents": {
        "planning": {
            "enabled": true,
            "timeout": 300,
            "complexity_analysis": true,
            "sequential_thinking": true
        },
        "execution": {
            "enabled": true,
            "timeout": 600,
            "auto_install_deps": true,
            "run_tests": true
        },
        "quality": {
            "enabled": true,
            "timeout": 300,
            "auto_fix": false,
            "git_integration": true
        }
    },
    "workflows": {
        "full-dev": {
            "phases": ["analysis", "repo", "execution", "quality"],
            "timeout": 1200
        }
    }
}
EOF
    echo "✅ Created default configuration"
fi

echo
echo "🎉 Setup Complete!"
echo "=================="
echo
echo "Quick Start Commands:"
echo "  ./master-agent.py status                    # Check system status"
echo "  ./master-agent.py analyze --tag your-tag    # Run analysis"
echo "  ./master-agent.py workflow --type full-dev  # Run full workflow"
echo
echo "📖 For detailed usage, see:"
echo "  ./master-agent.py --help"
echo "  cat README.md"
echo
echo "🚀 System is ready to use!"