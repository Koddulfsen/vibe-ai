#!/usr/bin/env python3
"""
Claude Code Intelligent Wrapper
===============================

The ultimate preprocessing filter for Claude Code that automatically improves
every interaction by intelligently routing requests to specialized agents when
beneficial, while handling simple queries directly.

This wrapper acts as a transparent enhancement layer that:
✅ Analyzes EVERY prompt before Claude Code processes it
✅ Uses sequential thinking to determine optimal handling
✅ Routes complex tasks to specialized automation agents
✅ Handles simple queries directly for speed
✅ Provides seamless, enhanced experience

Integration with Claude Code:
    1. Place this in your Claude Code tools directory
    2. Route all prompts through this wrapper first
    3. Enjoy enhanced automation and smarter task handling

Usage:
    python3 claude-code-wrapper.py --filter "your prompt here"
    python3 claude-code-wrapper.py --batch file.txt
    python3 claude-code-wrapper.py --daemon  # Background service mode
"""

import sys
import json
import time
import argparse
from pathlib import Path
from typing import Dict, Any, List, Optional
import subprocess

# Import our intelligent systems
from claude_code_filter import ClaudeCodeFilter, RoutingDecision

class ClaudeCodeWrapper:
    """The main wrapper that enhances Claude Code with intelligent agent routing"""
    
    def __init__(self, verbose: bool = False):
        self.filter = ClaudeCodeFilter()
        self.verbose = verbose
        self.stats = {
            'total_requests': 0,
            'direct_handled': 0,
            'agent_routed': 0,
            'hybrid_processed': 0,
            'processing_time': 0
        }
    
    def process_prompt(self, prompt: str, silent: bool = False) -> Dict[str, Any]:
        """
        Main entry point: intelligently process any prompt for Claude Code
        
        Returns a decision about how the prompt should be handled:
        - 'direct': Handle directly in Claude Code (no agents needed)
        - 'agents': Route to specialized agents first, then return to Claude Code
        - 'hybrid': Use agents for analysis, then continue with Claude Code
        """
        
        start_time = time.time()
        self.stats['total_requests'] += 1
        
        if not silent:
            print("🧠 Intelligent Claude Code Filter Active...")
        
        # Step 1: Analyze the prompt
        analysis = self.filter.filter_prompt(prompt, verbose=self.verbose)
        
        # Step 2: Generate processing recommendation
        recommendation = self._generate_recommendation(analysis, prompt)
        
        # Step 3: Update statistics
        processing_time = time.time() - start_time
        self.stats['processing_time'] += processing_time
        
        if analysis['decision'] == 'handle_directly':
            self.stats['direct_handled'] += 1
        elif analysis['decision'] == 'route_to_agents':
            self.stats['agent_routed'] += 1
        else:
            self.stats['hybrid_processed'] += 1
        
        if not silent:
            self._display_recommendation(recommendation, analysis)
        
        return recommendation
    
    def _generate_recommendation(self, analysis: Dict[str, Any], prompt: str) -> Dict[str, Any]:
        """Generate a comprehensive recommendation for Claude Code"""
        
        recommendation = {
            'original_prompt': prompt,
            'decision': analysis['decision'],
            'confidence': analysis['confidence'],
            'complexity': analysis['complexity'],
            'reasoning': analysis['reasoning'],
            'estimated_benefit': self._calculate_benefit_score(analysis),
            'claude_code_action': self._determine_claude_action(analysis),
            'preprocessing_needed': analysis['decision'] != 'handle_directly',
            'agent_command': analysis.get('agent_command'),
            'processing_time': self.stats['processing_time']
        }
        
        # Add execution plan
        if recommendation['preprocessing_needed']:
            recommendation['execution_plan'] = self._create_execution_plan(analysis)
        
        return recommendation
    
    def _calculate_benefit_score(self, analysis: Dict[str, Any]) -> float:
        """Calculate the potential benefit of using agents vs direct handling"""
        base_score = analysis['confidence']
        
        # Boost score for complex tasks
        if analysis['complexity'] in ['complex', 'multi_agent']:
            base_score *= 1.3
        
        # Boost for high-confidence agent routing
        if analysis['decision'] == 'route_to_agents' and analysis['confidence'] > 0.8:
            base_score *= 1.2
        
        return min(1.0, base_score)
    
    def _determine_claude_action(self, analysis: Dict[str, Any]) -> str:
        """Determine what Claude Code should do based on analysis"""
        
        if analysis['decision'] == 'handle_directly':
            return 'proceed_normally'
        elif analysis['decision'] == 'route_to_agents':
            return 'wait_for_agent_completion'
        elif analysis['decision'] == 'hybrid_approach':
            return 'use_agent_context'
        else:
            return 'user_decision_required'
    
    def _create_execution_plan(self, analysis: Dict[str, Any]) -> List[Dict[str, str]]:
        """Create a step-by-step execution plan"""
        plan = []
        
        if analysis['decision'] == 'route_to_agents':
            plan = [
                {
                    'step': 1,
                    'action': 'execute_agents',
                    'command': analysis.get('agent_command', ''),
                    'description': 'Run specialized agents for analysis and execution'
                },
                {
                    'step': 2,
                    'action': 'process_agent_results',
                    'description': 'Integrate agent results with Claude Code context'
                },
                {
                    'step': 3,
                    'action': 'continue_claude_code',
                    'description': 'Proceed with enhanced context and results'
                }
            ]
        elif analysis['decision'] == 'hybrid_approach':
            plan = [
                {
                    'step': 1,
                    'action': 'agent_preprocessing',
                    'command': analysis.get('agent_command', ''),
                    'description': 'Use agents for initial analysis and planning'
                },
                {
                    'step': 2,
                    'action': 'claude_code_implementation',
                    'description': 'Use Claude Code for main implementation with agent insights'
                }
            ]
        
        return plan
    
    def _display_recommendation(self, recommendation: Dict[str, Any], analysis: Dict[str, Any]):
        """Display the recommendation in a user-friendly format"""
        
        decision_icons = {
            'handle_directly': '✅',
            'route_to_agents': '🤖',
            'hybrid_approach': '🔄',
            'user_choice': '🤔'
        }
        
        icon = decision_icons.get(analysis['decision'], '❓')
        
        print(f"\n{icon} **RECOMMENDATION**")
        print(f"📊 Complexity: {analysis['complexity']} | Confidence: {analysis['confidence']:.0%}")
        print(f"💡 {analysis['reasoning']}")
        
        if recommendation['preprocessing_needed']:
            benefit = recommendation['estimated_benefit']
            print(f"🎯 Estimated benefit: {benefit:.0%}")
            
            if recommendation.get('execution_plan'):
                print(f"📋 Execution plan:")
                for step in recommendation['execution_plan']:
                    print(f"   {step['step']}. {step['description']}")
        
        print()
    
    def execute_recommendation(self, recommendation: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the recommendation (run agents if needed)"""
        
        if not recommendation['preprocessing_needed']:
            return {
                'status': 'direct_execution',
                'message': 'No preprocessing needed, Claude Code can proceed normally'
            }
        
        if recommendation.get('agent_command'):
            print(f"🚀 Executing: {recommendation['agent_command']}")
            
            try:
                result = subprocess.run(
                    recommendation['agent_command'].split(),
                    capture_output=True,
                    text=True,
                    timeout=300
                )
                
                if result.returncode == 0:
                    return {
                        'status': 'preprocessing_complete',
                        'agent_output': result.stdout,
                        'message': 'Agents completed successfully, Claude Code can proceed with enhanced context'
                    }
                else:
                    return {
                        'status': 'preprocessing_failed',
                        'error': result.stderr,
                        'message': 'Agent preprocessing failed, Claude Code should proceed normally'
                    }
                    
            except Exception as e:
                return {
                    'status': 'preprocessing_error',
                    'error': str(e),
                    'message': 'Agent preprocessing encountered an error, Claude Code should proceed normally'
                }
        
        return {
            'status': 'no_command',
            'message': 'No agent command specified'
        }
    
    def batch_process(self, prompts: List[str]) -> List[Dict[str, Any]]:
        """Process multiple prompts in batch"""
        results = []
        
        print(f"📦 Processing {len(prompts)} prompts in batch mode...")
        
        for i, prompt in enumerate(prompts, 1):
            print(f"🔄 Processing {i}/{len(prompts)}: {prompt[:50]}...")
            result = self.process_prompt(prompt, silent=True)
            results.append(result)
        
        self._display_batch_summary(results)
        return results
    
    def _display_batch_summary(self, results: List[Dict[str, Any]]):
        """Display summary of batch processing"""
        total = len(results)
        direct = sum(1 for r in results if r['decision'] == 'handle_directly')
        agents = sum(1 for r in results if r['decision'] == 'route_to_agents')
        hybrid = sum(1 for r in results if r['decision'] == 'hybrid_approach')
        
        print(f"\n📊 Batch Processing Summary:")
        print(f"   Total prompts: {total}")
        print(f"   Direct handling: {direct} ({direct/total:.0%})")
        print(f"   Agent routing: {agents} ({agents/total:.0%})")
        print(f"   Hybrid approach: {hybrid} ({hybrid/total:.0%})")
        print(f"   Average benefit: {sum(r['estimated_benefit'] for r in results)/total:.0%}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get processing statistics"""
        total = self.stats['total_requests']
        if total == 0:
            return {'message': 'No requests processed yet'}
        
        return {
            'total_requests': total,
            'direct_handled': self.stats['direct_handled'],
            'agent_routed': self.stats['agent_routed'],
            'hybrid_processed': self.stats['hybrid_processed'],
            'direct_percentage': (self.stats['direct_handled'] / total) * 100,
            'agent_percentage': (self.stats['agent_routed'] / total) * 100,
            'hybrid_percentage': (self.stats['hybrid_processed'] / total) * 100,
            'average_processing_time': self.stats['processing_time'] / total
        }

def main():
    """CLI interface for the Claude Code wrapper"""
    parser = argparse.ArgumentParser(description='Claude Code Intelligent Wrapper')
    parser.add_argument('--filter', type=str, help='Filter a specific prompt')
    parser.add_argument('--execute', action='store_true', help='Execute the recommendation')
    parser.add_argument('--batch', type=str, help='Process prompts from file (one per line)')
    parser.add_argument('--stats', action='store_true', help='Show processing statistics')
    parser.add_argument('--verbose', action='store_true', help='Verbose output')
    parser.add_argument('--demo', action='store_true', help='Run demonstration')
    
    args = parser.parse_args()
    
    wrapper = ClaudeCodeWrapper(verbose=args.verbose)
    
    if args.filter:
        recommendation = wrapper.process_prompt(args.filter)
        
        if args.execute:
            print("\n🚀 Executing recommendation...")
            result = wrapper.execute_recommendation(recommendation)
            print(f"✅ {result['message']}")
        
        print(f"\n📋 Full recommendation:")
        print(json.dumps(recommendation, indent=2))
        
    elif args.batch:
        batch_file = Path(args.batch)
        if batch_file.exists():
            prompts = batch_file.read_text().strip().split('\n')
            results = wrapper.batch_process(prompts)
        else:
            print(f"❌ Batch file not found: {args.batch}")
            
    elif args.stats:
        stats = wrapper.get_statistics()
        print("📊 Processing Statistics:")
        print(json.dumps(stats, indent=2))
        
    elif args.demo:
        run_demo(wrapper)
        
    else:
        print("🎯 Claude Code Intelligent Wrapper")
        print("=" * 50)
        print("Enhances Claude Code with intelligent agent routing")
        print()
        print("Usage:")
        print("  --filter 'prompt'     Analyze a specific prompt")
        print("  --execute            Execute the recommendation")
        print("  --batch file.txt     Process multiple prompts")
        print("  --stats              Show processing statistics")
        print("  --demo               Run demonstration")
        print()
        print("Examples:")
        print("  python3 claude-code-wrapper.py --filter 'implement authentication'")
        print("  python3 claude-code-wrapper.py --filter 'what is 2+2?' --execute")

def run_demo(wrapper: ClaudeCodeWrapper):
    """Run a demonstration of the wrapper"""
    demo_prompts = [
        "what is the capital of France?",
        "read the package.json file and show me the dependencies",
        "implement a complete REST API with authentication and database integration",
        "fix the syntax error on line 25",
        "analyze the entire codebase and create a comprehensive testing strategy",
        "what does this error message mean?"
    ]
    
    print("🎭 Claude Code Wrapper Demonstration")
    print("=" * 50)
    print("This shows how the wrapper intelligently routes different types of requests")
    print()
    
    for i, prompt in enumerate(demo_prompts, 1):
        print(f"📝 Demo {i}: {prompt}")
        recommendation = wrapper.process_prompt(prompt, silent=False)
        print("-" * 40)
        time.sleep(1)
    
    print("\n📊 Demo Complete!")
    stats = wrapper.get_statistics()
    print(f"Processed {stats['total_requests']} requests:")
    print(f"  {stats['direct_percentage']:.0f}% handled directly")
    print(f"  {stats['agent_percentage']:.0f}% routed to agents")
    print(f"  {stats['hybrid_percentage']:.0f}% used hybrid approach")

if __name__ == "__main__":
    main()