#!/usr/bin/env python3
"""
Claude Code Hook for Automatic TaskMaster Integration
=====================================================

This hook integrates with Claude Code to automatically trigger TaskMaster
when native complexity rating exceeds thresholds.

Integration Flow:
1. Claude Code detects high complexity task
2. Calls this hook with task details
3. Hook generates PRD and routes to TaskMaster
4. Results fed back to Claude Code

Usage in Claude Code:
    When complexity > threshold:
        result = subprocess.run(['python3', 'claude_code_hook.py', 'auto', task])
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from claude_taskmaster_bridge import ClaudeTaskMasterBridge, PRD

class ClaudeCodeHook:
    """Hook for automatic TaskMaster integration"""
    
    def __init__(self):
        self.bridge = ClaudeTaskMasterBridge()
        self.hook_config_file = Path(__file__).parent / "hook_config.json"
        self.load_hook_config()
    
    def load_hook_config(self):
        """Load hook-specific configuration"""
        if self.hook_config_file.exists():
            try:
                with open(self.hook_config_file, 'r') as f:
                    self.config = json.load(f)
            except Exception:
                self.config = {}
        else:
            self.config = {
                'auto_threshold': 7.0,
                'silent_mode': False,
                'return_prd': True
            }
    
    def auto_process(self, task: str, complexity_score: Optional[float] = None) -> Dict[str, Any]:
        """
        Automatically process high-complexity task from Claude Code
        
        This is the main integration point - Claude Code calls this when
        it detects a high-complexity task.
        """
        
        if not self.config.get('silent_mode'):
            print(f"\n🔄 Claude Code Hook Activated")
            print(f"📋 Task: {task[:100]}...")
            if complexity_score:
                print(f"📊 Claude Complexity: {complexity_score}")
        
        # Process through bridge
        result = self.bridge.process_task(task, auto_execute=True)
        
        # Format response for Claude Code
        response = {
            'success': True,
            'action_taken': result['action'],
            'complexity_score': result['complexity_score'],
            'taskmaster_activated': result['action'] in ['executed', 'prd_generated']
        }
        
        if result['prd'] and self.config.get('return_prd'):
            response['prd'] = {
                'task_id': result['prd'].task_id,
                'title': result['prd'].title,
                'objectives': result['prd'].objectives,
                'suggested_agents': result['prd'].suggested_agents
            }
        
        if result['execution']:
            response['execution'] = {
                'success': result['execution']['success'],
                'workflow_used': result['agent_plan']['workflow_type'] if 'agent_plan' in result else None
            }
        
        return response
    
    def generate_prd_only(self, task: str) -> Dict[str, Any]:
        """Generate PRD without executing TaskMaster workflow"""
        
        # Analyze task
        analysis = self.bridge.filter.filter_prompt(task, verbose=False)
        complexity_score = self.bridge._calculate_complexity_score(analysis)
        
        # Generate PRD
        prd = self.bridge.generate_prd(task, analysis, complexity_score)
        
        # Save PRD
        prd_path = self.bridge.save_prd(prd)
        
        return {
            'prd_path': str(prd_path),
            'prd_id': prd.task_id,
            'complexity_score': complexity_score,
            'suggested_workflow': self.bridge._determine_workflow_type(prd)
        }
    
    def check_threshold(self, complexity_score: float) -> bool:
        """Check if complexity exceeds auto-trigger threshold"""
        return complexity_score >= self.config.get('auto_threshold', 7.0)

# Integration function for Claude Code
def claude_code_integration(task: str, complexity_score: Optional[float] = None) -> Dict[str, Any]:
    """
    Main integration point for Claude Code
    
    Call this function when Claude detects high complexity:
    
    from claude_code_hook import claude_code_integration
    
    if task_complexity > 7.0:
        result = claude_code_integration(task, task_complexity)
        if result['taskmaster_activated']:
            # Use TaskMaster results
        else:
            # Continue with Claude Code
    """
    hook = ClaudeCodeHook()
    return hook.auto_process(task, complexity_score)

def main():
    """CLI interface for testing and manual execution"""
    if len(sys.argv) < 2:
        print("Usage: claude_code_hook.py <command> [args...]")
        print("Commands:")
        print("  auto <task>           - Auto-process task")
        print("  prd <task>            - Generate PRD only")
        print("  check <score>         - Check if score exceeds threshold")
        return
    
    command = sys.argv[1]
    hook = ClaudeCodeHook()
    
    if command == 'auto' and len(sys.argv) > 2:
        task = ' '.join(sys.argv[2:])
        result = hook.auto_process(task)
        print(json.dumps(result, indent=2))
    
    elif command == 'prd' and len(sys.argv) > 2:
        task = ' '.join(sys.argv[2:])
        result = hook.generate_prd_only(task)
        print(json.dumps(result, indent=2))
    
    elif command == 'check' and len(sys.argv) > 2:
        score = float(sys.argv[2])
        exceeds = hook.check_threshold(score)
        print(f"Exceeds threshold: {exceeds}")

if __name__ == "__main__":
    main()