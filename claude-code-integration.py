#!/usr/bin/env python3
"""
Claude Code Integration Interface
=================================

Seamless integration layer that acts as a preprocessing filter for Claude Code.
This system intelligently determines when to engage the Task Master Agent System
vs handling requests directly, improving the overall Claude Code experience.

This acts as a "smart router" that:
- Intercepts all prompts before they reach Claude Code
- Uses sequential thinking to analyze complexity and intent
- Routes complex tasks to specialized agents
- Handles simple queries directly
- Provides a unified, enhanced experience

Usage:
    python3 claude-code-integration.py --prompt "your request here"
    python3 claude-code-integration.py --interactive
"""

import sys
import json
import subprocess
import time
from pathlib import Path
from typing import Dict, Any, Optional
import argparse

# Import our intelligent filter
from claude_code_filter import ClaudeCodeFilter, RoutingDecision

class ClaudeCodeEnhancer:
    """Main integration class that enhances Claude Code with intelligent agent routing"""
    
    def __init__(self):
        self.filter = ClaudeCodeFilter()
        self.agent_system_path = Path(__file__).parent / "master-agent.py"
        
    def process_request(self, prompt: str, auto_execute: bool = False) -> Dict[str, Any]:
        """Main entry point for processing Claude Code requests"""
        
        print("🧠 Analyzing your request...")
        
        # Step 1: Intelligent filtering
        filter_result = self.filter.filter_prompt(prompt, verbose=False)
        
        # Step 2: Display analysis
        self._display_filter_decision(filter_result, prompt)
        
        # Step 3: Execute based on decision
        if auto_execute:
            return self._auto_execute(filter_result, prompt)
        else:
            return self._interactive_execute(filter_result, prompt)
    
    def _display_filter_decision(self, result: Dict[str, Any], prompt: str):
        """Display the filter's decision in a user-friendly way"""
        print(f"\n📝 Request: {prompt[:80]}{'...' if len(prompt) > 80 else ''}")
        print(f"🎯 Analysis: {result['complexity']} complexity, {result['confidence']:.0%} confidence")
        print(f"💡 Decision: {result['message']}")
        
        if result['decision'] == 'route_to_agents':
            print(f"🤖 Will use {len(result.get('agent_command', '').split())} specialized agents")
        elif result['decision'] == 'hybrid_approach':
            print("🔄 Will combine agent assistance with direct handling")
        
        print()
    
    def _auto_execute(self, filter_result: Dict[str, Any], prompt: str) -> Dict[str, Any]:
        """Automatically execute based on filter decision"""
        
        if filter_result['decision'] == 'handle_directly':
            return {
                'status': 'direct_handling',
                'message': "Handled directly by Claude Code",
                'execution_time': 0
            }
            
        elif filter_result['decision'] in ['route_to_agents', 'hybrid_approach']:
            return self._execute_agents(filter_result['agent_command'])
            
        else:  # user_choice
            print("🤔 This request could benefit from agent assistance.")
            print("   Since auto-execute is enabled, proceeding with agents...")
            return self._execute_agents(filter_result.get('agent_command', 
                f"python3 {self.agent_system_path} analyze --tag general"))
    
    def _interactive_execute(self, filter_result: Dict[str, Any], prompt: str) -> Dict[str, Any]:
        """Interactive execution with user confirmation"""
        
        if filter_result['decision'] == 'handle_directly':
            print("✅ This can be handled directly by Claude Code.")
            print("   No agent assistance needed. Proceeding...")
            return {
                'status': 'direct_handling',
                'message': "Handled directly by Claude Code",
                'execution_time': 0
            }
            
        elif filter_result['decision'] == 'route_to_agents':
            print("🤖 This task would benefit from specialized agent assistance.")
            choice = input("   Proceed with agents? (Y/n): ").strip().lower()
            
            if choice in ['', 'y', 'yes']:
                return self._execute_agents(filter_result['agent_command'])
            else:
                print("📝 Proceeding with direct Claude Code handling...")
                return {'status': 'user_declined_agents', 'message': "User chose direct handling"}
                
        elif filter_result['decision'] == 'hybrid_approach':
            print("🔄 This could benefit from partial agent assistance.")
            choice = input("   Use hybrid approach? (Y/n): ").strip().lower()
            
            if choice in ['', 'y', 'yes']:
                print("🔄 Running agent pre-analysis...")
                agent_result = self._execute_agents(filter_result['agent_command'])
                print("✅ Agent analysis complete. Now proceeding with direct handling...")
                return {
                    'status': 'hybrid_complete',
                    'agent_result': agent_result,
                    'message': "Hybrid approach completed"
                }
            else:
                return {'status': 'user_declined_hybrid', 'message': "User chose direct handling"}
                
        else:  # user_choice
            print("🤔 This request is ambiguous. How would you like to proceed?")
            print("   1) Use specialized agents")
            print("   2) Handle directly in Claude Code")
            
            choice = input("   Choose (1-2): ").strip()
            
            if choice == '1':
                command = filter_result.get('agent_command', 
                    f"python3 {self.agent_system_path} analyze --tag general")
                return self._execute_agents(command)
            else:
                return {'status': 'user_chose_direct', 'message': "User chose direct handling"}
    
    def _execute_agents(self, command: str) -> Dict[str, Any]:
        """Execute the agent system with the given command"""
        print(f"🚀 Executing: {command}")
        print("   (This may take a moment...)")
        
        start_time = time.time()
        
        try:
            # Execute the agent command
            result = subprocess.run(
                command.split(),
                cwd=Path.cwd(),
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            execution_time = time.time() - start_time
            
            if result.returncode == 0:
                print(f"✅ Agents completed successfully in {execution_time:.1f}s")
                return {
                    'status': 'agents_success',
                    'execution_time': execution_time,
                    'output': result.stdout,
                    'message': f"Agents completed successfully in {execution_time:.1f}s"
                }
            else:
                print(f"❌ Agents failed with return code {result.returncode}")
                print(f"Error: {result.stderr}")
                return {
                    'status': 'agents_failed',
                    'execution_time': execution_time,
                    'error': result.stderr,
                    'message': f"Agents failed after {execution_time:.1f}s"
                }
                
        except subprocess.TimeoutExpired:
            print("⏰ Agent execution timed out after 5 minutes")
            return {
                'status': 'agents_timeout',
                'execution_time': 300,
                'message': "Agent execution timed out"
            }
        except Exception as e:
            print(f"💥 Unexpected error: {e}")
            return {
                'status': 'agents_error',
                'error': str(e),
                'message': f"Unexpected error: {e}"
            }
    
    def interactive_mode(self):
        """Run in interactive mode for testing and demonstration"""
        print("🎯 Claude Code Enhanced Interactive Mode")
        print("=" * 50)
        print("This demonstrates the intelligent filter that preprocesses")
        print("all Claude Code requests to determine optimal handling.")
        print()
        print("Type 'quit' to exit")
        print()
        
        while True:
            try:
                prompt = input("💬 Enter your request: ").strip()
                
                if prompt.lower() in ['quit', 'exit', 'q']:
                    print("👋 Goodbye!")
                    break
                
                if not prompt:
                    continue
                
                print()
                result = self.process_request(prompt, auto_execute=False)
                print(f"🏁 Result: {result['message']}")
                print("-" * 50)
                
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except EOFError:
                break

def main():
    """CLI interface for Claude Code integration"""
    parser = argparse.ArgumentParser(description='Claude Code Enhanced Integration')
    parser.add_argument('--prompt', type=str, help='Process a specific prompt')
    parser.add_argument('--auto-execute', action='store_true', help='Auto-execute without user confirmation')
    parser.add_argument('--interactive', action='store_true', help='Run in interactive mode')
    parser.add_argument('--test', action='store_true', help='Run test scenarios')
    
    args = parser.parse_args()
    
    enhancer = ClaudeCodeEnhancer()
    
    if args.interactive:
        enhancer.interactive_mode()
        
    elif args.test:
        run_test_scenarios(enhancer)
        
    elif args.prompt:
        result = enhancer.process_request(args.prompt, args.auto_execute)
        print(f"\n🏁 Final Result: {result}")
        
    else:
        print("Claude Code Enhanced Integration")
        print("=" * 40)
        print("Usage:")
        print("  --prompt 'your request'    Process a specific request")
        print("  --interactive             Interactive testing mode")
        print("  --test                    Run test scenarios")
        print("  --auto-execute            Auto-execute without confirmation")
        print()
        print("Examples:")
        print("  python3 claude-code-integration.py --prompt 'implement a login system'")
        print("  python3 claude-code-integration.py --interactive")

def run_test_scenarios(enhancer: ClaudeCodeEnhancer):
    """Run test scenarios to demonstrate the system"""
    test_prompts = [
        "what is 2+2?",
        "read the README file",
        "implement a user authentication system",
        "analyze the codebase and suggest improvements",
        "create a complete CI/CD pipeline with testing and deployment",
        "fix the bug in line 42 of main.py"
    ]
    
    print("🧪 Running Test Scenarios")
    print("=" * 40)
    
    for i, prompt in enumerate(test_prompts, 1):
        print(f"\n📝 Test {i}: {prompt}")
        print("-" * 30)
        
        result = enhancer.process_request(prompt, auto_execute=True)
        print(f"   Result: {result['status']}")
        
        time.sleep(1)  # Brief pause between tests

if __name__ == "__main__":
    main()