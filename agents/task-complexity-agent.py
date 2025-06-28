#!/usr/bin/env python3
"""
Task Master Complexity Analyzer Agent

Automatically analyzes Task Master tasks for complexity and suggests subtask breakdowns.
Integrates with the existing Task Master CLI to provide intelligent task management.
"""

import json
import subprocess
import re
import argparse
import sys
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path

@dataclass
class ComplexityScore:
    """Represents the complexity analysis of a task"""
    total_score: int
    indicators: Dict[str, int]
    recommendation: str
    suggested_subtasks: int
    should_expand: bool

class TaskComplexityAgent:
    """
    Analyzes Task Master tasks for complexity and automatically suggests/creates subtasks
    """
    
    def __init__(self, config_path: Optional[str] = None):
        self.config = self._load_config(config_path)
        self.complexity_indicators = self._get_complexity_indicators()
        self.task_type_patterns = self._get_task_type_patterns()
        
    def _load_config(self, config_path: Optional[str]) -> Dict:
        """Load configuration or use defaults"""
        default_config = {
            "expansion_threshold": 6,
            "max_subtasks": 8,
            "min_subtasks": 3,
            "auto_expand": False,
            "dry_run": False,
            "verbose": False
        }
        
        if config_path and Path(config_path).exists():
            with open(config_path, 'r') as f:
                user_config = json.load(f)
                default_config.update(user_config)
        
        return default_config
    
    def _get_complexity_indicators(self) -> Dict[str, int]:
        """
        Define complexity indicators and their weights
        Higher scores = more complex = more likely to need subtasks
        """
        return {
            # Technology/Integration complexity
            'api': 3, 'integration': 4, 'database': 3, 'authentication': 3,
            'third-party': 3, 'external': 2, 'service': 2, 'endpoint': 2,
            
            # Implementation complexity  
            'algorithm': 4, 'optimization': 3, 'performance': 3, 'security': 4,
            'error handling': 3, 'validation': 2, 'caching': 3, 'offline': 4,
            
            # UI/UX complexity
            'component': 2, 'interface': 2, 'modal': 2, 'animation': 3,
            'responsive': 2, 'accessibility': 3, 'cross-browser': 3,
            
            # Testing complexity
            'testing': 2, 'unit test': 1, 'integration test': 3, 'e2e': 4,
            'cross-device': 3, 'compatibility': 3,
            
            # Infrastructure complexity
            'deployment': 4, 'configuration': 2, 'environment': 2,
            'monitoring': 3, 'logging': 2, 'analytics': 3,
            
            # Mobile/PWA specific
            'camera': 3, 'permissions': 2, 'pwa': 3, 'service worker': 4,
            'push notifications': 3, 'geolocation': 2,
            
            # Business logic complexity
            'workflow': 3, 'state management': 3, 'data transformation': 3,
            'business rules': 4, 'calculations': 2, 'reporting': 3,
            
            # Quality indicators
            'comprehensive': 2, 'robust': 2, 'complete': 2, 'production': 3,
            'scalable': 3, 'maintainable': 2,
            
            # Scope indicators
            'multiple': 2, 'various': 2, 'different': 1, 'across': 2,
            'implement': 1, 'create': 1, 'build': 1, 'develop': 1,
            'setup': 1, 'configure': 1, 'integrate': 2, 'connect': 1
        }
    
    def _get_task_type_patterns(self) -> Dict[str, Dict]:
        """Define patterns for different types of tasks and their characteristics"""
        return {
            'setup': {
                'patterns': ['install', 'configure', 'setup', 'initialize', 'create project'],
                'base_complexity': 2,
                'typical_subtasks': 4
            },
            'api_integration': {
                'patterns': ['api', 'endpoint', 'integration', 'service', 'external'],
                'base_complexity': 4,
                'typical_subtasks': 5
            },
            'ui_component': {
                'patterns': ['component', 'interface', 'ui', 'button', 'modal', 'form'],
                'base_complexity': 3,
                'typical_subtasks': 4
            },
            'data_pipeline': {
                'patterns': ['pipeline', 'data flow', 'transformation', 'processing'],
                'base_complexity': 5,
                'typical_subtasks': 6
            },
            'testing': {
                'patterns': ['test', 'testing', 'verification', 'validation'],
                'base_complexity': 3,
                'typical_subtasks': 4
            },
            'optimization': {
                'patterns': ['optimize', 'performance', 'improve', 'enhance'],
                'base_complexity': 4,
                'typical_subtasks': 5
            },
            'deployment': {
                'patterns': ['deploy', 'production', 'release', 'launch'],
                'base_complexity': 5,
                'typical_subtasks': 6
            }
        }
    
    def analyze_task_complexity(self, task: Dict) -> ComplexityScore:
        """
        Analyze a single task and return complexity score with recommendations
        """
        # Combine all text fields for analysis
        text_to_analyze = ' '.join([
            task.get('title', ''),
            task.get('description', ''),
            task.get('details', '') or '',
            task.get('testStrategy', '') or ''
        ]).lower()
        
        # Calculate complexity score
        indicators_found = {}
        total_score = 0
        
        for indicator, weight in self.complexity_indicators.items():
            if indicator in text_to_analyze:
                indicators_found[indicator] = weight
                total_score += weight
        
        # Apply task type modifiers
        task_type_bonus = self._get_task_type_bonus(text_to_analyze)
        total_score += task_type_bonus['bonus']
        
        # Determine if task should be expanded
        should_expand = total_score >= self.config['expansion_threshold']
        
        # Calculate suggested number of subtasks
        suggested_subtasks = self._calculate_suggested_subtasks(
            total_score, task_type_bonus['type'], task
        )
        
        # Generate recommendation
        recommendation = self._generate_recommendation(total_score, should_expand, suggested_subtasks)
        
        return ComplexityScore(
            total_score=total_score,
            indicators=indicators_found,
            recommendation=recommendation,
            suggested_subtasks=suggested_subtasks,
            should_expand=should_expand
        )
    
    def _get_task_type_bonus(self, text: str) -> Dict:
        """Determine task type and apply appropriate complexity bonus"""
        for task_type, config in self.task_type_patterns.items():
            for pattern in config['patterns']:
                if pattern in text:
                    return {
                        'type': task_type,
                        'bonus': config['base_complexity']
                    }
        return {'type': 'general', 'bonus': 0}
    
    def _calculate_suggested_subtasks(self, score: int, task_type: str, task: Dict) -> int:
        """Calculate the optimal number of subtasks based on complexity score"""
        if not task_type or task_type == 'general':
            # Base calculation on score
            if score >= 12:
                return min(self.config['max_subtasks'], 7)
            elif score >= 8:
                return 5
            elif score >= 6:
                return 4
            elif score >= 4:
                return 3
            else:
                return 0
        else:
            # Use task type specific recommendations
            type_config = self.task_type_patterns.get(task_type, {})
            base_subtasks = type_config.get('typical_subtasks', 4)
            
            # Adjust based on actual complexity
            if score >= 10:
                return min(self.config['max_subtasks'], base_subtasks + 2)
            elif score >= 8:
                return min(self.config['max_subtasks'], base_subtasks + 1)
            else:
                return max(self.config['min_subtasks'], base_subtasks)
    
    def _generate_recommendation(self, score: int, should_expand: bool, subtasks: int) -> str:
        """Generate human-readable recommendation"""
        if not should_expand:
            return f"Task is straightforward (score: {score}). No subtasks needed."
        
        urgency = "High" if score >= 10 else "Medium" if score >= 8 else "Low"
        return f"{urgency} complexity task (score: {score}). Recommend {subtasks} subtasks."
    
    def get_taskmaster_tasks(self, tag: str = 'agents') -> List[Dict]:
        """Fetch tasks from Task Master tasks.json file"""
        try:
            # Read directly from tasks.json file
            tasks_file = Path('.taskmaster/tasks/tasks.json')
            if not tasks_file.exists():
                print(f"Task Master tasks file not found: {tasks_file}")
                return []
                
            with open(tasks_file, 'r') as f:
                data = json.load(f)
                
            # Handle new format with tags - prioritize specified tag
            if isinstance(data, dict) and tag in data:
                tasks = data[tag]['tasks']
                if self.config['verbose']:
                    print(f"📁 Loaded {len(tasks)} tasks from {tag} tag")
            elif isinstance(data, dict) and 'master' in data:
                tasks = data['master']['tasks']
                if self.config['verbose']:
                    print(f"📁 Loaded {len(tasks)} tasks from master tag (fallback)")
            elif isinstance(data, dict) and 'tasks' in data:
                tasks = data['tasks']
                if self.config['verbose']:
                    print(f"📁 Loaded {len(tasks)} tasks from legacy format")
            elif isinstance(data, list):
                tasks = data
                if self.config['verbose']:
                    print(f"📁 Loaded {len(tasks)} tasks from array format")
            else:
                print(f"Unexpected tasks.json format: {type(data)}")
                return []
                
            return tasks
                        
        except (json.JSONDecodeError, FileNotFoundError) as e:
            print(f"Error reading tasks from Task Master: {e}")
            return []
    
    def analyze_all_tasks(self, tag: str = 'agents') -> List[Tuple[Dict, ComplexityScore]]:
        """Analyze all tasks and return results"""
        tasks = self.get_taskmaster_tasks(tag)
        results = []
        
        for task in tasks:
            # Skip tasks that already have subtasks
            if task.get('subtasks') and len(task['subtasks']) > 0:
                continue
                
            complexity = self.analyze_task_complexity(task)
            results.append((task, complexity))
        
        return results
    
    def auto_expand_tasks(self, results: List[Tuple[Dict, ComplexityScore]]) -> None:
        """Automatically expand tasks that meet the complexity threshold"""
        for task, complexity in results:
            if complexity.should_expand:
                if self.config['verbose']:
                    print(f"Auto-expanding Task {task['id']}: {task['title']}")
                    print(f"  Complexity Score: {complexity.total_score}")
                    print(f"  Suggested Subtasks: {complexity.suggested_subtasks}")
                
                if not self.config['dry_run']:
                    try:
                        subprocess.run([
                            'task-master', 'expand', 
                            f"--id={task['id']}", 
                            f"--num={complexity.suggested_subtasks}",
                            '--research'
                        ], check=True)
                        print(f"✅ Expanded Task {task['id']} into {complexity.suggested_subtasks} subtasks")
                    except subprocess.CalledProcessError as e:
                        print(f"❌ Failed to expand Task {task['id']}: {e}")
                else:
                    print(f"🔍 [DRY RUN] Would expand Task {task['id']} into {complexity.suggested_subtasks} subtasks")
    
    def print_analysis_report(self, results: List[Tuple[Dict, ComplexityScore]]) -> None:
        """Print a detailed analysis report"""
        print("\n" + "="*80)
        print("🧠 TASK COMPLEXITY ANALYSIS REPORT")
        print("="*80)
        
        total_tasks = len(results)
        expandable_tasks = sum(1 for _, complexity in results if complexity.should_expand)
        
        print(f"\n📊 SUMMARY:")
        print(f"   Total Tasks Analyzed: {total_tasks}")
        print(f"   Tasks Needing Expansion: {expandable_tasks}")
        print(f"   Expansion Threshold: {self.config['expansion_threshold']}")
        
        print(f"\n📋 DETAILED ANALYSIS:")
        
        for task, complexity in sorted(results, key=lambda x: x[1].total_score, reverse=True):
            status_icon = "🔴" if complexity.should_expand else "🟢"
            print(f"\n{status_icon} Task {task['id']}: {task['title'][:50]}...")
            print(f"   Complexity Score: {complexity.total_score}")
            print(f"   Recommendation: {complexity.recommendation}")
            
            if complexity.indicators:
                print(f"   Complexity Indicators: {', '.join(complexity.indicators.keys())}")
            
            if complexity.should_expand:
                print(f"   🎯 Suggested Action: task-master expand --id={task['id']} --num={complexity.suggested_subtasks}")
        
        print("\n" + "="*80)

def main():
    parser = argparse.ArgumentParser(description='Task Master Complexity Analyzer Agent')
    parser.add_argument('--config', type=str, help='Path to configuration file')
    parser.add_argument('--auto-expand', action='store_true', help='Automatically expand complex tasks')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be done without making changes')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    parser.add_argument('--threshold', type=int, default=6, help='Complexity threshold for expansion (default: 6)')
    parser.add_argument('--max-subtasks', type=int, default=8, help='Maximum subtasks to create (default: 8)')
    parser.add_argument('--tag', type=str, default='agents', help='Task Master tag to analyze (default: agents)')
    
    args = parser.parse_args()
    
    # Create agent with configuration
    agent = TaskComplexityAgent(args.config)
    agent.config.update({
        'auto_expand': args.auto_expand,
        'dry_run': args.dry_run,
        'verbose': args.verbose,
        'expansion_threshold': args.threshold,
        'max_subtasks': args.max_subtasks
    })
    
    print("🤖 Task Master Complexity Analyzer Agent")
    print("==========================================")
    
    # Analyze all tasks
    results = agent.analyze_all_tasks(args.tag)
    
    if not results:
        print(f"No tasks found to analyze in '{args.tag}' tag. Make sure you're in a Task Master project directory.")
        sys.exit(1)
    
    # Print analysis report
    agent.print_analysis_report(results)
    
    # Auto-expand if requested
    if args.auto_expand:
        print(f"\n🚀 AUTO-EXPANSION MODE {'(DRY RUN)' if args.dry_run else ''}")
        print("-" * 50)
        agent.auto_expand_tasks(results)
    
    print("\n✅ Analysis complete!")

if __name__ == "__main__":
    main()