#!/usr/bin/env python3
"""
Quick Build - Skip philosophy, go straight to building with agents
"""

import sys
import os
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from agent_based_solution_engine import AgentBasedSolutionEngine
from prompting_oracle_agent import PromptingOracleAgent

def quick_build(idea: str, output_dir: str = None):
    """Quickly build a solution using agents without philosophical discussion"""
    
    print(f"\n🚀 Quick Build Mode - Let's create: {idea}")
    
    # Use Oracle to enhance the prompt
    print("\n🔮 Enhancing your idea with the Oracle...")
    oracle = PromptingOracleAgent()
    oracle_result = oracle.divine_task_essence(idea)
    
    # Extract the enhanced description
    enhanced_idea = oracle_result.get('enhanced_prompt', idea)
    
    # Default output directory
    if not output_dir:
        # Create a folder name from the idea
        folder_name = idea.lower().replace(" ", "-")[:30]
        folder_name = ''.join(c if c.isalnum() or c == '-' else '-' for c in folder_name)
        output_dir = folder_name.strip('-') or "quick-build"
    
    print(f"\n📁 Output directory: {output_dir}")
    
    # Use the agent-based solution engine directly
    print("\n🤖 Activating agent system...")
    engine = AgentBasedSolutionEngine()
    
    # Create complete solution using agents
    result = engine.create_complete_solution(enhanced_idea, output_dir)
    
    if result.get("success"):
        print(f"\n✅ Solution created successfully in: {output_dir}")
        print("\n📋 Next steps:")
        print(f"  1. cd {output_dir}")
        print("  2. Review the generated files")
        print("  3. Follow README.md instructions")
    else:
        print(f"\n❌ Error: {result.get('error', 'Unknown error')}")
    
    return result


def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print("Usage: quick_build.py \"your idea\" [output-dir]")
        print("\nExample:")
        print('  quick_build.py "make a website meetup platform for old people"')
        print('  quick_build.py "build a todo app" my-todo-app')
        sys.exit(1)
    
    idea = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else None
    
    quick_build(idea, output_dir)


if __name__ == "__main__":
    main()