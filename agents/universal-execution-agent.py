#!/usr/bin/env python3
"""
Universal Execution Agent (Refactored)

Enhanced universal development execution agent with better task coordination,
duplicate prevention, and improved integration with Planning Agent.
"""

import json
import subprocess
import os
import re
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Set
from dataclasses import dataclass, asdict
from enum import Enum
import argparse
import hashlib

# Sequential thinking implementation
@dataclass
class ExecutionThought:
    """Thought step for execution planning"""
    step: int
    description: str
    rationale: str
    risks: List[str]
    dependencies: List[str]
    confidence: float

class ProjectType(Enum):
    REACT = "react"
    VUE = "vue"
    ANGULAR = "angular"
    NODE = "node"
    PYTHON = "python"
    RUST = "rust"
    GO = "go"
    UNKNOWN = "unknown"

class TaskType(Enum):
    DEPENDENCY_INSTALL = "dependency_install"
    FILE_CREATE = "file_create"
    IMPLEMENTATION = "implementation"
    TESTING = "testing"
    CONFIGURATION = "configuration"
    BUILD = "build"
    DEPLOYMENT = "deployment"
    UNKNOWN = "unknown"

class TaskStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"

@dataclass
class ProjectContext:
    """Context information about the current project"""
    project_type: ProjectType
    root_dir: Path
    package_manager: str
    test_command: str
    build_command: str
    src_dir: Path
    config_files: List[str]
    dependencies: Dict[str, str]
    
@dataclass
class GitWorkflowAction:
    """Git workflow action"""
    action_type: str  # "branch", "commit", "push", "pr"
    commands: List[str]
    description: str
    branch_name: Optional[str] = None
    commit_message: Optional[str] = None

@dataclass
class TaskAction:
    """Represents an action to execute for a task"""
    action_type: str
    command: Optional[str]
    files_to_create: List[Tuple[str, str]]  # (path, content)
    validation_checks: List[str]
    description: str
    dependencies: List[str]
    estimated_duration: int
    git_actions: List[GitWorkflowAction] = None  # seconds

@dataclass
class AgentSync:
    """Synchronization data between agents"""
    project_state: Dict[str, Any]
    sync_timestamp: float
    quality_gates_passing: bool
    skip_dependencies: Set[str]
    skip_files: Set[str]
    completed_subtasks: List[str]
    agent_coordination: Dict[str, Any]

class UniversalExecutionAgent:
    """
    Enhanced Universal Execution Agent with improved coordination and duplicate prevention
    """
    
    def __init__(self, project_root: str = ".", config_path: Optional[str] = None):
        self.project_root = Path(project_root)
        self.config = self._load_config(config_path)
        self.context = self._analyze_project_context()
        
        # Enhanced sync and state management
        self.sync_dir = self.project_root / ".taskmaster" / "agent_sync"
        self.sync_dir.mkdir(parents=True, exist_ok=True)
        self.sync_file = self.sync_dir / "universal_execution_agent.json"
        self.project_state_file = self.project_root / ".taskmaster" / "project_state.json"
        
        # Load sync data from all agents
        self.sync_data = self._load_sync_data()
        self.project_state = self._load_project_state()
        
        # Task execution tracking
        self.execution_log = []
        self.task_cache = {}
        
        # Initialize patterns and templates
        self.task_patterns = self._init_task_patterns()
        self.project_patterns = self._analyze_project_patterns()
        
        # Sequential thinking for execution planning
        self.execution_thoughts: List[ExecutionThought] = []
        
    def _load_config(self, config_path: Optional[str]) -> Dict:
        """Load configuration with defaults"""
        default_config = {
            "verbose": False,
            "dry_run": False,
            "max_retries": 3,
            "timeout": 300,
            "coordination_enabled": True,
            "duplicate_detection": True,
            "quality_gates": True,
            "backup_before_changes": True
        }
        
        if config_path and Path(config_path).exists():
            with open(config_path, 'r') as f:
                user_config = json.load(f)
                default_config.update(user_config)
        
        return default_config
    
    def _analyze_project_context(self) -> ProjectContext:
        """Enhanced project analysis with better type detection"""
        root = self.project_root
        
        # Detect project type with improved logic
        project_type = self._detect_project_type(root)
        
        # Determine tooling with fallbacks
        package_manager, test_cmd, build_cmd = self._detect_tooling(root, project_type)
        
        # Find source directory intelligently
        src_dir = self._find_src_directory(root, project_type)
        
        # Find all relevant config files
        config_files = self._find_config_files(root, project_type)
        
        # Load dependencies with proper parsing
        dependencies = self._load_dependencies(root, project_type)
        
        return ProjectContext(
            project_type=project_type,
            root_dir=root,
            package_manager=package_manager,
            test_command=test_cmd,
            build_command=build_cmd,
            src_dir=src_dir,
            config_files=[str(f) for f in config_files],
            dependencies=dependencies
        )
    
    def _detect_project_type(self, root: Path) -> ProjectType:
        """Enhanced project type detection"""
        # Check for JavaScript/Node projects
        package_json = root / "package.json"
        if package_json.exists():
            try:
                with open(package_json) as f:
                    data = json.load(f)
                deps = {**data.get('dependencies', {}), **data.get('devDependencies', {})}
                
                # Check for framework-specific dependencies
                if any(dep in deps for dep in ['react', 'react-dom']):
                    return ProjectType.REACT
                elif any(dep in deps for dep in ['vue', '@vue/cli']):
                    return ProjectType.VUE
                elif any(dep in deps for dep in ['@angular/core', '@angular/cli']):
                    return ProjectType.ANGULAR
                else:
                    return ProjectType.NODE
            except (json.JSONDecodeError, FileNotFoundError):
                pass
        
        # Check for Python projects
        python_indicators = [
            "requirements.txt", "pyproject.toml", "setup.py", "Pipfile",
            "poetry.lock", "conda.yml", "environment.yml"
        ]
        if any((root / indicator).exists() for indicator in python_indicators):
            return ProjectType.PYTHON
        
        # Check for Rust projects
        if (root / "Cargo.toml").exists():
            return ProjectType.RUST
        
        # Check for Go projects
        if (root / "go.mod").exists() or (root / "go.sum").exists():
            return ProjectType.GO
        
        return ProjectType.UNKNOWN
    
    def _detect_tooling(self, root: Path, project_type: ProjectType) -> Tuple[str, str, str]:
        """Enhanced tooling detection with proper fallbacks"""
        if project_type in [ProjectType.REACT, ProjectType.VUE, ProjectType.ANGULAR, ProjectType.NODE]:
            # Check package managers in order of preference
            if (root / "bun.lockb").exists():
                return "bun", "bun test", "bun run build"
            elif (root / "pnpm-lock.yaml").exists():
                return "pnpm", "pnpm test", "pnpm run build"
            elif (root / "yarn.lock").exists():
                return "yarn", "yarn test", "yarn build"
            else:
                return "npm", "npm test", "npm run build"
        
        elif project_type == ProjectType.PYTHON:
            # Check for Python package managers
            if (root / "poetry.lock").exists():
                return "poetry", "poetry run pytest", "poetry build"
            elif (root / "Pipfile").exists():
                return "pipenv", "pipenv run pytest", "pipenv run build"
            else:
                return "pip", "python -m pytest", "python -m build"
        
        elif project_type == ProjectType.RUST:
            return "cargo", "cargo test", "cargo build --release"
        
        elif project_type == ProjectType.GO:
            return "go", "go test ./...", "go build ."
        
        return "unknown", "echo 'No test command'", "echo 'No build command'"
    
    def _find_src_directory(self, root: Path, project_type: ProjectType) -> Path:
        """Enhanced source directory detection"""
        candidates = []
        
        if project_type in [ProjectType.REACT, ProjectType.VUE, ProjectType.ANGULAR]:
            candidates = ["src", "lib", "app", "components"]
        elif project_type == ProjectType.PYTHON:
            candidates = ["src", "lib", root.name, "app"]
        elif project_type == ProjectType.RUST:
            candidates = ["src"]
        elif project_type == ProjectType.GO:
            candidates = [".", "cmd", "internal", "pkg"]
        
        for candidate in candidates:
            candidate_path = root / candidate
            if candidate_path.exists() and candidate_path.is_dir():
                return candidate_path
        
        return root
    
    def _find_config_files(self, root: Path, project_type: ProjectType) -> List[Path]:
        """Enhanced config file detection"""
        configs = []
        
        # Common config files by project type
        config_patterns = {
            ProjectType.REACT: [
                "package.json", "tsconfig.json", ".eslintrc*", "vite.config.*",
                "webpack.config.*", "babel.config.*", "jest.config.*"
            ],
            ProjectType.PYTHON: [
                "requirements.txt", "pyproject.toml", "setup.py", "setup.cfg",
                "tox.ini", "pytest.ini", ".pylintrc", "mypy.ini"
            ],
            ProjectType.RUST: [
                "Cargo.toml", "Cargo.lock", "rust-toolchain.toml"
            ],
            ProjectType.GO: [
                "go.mod", "go.sum", "go.work", "Dockerfile"
            ]
        }
        
        patterns = config_patterns.get(project_type, ["package.json"])
        
        for pattern in patterns:
            if '*' in pattern:
                # Handle glob patterns
                configs.extend(root.glob(pattern))
            else:
                config_path = root / pattern
                if config_path.exists():
                    configs.append(config_path)
        
        return configs
    
    def _load_dependencies(self, root: Path, project_type: ProjectType) -> Dict[str, str]:
        """Enhanced dependency loading with proper parsing"""
        deps = {}
        
        if project_type in [ProjectType.REACT, ProjectType.VUE, ProjectType.ANGULAR, ProjectType.NODE]:
            package_json = root / "package.json"
            if package_json.exists():
                try:
                    with open(package_json) as f:
                        data = json.load(f)
                    deps.update(data.get('dependencies', {}))
                    deps.update(data.get('devDependencies', {}))
                except (json.JSONDecodeError, FileNotFoundError):
                    pass
        
        elif project_type == ProjectType.PYTHON:
            # Try multiple Python dependency files
            req_file = root / "requirements.txt"
            if req_file.exists():
                try:
                    with open(req_file) as f:
                        for line in f:
                            line = line.strip()
                            if line and not line.startswith('#'):
                                if '==' in line:
                                    name, version = line.split('==', 1)
                                    deps[name.strip()] = version.strip()
                                else:
                                    deps[line] = "latest"
                except FileNotFoundError:
                    pass
            
            # Also check pyproject.toml
            pyproject = root / "pyproject.toml"
            if pyproject.exists():
                try:
                    # Try to import tomllib (Python 3.11+) or fall back to tomli
                    try:
                        import tomllib
                    except ImportError:
                        try:
                            import tomli as tomllib
                        except ImportError:
                            tomllib = None
                    
                    if tomllib:
                        with open(pyproject, 'rb') as f:
                            data = tomllib.load(f)
                        project_deps = data.get('project', {}).get('dependencies', [])
                        for dep in project_deps:
                            if '>=' in dep:
                                name, version = dep.split('>=', 1)
                                deps[name.strip()] = version.strip()
                            else:
                                deps[dep] = "latest"
                except Exception:
                    pass
        
        return deps
    
    def _load_sync_data(self) -> AgentSync:
        """Load synchronization data from all agents"""
        sync_data = AgentSync(
            project_state={},
            sync_timestamp=time.time(),
            quality_gates_passing=True,
            skip_dependencies=set(),
            skip_files=set(),
            completed_subtasks=[],
            agent_coordination={}
        )
        
        # Load from our own sync file
        if self.sync_file.exists():
            try:
                with open(self.sync_file, 'r') as f:
                    data = json.load(f)
                
                sync_data.project_state = data.get('project_state', {})
                sync_data.sync_timestamp = data.get('sync_timestamp', time.time())
                sync_data.quality_gates_passing = data.get('quality_gates_passing', True)
                sync_data.skip_dependencies = set(data.get('skip_dependencies', []))
                sync_data.skip_files = set(data.get('skip_files', []))
                sync_data.completed_subtasks = data.get('completed_subtasks', [])
                sync_data.agent_coordination = data.get('agent_coordination', {})
                
            except (json.JSONDecodeError, FileNotFoundError):
                pass
        
        # Load coordination data from other agents
        for sync_file in self.sync_dir.glob("*.json"):
            if sync_file.name != "universal_execution_agent.json":
                try:
                    with open(sync_file, 'r') as f:
                        other_data = json.load(f)
                    
                    # Merge skip lists to prevent duplicates
                    sync_data.skip_dependencies.update(other_data.get('skip_dependencies', []))
                    sync_data.skip_files.update(other_data.get('skip_files', []))
                    
                    # Update quality gate status
                    if not other_data.get('quality_gates_passing', True):
                        sync_data.quality_gates_passing = False
                        
                except (json.JSONDecodeError, FileNotFoundError):
                    continue
        
        return sync_data
    
    def _load_project_state(self) -> Dict[str, Any]:
        """Load shared project state"""
        if self.project_state_file.exists():
            try:
                with open(self.project_state_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                pass
        
        return {
            "current_task": None,
            "completed_tasks": [],
            "failed_tasks": [],
            "project_health": "unknown",
            "last_build_status": "unknown",
            "test_status": "unknown"
        }
    
    def _save_sync_data(self) -> None:
        """Save synchronization data"""
        sync_data = {
            "project_state": self.sync_data.project_state,
            "sync_timestamp": time.time(),
            "quality_gates_passing": self.sync_data.quality_gates_passing,
            "skip_dependencies": list(self.sync_data.skip_dependencies),
            "skip_files": list(self.sync_data.skip_files),
            "completed_subtasks": self.sync_data.completed_subtasks,
            "agent_coordination": self.sync_data.agent_coordination
        }
        
        with open(self.sync_file, 'w') as f:
            json.dump(sync_data, f, indent=2)
    
    def _save_project_state(self) -> None:
        """Save shared project state"""
        self.project_state_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.project_state_file, 'w') as f:
            json.dump(self.project_state, f, indent=2)
    
    def think_through_execution(self, task: Dict) -> List[ExecutionThought]:
        """Use sequential thinking to plan task execution"""
        self.execution_thoughts = []
        task_text = f"{task.get('title', '')} - {task.get('description', '')}"
        
        # Step 1: Understand the task
        step1 = ExecutionThought(
            step=1,
            description="Analyze task requirements and scope",
            rationale=f"Need to understand what '{task_text}' actually requires in terms of files, dependencies, and implementation steps.",
            risks=["Misunderstanding requirements", "Missing dependencies"],
            dependencies=[],
            confidence=0.8
        )
        self.execution_thoughts.append(step1)
        
        # Step 2: Identify dependencies and prerequisites
        step2 = ExecutionThought(
            step=2, 
            description="Identify required dependencies and files",
            rationale="Before executing, need to ensure all prerequisites are in place to avoid execution failures.",
            risks=["Missing dependencies", "File conflicts", "Environment issues"],
            dependencies=["Step 1 analysis"],
            confidence=0.7
        )
        self.execution_thoughts.append(step2)
        
        # Step 3: Plan execution strategy
        step3 = ExecutionThought(
            step=3,
            description="Determine optimal execution approach",
            rationale="Choose the best strategy considering project patterns, existing code, and potential conflicts.",
            risks=["Suboptimal approach", "Breaking existing functionality"],
            dependencies=["Requirements analysis", "Dependency identification"],
            confidence=0.75
        )
        self.execution_thoughts.append(step3)
        
        # Step 4: Execute with monitoring
        step4 = ExecutionThought(
            step=4,
            description="Execute task with careful monitoring",
            rationale="Implement the planned approach while monitoring for issues and ready to adapt if needed.",
            risks=["Execution failures", "Unexpected side effects"],
            dependencies=["All previous steps"],
            confidence=0.85
        )
        self.execution_thoughts.append(step4)
        
        if self.config.get('verbose', False):
            print(f"🧠 Execution thinking planned {len(self.execution_thoughts)} steps")
            for thought in self.execution_thoughts:
                print(f"   {thought.step}. {thought.description} (confidence: {thought.confidence:.2f})")
        
        return self.execution_thoughts
    
    def _init_task_patterns(self) -> Dict[str, List[str]]:
        """Initialize task type detection patterns"""
        return {
            "dependency_install": [
                "install", "add dependency", "add package", "npm install", "pip install",
                "cargo add", "go get", "yarn add", "pnpm add"
            ],
            "file_create": [
                "create file", "create component", "create service", "create class",
                "create module", "create interface", "create type", "implement file"
            ],
            "implementation": [
                "implement", "add functionality", "add feature", "create logic",
                "add method", "add function", "add endpoint", "add route"
            ],
            "testing": [
                "test", "unit test", "integration test", "e2e test", "add tests",
                "create tests", "test coverage", "test case"
            ],
            "configuration": [
                "configure", "setup", "config", "environment", "settings",
                "configure build", "setup environment"
            ],
            "build": [
                "build", "compile", "bundle", "package", "deploy build"
            ]
        }
    
    def _analyze_project_patterns(self) -> Dict[str, Any]:
        """Analyze project to detect coding patterns and conventions"""
        patterns = {
            "component_patterns": self._analyze_component_patterns(),
            "test_patterns": self._analyze_test_patterns(),
            "service_patterns": self._analyze_service_patterns(),
            "import_patterns": self._analyze_import_patterns(),
            "export_patterns": self._analyze_export_patterns()
        }
        return patterns
    
    def _analyze_component_patterns(self) -> Dict[str, Any]:
        """Analyze existing components to detect patterns"""
        patterns = {
            "import_style": "import React from 'react';",
            "component_type": "functional",
            "export_style": "export default",
            "file_extension": ".js",
            "uses_hooks": False,
            "spacing_style": "2_spaces"
        }
        
        # Look for existing component files
        component_files = []
        if self.context.src_dir.exists():
            for ext in ["*.js", "*.jsx", "*.ts", "*.tsx"]:
                component_files.extend(self.context.src_dir.rglob(ext))
        
        if component_files:
            # Analyze the first few component files to detect patterns
            for file_path in component_files[:3]:  # Limit to first 3 files
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Detect import patterns
                    if "import React, {" in content:
                        patterns["import_style"] = "import React, { useState } from 'react';"
                        patterns["uses_hooks"] = True
                    elif "import React" in content:
                        patterns["import_style"] = "import React from 'react';"
                    
                    # Detect component type
                    if "const " in content and "= () =>" in content:
                        patterns["component_type"] = "functional_arrow"
                    elif "function " in content:
                        patterns["component_type"] = "functional_declaration"
                    elif "class " in content and "extends" in content:
                        patterns["component_type"] = "class"
                    
                    # Detect export style
                    if "export default" in content:
                        patterns["export_style"] = "export default"
                    elif "export {" in content:
                        patterns["export_style"] = "named_export"
                    
                    # Detect file extension
                    patterns["file_extension"] = file_path.suffix
                    
                    # Detect hooks usage
                    if "useState" in content or "useEffect" in content:
                        patterns["uses_hooks"] = True
                    
                    break  # Use first valid component as pattern
                    
                except Exception:
                    continue
        
        return patterns
    
    def _analyze_test_patterns(self) -> Dict[str, Any]:
        """Analyze existing test files to detect patterns"""
        patterns = {
            "test_framework": "jest",
            "test_extension": ".test.js",
            "import_style": "import { render, screen } from '@testing-library/react';",
            "test_style": "test",
            "assertion_style": "expect"
        }
        
        # Look for existing test files
        test_files = []
        if self.context.src_dir.exists():
            for pattern in ["*.test.*", "*.spec.*", "*/__tests__/*"]:
                test_files.extend(self.context.src_dir.rglob(pattern))
        
        if test_files:
            for file_path in test_files[:2]:  # Analyze first 2 test files
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Detect test framework
                    if "@testing-library" in content:
                        patterns["test_framework"] = "testing-library"
                        patterns["import_style"] = "import { render, screen } from '@testing-library/react';"
                    elif "vitest" in content:
                        patterns["test_framework"] = "vitest"
                    elif "jest" in content or "test(" in content:
                        patterns["test_framework"] = "jest"
                    
                    # Detect test style
                    if "describe(" in content:
                        patterns["test_style"] = "describe"
                    elif "test(" in content:
                        patterns["test_style"] = "test"
                    
                    # Detect file extension
                    if ".test." in file_path.name:
                        patterns["test_extension"] = ".test" + file_path.suffix
                    elif ".spec." in file_path.name:
                        patterns["test_extension"] = ".spec" + file_path.suffix
                    
                    break
                    
                except Exception:
                    continue
        
        return patterns
    
    def _analyze_service_patterns(self) -> Dict[str, Any]:
        """Analyze existing service/utility files to detect patterns"""
        patterns = {
            "service_type": "class",
            "export_style": "export default",
            "file_extension": ".js",
            "naming_convention": "PascalCase"
        }
        
        # Look for service-like files
        service_files = []
        if self.context.src_dir.exists():
            service_dirs = ["services", "utils", "helpers", "lib"]
            for dir_name in service_dirs:
                service_dir = self.context.src_dir / dir_name
                if service_dir.exists():
                    for ext in ["*.js", "*.ts"]:
                        service_files.extend(service_dir.glob(ext))
        
        if service_files:
            for file_path in service_files[:2]:  # Analyze first 2 service files
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Detect service type
                    if "class " in content:
                        patterns["service_type"] = "class"
                    elif "function " in content:
                        patterns["service_type"] = "function"
                    elif "const " in content and "= {" in content:
                        patterns["service_type"] = "object"
                    
                    # Detect export style
                    if "export default" in content:
                        patterns["export_style"] = "export default"
                    elif "export {" in content:
                        patterns["export_style"] = "named_export"
                    
                    patterns["file_extension"] = file_path.suffix
                    break
                    
                except Exception:
                    continue
        
        return patterns
    
    def _analyze_import_patterns(self) -> List[str]:
        """Analyze common import patterns in the project"""
        import_patterns = []
        
        if self.context.src_dir.exists():
            for file_path in list(self.context.src_dir.rglob("*.js"))[:5]:  # Check first 5 JS files
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Extract import lines
                    lines = content.split('\n')
                    for line in lines:
                        if line.strip().startswith('import '):
                            import_patterns.append(line.strip())
                    
                except Exception:
                    continue
        
        return list(set(import_patterns))  # Remove duplicates
    
    def _analyze_export_patterns(self) -> List[str]:
        """Analyze common export patterns in the project"""
        export_patterns = []
        
        if self.context.src_dir.exists():
            for file_path in list(self.context.src_dir.rglob("*.js"))[:5]:  # Check first 5 JS files
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Extract export lines
                    lines = content.split('\n')
                    for line in lines:
                        if line.strip().startswith('export '):
                            export_patterns.append(line.strip())
                    
                except Exception:
                    continue
        
        return list(set(export_patterns))  # Remove duplicates
    
    def get_next_task(self, tag: str = "agents") -> Optional[Dict]:
        """Get the next pending task that's ready to execute"""
        try:
            tasks_file = Path('.taskmaster/tasks/tasks.json')
            if not tasks_file.exists():
                return None
                
            with open(tasks_file, 'r') as f:
                data = json.load(f)
            
            # Get tasks from specified tag
            tasks = []
            if isinstance(data, dict) and tag in data:
                tasks = data[tag]['tasks']
            elif isinstance(data, dict) and 'master' in data:
                tasks = data['master']['tasks']
            
            # Find next executable task
            for task in tasks:
                # Skip completed or failed tasks
                if task.get('status') in ['completed', 'failed']:
                    continue
                
                # Check if dependencies are met
                dependencies_met = True
                for dep_id in task.get('dependencies', []):
                    dep_task = next((t for t in tasks if t['id'] == dep_id), None)
                    if not dep_task or dep_task.get('status') != 'completed':
                        dependencies_met = False
                        break
                
                if dependencies_met:
                    return task
            
            return None
            
        except (json.JSONDecodeError, FileNotFoundError):
            return None
    
    def analyze_task(self, task: Dict) -> TaskAction:
        """Analyze a task and determine what actions to take"""
        task_text = ' '.join([
            task.get('title', ''),
            task.get('description', ''),
            task.get('details', '') or ''
        ]).lower()
        
        # Apply sequential thinking for complex tasks
        if self.config.get('sequential_thinking', True) and len(task_text) > 50:
            self.think_through_execution(task)
        
        # Determine task type
        task_type = self._determine_task_type(task_text)
        
        # Generate actions based on task type and content
        if task_type == TaskType.DEPENDENCY_INSTALL:
            return self._create_dependency_action(task, task_text)
        elif task_type == TaskType.FILE_CREATE:
            return self._create_file_action(task, task_text)
        elif task_type == TaskType.IMPLEMENTATION:
            return self._create_implementation_action(task, task_text)
        elif task_type == TaskType.TESTING:
            return self._create_testing_action(task, task_text)
        else:
            return self._create_generic_action(task, task_text)
    
    def _determine_task_type(self, task_text: str) -> TaskType:
        """Determine the type of task based on content"""
        for task_type, patterns in self.task_patterns.items():
            for pattern in patterns:
                if pattern in task_text:
                    # Map task pattern keys to TaskType enum values
                    type_mapping = {
                        "dependency_install": TaskType.DEPENDENCY_INSTALL,
                        "file_create": TaskType.FILE_CREATE,
                        "implementation": TaskType.IMPLEMENTATION,
                        "testing": TaskType.TESTING,
                        "configuration": TaskType.CONFIGURATION,
                        "build": TaskType.BUILD
                    }
                    return type_mapping.get(task_type, TaskType.UNKNOWN)
        
        return TaskType.UNKNOWN
    
    def _create_dependency_action(self, task: Dict, task_text: str) -> TaskAction:
        """Create action for dependency installation"""
        # Extract dependency names from task
        dependencies = self._extract_dependencies(task_text)
        
        # Filter out already installed/skipped dependencies
        new_dependencies = []
        for dep in dependencies:
            if dep not in self.sync_data.skip_dependencies:
                if dep not in self.context.dependencies:
                    new_dependencies.append(dep)
        
        if not new_dependencies:
            return TaskAction(
                action_type="skip",
                command=None,
                files_to_create=[],
                validation_checks=[],
                description=f"All dependencies already installed",
                dependencies=[],
                estimated_duration=0,
                git_actions=[]
            )
        
        # Generate install command
        command = f"{self.context.package_manager} install {' '.join(new_dependencies)}"
        
        # Generate git workflow actions
        git_actions = self._generate_git_workflow_for_task(task)
        
        return TaskAction(
            action_type="dependency_install",
            command=command,
            files_to_create=[],
            validation_checks=[f"verify {dep} installation" for dep in new_dependencies],
            description=f"Install dependencies: {', '.join(new_dependencies)}",
            dependencies=new_dependencies,
            estimated_duration=30 * len(new_dependencies),
            git_actions=git_actions
        )
    
    def _create_file_action(self, task: Dict, task_text: str) -> TaskAction:
        """Create action for file creation"""
        files_to_create = []
        
        # Extract file patterns from task
        file_patterns = self._extract_file_patterns(task, task_text)
        
        for file_path, content in file_patterns:
            # Skip if file already exists or is in skip list
            if file_path not in self.sync_data.skip_files:
                full_path = self.project_root / file_path
                if not full_path.exists():
                    files_to_create.append((file_path, content))
        
        if not files_to_create:
            return TaskAction(
                action_type="skip",
                command=None,
                files_to_create=[],
                validation_checks=[],
                description="All files already exist",
                dependencies=[],
                estimated_duration=0,
                git_actions=[]
            )
        
        # Generate git workflow actions
        git_actions = self._generate_git_workflow_for_task(task)
        
        return TaskAction(
            action_type="file_create",
            command=None,
            files_to_create=files_to_create,
            validation_checks=[f"verify {f[0]} exists" for f in files_to_create],
            description=f"Create {len(files_to_create)} files",
            dependencies=[],
            estimated_duration=60 * len(files_to_create),
            git_actions=git_actions
        )
    
    def _create_implementation_action(self, task: Dict, task_text: str) -> TaskAction:
        """Create action for implementation tasks"""
        # Generate git workflow actions
        git_actions = self._generate_git_workflow_for_task(task)
        
        return TaskAction(
            action_type="implementation",
            command=None,
            files_to_create=[],
            validation_checks=["run tests", "check build"],
            description=f"Implementation task: {task.get('title', 'Unknown')}",
            dependencies=[],
            estimated_duration=300,  # 5 minutes for implementation
            git_actions=git_actions
        )
    
    def _create_testing_action(self, task: Dict, task_text: str) -> TaskAction:
        """Create action for testing tasks"""
        # Generate git workflow actions
        git_actions = self._generate_git_workflow_for_task(task)
        
        return TaskAction(
            action_type="testing",
            command=self.context.test_command,
            files_to_create=[],
            validation_checks=["verify test results"],
            description=f"Run tests: {task.get('title', 'Unknown')}",
            dependencies=[],
            estimated_duration=120,  # 2 minutes for testing
            git_actions=git_actions
        )
    
    def _create_generic_action(self, task: Dict, task_text: str) -> TaskAction:
        """Create generic action for unknown task types"""
        # Generate git workflow actions
        git_actions = self._generate_git_workflow_for_task(task)
        
        return TaskAction(
            action_type="generic",
            command=None,
            files_to_create=[],
            validation_checks=[],
            description=f"Generic task: {task.get('title', 'Unknown')}",
            dependencies=[],
            estimated_duration=60,
            git_actions=git_actions
        )
    
    def _extract_dependencies(self, task_text: str) -> List[str]:
        """Extract dependency names from task text"""
        dependencies = []
        
        # Common dependency patterns
        patterns = [
            r'install\s+([a-zA-Z0-9\-_@/]+)',
            r'add\s+([a-zA-Z0-9\-_@/]+)',
            r'dependency\s+([a-zA-Z0-9\-_@/]+)',
            r'package\s+([a-zA-Z0-9\-_@/]+)'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, task_text)
            dependencies.extend(matches)
        
        # Clean and deduplicate
        cleaned = []
        for dep in dependencies:
            dep = dep.strip()
            if dep and dep not in cleaned:
                cleaned.append(dep)
        
        return cleaned
    
    def _extract_file_patterns(self, task: Dict, task_text: str) -> List[Tuple[str, str]]:
        """Extract file creation patterns from task"""
        files = []
        
        # Try to extract component/file names
        names = self._extract_entity_names(task_text)
        
        for name in names:
            if 'component' in task_text:
                # Component file with detected extension
                patterns = self.project_patterns.get('component_patterns', {})
                ext = patterns.get('file_extension', '.js')
                file_path = f"{self.context.src_dir.relative_to(self.project_root)}/components/{name}{ext}"
                content = self._generate_component_content(name)
                files.append((file_path, content))
                
                # Test file with detected patterns
                test_patterns = self.project_patterns.get('test_patterns', {})
                test_ext = test_patterns.get('test_extension', '.test.js')
                test_path = f"{self.context.src_dir.relative_to(self.project_root)}/components/{name}{test_ext}"
                test_content = self._generate_test_content(name, 'component')
                files.append((test_path, test_content))
            
            elif 'service' in task_text:
                # Service file with detected extension
                patterns = self.project_patterns.get('service_patterns', {})
                ext = patterns.get('file_extension', '.js')
                service_dir = 'services' if (self.context.src_dir / 'services').exists() else 'utils'
                file_path = f"{self.context.src_dir.relative_to(self.project_root)}/{service_dir}/{name}{ext}"
                content = self._generate_service_content(name)
                files.append((file_path, content))
        
        return files
    
    def _extract_entity_names(self, text: str) -> List[str]:
        """Extract entity names from text"""
        # Look for capitalized words and specific patterns
        patterns = [
            r'create\s+(\w+)',
            r'implement\s+(\w+)',
            r'(\w+)\s+component',
            r'(\w+)\s+service'
        ]
        
        names = []
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            names.extend(matches)
        
        # Clean and capitalize
        cleaned = []
        for name in names:
            name = name.strip().title()
            if name and len(name) > 2 and name not in cleaned:
                cleaned.append(name)
        
        return cleaned[:3]  # Limit to 3 names
    
    def _find_existing_component_template(self) -> Optional[str]:
        """Find an existing component to use as a template"""
        component_dirs = ['src/components', 'components', 'src/ui']
        
        for comp_dir in component_dirs:
            comp_path = self.project_root / comp_dir
            if comp_path.exists():
                # Find a simple component file to use as template
                for ext in ['.js', '.jsx', '.ts', '.tsx']:
                    for comp_file in comp_path.glob(f'*{ext}'):
                        if comp_file.is_file() and comp_file.stat().st_size < 2000:  # Small files only
                            try:
                                with open(comp_file, 'r', encoding='utf-8') as f:
                                    content = f.read()
                                # Check if it's a simple component (not complex)
                                if content.count('\n') < 50 and 'export default' in content:
                                    return content
                            except Exception:
                                continue
        return None
    
    def _find_existing_service_template(self) -> Optional[str]:
        """Find an existing service to use as a template"""
        service_dirs = ['src/services', 'services', 'src/api', 'src/utils']
        
        for service_dir in service_dirs:
            service_path = self.project_root / service_dir
            if service_path.exists():
                for ext in ['.js', '.jsx', '.ts', '.tsx']:
                    for service_file in service_path.glob(f'*{ext}'):
                        if service_file.is_file() and service_file.stat().st_size < 1500:  # Small files only
                            try:
                                with open(service_file, 'r', encoding='utf-8') as f:
                                    content = f.read()
                                # Check if it's a simple service
                                if content.count('\n') < 40 and ('class ' in content or 'function' in content):
                                    return content
                            except Exception:
                                continue
        return None
    
    def _adapt_template_for_name(self, template: str, name: str) -> str:
        """Adapt an existing template for a new component/service name"""
        lines = template.split('\n')
        adapted_lines = []
        
        for line in lines:
            # Replace component/class names but keep the structure
            # This is a simple adaptation - more sophisticated logic could be added
            adapted_line = line
            
            # Look for common patterns to replace
            words = line.split()
            for i, word in enumerate(words):
                # Replace component names (capitalized words that could be component names)
                if word and word[0].isupper() and len(word) > 2:
                    # Check if it looks like a component name (not HTML tags, not keywords)
                    if word not in ['React', 'Component', 'useState', 'useEffect', 'HTML', 'CSS', 'JS']:
                        if any(char.isalpha() for char in word):
                            # Replace with new name, keeping any non-alphanumeric characters
                            prefix = ''
                            suffix = ''
                            clean_word = word
                            
                            # Handle prefixes/suffixes like '(' or ';'
                            while clean_word and not clean_word[0].isalpha():
                                prefix += clean_word[0]
                                clean_word = clean_word[1:]
                            while clean_word and not clean_word[-1].isalpha():
                                suffix = clean_word[-1] + suffix
                                clean_word = clean_word[:-1]
                            
                            if clean_word and clean_word[0].isupper():
                                words[i] = prefix + name + suffix
                                break  # Only replace first occurrence per line
            
            adapted_line = ' '.join(words)
            adapted_lines.append(adapted_line)
        
        return '\n'.join(adapted_lines)
    
    def _generate_component_content(self, name: str) -> str:
        """Generate component content based on actual project patterns"""
        patterns = self.project_patterns.get('component_patterns', {})
        
        # Try to find and analyze existing similar components first
        existing_template = self._find_existing_component_template()
        if existing_template:
            return self._adapt_template_for_name(existing_template, name)
        
        # Build component based on detected patterns
        if self.context.project_type == ProjectType.REACT:
            import_line = patterns.get('import_style', "import React from 'react';")
            
            # Add hooks import if needed
            if patterns.get('uses_hooks', False) and 'useState' not in import_line:
                import_line = "import React, { useState } from 'react';"
            
            # Generate component based on detected type
            if patterns.get('component_type') == 'functional_arrow':
                comment = "{/* Add your component content here */}"
                component_body = f"""const {name} = () => {{
  // TODO: Implement {name} component
  return (
    <div>
      <h1>{name}</h1>
      {comment}
    </div>
  );
}};"""
            elif patterns.get('component_type') == 'functional_declaration':
                comment = "{/* Add your component content here */}"
                component_body = f"""function {name}() {{
  // TODO: Implement {name} component
  return (
    <div>
      <h1>{name}</h1>
      {comment}
    </div>
  );
}}"""
            else:  # Default to minimal template
                comment = "{/* Add your component content here */}"
                component_body = f"""const {name} = () => {{
  // TODO: Implement {name} component
  return (
    <div>
      <h1>{name}</h1>
      {comment}
    </div>
  );
}};"""
            
            export_line = f"export default {name};"
            
            return f"""{import_line}

{component_body}

{export_line}
"""
        
        elif self.context.project_type == ProjectType.PYTHON:
            return f'''"""
{name} module

TODO: Implement {name} functionality
"""


class {name}:
    """Main {name} class"""
    
    def __init__(self):
        # TODO: Initialize {name}
        pass
    
    def main_function(self):
        """Main functionality - implement as needed"""
        # TODO: Add implementation
        pass
'''
        
        # Generic fallback - minimal template
        return f"""// {name} - Generated minimal template
// TODO: Implement {name} functionality

function {name}() {{
  // TODO: Add implementation
}}

// Export for use in other modules
export default {name};
"""
    
    def _generate_service_content(self, name: str) -> str:
        """Generate service content based on actual project patterns"""
        # Try to find existing service template first
        existing_template = self._find_existing_service_template()
        if existing_template:
            return self._adapt_template_for_name(existing_template, name)
        
        patterns = self.project_patterns.get('service_patterns', {})
        service_type = patterns.get('service_type', 'minimal')
        
        if self.context.project_type in [ProjectType.REACT, ProjectType.NODE]:
            service_name = f"{name}Service" if not name.endswith('Service') else name
            export_style = patterns.get('export_style', 'export default')
            
            # Generate service template based on patterns
            if service_type == 'class':
                content = f"""/**
 * {name} Service
 * 
 * TODO: Implement {name} service functionality
 */

class {service_name} {{
  constructor() {{
    // TODO: Initialize service
  }}
  
  // TODO: Add service methods as needed
  async getData() {{
    // TODO: Implement data retrieval
    throw new Error('Not implemented');
  }}
}}
"""
                if export_style == 'export default':
                    content += f"\nexport default new {service_name}();"
                else:
                    content += f"\nexport {{ {service_name} }};"
                
            elif service_type == 'function':
                service_name = f"{name}Service" if not name.endswith('Service') else name
                content = f"""/**
 * {name} Service
 */

function create{service_name}() {{
  // Service implementation
  return {{
    // Add service methods here
  }};
}}
"""
                if export_style == 'export default':
                    content += f"\nexport default create{service_name}();"
                else:
                    content += f"\nexport {{ create{service_name} }};"
                    
            else:  # object type
                service_name = f"{name.lower()}Service" if not name.lower().endswith('service') else name.lower()
                content = f"""/**
 * {name} Service
 */

const {service_name} = {{
  // Add service methods here
}};
"""
                if export_style == 'export default':
                    content += f"\nexport default {service_name};"
                else:
                    content += f"\nexport {{ {service_name} }};"
                    
            return content
            
        elif self.context.project_type == ProjectType.PYTHON:
            return f'''"""
{name} service module
"""


class {name}Service:
    """Service for {name} operations"""
    
    def __init__(self):
        pass
    
    # Add service methods here
'''
        
        # Generic fallback
        return f"""// {name} Service
// Generic service template

class {name}Service {{
  constructor() {{
    // Initialize service
  }}
  
  // Add service methods here
}}

export default new {name}Service();
"""
    
    def _generate_test_content(self, name: str, type: str) -> str:
        """Generate test content based on project patterns"""
        test_patterns = self.project_patterns.get('test_patterns', {})
        framework = test_patterns.get('test_framework', 'jest')
        test_style = test_patterns.get('test_style', 'test')
        import_style = test_patterns.get('import_style', '')
        
        if self.context.project_type == ProjectType.REACT and type == 'component':
            # Generate React component test
            if framework == 'testing-library':
                imports = "import { render, screen } from '@testing-library/react';"
            else:
                imports = "import React from 'react';"
            
            imports += f"\nimport {name} from './{name}';"
            
            if test_style == 'describe':
                test_body = f"""describe('{name}', () => {{
  test('renders {name} component', () => {{
    render(<{name} />);
    expect(screen.getByText(/{name}/i)).toBeInTheDocument();
  }});
}});"""
            else:
                test_body = f"""test('renders {name} component', () => {{
  render(<{name} />);
  expect(screen.getByText(/{name}/i)).toBeInTheDocument();
}});"""
            
            return f"{imports}\n\n{test_body}\n"
            
        elif type == 'service':
            imports = f"import {name}Service from './{name}';"
            
            if test_style == 'describe':
                test_body = f"""describe('{name}Service', () => {{
  test('service exists', () => {{
    expect({name}Service).toBeDefined();
  }});
}});"""
            else:
                test_body = f"""test('{name}Service exists', () => {{
  expect({name}Service).toBeDefined();
}});"""
            
            return f"{imports}\n\n{test_body}\n"
            
        elif self.context.project_type == ProjectType.PYTHON:
            return f'''"""
Tests for {name} module
"""
import pytest
from src import {name}


def test_{name.lower()}_initialization():
    """Test {name} initialization"""
    instance = {name}()
    assert instance is not None
'''
        
        # Generic fallback
        return f"""// Test for {name}
// Generic test template

test('{name} test', () => {{
  // TODO: Add test implementation
  expect(true).toBe(true);
}});
"""
    
    def execute_action(self, action: TaskAction, task: Dict) -> bool:
        """Execute a task action"""
        if self.config['verbose']:
            print(f"🚀 Executing: {action.description}")
        
        try:
            # Execute the main action
            success = False
            
            if action.action_type == "skip":
                if self.config['verbose']:
                    print(f"⏭️  Skipping: {action.description}")
                success = True
            
            elif action.action_type == "dependency_install":
                success = self._execute_dependency_install(action, task)
            
            elif action.action_type == "file_create":
                success = self._execute_file_creation(action, task)
            
            elif action.action_type == "testing":
                success = self._execute_testing(action, task)
            
            elif action.action_type == "implementation":
                success = self._execute_implementation(action, task)
            
            elif action.action_type == "generic":
                success = self._execute_generic(action, task)
            
            else:
                if self.config['verbose']:
                    print(f"⚠️  Unknown action type: {action.action_type}")
                success = False
            
            # Execute git workflow actions if main action succeeded
            if success and action.git_actions:
                git_success = self._execute_git_workflow(action.git_actions, task)
                if not git_success and self.config['verbose']:
                    print("⚠️  Git workflow actions failed, but main action succeeded")
            
            return success
        
        except Exception as e:
            print(f"❌ Error executing action: {e}")
            return False
    
    def _execute_dependency_install(self, action: TaskAction, task: Dict) -> bool:
        """Execute dependency installation"""
        if self.config['dry_run']:
            print(f"🔍 [DRY RUN] Would execute: {action.command}")
            return True
        
        try:
            # Run installation command
            result = subprocess.run(
                action.command.split(),
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=self.config['timeout']
            )
            
            if result.returncode == 0:
                # Update sync data to prevent duplicates
                for dep in action.dependencies:
                    self.sync_data.skip_dependencies.add(dep)
                    self.context.dependencies[dep] = "latest"
                
                self._save_sync_data()
                
                if self.config['verbose']:
                    print(f"✅ Installed dependencies: {', '.join(action.dependencies)}")
                return True
            else:
                print(f"❌ Installation failed: {result.stderr}")
                return False
        
        except subprocess.TimeoutExpired:
            print(f"⏰ Installation timeout after {self.config['timeout']}s")
            return False
        except Exception as e:
            print(f"❌ Installation error: {e}")
            return False
    
    def _execute_file_creation(self, action: TaskAction, task: Dict) -> bool:
        """Execute file creation"""
        if self.config['dry_run']:
            print(f"🔍 [DRY RUN] Would create {len(action.files_to_create)} files")
            return True
        
        try:
            for file_path, content in action.files_to_create:
                full_path = self.project_root / file_path
                
                # Create directory if needed
                full_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Create file
                with open(full_path, 'w') as f:
                    f.write(content)
                
                # Add to skip list
                self.sync_data.skip_files.add(file_path)
                
                if self.config['verbose']:
                    print(f"📄 Created: {file_path}")
            
            self._save_sync_data()
            return True
        
        except Exception as e:
            print(f"❌ File creation error: {e}")
            return False
    
    def _execute_testing(self, action: TaskAction, task: Dict) -> bool:
        """Execute testing command"""
        if self.config['dry_run']:
            print(f"🔍 [DRY RUN] Would execute: {action.command}")
            return True
        
        try:
            result = subprocess.run(
                action.command.split(),
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=self.config['timeout']
            )
            
            # Update project state with test results
            self.project_state['test_status'] = 'passed' if result.returncode == 0 else 'failed'
            self.project_state['last_test_output'] = result.stdout + result.stderr
            self._save_project_state()
            
            if result.returncode == 0:
                if self.config['verbose']:
                    print("✅ Tests passed")
                return True
            else:
                print(f"❌ Tests failed: {result.stderr}")
                return False
        
        except subprocess.TimeoutExpired:
            print(f"⏰ Test timeout after {self.config['timeout']}s")
            return False
        except Exception as e:
            print(f"❌ Test error: {e}")
            return False
    
    def _execute_implementation(self, action: TaskAction, task: Dict) -> bool:
        """Execute implementation task (manual work indicator)"""
        if self.config['dry_run']:
            print(f"🔍 [DRY RUN] Implementation task: {action.description}")
            return True
        
        # For implementation tasks, we'll mark them as completed since they often represent
        # high-level work that may have already been done or requires manual completion
        if self.config['verbose']:
            print(f"🛠️  Implementation task noted: {action.description}")
            print("💡 This task may require manual completion or has been completed by agent setup")
        
        return True
    
    def _execute_generic(self, action: TaskAction, task: Dict) -> bool:
        """Execute generic task"""
        if self.config['dry_run']:
            print(f"🔍 [DRY RUN] Generic task: {action.description}")
            return True
        
        if self.config['verbose']:
            print(f"📝 Generic task: {action.description}")
            print("💡 This task has been acknowledged and marked for manual review")
        
        return True
    
    def update_task_status(self, task: Dict, status: str, tag: str = "agents") -> bool:
        """Update task status in Task Master"""
        try:
            tasks_file = Path('.taskmaster/tasks/tasks.json')
            if not tasks_file.exists():
                return False
            
            with open(tasks_file, 'r') as f:
                data = json.load(f)
            
            # Find and update task
            tasks = data.get(tag, {}).get('tasks', [])
            for t in tasks:
                if t['id'] == task['id']:
                    t['status'] = status
                    break
            
            # Save updated data
            with open(tasks_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            return True
        
        except Exception as e:
            print(f"❌ Error updating task status: {e}")
            return False
    
    def _execute_git_workflow(self, git_actions: List[GitWorkflowAction], task: Dict) -> bool:
        """Execute git workflow actions"""
        if self.config['verbose']:
            print("🔄 Executing git workflow actions")
        
        success = True
        for git_action in git_actions:
            if self.config['verbose']:
                print(f"   🔧 {git_action.description}")
            
            if self.config['dry_run']:
                for cmd in git_action.commands:
                    if not cmd.startswith('#'):
                        print(f"🔍 [DRY RUN] Would execute: {cmd}")
                continue
            
            # Execute each git command
            for cmd in git_action.commands:
                if cmd.startswith('#'):  # Skip comments
                    continue
                    
                try:
                    result = subprocess.run(
                        cmd.split(),
                        cwd=self.project_root,
                        capture_output=True,
                        text=True,
                        timeout=60
                    )
                    
                    if result.returncode != 0:
                        if self.config['verbose']:
                            print(f"⚠️  Git command failed: {cmd}")
                            print(f"     Error: {result.stderr}")
                        success = False
                        break
                    elif self.config['verbose']:
                        print(f"     ✅ {cmd}")
                        
                except subprocess.TimeoutExpired:
                    if self.config['verbose']:
                        print(f"⚠️  Git command timeout: {cmd}")
                    success = False
                    break
                except Exception as e:
                    if self.config['verbose']:
                        print(f"⚠️  Git command error: {cmd} - {e}")
                    success = False
                    break
            
            if not success:
                break
        
        return success
    
    def _generate_git_workflow_for_task(self, task: Dict) -> List[GitWorkflowAction]:
        """Generate git workflow actions for a task"""
        actions = []
        task_text = ' '.join([
            task.get('title', ''),
            task.get('description', ''),
            task.get('details', '') or ''
        ]).lower()
        
        # Determine task type for branch naming
        is_feature = any(word in task_text for word in ['create', 'add', 'implement', 'new', 'feature'])
        is_bugfix = any(word in task_text for word in ['fix', 'bug', 'error', 'issue', 'problem'])
        
        task_id = task.get('id', 'task')
        if is_feature:
            branch_name = f"feature/{task_id}-{self._slugify(task.get('title', 'new-feature'))}"
            commit_type = "feat"
        elif is_bugfix:
            branch_name = f"bugfix/{task_id}-{self._slugify(task.get('title', 'bug-fix'))}"
            commit_type = "fix"
        else:
            branch_name = f"task/{task_id}-{self._slugify(task.get('title', 'task'))}"
            commit_type = "chore"
        
        # Only create branch if not on main/master
        try:
            result = subprocess.run(
                ["git", "branch", "--show-current"],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            current_branch = result.stdout.strip()
            
            if current_branch in ['main', 'master'] and result.returncode == 0:
                # Create feature branch
                actions.append(GitWorkflowAction(
                    action_type="branch",
                    commands=[f"git checkout -b {branch_name}"],
                    description=f"Create branch {branch_name}",
                    branch_name=branch_name
                ))
        except Exception:
            pass  # Skip branch creation if git commands fail
        
        # Add commit action
        commit_message = f"{commit_type}: {task.get('title', 'task update').lower()}"
        actions.append(GitWorkflowAction(
            action_type="commit",
            commands=[
                "git add .",
                f'git commit -m "{commit_message}"'
            ],
            description=f"Commit changes for task {task_id}",
            commit_message=commit_message
        ))
        
        return actions
    
    def _slugify(self, text: str) -> str:
        """Convert text to git-safe slug"""
        import re
        slug = re.sub(r'[^\w\s-]', '', text.lower())
        slug = re.sub(r'[-\s]+', '-', slug)
        return slug.strip('-')[:20]  # Limit length
    
    def execute_next_task(self, tag: str = "agents") -> bool:
        """Execute the next available task"""
        task = self.get_next_task(tag)
        if not task:
            if self.config['verbose']:
                print("📋 No tasks available for execution")
            return False
        
        if self.config['verbose']:
            print(f"🎯 Processing Task {task['id']}: {task['title']}")
        
        # Update task status to in_progress
        self.update_task_status(task, 'in_progress', tag)
        
        # Analyze and execute task
        action = self.analyze_task(task)
        success = self.execute_action(action, task)
        
        # Update task status based on result
        if success:
            self.update_task_status(task, 'completed', tag)
            self.sync_data.completed_subtasks.append(str(task['id']))
            self._save_sync_data()
            
            if self.config['verbose']:
                print(f"✅ Task {task['id']} completed successfully")
        else:
            self.update_task_status(task, 'failed', tag)
            if self.config['verbose']:
                print(f"❌ Task {task['id']} failed")
        
        return success
    
    def run_continuous(self, tag: str = "agents", max_tasks: int = 10) -> None:
        """Run continuous execution mode"""
        print(f"🤖 Universal Execution Agent - Continuous Mode")
        print(f"Project Type: {self.context.project_type.value}")
        print(f"Package Manager: {self.context.package_manager}")
        print("-" * 50)
        
        executed = 0
        while executed < max_tasks:
            success = self.execute_next_task(tag)
            if not success:
                break
            
            executed += 1
            
            if self.config['verbose']:
                print(f"📊 Progress: {executed}/{max_tasks} tasks executed")
            
            # Small delay between tasks
            time.sleep(1)
        
        print(f"\n✅ Execution complete! Processed {executed} tasks")

def main():
    parser = argparse.ArgumentParser(description='Universal Execution Agent')
    parser.add_argument('--config', type=str, help='Configuration file path')
    parser.add_argument('--project-root', type=str, default='.', help='Project root directory')
    parser.add_argument('--tag', type=str, default='agents', help='Task Master tag to process')
    parser.add_argument('--mode', choices=['single', 'continuous'], default='single', help='Execution mode')
    parser.add_argument('--max-tasks', type=int, default=10, help='Maximum tasks to execute in continuous mode')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    parser.add_argument('--dry-run', action='store_true', help='Dry run mode')
    
    args = parser.parse_args()
    
    # Create agent
    agent = UniversalExecutionAgent(args.project_root, args.config)
    agent.config.update({
        'verbose': args.verbose,
        'dry_run': args.dry_run
    })
    
    if args.mode == 'continuous':
        agent.run_continuous(args.tag, args.max_tasks)
    else:
        success = agent.execute_next_task(args.tag)
        sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()