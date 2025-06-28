#!/usr/bin/env python3
"""
Test the full vibe.ai system with working agents
"""

import subprocess
import sys
import os

def test_full_flow():
    """Test the complete flow from idea to execution"""
    
    print("🚀 Testing Full vibe.ai System")
    print("=" * 60)
    
    # Step 1: Create a simple test task
    test_idea = "create a hello world python script"
    
    print(f"\n1️⃣ Test Idea: '{test_idea}'")
    
    # Step 2: Use master-agent to analyze
    print("\n2️⃣ Running Planning & Analysis Agent...")
    cmd = ["python3", "master-agent.py", "agent", "planning-analysis-agent"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ Planning agent succeeded!")
        print(f"   Output lines: {len(result.stdout.splitlines())}")
    else:
        print(f"❌ Planning agent failed: {result.stderr}")
        return False
    
    # Step 3: Run execution agent
    print("\n3️⃣ Running Universal Execution Agent...")
    cmd = ["python3", "master-agent.py", "agent", "universal-execution-agent", 
           "--task", test_idea, "--output", "test-output"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ Execution agent succeeded!")
        # Check if files were created
        if os.path.exists("test-output"):
            files = os.listdir("test-output")
            print(f"   Created files: {files}")
        else:
            print("   No output directory created")
    else:
        print(f"❌ Execution agent failed: {result.stderr}")
    
    # Step 4: Run quality check
    print("\n4️⃣ Running Quality Check Agent...")
    cmd = ["python3", "master-agent.py", "agent", "quality-git-agent", "--mode", "validate"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ Quality agent succeeded!")
    else:
        print(f"⚠️  Quality agent had issues: {result.stderr}")
    
    print("\n" + "=" * 60)
    print("✅ Test Complete!")
    
    # Show how to use with vibe.py
    print("\n📝 To use with vibe.py:")
    print("1. Run: python3 vibe.py")
    print("2. Choose option 1 (Make something new)")
    print("3. Enter your idea")
    print("4. Have philosophical conversation with Deep Planner")
    print("5. When done, it will generate PRD and offer to build")
    print("\n⚠️  Note: The agent system needs proper task context to work correctly")

if __name__ == "__main__":
    test_full_flow()