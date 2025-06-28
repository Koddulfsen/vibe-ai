#!/usr/bin/env python3
"""
Planning & Analysis Agent

Combines task complexity analysis with intelligent task discovery into a unified agent.
Provides comprehensive project analysis, complexity scoring, and dynamic subtask generation.
"""

import json
import subprocess
import re
import argparse
import sys
import os
import time
from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass, asdict
from pathlib import Path

# Import enhanced planning prompts
try:
    import sys
    import os
    import importlib.util
    
    # Import the enhanced prompts module directly
    current_dir = os.path.dirname(os.path.abspath(__file__))
    module_path = os.path.join(current_dir, "enhanced-planning-prompts.py")
    
    spec = importlib.util.spec_from_file_location("enhanced_planning_prompts", module_path)
    enhanced_prompts_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(enhanced_prompts_module)
    
    # Extract classes from module
    EnhancedPlanningPrompts = enhanced_prompts_module.EnhancedPlanningPrompts
    ImprovementSuggestion = enhanced_prompts_module.ImprovementSuggestion
    ENHANCED_PROMPTS_AVAILABLE = True
except Exception as e:
    ENHANCED_PROMPTS_AVAILABLE = False
    # Debug: uncomment next line to see import error
    # print(f"Enhanced prompts import failed: {e}")

@dataclass
class ComplexityScore:
    """Represents the complexity analysis of a task"""
    total_score: int
    indicators: Dict[str, int]
    recommendation: str
    suggested_subtasks: int
    should_expand: bool

@dataclass 
class GitWorkflowSuggestion:
    """Git workflow suggestion"""
    action: str  # "branch", "commit", "push", "pr"
    description: str
    commands: List[str]
    rationale: str

@dataclass
class TaskAnalysis:
    """Analysis results for a task"""
    missing_files: List[str]
    missing_dependencies: List[str]
    missing_tests: List[str]
    implementation_gaps: List[str]
    discovered_subtasks: List[Dict]
    complexity_score: ComplexityScore
    improvement_suggestions: List[Dict] = None
    innovation_opportunities: List[str] = None
    quality_enhancements: List[str] = None
    implementation_roadmap: List[Dict] = None
    git_workflow_suggestions: List[GitWorkflowSuggestion] = None

@dataclass
class ThoughtStep:
    """Represents a step in sequential thinking process"""
    thought_number: int
    thought: str
    next_thought_needed: bool
    total_thoughts: int
    is_revision: bool = False
    revises_thought: Optional[int] = None
    branch_from_thought: Optional[int] = None
    branch_id: Optional[str] = None
    needs_more_thoughts: bool = False

@dataclass
class SequentialThinkingResult:
    """Result of sequential thinking process"""
    thoughts: List[ThoughtStep]
    final_solution: str
    confidence_score: float
    reasoning_quality: str
    duration: float

class SequentialThinking:
    """Sequential thinking engine for complex problem solving"""
    
    def __init__(self):
        self.thoughts: List[ThoughtStep] = []
        self.start_time: float = 0
        self.branches: Dict[str, List[ThoughtStep]] = {}
    
    def think_through_problem(self, problem: str, initial_estimate: int = 3) -> SequentialThinkingResult:
        """Think through a problem using sequential reasoning"""
        self.start_time = time.time()
        self.thoughts = []
        
        current_thought = 1
        total_thoughts = initial_estimate
        
        print(f"🧠 Starting sequential thinking for: {problem[:100]}...")
        
        while current_thought <= total_thoughts:
            # Safety check to prevent infinite loops
            if current_thought > 20:
                print(f"⚠️ Stopping thinking process at {current_thought} thoughts to prevent infinite loop")
                break
                
            # Generate thought based on previous context
            if current_thought == 1:
                thought_content = self._generate_initial_thought(problem)
            else:
                thought_content = self._generate_next_thought(problem, current_thought)
            
            # Determine if more thoughts are needed (will be False on last iteration)
            next_needed = current_thought < total_thoughts and current_thought < 20
            
            # Create thought step
            thought_step = ThoughtStep(
                thought_number=current_thought,
                thought=thought_content,
                next_thought_needed=next_needed,
                total_thoughts=min(total_thoughts, 20),  # Cap total thoughts
                is_revision=False
            )
            
            self.thoughts.append(thought_step)
            
            # Check if we need to adjust total thoughts (with stricter conditions)
            if current_thought >= 3 and current_thought < 15 and self._should_extend_thinking():
                total_thoughts = min(total_thoughts + 2, 20)  # Cap at 20
                print(f"🔄 Extending thinking process to {total_thoughts} thoughts")
            
            current_thought += 1
        
        # Generate final solution
        final_solution = self._synthesize_solution()
        
        # Calculate metrics
        duration = time.time() - self.start_time
        confidence = self._calculate_confidence()
        quality = self._assess_reasoning_quality()
        
        print(f"✅ Sequential thinking complete ({len(self.thoughts)} thoughts, {duration:.1f}s)")
        
        return SequentialThinkingResult(
            thoughts=self.thoughts,
            final_solution=final_solution,
            confidence_score=confidence,
            reasoning_quality=quality,
            duration=duration
        )
    
    def _generate_initial_thought(self, problem: str) -> str:
        """Generate the first thought about the problem"""
        return f"Looking at this problem: {problem}. I need to break this down systematically. First, let me understand what we're trying to achieve and identify the key components involved."
    
    def _generate_next_thought(self, problem: str, thought_number: int) -> str:
        """Generate the next thought based on previous thoughts"""
        previous_thoughts = [t.thought for t in self.thoughts[-3:]]  # Last 3 thoughts for context
        
        if thought_number == 2:
            return "Now I'll analyze the complexity and dependencies. What are the main challenges and what information do I need to gather?"
        elif thought_number == 3:
            return "Let me consider different approaches and evaluate their trade-offs. What are the pros and cons of each option?"
        elif thought_number == 4:
            return "Based on my analysis, I'll outline a structured approach. What are the specific steps needed to implement this solution?"
        else:
            return f"Continuing analysis from previous thoughts. Let me refine my understanding and consider any edge cases or improvements."
    
    def _should_extend_thinking(self) -> bool:
        """Determine if we need more thoughts"""
        # Add hard limit to prevent infinite loops
        if len(self.thoughts) >= 15:
            return False
            
        # Don't extend if we've already extended multiple times recently
        if len(self.thoughts) >= 10 and len(self.thoughts) % 5 != 0:
            return False
            
        recent_thoughts = [t.thought for t in self.thoughts[-2:]]
        
        # Only extend for specific uncertainty indicators, not common words
        critical_indicators = ['need more analysis', 'insufficient information', 'requires deeper', 'unclear requirements']
        return any(indicator in ' '.join(recent_thoughts).lower() for indicator in critical_indicators)
    
    def _synthesize_solution(self) -> str:
        """Synthesize all thoughts into a final solution"""
        return f"Based on {len(self.thoughts)} thoughts, here's the synthesized solution: A structured approach that incorporates the analysis and considerations from the sequential thinking process."
    
    def _calculate_confidence(self) -> float:
        """Calculate confidence in the solution"""
        base_confidence = 0.7
        thought_bonus = min(len(self.thoughts) * 0.05, 0.25)
        return min(base_confidence + thought_bonus, 0.95)
    
    def _assess_reasoning_quality(self) -> str:
        """Assess the quality of reasoning"""
        if len(self.thoughts) >= 6:
            return "thorough"
        elif len(self.thoughts) >= 4:
            return "good"
        else:
            return "basic"

class PlanningAnalysisAgent:
    """
    Unified Planning & Analysis Agent that combines complexity analysis with intelligent task discovery
    """
    
    def __init__(self, project_root: str = ".", config_path: Optional[str] = None):
        self.project_root = Path(project_root)
        self.src_dir = self.project_root / "src"
        self.package_json = self.project_root / "package.json"
        
        # Load configuration
        self.config = self._load_config(config_path)
        
        # Detect project type first
        self.project_type = self._detect_project_type()
        
        # Initialize analysis components
        self.complexity_indicators = self._get_complexity_indicators()
        self.task_type_patterns = self._get_task_type_patterns()
        self.file_patterns = self._get_file_patterns()
        self.dependency_patterns = self._get_dependency_patterns()
        self.implementation_patterns = self._get_implementation_patterns()
        
        # Initialize enhanced planning prompts
        if ENHANCED_PROMPTS_AVAILABLE:
            self.enhanced_prompts = EnhancedPlanningPrompts(self.project_type)
        else:
            self.enhanced_prompts = None
        
        # Initialize sequential thinking engine
        self.sequential_thinking = SequentialThinking()
        
    def _load_config(self, config_path: Optional[str]) -> Dict:
        """Load configuration or use defaults"""
        default_config = {
            "expansion_threshold": 6,
            "max_subtasks": 8,
            "min_subtasks": 3,
            "auto_expand": False,
            "dry_run": False,
            "verbose": False,
            "intelligent_discovery": True,
            "codebase_analysis": True,
            "enhanced_analysis": True,
            "innovation_mode": True,
            "quality_focus": True
        }
        
        if config_path and Path(config_path).exists():
            with open(config_path, 'r') as f:
                user_config = json.load(f)
                default_config.update(user_config)
        
        return default_config
    
    def _detect_project_type(self) -> str:
        """Detect project type based on files and structure"""
        if self.package_json.exists():
            with open(self.package_json, 'r') as f:
                data = json.load(f)
                deps = {**data.get('dependencies', {}), **data.get('devDependencies', {})}
                
                if 'react' in deps:
                    return 'react'
                elif 'vue' in deps:
                    return 'vue'
                elif 'angular' in deps:
                    return 'angular'
                else:
                    return 'nodejs'
        
        if (self.project_root / 'Cargo.toml').exists():
            return 'rust'
        if (self.project_root / 'go.mod').exists():
            return 'go'
        if (self.project_root / 'requirements.txt').exists() or (self.project_root / 'setup.py').exists():
            return 'python'
        
        return 'unknown'
    
    def _get_complexity_indicators(self) -> Dict[str, int]:
        """Define complexity indicators and their weights"""
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
    
    def _get_file_patterns(self) -> Dict[str, List[str]]:
        """Dynamically determine file patterns from actual project structure"""
        patterns = self._analyze_project_structure()
        return patterns.get(self.project_type, self._get_default_patterns())
    
    def _analyze_project_structure(self) -> Dict[str, Dict[str, List[str]]]:
        """Analyze actual project structure to determine file patterns"""
        patterns = {}
        
        # Analyze existing project structure
        if self.project_type == 'react':
            patterns['react'] = self._analyze_react_structure()
        elif self.project_type == 'python':
            patterns['python'] = self._analyze_python_structure()
        else:
            patterns[self.project_type] = self._analyze_generic_structure()
        
        return patterns
    
    def _analyze_react_structure(self) -> Dict[str, List[str]]:
        """Analyze React project structure"""
        patterns = {}
        
        # Find actual component patterns
        component_dirs = ['src/components', 'src/ui', 'components']
        for comp_dir in component_dirs:
            if (self.project_root / comp_dir).exists():
                # Analyze existing components to determine patterns
                existing_files = list((self.project_root / comp_dir).glob('*'))
                if existing_files:
                    patterns['component'] = self._infer_component_patterns(comp_dir, existing_files)
                    break
        
        # Find service patterns
        service_dirs = ['src/services', 'src/api', 'services']
        for service_dir in service_dirs:
            if (self.project_root / service_dir).exists():
                patterns['service'] = [f'{service_dir}/{{name}}.js', f'{service_dir}/{{name}}.test.js']
                break
        
        # Find test patterns from existing tests
        test_patterns = self._find_test_patterns()
        if test_patterns:
            patterns['test'] = test_patterns
        
        return patterns if patterns else self._get_default_react_patterns()
    
    def _analyze_python_structure(self) -> Dict[str, List[str]]:
        """Analyze Python project structure"""
        patterns = {}
        
        # Check for common Python patterns
        if (self.project_root / 'src').exists():
            patterns['module'] = ['src/{name}.py', 'tests/test_{name}.py']
        elif (self.project_root / 'lib').exists():
            patterns['module'] = ['lib/{name}.py', 'tests/test_{name}.py']
        else:
            patterns['module'] = ['{name}.py', 'tests/test_{name}.py']
        
        # Find actual test directory
        test_dirs = ['tests', 'test', 'src/tests']
        for test_dir in test_dirs:
            if (self.project_root / test_dir).exists():
                patterns['test'] = [f'{test_dir}/test_{{name}}.py']
                break
        
        return patterns if patterns else self._get_default_python_patterns()
    
    def _analyze_generic_structure(self) -> Dict[str, List[str]]:
        """Analyze generic project structure"""
        patterns = {}
        
        # Look for common patterns in any project type
        if (self.project_root / 'src').exists():
            patterns['file'] = ['src/{name}', 'tests/{name}_test']
        else:
            patterns['file'] = ['{name}', 'tests/{name}_test']
        
        return patterns
    
    def _infer_component_patterns(self, comp_dir: str, existing_files: List[Path]) -> List[str]:
        """Infer component patterns from existing files"""
        patterns = []
        
        # Check for common extensions
        extensions = set()
        for file in existing_files:
            if file.is_file():
                extensions.add(file.suffix)
        
        # Build patterns based on found extensions
        for ext in extensions:
            if ext in ['.js', '.jsx', '.ts', '.tsx']:
                patterns.append(f'{comp_dir}/{{name}}{ext}')
            elif ext == '.css':
                patterns.append(f'{comp_dir}/{{name}}.css')
        
        # Add test pattern if tests exist
        test_files = [f for f in existing_files if 'test' in f.name or 'spec' in f.name]
        if test_files:
            test_ext = test_files[0].suffix
            patterns.append(f'{comp_dir}/{{name}}.test{test_ext}')
        
        return patterns if patterns else [f'{comp_dir}/{{name}}.js']
    
    def _find_test_patterns(self) -> List[str]:
        """Find actual test patterns from project"""
        test_patterns = []
        
        # Common test directories
        test_dirs = ['tests', 'test', '__tests__', 'src/tests', 'src/__tests__']
        
        for test_dir in test_dirs:
            test_path = self.project_root / test_dir
            if test_path.exists():
                test_files = list(test_path.glob('*'))
                if test_files:
                    # Analyze test file naming patterns
                    for test_file in test_files[:3]:  # Check first 3 files
                        if test_file.is_file():
                            if 'test' in test_file.name:
                                test_patterns.append(f'{test_dir}/{{name}}.test{test_file.suffix}')
                            elif 'spec' in test_file.name:
                                test_patterns.append(f'{test_dir}/{{name}}.spec{test_file.suffix}')
                    break
        
        return test_patterns
    
    def _get_default_patterns(self) -> Dict[str, List[str]]:
        """Get minimal default patterns as fallback"""
        if self.project_type == 'react':
            return self._get_default_react_patterns()
        elif self.project_type == 'python':
            return self._get_default_python_patterns()
        else:
            return {'file': ['{name}', 'tests/{name}_test']}
    
    def _get_default_react_patterns(self) -> Dict[str, List[str]]:
        """Default React patterns as fallback"""
        return {
            'component': ['src/components/{name}.js'],
            'service': ['src/services/{name}.js'],
            'test': ['src/components/{name}.test.js']
        }
    
    def _get_default_python_patterns(self) -> Dict[str, List[str]]:
        """Default Python patterns as fallback"""
        return {
            'module': ['{name}.py'],
            'test': ['tests/test_{name}.py']
        }
    
    def _get_dependency_patterns(self) -> Dict[str, List[str]]:
        """Dynamically determine missing dependencies based on task requirements"""
        # Get existing dependencies first
        existing_deps = self._get_existing_dependencies()
        
        # Analyze what's commonly needed but missing
        return self._analyze_common_dependencies_for_project_type(existing_deps)
    
    def _analyze_common_dependencies_for_project_type(self, existing_deps: List[str]) -> Dict[str, List[str]]:
        """Analyze common dependencies based on project type and existing setup"""
        patterns = {}
        existing_set = set(existing_deps)
        
        if self.project_type == 'react':
            patterns = self._get_react_dependency_suggestions(existing_set)
        elif self.project_type == 'python':
            patterns = self._get_python_dependency_suggestions(existing_set)
        elif self.project_type in ['vue', 'angular']:
            patterns = self._get_frontend_dependency_suggestions(existing_set)
        else:
            patterns = self._get_generic_dependency_suggestions(existing_set)
        
        return patterns
    
    def _get_react_dependency_suggestions(self, existing_deps: set) -> Dict[str, List[str]]:
        """Get React-specific dependency suggestions"""
        suggestions = {}
        
        # Only suggest if not already present
        if not any(dep in existing_deps for dep in ['axios', 'fetch']):
            suggestions['api_client'] = ['axios']
        
        if not any(dep in existing_deps for dep in ['@testing-library/react', 'enzyme']):
            suggestions['testing'] = ['@testing-library/react', '@testing-library/jest-dom']
        
        if 'typescript' in existing_deps and 'types' not in str(existing_deps):
            suggestions['typescript'] = ['@types/react', '@types/node']
        
        # Check for PWA indicators
        if (self.project_root / 'public' / 'manifest.json').exists():
            if 'workbox' not in str(existing_deps):
                suggestions['pwa'] = ['workbox-webpack-plugin']
        
        return suggestions
    
    def _get_python_dependency_suggestions(self, existing_deps: set) -> Dict[str, List[str]]:
        """Get Python-specific dependency suggestions"""
        suggestions = {}
        
        # Web framework suggestions
        if not any(fw in existing_deps for fw in ['flask', 'django', 'fastapi', 'tornado']):
            suggestions['web_framework'] = ['fastapi']  # Modern default
        
        # Testing framework
        if not any(test in existing_deps for test in ['pytest', 'unittest', 'nose']):
            suggestions['testing'] = ['pytest']
        
        # HTTP client
        if not any(client in existing_deps for client in ['requests', 'httpx', 'aiohttp']):
            suggestions['api_client'] = ['requests']
        
        return suggestions
    
    def _get_frontend_dependency_suggestions(self, existing_deps: set) -> Dict[str, List[str]]:
        """Get general frontend dependency suggestions"""
        suggestions = {}
        
        if not any(dep in existing_deps for dep in ['axios', 'fetch']):
            suggestions['api_client'] = ['axios']
        
        return suggestions
    
    def _get_generic_dependency_suggestions(self, existing_deps: set) -> Dict[str, List[str]]:
        """Get generic dependency suggestions"""
        return {}
    
    def _get_existing_dependencies(self) -> List[str]:
        """Get list of existing dependencies"""
        deps = []
        
        if self.project_type in ["react", "vue", "angular", "node"]:
            if self.package_json.exists():
                try:
                    with open(self.package_json) as f:
                        data = json.load(f)
                    deps.extend(data.get('dependencies', {}).keys())
                    deps.extend(data.get('devDependencies', {}).keys())
                except:
                    pass
        
        return deps
    
    def _get_implementation_patterns(self) -> Dict[str, List[str]]:
        """Patterns to identify implementation requirements"""
        return {
            'api_integration': [
                'error handling',
                'rate limiting', 
                'response caching',
                'request retry logic',
                'data transformation',
                'loading states'
            ],
            'component_development': [
                'prop validation',
                'accessibility',
                'responsive design',
                'error boundaries',
                'loading states',
                'keyboard navigation'
            ],
            'testing_implementation': [
                'unit tests',
                'integration tests',
                'mock setup',
                'test utilities',
                'coverage reporting'
            ],
            'deployment_setup': [
                'build configuration',
                'environment variables',
                'deployment scripts',
                'monitoring setup',
                'logging configuration'
            ]
        }
    
    def analyze_task_complexity(self, task: Dict) -> ComplexityScore:
        """Analyze a single task and return complexity score with recommendations"""
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
    
    def analyze_task_intelligently(self, task: Dict) -> TaskAnalysis:
        """Perform intelligent analysis of a task to discover missing work"""
        if not self.config['intelligent_discovery']:
            # Return basic analysis with just complexity
            complexity = self.analyze_task_complexity(task)
            return TaskAnalysis(
                missing_files=[],
                missing_dependencies=[],
                missing_tests=[],
                implementation_gaps=[],
                discovered_subtasks=[],
                complexity_score=complexity,
                improvement_suggestions=[],
                innovation_opportunities=[],
                quality_enhancements=[],
                implementation_roadmap=[]
            )
        
        # Analyze task for missing components
        missing_files = self._analyze_missing_files(task)
        missing_dependencies = self._analyze_missing_dependencies(task)
        missing_tests = self._analyze_missing_tests(task)
        implementation_gaps = self._analyze_implementation_gaps(task)
        
        # Generate intelligent subtasks
        discovered_subtasks = self._generate_intelligent_subtasks(
            task, missing_files, missing_dependencies, missing_tests, implementation_gaps
        )
        
        # Get complexity score
        complexity = self.analyze_task_complexity(task)
        
        # Enhanced analysis with prompts (if available)
        improvement_suggestions = []
        innovation_opportunities = []
        quality_enhancements = []
        implementation_roadmap = []
        
        if (self.config.get('enhanced_analysis', True) and 
            self.enhanced_prompts and 
            ENHANCED_PROMPTS_AVAILABLE):
            
            # Create project context
            project_context = {
                "project_type": self.project_type,
                "dependencies": self._get_existing_dependencies(),
                "complexity_score": complexity.total_score,
                "missing_files": missing_files,
                "missing_dependencies": missing_dependencies,
                "implementation_gaps": implementation_gaps
            }
            
            # Generate enhanced analysis
            enhanced_analysis = self.enhanced_prompts.generate_improvement_analysis(task, project_context)
            
            improvement_suggestions = [
                {
                    "title": suggestion.title,
                    "description": suggestion.description,
                    "category": suggestion.category,
                    "impact": suggestion.impact,
                    "effort": suggestion.effort,
                    "implementation_details": suggestion.implementation_details,
                    "best_practices": suggestion.best_practices,
                    "success_metrics": suggestion.success_metrics
                }
                for suggestion in enhanced_analysis.get("improvement_suggestions", [])
            ]
            
            innovation_opportunities = enhanced_analysis.get("innovation_opportunities", [])
            quality_enhancements = enhanced_analysis.get("quality_enhancements", [])
            implementation_roadmap = enhanced_analysis.get("implementation_roadmap", [])
        
        # Generate git workflow suggestions
        git_workflow_suggestions = self._generate_git_workflow_suggestions(task, complexity)
        
        # Apply sequential thinking for complex tasks
        if complexity.total_score >= 7 and self.config.get('sequential_thinking', True):
            task_description = task.get('title', '') + ' - ' + task.get('description', '')
            thinking_result = self.sequential_thinking.think_through_problem(
                f"Complex task analysis: {task_description}", 
                initial_estimate=max(4, complexity.total_score // 2)
            )
            
            if self.config.get('verbose', False):
                print(f"🧠 Sequential thinking applied:")
                print(f"   💡 Solution confidence: {thinking_result.confidence_score:.2f}")
                print(f"   🎯 Reasoning quality: {thinking_result.reasoning_quality}")
                print(f"   ⏱️  Analysis duration: {thinking_result.duration:.1f}s")
        
        return TaskAnalysis(
            missing_files=missing_files,
            missing_dependencies=missing_dependencies,
            missing_tests=missing_tests,
            implementation_gaps=implementation_gaps,
            discovered_subtasks=discovered_subtasks,
            complexity_score=complexity,
            improvement_suggestions=improvement_suggestions,
            innovation_opportunities=innovation_opportunities,
            quality_enhancements=quality_enhancements,
            implementation_roadmap=implementation_roadmap,
            git_workflow_suggestions=git_workflow_suggestions
        )
    
    def _analyze_missing_files(self, task: Dict) -> List[str]:
        """Analyze what files are missing for this task"""
        missing_files = []
        task_text = ' '.join([
            task.get('title', ''),
            task.get('description', ''),
            task.get('details', '') or ''
        ]).lower()
        
        # Extract component/service names from task
        names = self._extract_entity_names(task_text)
        
        for name in names:
            for pattern_type, file_patterns in self.file_patterns.items():
                if pattern_type in task_text:
                    for pattern in file_patterns:
                        file_path = pattern.format(name=name)
                        full_path = self.project_root / file_path
                        if not full_path.exists():
                            missing_files.append(file_path)
        
        return missing_files
    
    def _analyze_missing_dependencies(self, task: Dict) -> List[str]:
        """Analyze what dependencies are missing for this task"""
        missing_deps = []
        task_text = ' '.join([
            task.get('title', ''),
            task.get('description', ''),
            task.get('details', '') or ''
        ]).lower()
        
        # Check existing dependencies
        existing_deps = set()
        if self.package_json.exists():
            with open(self.package_json, 'r') as f:
                data = json.load(f)
                existing_deps.update(data.get('dependencies', {}).keys())
                existing_deps.update(data.get('devDependencies', {}).keys())
        
        # Check for missing dependencies based on task content
        for dep_type, deps in self.dependency_patterns.items():
            if any(keyword in task_text for keyword in dep_type.split('_')):
                for dep in deps:
                    if dep not in existing_deps:
                        missing_deps.append(dep)
        
        return missing_deps
    
    def _analyze_missing_tests(self, task: Dict) -> List[str]:
        """Analyze what tests are missing for this task based on actual project structure"""
        missing_tests = []
        task_text = ' '.join([
            task.get('title', ''),
            task.get('description', ''),
            task.get('details', '') or ''
        ]).lower()
        
        # Extract entity names
        names = self._extract_entity_names(task_text)
        
        # Get actual test patterns from project
        test_patterns = self._find_test_patterns()
        if not test_patterns:
            test_patterns = self._get_default_test_patterns()
        
        for name in names:
            for pattern in test_patterns:
                test_file = pattern.format(name=name)
                full_path = self.project_root / test_file
                if not full_path.exists():
                    missing_tests.append(test_file)
        
        return missing_tests
    
    def _get_default_test_patterns(self) -> List[str]:
        """Get default test patterns based on project type"""
        if self.project_type == 'react':
            return ['src/components/{name}.test.js', 'src/services/{name}.test.js']
        elif self.project_type == 'python':
            return ['tests/test_{name}.py']
        else:
            return ['tests/{name}_test.js']
    
    def _analyze_implementation_gaps(self, task: Dict) -> List[str]:
        """Analyze implementation gaps based on task requirements"""
        gaps = []
        task_text = ' '.join([
            task.get('title', ''),
            task.get('description', ''),
            task.get('details', '') or ''
        ]).lower()
        
        # Check for implementation gaps based on patterns
        for gap_type, requirements in self.implementation_patterns.items():
            if any(keyword in task_text for keyword in gap_type.split('_')):
                for req in requirements:
                    if req.lower() not in task_text:
                        gaps.append(req)
        
        return gaps
    
    def _extract_entity_names(self, text: str) -> List[str]:
        """Extract entity names (components, services, etc.) from task text"""
        names = []
        
        # Look for capitalized words that could be component names
        words = re.findall(r'\b[A-Z][a-zA-Z]+\b', text)
        names.extend(words)
        
        # Look for specific patterns
        patterns = [
            r'(\w+)\s+component',
            r'(\w+)\s+service',
            r'(\w+)\s+api',
            r'(\w+)\s+hook'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            names.extend(matches)
        
        # Clean and deduplicate
        cleaned_names = []
        for name in names:
            name = name.strip().title()
            if name and name not in cleaned_names and len(name) > 2:
                cleaned_names.append(name)
        
        return cleaned_names[:5]  # Limit to 5 names
    
    def _generate_intelligent_subtasks(self, task: Dict, missing_files: List[str], 
                                     missing_dependencies: List[str], missing_tests: List[str],
                                     implementation_gaps: List[str]) -> List[Dict]:
        """Generate intelligent subtasks based on analysis"""
        subtasks = []
        
        # Add dependency installation subtasks
        for dep in missing_dependencies:
            subtasks.append({
                'title': f'Install {dep} dependency',
                'description': f'Add {dep} to package.json and configure for use',
                'details': f'Run package manager install command for {dep}',
                'priority': 'high',
                'type': 'dependency'
            })
        
        # Add file creation subtasks
        for file_path in missing_files:
            file_name = Path(file_path).stem
            subtasks.append({
                'title': f'Create {file_name} file',
                'description': f'Implement {file_path} with required functionality',
                'details': f'Create {file_path} with proper structure and exports',
                'priority': 'high',
                'type': 'file_creation'
            })
        
        # Add implementation gap subtasks
        for gap in implementation_gaps:
            subtasks.append({
                'title': f'Implement {gap}',
                'description': f'Add {gap} to meet task requirements',
                'details': f'Research and implement {gap} following best practices',
                'priority': 'medium',
                'type': 'implementation'
            })
        
        # Add test creation subtasks
        for test_path in missing_tests:
            test_name = Path(test_path).stem
            subtasks.append({
                'title': f'Create {test_name} test',
                'description': f'Implement {test_path} with comprehensive tests',
                'details': f'Create {test_path} with unit tests and integration tests',
                'priority': 'medium',
                'type': 'testing'
            })
        
        return subtasks
    
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
    
    def _generate_git_workflow_suggestions(self, task: Dict, complexity: ComplexityScore) -> List[GitWorkflowSuggestion]:
        """Generate git workflow suggestions based on task analysis"""
        suggestions = []
        task_text = ' '.join([
            task.get('title', ''),
            task.get('description', ''),
            task.get('details', '') or ''
        ]).lower()
        
        # Determine if this is a new feature, bug fix, or other type
        is_feature = any(word in task_text for word in ['create', 'add', 'implement', 'new', 'feature'])
        is_bugfix = any(word in task_text for word in ['fix', 'bug', 'error', 'issue', 'problem'])
        is_refactor = any(word in task_text for word in ['refactor', 'improve', 'optimize', 'enhance'])
        
        # Branch naming suggestion
        task_id = task.get('id', 'task')
        if is_feature:
            branch_name = f"feature/{task_id}-{self._slugify(task.get('title', 'new-feature'))}"
            branch_type = "feature"
        elif is_bugfix:
            branch_name = f"bugfix/{task_id}-{self._slugify(task.get('title', 'bug-fix'))}"
            branch_type = "bugfix"
        elif is_refactor:
            branch_name = f"refactor/{task_id}-{self._slugify(task.get('title', 'refactor'))}"
            branch_type = "refactor"
        else:
            branch_name = f"task/{task_id}-{self._slugify(task.get('title', 'task'))}"
            branch_type = "task"
        
        # Branch creation suggestion
        suggestions.append(GitWorkflowSuggestion(
            action="branch",
            description=f"Create {branch_type} branch for task {task_id}",
            commands=[
                f"git checkout -b {branch_name}",
                f"git push -u origin {branch_name}"
            ],
            rationale=f"Isolates {branch_type} work and enables parallel development"
        ))
        
        # Commit strategy based on complexity
        if complexity.should_expand:
            # High complexity - multiple commits
            suggestions.append(GitWorkflowSuggestion(
                action="commit",
                description="Use atomic commits for each subtask",
                commands=[
                    "git add <specific-files>",
                    "git commit -m 'feat(scope): implement specific feature'",
                    "# Repeat for each logical change"
                ],
                rationale="Complex tasks benefit from granular commits for easier review and rollback"
            ))
        else:
            # Simple task - single commit
            suggestions.append(GitWorkflowSuggestion(
                action="commit", 
                description="Single commit for straightforward task",
                commands=[
                    "git add .",
                    f"git commit -m '{self._generate_commit_message(task, branch_type)}'"
                ],
                rationale="Simple tasks can be committed atomically"
            ))
        
        # Repository creation suggestion if no remote exists
        if not self._has_git_remote():
            suggestions.append(GitWorkflowSuggestion(
                action="repository",
                description="Create GitHub repository for project",
                commands=[
                    "python3 agents/quality-git-agent.py --mode repo --create-repo",
                    "# or use: python3 agents/repo-manager-agent.py --interactive"
                ],
                rationale="Project needs remote repository for collaboration and backup"
            ))
        
        # Pull request suggestion for complex tasks
        if complexity.should_expand or is_feature:
            suggestions.append(GitWorkflowSuggestion(
                action="pr",
                description="Create pull request for review",
                commands=[
                    "git push origin " + branch_name,
                    "gh pr create --title 'Title' --body 'Description'",
                    "# or create PR through GitHub web interface"
                ],
                rationale="Complex changes benefit from code review and discussion"
            ))
        
        return suggestions
    
    def _slugify(self, text: str) -> str:
        """Convert text to git-safe slug"""
        import re
        # Convert to lowercase and replace spaces/special chars with hyphens
        slug = re.sub(r'[^\w\s-]', '', text.lower())
        slug = re.sub(r'[-\s]+', '-', slug)
        return slug.strip('-')[:30]  # Limit length
    
    def _has_git_remote(self) -> bool:
        """Check if git remote exists"""
        try:
            import subprocess
            result = subprocess.run(
                ["git", "remote", "get-url", "origin"],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            return result.returncode == 0
        except Exception:
            return False
    
    def _generate_commit_message(self, task: Dict, branch_type: str) -> str:
        """Generate conventional commit message"""
        title = task.get('title', 'Task update')
        
        # Determine commit type based on branch type
        if branch_type == "feature":
            prefix = "feat"
        elif branch_type == "bugfix":
            prefix = "fix"
        elif branch_type == "refactor":
            prefix = "refactor"
        else:
            prefix = "chore"
        
        # Try to extract scope from title
        scope = ""
        if "component" in title.lower():
            scope = "component"
        elif "service" in title.lower():
            scope = "service"
        elif "test" in title.lower():
            scope = "test"
        elif "doc" in title.lower():
            scope = "docs"
        
        scope_part = f"({scope})" if scope else ""
        return f"{prefix}{scope_part}: {title.lower()}"
    
    def get_taskmaster_tasks(self, tag: str = 'agents') -> List[Dict]:
        """Fetch tasks from Task Master tasks.json file"""
        try:
            tasks_file = Path('.taskmaster/tasks/tasks.json')
            if not tasks_file.exists():
                if self.config['verbose']:
                    print(f"Task Master tasks file not found: {tasks_file}")
                return []
                
            with open(tasks_file, 'r') as f:
                data = json.load(f)
                
            # Handle new format with tags
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
    
    def analyze_all_tasks(self, tag: str = 'agents') -> List[Tuple[Dict, TaskAnalysis]]:
        """Analyze all tasks and return comprehensive results"""
        tasks = self.get_taskmaster_tasks(tag)
        results = []
        
        for task in tasks:
            # Skip tasks that already have subtasks
            if task.get('subtasks') and len(task['subtasks']) > 0:
                continue
                
            analysis = self.analyze_task_intelligently(task)
            results.append((task, analysis))
        
        return results
    
    def print_analysis_report(self, results: List[Tuple[Dict, TaskAnalysis]]) -> None:
        """Print a comprehensive analysis report"""
        print("\n" + "="*80)
        print("🧠 PLANNING & ANALYSIS AGENT REPORT")
        print("="*80)
        
        total_tasks = len(results)
        expandable_tasks = sum(1 for _, analysis in results if analysis.complexity_score.should_expand)
        
        print(f"\n📊 SUMMARY:")
        print(f"   Total Tasks Analyzed: {total_tasks}")
        print(f"   Tasks Needing Expansion: {expandable_tasks}")
        print(f"   Project Type: {self.project_type}")
        print(f"   Expansion Threshold: {self.config['expansion_threshold']}")
        
        print(f"\n📋 DETAILED ANALYSIS:")
        
        for task, analysis in sorted(results, key=lambda x: x[1].complexity_score.total_score, reverse=True):
            complexity = analysis.complexity_score
            status_icon = "🔴" if complexity.should_expand else "🟢"
            
            print(f"\n{status_icon} Task {task['id']}: {task['title'][:50]}...")
            print(f"   Complexity Score: {complexity.total_score}")
            print(f"   Recommendation: {complexity.recommendation}")
            
            if complexity.indicators:
                print(f"   Complexity Indicators: {', '.join(complexity.indicators.keys())}")
            
            if self.config['intelligent_discovery']:
                if analysis.missing_files:
                    print(f"   📄 Missing Files: {len(analysis.missing_files)}")
                if analysis.missing_dependencies:
                    print(f"   📦 Missing Dependencies: {', '.join(analysis.missing_dependencies)}")
                if analysis.missing_tests:
                    print(f"   🧪 Missing Tests: {len(analysis.missing_tests)}")
                if analysis.implementation_gaps:
                    print(f"   ⚠️  Implementation Gaps: {len(analysis.implementation_gaps)}")
                if analysis.discovered_subtasks:
                    print(f"   🎯 Discovered Subtasks: {len(analysis.discovered_subtasks)}")
            
            # Enhanced analysis information
            if (self.config.get('enhanced_analysis', True) and 
                analysis.improvement_suggestions and 
                ENHANCED_PROMPTS_AVAILABLE):
                print(f"   ✨ Enhanced Analysis Available:")
                if analysis.improvement_suggestions:
                    print(f"      🔧 Improvement Suggestions: {len(analysis.improvement_suggestions)}")
                    for suggestion in analysis.improvement_suggestions[:2]:  # Show top 2
                        print(f"         • {suggestion['title']} ({suggestion['impact']} impact)")
                if analysis.innovation_opportunities:
                    print(f"      💡 Innovation Opportunities: {len(analysis.innovation_opportunities)}")
                if analysis.quality_enhancements:
                    print(f"      🎯 Quality Enhancements: {len(analysis.quality_enhancements)}")
                if analysis.implementation_roadmap:
                    print(f"      🗺️  Implementation Roadmap: {len(analysis.implementation_roadmap)} phases")
            
            # Git workflow suggestions
            if analysis.git_workflow_suggestions:
                print(f"   🔄 Git Workflow Suggestions:")
                for suggestion in analysis.git_workflow_suggestions[:3]:  # Show top 3
                    print(f"      {suggestion.action.title()}: {suggestion.description}")
                    if len(suggestion.commands) <= 2:
                        for cmd in suggestion.commands:
                            if not cmd.startswith('#'):
                                print(f"         $ {cmd}")
            
            if complexity.should_expand:
                print(f"   💡 Suggested Action: task-master expand --id={task['id']} --num={complexity.suggested_subtasks}")
        
        print("\n" + "="*80)

def main():
    parser = argparse.ArgumentParser(description='Planning & Analysis Agent')
    parser.add_argument('--config', type=str, help='Path to configuration file')
    parser.add_argument('--project-root', type=str, default='.', help='Project root directory')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    parser.add_argument('--threshold', type=int, default=6, help='Complexity threshold for expansion')
    parser.add_argument('--tag', type=str, default='agents', help='Task Master tag to analyze')
    parser.add_argument('--no-intelligent-discovery', action='store_true', help='Disable intelligent task discovery')
    parser.add_argument('--no-codebase-analysis', action='store_true', help='Disable codebase analysis')
    parser.add_argument('--no-enhanced-analysis', action='store_true', help='Disable enhanced analysis with prompts')
    parser.add_argument('--no-innovation-mode', action='store_true', help='Disable innovation opportunity generation')
    parser.add_argument('--no-quality-focus', action='store_true', help='Disable quality enhancement suggestions')
    
    args = parser.parse_args()
    
    # Create agent with configuration
    agent = PlanningAnalysisAgent(args.project_root, args.config)
    agent.config.update({
        'verbose': args.verbose,
        'expansion_threshold': args.threshold,
        'intelligent_discovery': not args.no_intelligent_discovery,
        'codebase_analysis': not args.no_codebase_analysis,
        'enhanced_analysis': not args.no_enhanced_analysis,
        'innovation_mode': not args.no_innovation_mode,
        'quality_focus': not args.no_quality_focus
    })
    
    print("🤖 Planning & Analysis Agent")
    print("============================")
    print(f"Project Type: {agent.project_type} (detected from actual project)")
    print(f"Project Root: {agent.project_root.absolute()}")
    print(f"Intelligent Discovery: {agent.config['intelligent_discovery']}")
    print(f"Codebase Analysis: {agent.config['codebase_analysis']}")
    print(f"Enhanced Analysis: {agent.config['enhanced_analysis']} ({'Available' if ENHANCED_PROMPTS_AVAILABLE else 'Module not found'})")
    print(f"Innovation Mode: {agent.config['innovation_mode']}")
    print(f"Quality Focus: {agent.config['quality_focus']}")
    
    # Analyze all tasks from actual Task Master system
    results = agent.analyze_all_tasks(args.tag)
    
    if not results:
        print(f"No tasks found to analyze in '{args.tag}' tag from Task Master system.")
        print(f"Checked: {agent.project_root / '.taskmaster/tasks/tasks.json'}")
        sys.exit(1)
    
    # Print analysis report
    agent.print_analysis_report(results)
    
    print("\n✅ Planning & Analysis complete!")
    print(f"Analyzed {len(results)} tasks from actual Task Master data")

if __name__ == "__main__":
    main()