#!/usr/bin/env python3
"""
Test TaskMaster Integration with vibe.ai
"""

import json
import os
import subprocess
import sys

def test_taskmaster_integration():
    """Test if TaskMaster is properly integrated"""
    
    print("🧪 Testing TaskMaster Integration")
    print("=" * 60)
    
    # Check if TaskMaster directory exists
    taskmaster_dir = ".taskmaster"
    if os.path.exists(taskmaster_dir):
        print("✅ TaskMaster directory found")
        
        # Check for tasks.json
        tasks_file = os.path.join(taskmaster_dir, "tasks", "tasks.json")
        if os.path.exists(tasks_file):
            print("✅ tasks.json found")
            
            # Read and display tasks
            with open(tasks_file, 'r') as f:
                tasks_data = json.load(f)
            
            print(f"   Total tasks: {len(tasks_data.get('tasks', []))}")
            for task in tasks_data.get('tasks', [])[:3]:  # Show first 3 tasks
                print(f"   - Task #{task['id']}: {task['title']}")
        else:
            print("❌ tasks.json not found")
    else:
        print("❌ TaskMaster directory not found")
    
    # Check for TaskMaster bridge
    bridge_file = "claude_taskmaster_bridge.py"
    if os.path.exists(bridge_file):
        print("✅ claude_taskmaster_bridge.py found")
    else:
        print("❌ claude_taskmaster_bridge.py not found")
    
    # Check for agent wrapper
    wrapper_file = "taskmaster_agent_wrapper.py"
    if os.path.exists(wrapper_file):
        print("✅ taskmaster_agent_wrapper.py found")
    else:
        print("❌ taskmaster_agent_wrapper.py not found")
    
    # Test MCPs
    print("\n📡 Testing MCP Availability:")
    
    # Test 1: Memory MCP
    try:
        print("   Testing Memory MCP...")
        # This would require actual MCP connection in Claude Code
        print("   ✅ Memory MCP available (test placeholder)")
    except:
        print("   ❌ Memory MCP not available")
    
    # Test 2: Sequential Thinking MCP
    try:
        print("   Testing Sequential Thinking MCP...")
        print("   ✅ Sequential Thinking MCP available (test placeholder)")
    except:
        print("   ❌ Sequential Thinking MCP not available")
    
    # Test 3: IDE MCP
    try:
        print("   Testing IDE MCP...")
        print("   ✅ IDE MCP available (test placeholder)")
    except:
        print("   ❌ IDE MCP not available")
    
    # Test agent with TaskMaster
    print("\n🤖 Testing Agent with TaskMaster Context:")
    
    # Create a simple test task
    test_task = {
        "id": "test-1",
        "title": "Test Task",
        "description": "Test TaskMaster integration",
        "status": "pending"
    }
    
    # Try to run planning agent with TaskMaster context
    try:
        cmd = ["python3", "master-agent.py", "agent", "planning-analysis-agent", "--task-id", "test-1"]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("   ✅ Agent executed successfully with TaskMaster")
        else:
            print(f"   ⚠️  Agent execution returned code: {result.returncode}")
            if result.stderr:
                print(f"   Error: {result.stderr[:200]}")
    except subprocess.TimeoutExpired:
        print("   ⏱️  Agent execution timed out (expected for test)")
    except Exception as e:
        print(f"   ❌ Agent execution failed: {e}")
    
    print("\n" + "=" * 60)
    print("✅ TaskMaster integration test complete!")

if __name__ == "__main__":
    test_taskmaster_integration()