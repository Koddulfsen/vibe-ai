#!/usr/bin/env python3
"""
Debug script to test why agents aren't producing real output
"""

import subprocess
import os
import sys
import json
import tempfile
from datetime import datetime

def test_master_agent():
    """Test master-agent.py directly"""
    print("🔍 Testing master-agent.py workflow...")
    
    cmd = [
        "python3", "master-agent.py",
        "workflow", "--type", "planning",
        "--tag", "test-debug"
    ]
    
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    print(f"\nReturn code: {result.returncode}")
    print(f"\nSTDOUT:\n{result.stdout}")
    print(f"\nSTDERR:\n{result.stderr}")
    
    return result.returncode == 0

def test_planning_agent():
    """Test planning-analysis-agent.py directly"""
    print("\n🔍 Testing planning-analysis-agent.py...")
    
    cmd = [
        "python3", "agents/planning-analysis-agent.py",
        "--project-root", ".",
        "--tag", "test-direct"
    ]
    
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    print(f"\nReturn code: {result.returncode}")
    print(f"\nSTDOUT:\n{result.stdout}")
    print(f"\nSTDERR:\n{result.stderr}")
    
    return result.returncode == 0

def test_agent_with_task():
    """Test with a specific task"""
    print("\n🔍 Testing with specific task...")
    
    # Create a test task
    task_data = {
        "description": "Create a simple hello world Python script",
        "subtasks": [
            "Create main.py file",
            "Add hello world function",
            "Add if __name__ == '__main__' block"
        ]
    }
    
    # Save to temp file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(task_data, f)
        task_file = f.name
    
    print(f"Created task file: {task_file}")
    print(f"Task content: {json.dumps(task_data, indent=2)}")
    
    # Try to execute
    cmd = [
        "python3", "master-agent.py",
        "execute", "--task-id", "1",
        "--auto"
    ]
    
    print(f"\nRunning: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True, env={**os.environ, "TASK_FILE": task_file})
    
    print(f"\nReturn code: {result.returncode}")
    print(f"\nSTDOUT:\n{result.stdout}")
    print(f"\nSTDERR:\n{result.stderr}")
    
    # Cleanup
    os.unlink(task_file)
    
    return result.returncode == 0

def check_agent_dependencies():
    """Check if required dependencies are available"""
    print("\n🔍 Checking agent dependencies...")
    
    # Check for task files
    task_files = [
        ".taskmaster/tasks/tasks.json",
        "tasks.json",
        ".task-agent-sync.json"
    ]
    
    for file in task_files:
        exists = os.path.exists(file)
        print(f"  {file}: {'✅ Found' if exists else '❌ Missing'}")
    
    # Check for required directories
    dirs = [
        "agents",
        ".taskmaster",
        "prds"
    ]
    
    print("\nDirectories:")
    for dir in dirs:
        exists = os.path.exists(dir)
        print(f"  {dir}/: {'✅ Found' if exists else '❌ Missing'}")
    
    # Check agent files
    print("\nAgent files:")
    agent_files = [
        "master-agent.py",
        "agents/planning-analysis-agent.py",
        "agents/universal-execution-agent.py",
        "agents/quality-git-agent.py"
    ]
    
    for file in agent_files:
        exists = os.path.exists(file)
        print(f"  {file}: {'✅ Found' if exists else '❌ Missing'}")

def main():
    print("🛠️  Agent System Debugger")
    print("=" * 50)
    
    # Check dependencies first
    check_agent_dependencies()
    
    # Test master agent
    if not test_master_agent():
        print("\n❌ Master agent failed!")
    
    # Test planning agent directly
    if not test_planning_agent():
        print("\n❌ Planning agent failed!")
    
    # Test with actual task
    if not test_agent_with_task():
        print("\n❌ Task execution failed!")
    
    print("\n" + "=" * 50)
    print("Debug complete!")

if __name__ == "__main__":
    main()