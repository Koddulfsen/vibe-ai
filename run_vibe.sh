#!/bin/bash
# Wrapper script to run vibe with proper environment

# Set API keys
# Set your Anthropic API key here or in your environment
# export ANTHROPIC_API_KEY='your-key-here'
export BRAVE_API_KEY='BSArXZ987KsjfuUmJRTvpXPjuYVP7-I'

# Check if argument provided
if [ $# -eq 0 ]; then
    echo "Usage: ./run_vibe.sh \"Your idea here\""
    exit 1
fi

# Run vibe in non-interactive mode
echo "🚀 Running vibe.ai with your idea: $1"
echo ""

# Use the simple solution generator for now which works well
python3 simple_solution_generator.py "$1" vibe-output

echo ""
echo "✅ Solution created in ./vibe-output/"
echo ""
echo "Files created:"
ls -la vibe-output/