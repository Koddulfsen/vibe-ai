#!/usr/bin/env python3
"""
Demo: Agent Principles in Action
Shows the difference between bloated and principled output
"""

from agent_principles import AgentResponse, PrincipledOutput, apply_principles
from concise_formatter import ConciseFormatter, OutputBuffer

def bloated_output():
    """Example of bloated agent output"""
    print("=" * 80)
    print("AGENT EXECUTION STARTED")
    print("=" * 80)
    print()
    print("Starting task analysis...")
    print("Initializing components...")
    print("Loading configuration...")
    print()
    print("PHASE 1: ANALYSIS")
    print("-" * 40)
    print("Analyzing project structure...")
    print("Found the following files:")
    print("  - src/main.py")
    print("  - src/utils.py")
    print("  - src/config.py")
    print("  - tests/test_main.py")
    print("  - tests/test_utils.py")
    print("  - README.md")
    print("  - setup.py")
    print("  - requirements.txt")
    print()
    print("Analysis complete!")
    print()
    print("PHASE 2: PROCESSING")
    print("-" * 40)
    print("Processing files...")
    print("Processing src/main.py...")
    print("Processing src/utils.py...")
    print("Processing complete!")
    print()
    print("=" * 80)
    print("TASK COMPLETED SUCCESSFULLY")
    print("=" * 80)

def principled_output():
    """Example of principled agent output"""
    response = AgentResponse()
    response.add_summary("Task analysis complete")
    response.add_detail("8 Python files found")
    response.add_detail("No critical issues")
    response.add_action("Project structure analyzed")
    
    print(response.render())

def compare_task_outputs():
    """Compare different output styles"""
    print("\n🚫 BLOATED OUTPUT (32 lines):")
    print("-" * 50)
    bloated_output()
    
    print("\n\n✅ PRINCIPLED OUTPUT (4 lines):")
    print("-" * 50)
    principled_output()
    
    print("\n\n💡 Savings: 87.5% fewer lines, same information")

def demo_formatter():
    """Demo the concise formatter"""
    formatter = ConciseFormatter()
    
    print("\n📊 FORMATTER EXAMPLES:")
    print("-" * 50)
    
    # Task result
    print("Task Result:")
    print(formatter.format_task_result("API endpoint created", "success", {"time": "1.2s"}))
    
    # Progress
    print("\nProgress:")
    print(formatter.format_progress(7, 10, "Running tests"))
    
    # Error
    print("\nError:")
    print(formatter.format_error("ImportError", "Module 'xyz' not found", "Run: pip install xyz"))
    
    # File list
    print("\nFile List:")
    files = [f"file{i}.py" for i in range(20)]
    print(formatter.format_file_list(files, max_files=5))

def demo_principles():
    """Demo the core principles"""
    print("\n🎯 CORE PRINCIPLES:")
    print("-" * 50)
    
    # ULTRATHINK
    print("1. ULTRATHINK:")
    long_analysis = "After analyzing the codebase, considering multiple architectural patterns, evaluating performance implications, reviewing best practices, and thinking about future scalability..."
    concise = PrincipledOutput.make_concise(long_analysis, 50)
    print(f"   Before: {len(long_analysis)} chars")
    print(f"   After:  {len(concise)} chars → '{concise}'")
    
    # BE CONCISE
    print("\n2. BE CONCISE:")
    buffer = OutputBuffer(max_lines=5)
    buffer.add("Found issues:", "warning")
    for i in range(10):
        buffer.add(f"Issue {i+1}")
    print("   " + buffer.render().replace("\n", "\n   "))
    
    # NO BLOAT
    print("\n3. NO BLOAT:")
    data = {
        "status": "success",
        "empty": "",
        "null": None,
        "empty_list": [],
        "useful": "important data"
    }
    clean = PrincipledOutput.make_dict_concise(data)
    print(f"   Before: {len(data)} keys")
    print(f"   After:  {len(clean)} keys → {clean}")

if __name__ == "__main__":
    print("🚀 VIBE.AI AGENT PRINCIPLES DEMO")
    print("=" * 60)
    
    compare_task_outputs()
    demo_formatter()
    demo_principles()
    
    print("\n\n✨ Remember: ULTRATHINK | BE CONCISE | NO BLOAT")