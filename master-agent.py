#!/usr/bin/env python3
"""
Task Master Agent System - Master Agent
========================================

Single entry point for the complete Task Master agent system.
Orchestrates all agents and provides unified CLI interface.

Usage:
    ./master-agent.py --help
    ./master-agent.py analyze --tag <tag>
    ./master-agent.py execute --task-id <id>
    ./master-agent.py workflow --type full-dev
    ./master-agent.py status
"""

import sys
import os
import argparse
import json
import subprocess
import time
import threading
import concurrent.futures
from pathlib import Path
from typing import Dict, List, Optional, Any, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum

# Add agents directory to path
AGENT_DIR = Path(__file__).parent / "agents"
sys.path.insert(0, str(AGENT_DIR))

# Import dynamic agent registry
try:
    from agent_registry import AgentRegistry
    DYNAMIC_REGISTRY_AVAILABLE = True
except ImportError:
    DYNAMIC_REGISTRY_AVAILABLE = False

# Import quality assessment engine
try:
    from quality_assessment import QualityAssessmentEngine, QualityReport, QualityDimension
    QUALITY_ASSESSMENT_AVAILABLE = True
except ImportError:
    QUALITY_ASSESSMENT_AVAILABLE = False

class WorkflowType(Enum):
    ANALYZE_ONLY = "analyze"
    EXECUTE_ONLY = "execute"
    QUALITY_CHECK = "quality"
    FULL_DEVELOPMENT = "full-dev"
    PLANNING_SESSION = "planning"
    QUICK_FIX = "quick-fix"

@dataclass
class EnhancedAgentResult:
    """Enhanced result from running an agent with comprehensive quality assessment"""
    agent_name: str
    success: bool
    output: str
    duration: float
    confidence_score: float = 0.0  # 0.0-1.0 how confident the agent is
    quality_score: float = 0.0     # 0.0-1.0 overall quality of work performed
    dependencies_met: Dict[str, float] = field(default_factory=dict)  # Dependencies satisfied
    provides_for: List[str] = field(default_factory=list)  # What agents can use this
    information_quality: str = "medium"  # "high", "medium", "low"
    filtered_output: Dict[str, Any] = field(default_factory=dict)  # Structured data
    quality_report: Optional['QualityReport'] = None  # Comprehensive quality assessment
    error: Optional[str] = None
    
    def get_dependency_score(self) -> float:
        """Calculate overall dependency satisfaction score"""
        if not self.dependencies_met:
            return 1.0  # No dependencies = fully satisfied
        return sum(self.dependencies_met.values()) / len(self.dependencies_met)
    
    def get_comprehensive_quality_score(self) -> float:
        """Get comprehensive quality score from quality report if available"""
        if self.quality_report:
            return self.quality_report.overall_score
        return self.quality_score

@dataclass 
class RequestIntent:
    """Analyzed user request intent"""
    primary_action: str  # "analyze", "execute", "quality", "workflow"
    required_agents: Set[str]  # Agents that must run
    optional_agents: Set[str]  # Agents that could be useful
    execution_order: List[str]  # Optimal execution order
    parallel_groups: List[Set[str]]  # Agents that can run in parallel
    information_flow: Dict[str, List[str]]  # What info flows between agents
    confidence: float = 0.0  # Confidence in this analysis

class RequestAnalyzer:
    """Analyzes user requests to determine optimal agent execution strategy"""
    
    # Agent capabilities and when to use them
    AGENT_CAPABILITIES = {
        'planning': {
            'keywords': ['analyze', 'plan', 'complexity', 'think', 'strategy', 'breakdown'],
            'outputs': ['task_analysis', 'complexity_scores', 'subtasks', 'recommendations'],
            'dependencies': [],
            'provides_for': ['execution', 'quality', 'coordinator']
        },
        'execution': {
            'keywords': ['execute', 'implement', 'run', 'build', 'code', 'develop'],
            'outputs': ['code_changes', 'implementations', 'test_results'],
            'dependencies': ['planning'],
            'provides_for': ['quality']
        },
        'quality': {
            'keywords': ['test', 'lint', 'quality', 'check', 'verify', 'validate'],
            'outputs': ['quality_report', 'test_results', 'lint_results'],
            'dependencies': ['execution'],
            'provides_for': []
        },
        'coordinator': {
            'keywords': ['coordinate', 'sync', 'manage', 'orchestrate'],
            'outputs': ['coordination_status', 'sync_results'],
            'dependencies': [],
            'provides_for': ['planning', 'execution', 'quality']
        },
        'repo': {
            'keywords': ['repo', 'files', 'structure', 'organize'],
            'outputs': ['file_structure', 'repo_status'],
            'dependencies': [],
            'provides_for': ['planning', 'execution']
        }
    }
    
    def analyze_request(self, command: str, args: Dict[str, Any]) -> RequestIntent:
        """Analyze user request to determine optimal execution strategy"""
        primary_action = command
        required_agents = set()
        optional_agents = set()
        
        # Determine required agents based on command
        if command == 'analyze':
            required_agents.add('planning')
            if args.get('complexity', True):
                optional_agents.add('repo')  # For better analysis context
                
        elif command == 'execute':
            required_agents.update(['planning', 'execution'])
            optional_agents.add('quality')  # Quality check after execution
            
        elif command == 'quality':
            required_agents.add('quality')
            if not args.get('skip_analysis', False):
                optional_agents.add('planning')  # For context
                
        elif command == 'workflow':
            workflow_type = args.get('type', 'full-dev')
            if workflow_type == 'full-dev':
                required_agents.update(['planning', 'execution', 'quality'])
                optional_agents.add('repo')
            elif workflow_type == 'planning':
                required_agents.update(['planning', 'coordinator'])
                optional_agents.add('repo')
            elif workflow_type == 'quick-fix':
                required_agents.update(['execution', 'quality'])
                
        # Create execution order based on dependencies
        execution_order = self._create_execution_order(required_agents | optional_agents)
        
        # Identify parallel execution opportunities
        parallel_groups = self._identify_parallel_groups(required_agents | optional_agents)
        
        # Map information flow
        information_flow = self._map_information_flow(required_agents | optional_agents)
        
        return RequestIntent(
            primary_action=primary_action,
            required_agents=required_agents,
            optional_agents=optional_agents,
            execution_order=execution_order,
            parallel_groups=parallel_groups,
            information_flow=information_flow,
            confidence=0.9  # High confidence in analysis
        )
    
    def _create_execution_order(self, agents: Set[str]) -> List[str]:
        """Create optimal execution order based on dependencies"""
        order = []
        remaining = agents.copy()
        
        while remaining:
            # Find agents with no unmet dependencies
            ready = []
            for agent in remaining:
                deps = set(self.AGENT_CAPABILITIES[agent]['dependencies'])
                if deps.issubset(set(order)) or not deps:
                    ready.append(agent)
            
            if not ready:
                # Break dependency cycles by adding remaining agents
                ready = list(remaining)
            
            # Add ready agents to order
            for agent in ready:
                order.append(agent)
                remaining.remove(agent)
        
        return order
    
    def _identify_parallel_groups(self, agents: Set[str]) -> List[Set[str]]:
        """Identify agents that can run in parallel"""
        groups = []
        processed = set()
        
        for agent in agents:
            if agent in processed:
                continue
                
            # Find agents with same dependency level
            deps = set(self.AGENT_CAPABILITIES[agent]['dependencies'])
            parallel_group = {agent}
            
            for other_agent in agents:
                if other_agent != agent and other_agent not in processed:
                    other_deps = set(self.AGENT_CAPABILITIES[other_agent]['dependencies'])
                    if deps == other_deps:  # Same dependencies = can run in parallel
                        parallel_group.add(other_agent)
            
            if len(parallel_group) > 1:
                groups.append(parallel_group)
                processed.update(parallel_group)
            else:
                processed.add(agent)
        
        return groups
    
    def _map_information_flow(self, agents: Set[str]) -> Dict[str, List[str]]:
        """Map what information flows between agents"""
        flow = {}
        
        for agent in agents:
            provides_for = self.AGENT_CAPABILITIES[agent]['provides_for']
            flow[agent] = [target for target in provides_for if target in agents]
        
        return flow

class InformationFilter:
    """Filters and routes information between agents"""
    
    def filter_for_agent(self, result: EnhancedAgentResult, target_agent: str) -> Dict[str, Any]:
        """Filter agent result for specific target agent"""
        if target_agent == 'planning':
            return {
                'context': result.output[:500],  # Summary for context
                'quality_indicators': result.quality_score,
                'confidence': result.confidence_score
            }
        elif target_agent == 'execution':
            return {
                'analysis_results': result.filtered_output.get('analysis', {}),
                'complexity_scores': result.filtered_output.get('complexity', {}),
                'recommended_approach': result.filtered_output.get('recommendations', [])
            }
        elif target_agent == 'quality':
            return {
                'implementation_results': result.filtered_output.get('implementations', []),
                'test_results': result.filtered_output.get('tests', {}),
                'code_changes': result.filtered_output.get('changes', [])
            }
        else:
            return {
                'summary': result.output[:200],
                'success': result.success,
                'quality': result.quality_score
            }
    
    def extract_structured_output(self, agent_name: str, raw_output: str) -> Dict[str, Any]:
        """Extract structured information from agent output"""
        structured = {}
        
        # Simple extraction based on common patterns
        if 'analysis' in agent_name:
            structured['analysis'] = self._extract_analysis_data(raw_output)
        elif 'execution' in agent_name:
            structured['implementations'] = self._extract_implementation_data(raw_output)
        elif 'quality' in agent_name:
            structured['quality_results'] = self._extract_quality_data(raw_output)
            
        return structured
    
    def _extract_analysis_data(self, output: str) -> Dict[str, Any]:
        """Extract analysis data from planning agent output"""
        return {
            'complexity_mentioned': 'complexity' in output.lower(),
            'tasks_found': output.count('task'),
            'recommendations_found': output.count('recommend')
        }
    
    def _extract_implementation_data(self, output: str) -> Dict[str, Any]:
        """Extract implementation data from execution agent output"""
        return {
            'files_mentioned': output.count('.py') + output.count('.js'),
            'tests_run': 'test' in output.lower(),
            'errors_found': 'error' in output.lower()
        }
    
    def _extract_quality_data(self, output: str) -> Dict[str, Any]:
        """Extract quality data from quality agent output"""
        return {
            'issues_found': output.count('issue') + output.count('error'),
            'tests_passed': 'passed' in output.lower(),
            'lint_clean': 'lint' in output.lower() and 'error' not in output.lower()
        }

class MasterAgent:
    """Enhanced master orchestrator with intelligent agent selection"""
    
    def __init__(self):
        self.agent_dir = AGENT_DIR
        self.config_dir = Path(__file__).parent / "config"
        self.scripts_dir = Path(__file__).parent / "scripts"
        
        # Initialize dynamic agent registry
        if DYNAMIC_REGISTRY_AVAILABLE:
            self.registry = AgentRegistry()
            self.registry.refresh_registry()  # Ensure we have latest agents
            # Build agents dict from registry
            self.agents = {
                agent.name: f"{agent.name}.py" 
                for agent in self.registry.agents.values()
            }
        else:
            # Fallback to static agent list
            self.registry = None
            self.agents = {
                'planning': 'planning-analysis-agent.py',
                'execution': 'universal-execution-agent.py',
                'quality': 'quality-git-agent.py',
                'coordinator': 'agent-coordinator.py',
                'repo': 'repo-manager-agent.py',
                # Also add the actual names so they can be called directly
                'planning-analysis-agent': 'planning-analysis-agent.py',
                'universal-execution-agent': 'universal-execution-agent.py',
                'quality-git-agent': 'quality-git-agent.py',
                'agent-coordinator': 'agent-coordinator.py',
                'repo-manager-agent': 'repo-manager-agent.py',
                'task-complexity-agent': 'task-complexity-agent.py',
                'intelligent-task-agent': 'intelligent-task-agent.py',
                'universal-dev-agent': 'universal-dev-agent.py'
            }
        
        self.analyzer = RequestAnalyzer()
        self.filter = InformationFilter()
        
        # Initialize quality assessment engine if available
        if QUALITY_ASSESSMENT_AVAILABLE:
            self.quality_engine = QualityAssessmentEngine(self.agent_dir.parent)
        else:
            self.quality_engine = None
        
    def run_agent_enhanced(self, agent_name: str, args: List[str], 
                          context: Dict[str, Any] = None) -> EnhancedAgentResult:
        """Run a specific agent with enhanced result tracking"""
        if agent_name not in self.agents:
            return EnhancedAgentResult(
                agent_name=agent_name,
                success=False,
                output="",
                duration=0,
                error=f"Unknown agent: {agent_name}"
            )
        
        agent_script = self.agent_dir / self.agents[agent_name]
        if not agent_script.exists():
            return EnhancedAgentResult(
                agent_name=agent_name,
                success=False,
                output="",
                duration=0,
                error=f"Agent script not found: {agent_script}"
            )
        
        start_time = time.time()
        try:
            # Check if we should use TaskMaster wrapper
            use_taskmaster = False
            task_id = None
            
            # Extract task ID from args
            for i, arg in enumerate(args):
                if arg == "--task-id" and i + 1 < len(args):
                    task_id = args[i + 1]
                    use_taskmaster = True
                    break
            
            # Check for TaskMaster environment variable
            if not task_id and os.environ.get("TASKMASTER_TASK_ID"):
                task_id = os.environ.get("TASKMASTER_TASK_ID")
                use_taskmaster = True
            
            # Check if .taskmaster/tasks/tasks.json exists
            taskmaster_file = self.agent_dir.parent / ".taskmaster" / "tasks" / "tasks.json"
            if taskmaster_file.exists() and use_taskmaster:
                # Use TaskMaster wrapper
                wrapper_script = self.agent_dir.parent / "taskmaster_agent_wrapper.py"
                if wrapper_script.exists():
                    cmd = ["python3", str(wrapper_script), agent_name]
                    if task_id:
                        cmd.extend(["--task-id", task_id])
                    print(f"   🔄 Executing with TaskMaster: {agent_name} (task: {task_id})")
                else:
                    # Fallback to direct execution
                    cmd = ["python3", str(agent_script)] + args
                    print(f"   🔄 Executing: {' '.join(cmd[:3])}... {' '.join(args[-2:]) if len(args) > 2 else ''}")
            else:
                # Direct execution without TaskMaster
                cmd = ["python3", str(agent_script)] + args
                print(f"   🔄 Executing: {' '.join(cmd[:3])}... {' '.join(args[-2:]) if len(args) > 2 else ''}")
            
            # Prepare environment with context
            env = os.environ.copy()
            if context:
                env["AGENT_CONTEXT"] = json.dumps(context)
            if task_id:
                env["TASKMASTER_TASK_ID"] = task_id
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
                cwd=self.agent_dir.parent,  # Ensure correct working directory
                env=env
            )
            
            duration = time.time() - start_time
            success = result.returncode == 0
            
            # Calculate basic quality and confidence scores (fallback)
            basic_quality_score = self._calculate_quality_score(result.stdout, success)
            confidence_score = self._calculate_confidence_score(result.stdout, success)
            
            # Extract structured output
            filtered_output = self.filter.extract_structured_output(agent_name, result.stdout)
            
            # Determine what this agent provides for
            capabilities = self.analyzer.AGENT_CAPABILITIES.get(agent_name, {})
            provides_for = capabilities.get('provides_for', [])
            
            # Calculate dependency satisfaction
            dependencies_met = self._calculate_dependencies_met(agent_name, context or {})
            
            # Perform comprehensive quality assessment if available
            quality_report = None
            final_quality_score = basic_quality_score
            
            if self.quality_engine and success:
                try:
                    request_context = context.get('request_context', '') if context else ''
                    result_context = {
                        'success': success,
                        'duration': duration,
                        'request_type': context.get('command', 'unknown') if context else 'unknown'
                    }
                    
                    quality_report = self.quality_engine.assess_agent_output(
                        agent_name, result.stdout, request_context, result_context
                    )
                    final_quality_score = quality_report.overall_score
                    
                    print(f"   🔍 Quality Assessment: {final_quality_score:.1%} overall")
                    if quality_report.critical_issues:
                        print(f"   ⚠️  Critical Issues: {len(quality_report.critical_issues)}")
                    
                except Exception as e:
                    print(f"   ⚠️  Quality assessment failed: {e}")
                    # Fall back to basic scoring
            
            return EnhancedAgentResult(
                agent_name=agent_name,
                success=success,
                output=result.stdout,
                duration=duration,
                confidence_score=confidence_score,
                quality_score=final_quality_score,
                dependencies_met=dependencies_met,
                provides_for=provides_for,
                information_quality=self._assess_information_quality(result.stdout),
                filtered_output=filtered_output,
                quality_report=quality_report,
                error=result.stderr if not success else None
            )
            
        except subprocess.TimeoutExpired:
            return EnhancedAgentResult(
                agent_name=agent_name,
                success=False,
                output="",
                duration=time.time() - start_time,
                error="Agent timed out after 5 minutes"
            )
        except Exception as e:
            return EnhancedAgentResult(
                agent_name=agent_name,
                success=False,
                output="",
                duration=time.time() - start_time,
                error=str(e)
            )
    
    def _calculate_quality_score(self, output: str, success: bool) -> float:
        """Calculate quality score based on output characteristics"""
        if not success:
            return 0.0
        
        score = 0.5  # Base score for success
        
        # Boost score based on output quality indicators
        if len(output) > 100:  # Substantial output
            score += 0.2
        if 'completed' in output.lower() or 'success' in output.lower():
            score += 0.2
        if output.count('\n') > 10:  # Detailed output
            score += 0.1
        
        return min(1.0, score)
    
    def _calculate_confidence_score(self, output: str, success: bool) -> float:
        """Calculate confidence score based on output analysis"""
        if not success:
            return 0.0
        
        confidence = 0.7  # Base confidence
        
        # Adjust based on uncertainty indicators
        uncertainty_words = ['maybe', 'might', 'could', 'uncertain', 'unclear']
        for word in uncertainty_words:
            if word in output.lower():
                confidence -= 0.1
        
        # Boost for definitive language
        definitive_words = ['completed', 'finished', 'success', 'done']
        for word in definitive_words:
            if word in output.lower():
                confidence += 0.1
        
        return max(0.0, min(1.0, confidence))
    
    def _calculate_dependencies_met(self, agent_name: str, context: Dict[str, Any]) -> Dict[str, float]:
        """Calculate how well dependencies were satisfied"""
        capabilities = self.analyzer.AGENT_CAPABILITIES.get(agent_name, {})
        dependencies = capabilities.get('dependencies', [])
        
        if not dependencies:
            return {}  # No dependencies to check
        
        deps_met = {}
        for dep in dependencies:
            if dep in context:
                # Score based on previous agent success and quality
                agent_context = context[dep]
                success_score = 1.0 if agent_context.get('success', False) else 0.0
                quality_score = agent_context.get('quality_score', 0.0)
                confidence_score = agent_context.get('confidence_score', 0.0)
                
                # Weighted average of different scores
                overall_score = (success_score * 0.5 + quality_score * 0.3 + confidence_score * 0.2)
                deps_met[dep] = max(0.0, min(1.0, overall_score))
            else:
                # Check if dependency is optional or critical
                if dep in ['repo']:  # repo agent is often optional
                    deps_met[dep] = 0.5  # Partial score for optional deps
                else:
                    deps_met[dep] = 0.0  # Dependency not met
        
        return deps_met
    
    def _assess_information_quality(self, output: str) -> str:
        """Assess the quality of information in output"""
        if len(output) < 50:
            return "low"
        elif len(output) > 500 and output.count('\n') > 5:
            return "high"
        else:
            return "medium"
    
    # Legacy methods for backward compatibility - now use smart workflow
    def analyze_project(self, tag: Optional[str] = None, complexity: bool = True) -> List[EnhancedAgentResult]:
        """Run planning and analysis (legacy wrapper)"""
        args = {'tag': tag, 'complexity': complexity}
        return self.run_smart_workflow('analyze', args)
    
    def execute_task(self, task_id: Optional[str] = None, auto_mode: bool = False) -> List[EnhancedAgentResult]:
        """Run task execution (legacy wrapper)"""
        args = {'task_id': task_id, 'auto': auto_mode}
        return self.run_smart_workflow('execute', args)
    
    def quality_check(self, fix_issues: bool = False) -> List[EnhancedAgentResult]:
        """Run quality and git operations (legacy wrapper)"""
        args = {'fix': fix_issues}
        return self.run_smart_workflow('quality', args)
    
    def run_smart_workflow(self, command: str, args: Dict[str, Any]) -> List[EnhancedAgentResult]:
        """Run intelligent workflow with dynamic agent selection"""
        
        # Step 1: Analyze the request
        print(f"🧠 Analyzing request: {command}")
        intent = self.analyzer.analyze_request(command, args)
        
        print(f"📋 Request Analysis:")
        print(f"   Required agents: {', '.join(intent.required_agents)}")
        print(f"   Optional agents: {', '.join(intent.optional_agents)}")
        print(f"   Execution order: {' → '.join(intent.execution_order)}")
        print(f"   Confidence: {intent.confidence:.1%}")
        
        # Step 2: Execute agents intelligently
        results = []
        context = {}
        
        print(f"\n🚀 Starting smart workflow execution...\n")
        
        # Check for parallel execution opportunities
        if intent.parallel_groups:
            print("⚡ Parallel execution opportunities detected")
            for group in intent.parallel_groups:
                if len(group) > 1:
                    print(f"   Running in parallel: {', '.join(group)}")
                    parallel_results = self._run_agents_parallel(list(group), args, context)
                    results.extend(parallel_results)
                    
                    # Update context with results
                    for result in parallel_results:
                        context[result.agent_name] = {
                            'success': result.success,
                            'quality_score': result.quality_score,
                            'filtered_data': self.filter.filter_for_agent(result, 'any')
                        }
        
        # Run remaining agents in dependency order
        remaining_agents = set(intent.execution_order) - {r.agent_name for r in results}
        
        for agent_name in intent.execution_order:
            if agent_name not in remaining_agents:
                continue
                
            print(f"🔄 Running {agent_name} agent...")
            
            # Determine arguments based on request and context
            agent_args = self._build_agent_args(agent_name, args, context)
            
            # Run the agent with context
            result = self.run_agent_enhanced(agent_name, agent_args, context)
            results.append(result)
            
            # Update context for next agents
            context[agent_name] = {
                'success': result.success,
                'quality_score': result.quality_score,
                'confidence_score': result.confidence_score,
                'dependency_score': result.get_dependency_score(),
                'filtered_data': self.filter.filter_for_agent(result, 'any')
            }
            
            # Show progress
            status_icon = "✅" if result.success else "❌"
            print(f"   {status_icon} {agent_name}: {result.information_quality} quality, "
                  f"{result.confidence_score:.1%} confidence, "
                  f"{result.get_dependency_score():.1%} dependencies met")
            
            # Early termination on critical failures
            if not result.success and agent_name in intent.required_agents:
                print(f"⚠️  Critical agent {agent_name} failed, stopping workflow")
                break
        
        return results
    
    def find_agents_for_task(self, task_description: str, workflow_type: Optional[str] = None) -> List[str]:
        """Dynamically find best agents for a given task using registry"""
        if not self.registry:
            # Fallback to static workflow mapping
            workflow_map = {
                'analyze': ['planning'],
                'execute': ['execution'],
                'quality': ['quality'],
                'full-dev': ['planning', 'execution', 'quality'],
                'planning': ['planning', 'coordinator'],
                'quick-fix': ['execution', 'quality']
            }
            return workflow_map.get(workflow_type, ['execution'])
        
        # Use registry to find optimal agents
        if workflow_type:
            # Get agents for specific workflow type
            workflow_agents = self.registry.get_workflow_agents(workflow_type)
            return [agent.name for agent in workflow_agents]
        else:
            # Find agents based on task description
            suitable_agents = self.registry.find_agents_for_task(task_description)
            return [agent.name for agent in suitable_agents[:3]]  # Top 3 matches
    
    def get_available_agents(self) -> Dict[str, Dict[str, Any]]:
        """Get information about all available agents"""
        agent_info = {}
        
        if self.registry:
            for agent_name, metadata in self.registry.agents.items():
                agent_info[agent_name] = {
                    'type': metadata.type,
                    'description': metadata.description,
                    'capabilities': metadata.capabilities.keywords,
                    'thinking_patterns': metadata.capabilities.thinking_patterns,
                    'template_source': metadata.template_source,
                    'file_path': str(metadata.file_path)
                }
        else:
            # Fallback info for static agents
            for agent_name, script in self.agents.items():
                agent_info[agent_name] = {
                    'type': agent_name,
                    'description': f"Static {agent_name} agent",
                    'capabilities': [agent_name],
                    'thinking_patterns': [],
                    'template_source': None,
                    'file_path': str(self.agent_dir / script)
                }
        
        return agent_info
    
    def refresh_agents(self) -> None:
        """Refresh the agent registry and update available agents"""
        if self.registry:
            self.registry.refresh_registry()
            # Rebuild agents dict
            self.agents = {
                agent.name: f"{agent.name}.py" 
                for agent in self.registry.agents.values()
            }
            print(f"🔄 Refreshed agent registry: {len(self.agents)} agents available")
        else:
            print("⚠️  Dynamic registry not available, using static agent list")
    
    def _run_agents_parallel(self, agent_names: List[str], args: Dict[str, Any], 
                           context: Dict[str, Any]) -> List[EnhancedAgentResult]:
        """Run multiple agents in parallel"""
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(agent_names)) as executor:
            futures = {}
            
            for agent_name in agent_names:
                agent_args = self._build_agent_args(agent_name, args, context)
                future = executor.submit(self.run_agent_enhanced, agent_name, agent_args, context)
                futures[future] = agent_name
            
            results = []
            for future in concurrent.futures.as_completed(futures):
                agent_name = futures[future]
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    # Create error result
                    error_result = EnhancedAgentResult(
                        agent_name=agent_name,
                        success=False,
                        output="",
                        duration=0,
                        error=f"Parallel execution error: {str(e)}"
                    )
                    results.append(error_result)
        
        return results
    
    def _build_agent_args(self, agent_name: str, request_args: Dict[str, Any], 
                         context: Dict[str, Any]) -> List[str]:
        """Build arguments for specific agent based on request and context"""
        args = ["--verbose"]
        
        # Add agent-specific arguments
        if agent_name == 'planning':
            if request_args.get('tag'):
                args.extend(['--tag', request_args['tag']])
            if not request_args.get('complexity', True):
                args.append('--no-complexity')
                
        elif agent_name == 'execution':
            if request_args.get('task_id'):
                args.extend(['--task-id', request_args['task_id']])
            if request_args.get('auto'):
                args.append('--auto')
                
        elif agent_name == 'quality':
            if request_args.get('fix'):
                args.append('--fix')
                
        elif agent_name == 'coordinator':
            workflow_type = request_args.get('type', 'default')
            args.extend(['--workflow', workflow_type])
            
        elif agent_name == 'repo':
            action = request_args.get('action', 'sync')
            args.extend(['--action', action])
        
        return args
    
    def show_status(self) -> Dict[str, Any]:
        """Show system status"""
        status = {
            "system": "Task Master Agent System",
            "agents": {},
            "directories": {
                "agents": str(self.agent_dir),
                "config": str(self.config_dir),
                "scripts": str(self.scripts_dir)
            }
        }
        
        # Check agent availability
        for name, script in self.agents.items():
            agent_path = self.agent_dir / script
            status["agents"][name] = {
                "script": script,
                "available": agent_path.exists(),
                "executable": agent_path.exists() and os.access(agent_path, os.X_OK)
            }
        
        return status
    
    def system_health_check(self) -> Dict[str, Any]:
        """Perform comprehensive system health check"""
        health = {
            "overall_status": "healthy",
            "agents": {},
            "dependencies": {},
            "recommendations": []
        }
        
        # Check agent availability and basic functionality
        for name, script in self.agents.items():
            agent_path = self.agent_dir / script
            agent_health = {
                "exists": agent_path.exists(),
                "executable": agent_path.is_file() and os.access(agent_path, os.X_OK),
                "help_accessible": False
            }
            
            # Test basic functionality
            if agent_health["executable"]:
                try:
                    result = subprocess.run(
                        ["python3", str(agent_path), "--help"],
                        capture_output=True,
                        text=True,
                        timeout=10,
                        cwd=self.agent_dir.parent
                    )
                    agent_health["help_accessible"] = result.returncode == 0
                except:
                    agent_health["help_accessible"] = False
            
            health["agents"][name] = agent_health
            
            # Generate recommendations
            if not agent_health["exists"]:
                health["recommendations"].append(f"Missing agent script: {script}")
            elif not agent_health["executable"]:
                health["recommendations"].append(f"Agent not executable: {script}")
            elif not agent_health["help_accessible"]:
                health["recommendations"].append(f"Agent {name} may have issues")
        
        # Check Python dependencies
        try:
            import requests
            health["dependencies"]["requests"] = "available"
        except ImportError:
            health["dependencies"]["requests"] = "missing"
            health["recommendations"].append("Install requests: pip install requests")
        
        # Determine overall status
        agent_issues = sum(1 for a in health["agents"].values() 
                          if not (a["exists"] and a["executable"]))
        if agent_issues > 0:
            health["overall_status"] = "degraded" if agent_issues < 3 else "unhealthy"
        
        return health
    
    def print_enhanced_results(self, results: List[EnhancedAgentResult]):
        """Print enhanced formatted results with dependency scoring"""
        print("\n" + "="*80)
        print("ENHANCED WORKFLOW RESULTS")
        print("="*80)
        
        total_duration = sum(r.duration for r in results)
        successful = sum(1 for r in results if r.success)
        avg_quality = sum(r.quality_score for r in results) / len(results) if results else 0
        avg_confidence = sum(r.confidence_score for r in results) / len(results) if results else 0
        
        print(f"📊 Summary:")
        print(f"   Total Agents Run: {len(results)}")
        print(f"   Successful: {successful} | Failed: {len(results) - successful}")
        print(f"   Total Duration: {total_duration:.1f}s")
        print(f"   Average Quality Score: {avg_quality:.1%}")
        print(f"   Average Confidence: {avg_confidence:.1%}")
        print()
        
        print(f"🔍 Agent Details:")
        for result in results:
            status_icon = "✅" if result.success else "❌"
            quality_score = result.get_comprehensive_quality_score()
            quality_bar = self._create_progress_bar(quality_score)
            confidence_bar = self._create_progress_bar(result.confidence_score)
            dependency_bar = self._create_progress_bar(result.get_dependency_score())
            
            print(f"{status_icon} {result.agent_name.upper()}")
            print(f"   ⏱️  Duration: {result.duration:.1f}s")
            print(f"   🎯 Quality: {quality_bar} {quality_score:.1%}")
            print(f"   🔮 Confidence: {confidence_bar} {result.confidence_score:.1%}")
            print(f"   🔗 Dependencies: {dependency_bar} {result.get_dependency_score():.1%}")
            print(f"   📈 Info Quality: {result.information_quality}")
            
            # Show comprehensive quality details if available
            if result.quality_report:
                self._print_quality_report_summary(result.quality_report)
            
            if result.provides_for:
                print(f"   📤 Provides for: {', '.join(result.provides_for)}")
            
            if result.dependencies_met:
                print(f"   📥 Dependencies met:")
                for dep, score in result.dependencies_met.items():
                    dep_bar = self._create_progress_bar(score)
                    print(f"      {dep}: {dep_bar} {score:.1%}")
            
            if result.error:
                print(f"   ❌ Error: {result.error}")
                # Provide troubleshooting hints
                if "unrecognized arguments" in result.error:
                    print(f"   💡 Hint: Agent may need argument compatibility updates")
                elif "No such file" in result.error:
                    print(f"   💡 Hint: Check agent script paths and file permissions")
                elif "timeout" in result.error.lower():
                    print(f"   💡 Hint: Agent execution took too long, consider optimization")
                elif "permission denied" in result.error.lower():
                    print(f"   💡 Hint: Check file permissions and execution rights")
            elif result.output:
                # Show first few lines of output
                output_lines = result.output.strip().split('\n')
                preview_lines = output_lines[:2]
                for line in preview_lines:
                    if line.strip():
                        print(f"   📝 {line[:70]}{'...' if len(line) > 70 else ''}")
                if len(output_lines) > 2:
                    print(f"   📜 ... ({len(output_lines) - 2} more lines)")
            print()
    
    def _print_quality_report_summary(self, report: 'QualityReport'):
        """Print a summary of the quality assessment report"""
        print(f"   🔬 Quality Assessment:")
        
        # Show top quality metrics
        sorted_metrics = sorted(report.metrics.items(), 
                               key=lambda x: x[1].score, reverse=True)
        
        for dimension, metric in sorted_metrics[:3]:  # Top 3 dimensions
            metric_bar = self._create_progress_bar(metric.score)
            dimension_name = dimension.value.replace('_', ' ').title()
            print(f"      {dimension_name}: {metric_bar} {metric.score:.1%}")
        
        # Show issues summary
        if report.critical_issues:
            print(f"      🚨 Critical: {len(report.critical_issues)} issues")
        if report.blockers:
            print(f"      🛑 Blockers: {len(report.blockers)} issues")
        if report.warnings:
            print(f"      ⚠️  Warnings: {len(report.warnings)} issues")
        
        # Show top recommendation
        if report.recommendations:
            print(f"      💡 Key Rec: {report.recommendations[0][:50]}...")
    
    def show_detailed_quality_report(self, result: EnhancedAgentResult):
        """Show detailed quality assessment report"""
        if not result.quality_report:
            print("No detailed quality report available")
            return
        
        report = result.quality_report
        print(f"\n{'='*80}")
        print(f"DETAILED QUALITY REPORT - {result.agent_name.upper()}")
        print(f"{'='*80}")
        
        print(f"📊 Overall Score: {report.overall_score:.1%} (Confidence: {report.confidence:.1%})")
        print()
        
        # Quality dimensions
        print("🎯 Quality Dimensions:")
        for dimension, metric in report.metrics.items():
            dimension_name = dimension.value.replace('_', ' ').title()
            quality_bar = self._create_progress_bar(metric.score)
            confidence_bar = self._create_progress_bar(metric.confidence)
            
            print(f"   {dimension_name}:")
            print(f"      Score: {quality_bar} {metric.score:.1%}")
            print(f"      Confidence: {confidence_bar} {metric.confidence:.1%}")
            
            if metric.evidence:
                print(f"      ✅ Evidence: {'; '.join(metric.evidence[:2])}")
            if metric.issues:
                print(f"      ⚠️  Issues: {'; '.join(metric.issues[:2])}")
            if metric.recommendations:
                print(f"      💡 Recommendations: {'; '.join(metric.recommendations[:1])}")
            print()
        
        # Issues breakdown
        if report.critical_issues or report.blockers or report.warnings:
            print("🚨 Issues Found:")
            if report.critical_issues:
                print(f"   Critical Issues ({len(report.critical_issues)}):")
                for issue in report.critical_issues[:3]:
                    print(f"      🔴 {issue}")
            
            if report.blockers:
                print(f"   Blockers ({len(report.blockers)}):")
                for issue in report.blockers[:3]:
                    print(f"      🟠 {issue}")
            
            if report.warnings:
                print(f"   Warnings ({len(report.warnings)}):")
                for issue in report.warnings[:3]:
                    print(f"      🟡 {issue}")
            print()
        
        # Recommendations
        if report.recommendations:
            print("💡 Key Recommendations:")
            for i, rec in enumerate(report.recommendations[:5], 1):
                print(f"   {i}. {rec}")
            print()
    
    def _create_progress_bar(self, score: float, width: int = 10) -> str:
        """Create a visual progress bar for scores"""
        filled = int(score * width)
        bar = "█" * filled + "░" * (width - filled)
        return f"[{bar}]"

def main():
    parser = argparse.ArgumentParser(
        description="Task Master Agent System - Master Orchestrator",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Analyze command
    analyze_parser = subparsers.add_parser('analyze', help='Run planning and analysis')
    analyze_parser.add_argument('--tag', help='Task tag to analyze')
    analyze_parser.add_argument('--no-complexity', action='store_true', help='Skip complexity analysis')
    
    # Execute command
    execute_parser = subparsers.add_parser('execute', help='Run task execution')
    execute_parser.add_argument('--task-id', help='Specific task ID to execute')
    execute_parser.add_argument('--auto', action='store_true', help='Auto mode execution')
    
    # Quality command
    quality_parser = subparsers.add_parser('quality', help='Run quality checks')
    quality_parser.add_argument('--fix', action='store_true', help='Auto-fix issues')
    
    # Workflow command
    workflow_parser = subparsers.add_parser('workflow', help='Run complete workflow')
    workflow_parser.add_argument('--type', 
                                choices=[wf.value for wf in WorkflowType],
                                default='full-dev',
                                help='Workflow type to run')
    workflow_parser.add_argument('--tag', help='Task tag for workflow')
    workflow_parser.add_argument('--task-id', help='Task ID for workflow')
    workflow_parser.add_argument('--auto', action='store_true', help='Auto mode')
    workflow_parser.add_argument('--fix', action='store_true', help='Auto-fix issues')
    
    # Status command
    subparsers.add_parser('status', help='Show system status')
    
    # Agent command (run specific agent) - now dynamic
    agent_parser = subparsers.add_parser('agent', help='Run specific agent')
    agent_parser.add_argument('name', help='Agent name to run')
    agent_parser.add_argument('args', nargs='*', help='Arguments to pass to agent')
    
    # List agents command  
    list_parser = subparsers.add_parser('list-agents', help='List all available agents')
    list_parser.add_argument('--verbose', action='store_true', help='Show detailed agent information')
    
    # Refresh agents command
    subparsers.add_parser('refresh-agents', help='Refresh agent registry')
    
    # Create agent command (integrated with factory)
    create_parser = subparsers.add_parser('create-agent', help='Create new agent using factory')
    create_parser.add_argument('--name', required=True, help='Agent name')
    create_parser.add_argument('--type', required=True, 
                              choices=['planning', 'execution', 'quality', 'coordination', 'custom'],
                              help='Agent template type')
    create_parser.add_argument('--description', help='Agent description')
    create_parser.add_argument('--interactive', action='store_true', help='Interactive creation')
    
    # Find agents command
    find_parser = subparsers.add_parser('find-agents', help='Find agents for specific task')
    find_parser.add_argument('task', help='Task description')
    find_parser.add_argument('--type', help='Preferred workflow type')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    master = MasterAgent()
    
    if args.command == 'status':
        status = master.show_status()
        print(json.dumps(status, indent=2))
        
    elif args.command == 'analyze':
        request_args = {
            'tag': args.tag,
            'complexity': not args.no_complexity
        }
        results = master.run_smart_workflow('analyze', request_args)
        master.print_enhanced_results(results)
        
    elif args.command == 'execute':
        request_args = {
            'task_id': args.task_id,
            'auto': args.auto
        }
        results = master.run_smart_workflow('execute', request_args)
        master.print_enhanced_results(results)
        
    elif args.command == 'quality':
        request_args = {
            'fix': args.fix
        }
        results = master.run_smart_workflow('quality', request_args)
        master.print_enhanced_results(results)
        
    elif args.command == 'workflow':
        request_args = {
            'type': args.type,
            'tag': args.tag,
            'task_id': args.task_id,
            'auto': args.auto,
            'fix': args.fix
        }
        results = master.run_smart_workflow('workflow', request_args)
        master.print_enhanced_results(results)
        
    elif args.command == 'agent':
        # For direct agent calls, use enhanced execution
        result = master.run_agent_enhanced(args.name, args.args)
        master.print_enhanced_results([result])
        
    elif args.command == 'list-agents':
        # List all available agents
        agent_info = master.get_available_agents()
        print(f"📋 Available Agents ({len(agent_info)} total)")
        print("=" * 60)
        
        agents_by_type = {}
        for name, info in agent_info.items():
            agent_type = info['type']
            if agent_type not in agents_by_type:
                agents_by_type[agent_type] = []
            agents_by_type[agent_type].append((name, info))
        
        for agent_type, agents in agents_by_type.items():
            print(f"\n🤖 {agent_type.upper()} AGENTS ({len(agents)})")
            print("-" * 40)
            
            for name, info in agents:
                print(f"   📄 {name}")
                if args.verbose:
                    print(f"      Description: {info['description']}")
                    print(f"      Capabilities: {', '.join(info['capabilities'])}")
                    if info['template_source']:
                        print(f"      Template: {info['template_source']}")
                    print(f"      Usage: ./master-agent.py agent {name} [args...]")
    
    elif args.command == 'refresh-agents':
        # Refresh agent registry
        master.refresh_agents()
        
    elif args.command == 'create-agent':
        # Create new agent using factory
        try:
            from agent_factory import AgentFactory
            factory = AgentFactory()
            
            agent_file = factory.create_agent(
                args.name, args.type, args.description, args.interactive
            )
            
            # Refresh master agent registry
            master.refresh_agents()
            
        except ImportError:
            print("❌ Agent factory not available")
        except Exception as e:
            print(f"❌ Error creating agent: {e}")
    
    elif args.command == 'find-agents':
        # Find agents for specific task
        suitable_agents = master.find_agents_for_task(args.task, args.type)
        print(f"🔍 Found {len(suitable_agents)} agents for task: {args.task}")
        
        for i, agent_name in enumerate(suitable_agents, 1):
            agent_info = master.get_available_agents().get(agent_name, {})
            print(f"  {i}. {agent_name} ({agent_info.get('type', 'unknown')})")
            print(f"     {agent_info.get('description', 'No description')}")
            print(f"     Usage: ./master-agent.py agent {agent_name} [args...]")

if __name__ == "__main__":
    main()