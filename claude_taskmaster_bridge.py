#!/usr/bin/env python3
"""
Claude-TaskMaster Bridge
========================

Automatic integration layer that monitors Claude Code's complexity assessment,
generates PRDs for complex tasks, and seamlessly routes to TaskMaster agents.

This creates a unified workflow:
1. Monitor Claude's native complexity rating
2. Generate PRD when complexity is high
3. Parse PRD and determine required agents
4. Execute TaskMaster workflow automatically
"""

import os
import sys
import json
import time
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
import hashlib

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from claude_code_filter import ClaudeCodeFilter, PromptComplexity
from agent_registry import AgentRegistry

@dataclass
class PRD:
    """Product Requirements Document structure"""
    title: str
    description: str
    complexity_score: float
    objectives: List[str]
    technical_requirements: List[str]
    constraints: List[str]
    success_criteria: List[str]
    estimated_effort: str
    suggested_agents: List[str]
    generated_at: str
    task_id: str

@dataclass
class ComplexityThresholds:
    """Configurable thresholds for automatic routing"""
    prd_generation: float = 6.0  # Generate PRD at this complexity
    auto_taskmaster: float = 7.0  # Auto-route to TaskMaster
    require_confirmation: float = 9.0  # Require user confirmation

class ClaudeTaskMasterBridge:
    """Bridges Claude Code with TaskMaster for automatic complex task handling"""
    
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.prds_dir = self.base_dir / "prds"
        self.prds_dir.mkdir(exist_ok=True)
        
        self.filter = ClaudeCodeFilter()
        self.registry = AgentRegistry()
        self.thresholds = ComplexityThresholds()
        
        # Load configuration if exists
        self.config_file = self.base_dir / "bridge_config.json"
        self.load_config()
    
    def load_config(self):
        """Load bridge configuration"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    self.thresholds = ComplexityThresholds(**config.get('thresholds', {}))
            except Exception as e:
                print(f"Warning: Could not load config: {e}")
    
    def save_config(self):
        """Save current configuration"""
        config = {
            'thresholds': asdict(self.thresholds),
            'last_updated': datetime.now().isoformat()
        }
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=2)
    
    def process_task(self, task_description: str, auto_execute: bool = True) -> Dict[str, Any]:
        """Main entry point - process task with automatic routing"""
        
        print("🔍 Analyzing task complexity...")
        
        # Step 1: Analyze complexity using Claude Code filter
        analysis = self.filter.filter_prompt(task_description, verbose=True)
        complexity_score = self._calculate_complexity_score(analysis)
        
        print(f"📊 Complexity Score: {complexity_score:.1f}")
        print(f"🎯 Decision: {analysis['decision']}")
        
        result = {
            'task': task_description,
            'complexity_score': complexity_score,
            'analysis': analysis,
            'prd': None,
            'execution': None
        }
        
        # Step 2: Determine action based on complexity
        if complexity_score < self.thresholds.prd_generation:
            print("✅ Task is simple enough for direct Claude Code handling")
            result['action'] = 'direct'
            return result
        
        # Step 3: Generate PRD for complex tasks
        print("\n📝 Generating Product Requirements Document...")
        prd = self.generate_prd(task_description, analysis, complexity_score)
        result['prd'] = prd
        
        # Save PRD
        prd_path = self.save_prd(prd)
        print(f"💾 PRD saved: {prd_path}")
        
        # Step 4: Parse PRD and determine agents
        agent_plan = self.parse_prd_for_agents(prd)
        result['agent_plan'] = agent_plan
        
        print(f"\n🤖 Recommended Agents: {', '.join(agent_plan['recommended_agents'])}")
        print(f"📋 Workflow Type: {agent_plan['workflow_type']}")
        
        # Step 5: Execute if appropriate
        if complexity_score >= self.thresholds.require_confirmation:
            print("\n⚠️  High complexity task - confirmation required")
            if not auto_execute:
                result['action'] = 'confirmation_required'
                return result
            
            response = input("Execute TaskMaster workflow? (y/n): ")
            if response.lower() != 'y':
                result['action'] = 'cancelled'
                return result
        
        if auto_execute and complexity_score >= self.thresholds.auto_taskmaster:
            print("\n🚀 Executing TaskMaster workflow...")
            execution_result = self.execute_taskmaster_workflow(prd, agent_plan)
            result['execution'] = execution_result
            result['action'] = 'executed'
        else:
            result['action'] = 'prd_generated'
        
        return result
    
    def _calculate_complexity_score(self, analysis: Dict[str, Any]) -> float:
        """Calculate numeric complexity score from analysis"""
        # Get base score from complexity level
        complexity_map = {
            'simple': 2.0,
            'moderate': 5.0,
            'complex': 8.0,
            'multi_agent': 10.0
        }
        
        base_score = complexity_map.get(analysis['complexity'], 5.0)
        
        # Adjust based on requirements
        if 'analysis' in analysis:
            requirements = analysis['analysis'].get('requirements', {})
            if requirements.get('file_operations'):
                base_score += 0.5
            if requirements.get('external_tools'):
                base_score += 1.0
            if requirements.get('planning'):
                base_score += 1.0
            if requirements.get('testing'):
                base_score += 0.5
        
        # Adjust based on confidence
        confidence = analysis.get('confidence', 0.7)
        if confidence < 0.6:
            base_score += 1.0  # Low confidence means higher complexity
        
        return min(base_score, 10.0)
    
    def generate_prd(self, task: str, analysis: Dict[str, Any], 
                    complexity_score: float) -> PRD:
        """Generate a comprehensive PRD from task analysis"""
        
        # Extract key information from analysis
        intent = analysis['analysis']['intent_category'] if 'analysis' in analysis else 'general'
        requirements = analysis['analysis'].get('requirements', {}) if 'analysis' in analysis else {}
        thinking = analysis['analysis'].get('sequential_thoughts', []) if 'analysis' in analysis else []
        
        # Generate task ID
        task_id = hashlib.md5(f"{task}{time.time()}".encode()).hexdigest()[:8]
        
        # Build objectives from thinking steps
        objectives = []
        for thought in thinking[:3]:  # Top 3 thoughts as objectives
            if thought.get('conclusion'):
                objectives.append(thought['conclusion'])
        
        if not objectives:
            objectives = [
                "Complete the requested task successfully",
                "Ensure high code quality and maintainability",
                "Implement comprehensive testing"
            ]
        
        # Determine technical requirements
        tech_requirements = []
        if requirements.get('file_operations'):
            tech_requirements.append("File system operations and management")
        if requirements.get('external_tools'):
            tech_requirements.append("External tool integration")
        if requirements.get('planning'):
            tech_requirements.append("Architectural planning and design")
        if requirements.get('testing'):
            tech_requirements.append("Comprehensive testing suite")
        
        if not tech_requirements:
            tech_requirements = ["Implementation of requested functionality"]
        
        # Success criteria
        success_criteria = [
            "All objectives completed successfully",
            "Code passes quality assessment (>70%)",
            "No critical errors or blockers",
            "Documentation provided"
        ]
        
        # Estimate effort
        effort_map = {
            "simple": "1-2 hours",
            "moderate": "2-4 hours",
            "complex": "4-8 hours",
            "multi_agent": "8+ hours"
        }
        estimated_effort = effort_map.get(analysis['complexity'], "4-8 hours")
        
        # Suggest agents based on requirements
        suggested_agents = self._suggest_agents_for_task(task, requirements, intent)
        
        return PRD(
            title=f"PRD: {task[:60]}..." if len(task) > 60 else f"PRD: {task}",
            description=task,
            complexity_score=complexity_score,
            objectives=objectives,
            technical_requirements=tech_requirements,
            constraints=[
                "Maintain existing code quality standards",
                "Ensure backward compatibility",
                "Follow security best practices"
            ],
            success_criteria=success_criteria,
            estimated_effort=estimated_effort,
            suggested_agents=suggested_agents,
            generated_at=datetime.now().isoformat(),
            task_id=task_id
        )
    
    def _suggest_agents_for_task(self, task: str, requirements: Dict[str, bool], 
                                intent: str) -> List[str]:
        """Suggest appropriate agents based on task analysis"""
        agents = []
        
        # Always start with planning for complex tasks
        agents.append("planning-analysis-agent")
        
        # Add based on intent
        if intent in ['implementation', 'general']:
            agents.append("universal-execution-agent")
        
        # Add based on requirements
        if requirements.get('testing'):
            agents.append("quality-git-agent")
        
        if requirements.get('file_operations'):
            agents.append("repo-manager-agent")
        
        # Use registry to find additional relevant agents
        task_agents = self.registry.find_agents_for_task(task)
        for agent in task_agents[:2]:  # Add top 2 matches
            if agent.name not in agents:
                agents.append(agent.name)
        
        return agents
    
    def save_prd(self, prd: PRD) -> Path:
        """Save PRD to file"""
        filename = f"prd_{prd.task_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = self.prds_dir / filename
        
        with open(filepath, 'w') as f:
            json.dump(asdict(prd), f, indent=2)
        
        return filepath
    
    def parse_prd_for_agents(self, prd: PRD) -> Dict[str, Any]:
        """Parse PRD and create agent execution plan"""
        
        # Determine workflow type based on requirements
        workflow_type = self._determine_workflow_type(prd)
        
        # Get recommended agents
        recommended_agents = prd.suggested_agents
        
        # Create execution order
        execution_order = self._create_execution_order(recommended_agents)
        
        # Build agent context
        agent_context = {
            'prd_id': prd.task_id,
            'objectives': prd.objectives,
            'requirements': prd.technical_requirements,
            'constraints': prd.constraints,
            'success_criteria': prd.success_criteria
        }
        
        return {
            'workflow_type': workflow_type,
            'recommended_agents': recommended_agents,
            'execution_order': execution_order,
            'agent_context': agent_context,
            'estimated_duration': prd.estimated_effort
        }
    
    def _determine_workflow_type(self, prd: PRD) -> str:
        """Determine appropriate workflow type from PRD"""
        
        # Check technical requirements
        has_planning = any('planning' in req.lower() or 'design' in req.lower() 
                          for req in prd.technical_requirements)
        has_testing = any('test' in req.lower() for req in prd.technical_requirements)
        has_implementation = any('implement' in obj.lower() or 'create' in obj.lower() 
                               for obj in prd.objectives)
        
        if has_planning and has_implementation and has_testing:
            return "full-dev"
        elif has_planning and not has_implementation:
            return "planning"
        elif has_implementation and not has_planning:
            return "execute"
        elif has_testing:
            return "quality"
        else:
            return "analyze"
    
    def _create_execution_order(self, agents: List[str]) -> List[List[str]]:
        """Create execution order with parallel opportunities"""
        
        # Group agents by type for parallel execution
        planning_agents = [a for a in agents if 'planning' in a or 'analysis' in a]
        execution_agents = [a for a in agents if 'execution' in a or 'universal' in a]
        quality_agents = [a for a in agents if 'quality' in a or 'test' in a]
        other_agents = [a for a in agents if a not in planning_agents + execution_agents + quality_agents]
        
        execution_order = []
        
        # Planning first
        if planning_agents:
            execution_order.append(planning_agents)
        
        # Execution and other agents in parallel
        parallel_group = execution_agents + other_agents
        if parallel_group:
            execution_order.append(parallel_group)
        
        # Quality last
        if quality_agents:
            execution_order.append(quality_agents)
        
        return execution_order
    
    def execute_taskmaster_workflow(self, prd: PRD, agent_plan: Dict[str, Any]) -> Dict[str, Any]:
        """Execute TaskMaster workflow based on PRD and agent plan"""
        
        # Build command
        master_agent = self.base_dir / "master-agent.py"
        
        cmd = [
            "python3", str(master_agent),
            "workflow",
            "--type", agent_plan['workflow_type'],
            "--tag", f"prd_{prd.task_id}"
        ]
        
        print(f"🔧 Executing: {' '.join(cmd)}")
        
        # Save context for agents
        context_file = self.base_dir / ".taskmaster" / f"prd_{prd.task_id}_context.json"
        context_file.parent.mkdir(exist_ok=True)
        
        with open(context_file, 'w') as f:
            json.dump({
                'prd': asdict(prd),
                'agent_plan': agent_plan,
                'timestamp': datetime.now().isoformat()
            }, f, indent=2)
        
        # Execute workflow
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=self.base_dir.parent.parent  # Run from project root
            )
            
            return {
                'success': result.returncode == 0,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'command': ' '.join(cmd),
                'context_file': str(context_file)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'command': ' '.join(cmd)
            }
    
    def monitor_claude_complexity(self, task: str) -> Dict[str, Any]:
        """Monitor Claude's complexity assessment and trigger PRD generation"""
        
        # This would integrate with Claude's actual complexity rating
        # For now, we use our filter as a proxy
        
        print("🔄 Monitoring Claude Code complexity...")
        result = self.process_task(task, auto_execute=True)
        
        if result['complexity_score'] >= self.thresholds.prd_generation:
            print(f"\n📈 Complexity threshold reached: {result['complexity_score']:.1f}")
            print("🤖 TaskMaster workflow activated")
        
        return result

def main():
    """CLI interface for the bridge"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Claude-TaskMaster Bridge - Automatic complex task routing"
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Process command
    process_parser = subparsers.add_parser('process', help='Process a task')
    process_parser.add_argument('task', help='Task description')
    process_parser.add_argument('--no-execute', action='store_true', 
                               help='Generate PRD only, do not execute')
    
    # Monitor command
    monitor_parser = subparsers.add_parser('monitor', help='Monitor complexity')
    monitor_parser.add_argument('task', help='Task to monitor')
    
    # Config command
    config_parser = subparsers.add_parser('config', help='Configure thresholds')
    config_parser.add_argument('--prd-threshold', type=float, help='PRD generation threshold')
    config_parser.add_argument('--auto-threshold', type=float, help='Auto-execution threshold')
    config_parser.add_argument('--confirm-threshold', type=float, help='Confirmation threshold')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    bridge = ClaudeTaskMasterBridge()
    
    if args.command == 'process':
        result = bridge.process_task(args.task, auto_execute=not args.no_execute)
        
        print("\n📊 Processing Complete")
        print("=" * 50)
        print(f"Action: {result['action']}")
        print(f"Complexity: {result['complexity_score']:.1f}")
        
        if result['prd']:
            print(f"PRD Generated: {result['prd'].task_id}")
        
        if result['execution']:
            print(f"Execution: {'Success' if result['execution']['success'] else 'Failed'}")
    
    elif args.command == 'monitor':
        result = bridge.monitor_claude_complexity(args.task)
        
    elif args.command == 'config':
        if args.prd_threshold:
            bridge.thresholds.prd_generation = args.prd_threshold
        if args.auto_threshold:
            bridge.thresholds.auto_taskmaster = args.auto_threshold
        if args.confirm_threshold:
            bridge.thresholds.require_confirmation = args.confirm_threshold
        
        bridge.save_config()
        print("✅ Configuration updated")
        print(f"PRD Generation: {bridge.thresholds.prd_generation}")
        print(f"Auto TaskMaster: {bridge.thresholds.auto_taskmaster}")
        print(f"Require Confirmation: {bridge.thresholds.require_confirmation}")

if __name__ == "__main__":
    main()