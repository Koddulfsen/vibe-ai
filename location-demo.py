#!/usr/bin/env python3
"""
Location Demo: How the Filter Works from Any Directory
======================================================

This shows exactly how you can install the task-master-agents folder once
and use it from any project directory.
"""

import os
import subprocess
from pathlib import Path

def demonstrate_usage_from_different_locations():
    """Show how the filter works from different project locations"""
    
    print("🎯 LOCATION DEMO: Using Task Master Agents from Any Directory")
    print("=" * 70)
    print()
    
    # Show current setup
    current_dir = Path.cwd()
    agents_dir = Path(__file__).parent
    
    print(f"📁 Current working directory: {current_dir}")
    print(f"🤖 Task Master Agents location: {agents_dir}")
    print()
    
    # Demonstrate different scenarios
    scenarios = [
        {
            "name": "React Project",
            "description": "Working in a React project directory",
            "simulated_location": "/home/user/projects/my-react-app",
            "files_present": ["package.json", "src/", "public/"],
            "prompt": "add user authentication with Redux"
        },
        {
            "name": "Python API Project", 
            "description": "Working in a Python API project",
            "simulated_location": "/home/user/projects/api-backend",
            "files_present": ["requirements.txt", "app.py", "models/"],
            "prompt": "implement rate limiting and caching"
        },
        {
            "name": "Empty Project",
            "description": "Starting a new project from scratch",
            "simulated_location": "/home/user/projects/new-project",
            "files_present": [],
            "prompt": "set up a complete development environment"
        }
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"🎬 SCENARIO {i}: {scenario['name']}")
        print(f"📍 Location: {scenario['simulated_location']}")
        print(f"📁 Files: {', '.join(scenario['files_present']) if scenario['files_present'] else 'Empty directory'}")
        print(f"💬 Developer asks: '{scenario['prompt']}'")
        print()
        
        # Show the command they would run
        print("🔧 Command they run:")
        print(f"   cd {scenario['simulated_location']}")
        print(f"   python3 {agents_dir}/claude_code_filter.py \"{scenario['prompt']}\"")
        print()
        
        # Show what happens
        print("✅ What happens:")
        print("   1. Filter analyzes the prompt")
        print("   2. Filter detects project type from current directory") 
        print("   3. Filter provides intelligent routing recommendation")
        print("   4. If agents recommended, they analyze the CURRENT project")
        print()
        print("-" * 50)
        print()

def show_installation_options():
    """Show different ways to install and use the system"""
    
    print("🏗️ INSTALLATION OPTIONS")
    print("=" * 30)
    print()
    
    print("📦 Option 1: Global Installation (Recommended)")
    print("```bash")
    print("# Install once in your home directory:")
    print("mkdir -p ~/dev-tools")
    print("cp -r task-master-agents ~/dev-tools/")
    print("")
    print("# Use from any project:")
    print("cd ~/projects/any-project")
    print("python3 ~/dev-tools/task-master-agents/claude_code_filter.py 'your prompt'")
    print("```")
    print()
    
    print("📦 Option 2: Per-Project Installation")
    print("```bash")
    print("# Copy to each project that needs it:")
    print("cp -r task-master-agents ~/projects/my-app/tools/")
    print("")
    print("# Use from project root:")
    print("cd ~/projects/my-app")
    print("python3 tools/task-master-agents/claude_code_filter.py 'your prompt'")
    print("```")
    print()
    
    print("📦 Option 3: PATH Installation (Most Convenient)")
    print("```bash")
    print("# Add to ~/.bashrc or ~/.zshrc:")
    print("export PATH=\"$PATH:~/dev-tools/vibe.ai\"")
    print("")
    print("# Then from anywhere:")
    print("cd ~/projects/any-project")
    print("claude_code_filter.py 'your prompt'")
    print("```")
    print()

def show_current_directory_detection():
    """Show how the system detects project type from current directory"""
    
    print("🔍 HOW PROJECT DETECTION WORKS")
    print("=" * 35)
    print()
    
    print("The filter automatically detects your project type by looking at:")
    print()
    print("🎯 JavaScript/Node.js Projects:")
    print("   Looks for: package.json, node_modules/, src/")
    print("   Result: Provides Node.js/React specific recommendations")
    print()
    print("🐍 Python Projects:")
    print("   Looks for: requirements.txt, setup.py, *.py files")
    print("   Result: Provides Python-specific recommendations")
    print()
    print("🚀 Git Repositories:")
    print("   Looks for: .git/, README.md, .gitignore")
    print("   Result: Provides Git workflow recommendations")
    print()
    print("📁 Generic Projects:")
    print("   Looks for: Any files, directory structure")
    print("   Result: Provides general development recommendations")
    print()
    
    print("💡 Key Point: The filter works on YOUR current project,")
    print("   wherever you are when you run it!")

def main():
    """Run the complete location demo"""
    demonstrate_usage_from_different_locations()
    show_installation_options()
    show_current_directory_detection()
    
    print("\n🎯 SUMMARY")
    print("=" * 15)
    print("✅ Install task-master-agents ONCE in a central location")
    print("✅ Use it from ANY project directory")
    print("✅ It automatically analyzes YOUR current project")
    print("✅ No need to copy files to every project")
    print("✅ Clean, flexible, reusable across all your work")

if __name__ == "__main__":
    main()