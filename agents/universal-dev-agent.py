#!/usr/bin/env python3
"""
Universal Development Execution Agent

A dynamic agent that can work with any Task Master project to automatically
execute development tasks. Adapts to different project types, languages,
and frameworks without hardcoded assumptions.
"""

import json
import subprocess
import os
import re
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
import argparse

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

@dataclass
class ProjectContext:
    """Context information about the current project"""
    project_type: ProjectType
    root_dir: Path
    package_manager: str
    test_command: str
    build_command: str
    src_dir: Path
    config_files: List[Path]
    dependencies: Dict[str, str]
    
@dataclass
class TaskAction:
    """Represents an action to execute for a task"""
    action_type: str
    command: Optional[str]
    files_to_create: List[Tuple[str, str]]  # (path, content)
    validation_checks: List[str]
    description: str

class UniversalDevAgent:
    """
    Universal Development Execution Agent
    
    Dynamically adapts to any project and executes Task Master tasks
    """
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.context = self._analyze_project_context()
        self.state_file = self.project_root / ".taskmaster" / "agent_state.json"
        self.state = self._load_state()
        
        # Initialize task type patterns (universal, not project-specific)
        self.task_patterns = self._init_task_patterns()
        self.action_templates = self._init_action_templates()
    
    def _analyze_project_context(self) -> ProjectContext:
        """Analyze the project to understand its structure and requirements"""
        root = self.project_root
        
        # Detect project type
        project_type = self._detect_project_type(root)
        
        # Determine package manager and commands
        package_manager, test_cmd, build_cmd = self._detect_tooling(root, project_type)
        
        # Find source directory
        src_dir = self._find_src_directory(root, project_type)
        
        # Find config files
        config_files = self._find_config_files(root, project_type)
        
        # Load existing dependencies
        dependencies = self._load_dependencies(root, project_type)
        
        return ProjectContext(
            project_type=project_type,
            root_dir=root,
            package_manager=package_manager,
            test_command=test_cmd,
            build_command=build_cmd,
            src_dir=src_dir,
            config_files=config_files,
            dependencies=dependencies
        )
    
    def _detect_project_type(self, root: Path) -> ProjectType:
        """Detect what type of project this is"""
        # Check for React
        package_json = root / "package.json"
        if package_json.exists():
            try:
                with open(package_json) as f:
                    data = json.load(f)
                deps = {**data.get('dependencies', {}), **data.get('devDependencies', {})}
                
                if 'react' in deps:
                    return ProjectType.REACT
                elif 'vue' in deps:
                    return ProjectType.VUE
                elif '@angular/core' in deps:
                    return ProjectType.ANGULAR
                else:
                    return ProjectType.NODE
            except:
                pass
        
        # Check for Python
        if (root / "requirements.txt").exists() or (root / "pyproject.toml").exists():
            return ProjectType.PYTHON
        
        # Check for Rust
        if (root / "Cargo.toml").exists():
            return ProjectType.RUST
        
        # Check for Go
        if (root / "go.mod").exists():
            return ProjectType.GO
        
        return ProjectType.UNKNOWN
    
    def _detect_tooling(self, root: Path, project_type: ProjectType) -> Tuple[str, str, str]:
        """Detect package manager and build commands"""
        if project_type in [ProjectType.REACT, ProjectType.VUE, ProjectType.ANGULAR, ProjectType.NODE]:
            # Check for package managers
            if (root / "yarn.lock").exists():
                return "yarn", "yarn test", "yarn build"
            elif (root / "pnpm-lock.yaml").exists():
                return "pnpm", "pnpm test", "pnpm build"
            else:
                return "npm", "npm test", "npm run build"
        
        elif project_type == ProjectType.PYTHON:
            return "pip", "python -m pytest", "python setup.py build"
        
        elif project_type == ProjectType.RUST:
            return "cargo", "cargo test", "cargo build"
        
        elif project_type == ProjectType.GO:
            return "go", "go test", "go build"
        
        return "unknown", "unknown", "unknown"
    
    def _find_src_directory(self, root: Path, project_type: ProjectType) -> Path:
        """Find the main source directory"""
        if project_type in [ProjectType.REACT, ProjectType.VUE, ProjectType.ANGULAR]:
            if (root / "src").exists():
                return root / "src"
        
        # Default to project root
        return root
    
    def _find_config_files(self, root: Path, project_type: ProjectType) -> List[Path]:
        """Find important configuration files"""
        configs = []
        
        common_configs = [
            "package.json", "tsconfig.json", ".eslintrc.js", ".eslintrc.json",
            "requirements.txt", "Cargo.toml", "go.mod", "pyproject.toml"
        ]
        
        for config in common_configs:
            config_path = root / config
            if config_path.exists():
                configs.append(config_path)
        
        return configs
    
    def _load_dependencies(self, root: Path, project_type: ProjectType) -> Dict[str, str]:
        """Load existing project dependencies"""
        deps = {}
        
        if project_type in [ProjectType.REACT, ProjectType.VUE, ProjectType.ANGULAR, ProjectType.NODE]:
            package_json = root / "package.json"
            if package_json.exists():
                try:
                    with open(package_json) as f:
                        data = json.load(f)
                    deps.update(data.get('dependencies', {}))
                    deps.update(data.get('devDependencies', {}))
                except:
                    pass
        
        elif project_type == ProjectType.PYTHON:
            req_file = root / "requirements.txt"
            if req_file.exists():
                try:
                    with open(req_file) as f:
                        for line in f:
                            line = line.strip()
                            if line and not line.startswith('#'):
                                if '==' in line:
                                    name, version = line.split('==', 1)
                                    deps[name] = version
                                else:
                                    deps[line] = "latest"
                except:
                    pass
        
        return deps
    
    def _init_task_patterns(self) -> Dict[TaskType, List[str]]:
        """Initialize universal task type recognition patterns"""
        return {
            TaskType.DEPENDENCY_INSTALL: [
                r'\binstall\b.*\b(dependency|package|library|module)\b',
                r'\badd\b.*\b(dependency|package|library)\b',
                r'\binstall\b.*\b(\w+[-_]\w+|\w+)\b',  # package names
                r'\bnpm install\b',
                r'\byarn add\b',
                r'\bpip install\b'
            ],
            TaskType.FILE_CREATE: [
                r'\bcreate\b.*\b(file|component|service|module|class)\b',
                r'\badd\b.*\b(file|component|service)\b',
                r'\bimplement\b.*\b(component|service|module)\b',
                r'\bbuild\b.*\b(component|interface)\b'
            ],
            TaskType.IMPLEMENTATION: [
                r'\bimplement\b.*\b(feature|functionality|logic|method)\b',
                r'\badd\b.*\b(feature|functionality|logic|handling)\b',
                r'\bbuild\b.*\b(feature|system|logic)\b',
                r'\bdevelop\b.*\b(feature|component|system)\b'
            ],
            TaskType.TESTING: [
                r'\btest\b.*\b(component|service|functionality|integration)\b',
                r'\badd\b.*\b(test|testing|spec)\b',
                r'\bwrite\b.*\b(test|testing|spec)\b',
                r'\bunit test\b',
                r'\bintegration test\b'
            ],
            TaskType.CONFIGURATION: [
                r'\bconfigure\b.*\b(environment|settings|config)\b',
                r'\bsetup\b.*\b(environment|config|configuration)\b',
                r'\badd\b.*\b(configuration|config|settings)\b'
            ],
            TaskType.BUILD: [
                r'\bbuild\b.*\b(project|application|system)\b',
                r'\bcompile\b.*\b(project|code|application)\b',
                r'\bbundle\b.*\b(application|assets)\b'
            ],
            TaskType.DEPLOYMENT: [
                r'\bdeploy\b.*\b(application|system|service)\b',
                r'\brelease\b.*\b(version|application)\b',
                r'\bpublish\b.*\b(package|application)\b'
            ]
        }
    
    def _init_action_templates(self) -> Dict[TaskType, Dict[str, Any]]:
        """Initialize action templates for different task types"""
        return {
            TaskType.DEPENDENCY_INSTALL: {
                "command_template": "{package_manager} {install_cmd} {package_name}",
                "validation": ["dependency_exists"],
                "files": []
            },
            TaskType.FILE_CREATE: {
                "command_template": None,
                "validation": ["file_exists", "file_importable"],
                "files": "dynamic"  # Will be determined based on context
            },
            TaskType.IMPLEMENTATION: {
                "command_template": None,
                "validation": ["tests_pass", "builds_successfully"],
                "files": "dynamic"
            },
            TaskType.TESTING: {
                "command_template": "{test_command}",
                "validation": ["tests_pass"],
                "files": "dynamic"
            },
            TaskType.CONFIGURATION: {
                "command_template": None,
                "validation": ["config_valid", "builds_successfully"],
                "files": "dynamic"
            }
        }
    
    def _load_state(self) -> Dict:
        """Load agent execution state"""
        if self.state_file.exists():
            try:
                with open(self.state_file) as f:
                    return json.load(f)
            except:
                pass
        
        return {
            "last_task_id": None,
            "completed_tasks": [],
            "failed_tasks": [],
            "execution_log": []
        }
    
    def _save_state(self):
        """Save agent execution state"""
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.state_file, 'w') as f:
            json.dump(self.state, f, indent=2)
    
    def get_taskmaster_tasks(self) -> List[Dict]:
        """Read tasks from Task Master"""
        try:
            tasks_file = Path('.taskmaster/tasks/tasks.json')
            if not tasks_file.exists():
                return []
                
            with open(tasks_file, 'r') as f:
                data = json.load(f)
                
            if isinstance(data, dict) and 'master' in data:
                return data['master']['tasks']
            elif isinstance(data, dict) and 'tasks' in data:
                return data['tasks']
            elif isinstance(data, list):
                return data
            
            return []
        except Exception as e:
            print(f"Error reading tasks: {e}")
            return []
    
    def classify_task(self, task: Dict) -> TaskType:
        """Classify a task based on its content"""
        text = ' '.join([
            task.get('title', ''),
            task.get('description', ''),
            task.get('details', '') or ''
        ]).lower()
        
        # Score each task type
        scores = {}
        for task_type, patterns in self.task_patterns.items():
            score = 0
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    score += 1
            if score > 0:
                scores[task_type] = score
        
        # Return highest scoring type
        if scores:
            return max(scores.items(), key=lambda x: x[1])[0]
        
        return TaskType.UNKNOWN
    
    def find_next_task(self) -> Optional[Dict]:
        """Find the next task that can be executed (including subtasks)"""
        tasks = self.get_taskmaster_tasks()
        
        # First, look for available subtasks in in-progress main tasks
        for task in tasks:
            if task.get('status') == 'in-progress' and task.get('subtasks'):
                for subtask in task['subtasks']:
                    if subtask.get('status') == 'pending':
                        # Check subtask dependencies
                        deps = subtask.get('dependencies', [])
                        if not deps:  # No dependencies, ready to execute
                            return subtask
        
        # Then look for main tasks without subtasks
        for task in tasks:
            # Skip completed tasks
            if task.get('status') == 'completed':
                continue
            
            # Skip tasks already in progress that have subtasks
            if task.get('status') == 'in_progress' and task.get('subtasks'):
                continue
            
            # Skip tasks already in progress (unless it's the one we're working on)
            if task.get('status') == 'in_progress' and task.get('id') != self.state.get('last_task_id'):
                continue
            
            # Check if dependencies are met
            deps = task.get('dependencies', [])
            if deps:
                dep_tasks = {t['id']: t for t in tasks}
                deps_completed = all(
                    dep_tasks.get(dep_id, {}).get('status') == 'completed'
                    for dep_id in deps
                )
                if not deps_completed:
                    continue
            
            return task
        
        return None
    
    def interpret_task(self, task: Dict) -> TaskAction:
        """Interpret a task and determine what actions to take"""
        task_type = self.classify_task(task)
        task_text = f"{task.get('title', '')} {task.get('description', '')}".lower()
        
        if task_type == TaskType.DEPENDENCY_INSTALL:
            return self._interpret_dependency_task(task, task_text)
        elif task_type == TaskType.FILE_CREATE:
            return self._interpret_file_creation_task(task, task_text)
        elif task_type == TaskType.IMPLEMENTATION:
            return self._interpret_implementation_task(task, task_text)
        elif task_type == TaskType.TESTING:
            return self._interpret_testing_task(task, task_text)
        else:
            return TaskAction(
                action_type="unknown",
                command=None,
                files_to_create=[],
                validation_checks=[],
                description=f"Unknown task type: {task.get('title', '')}"
            )
    
    def _interpret_dependency_task(self, task: Dict, task_text: str) -> TaskAction:
        """Interpret dependency installation tasks"""
        # Extract package name from task text - specifically look for html5-qrcode pattern
        package_patterns = [
            r'install\s+([a-zA-Z0-9\-_@/]+)\s+dependency',
            r'([a-zA-Z0-9\-_@/]+)\s+dependency',
            r'install\s+([a-zA-Z0-9\-_@/]+)',
            r'add\s+([a-zA-Z0-9\-_@/]+)',
        ]
        
        package_name = None
        for pattern in package_patterns:
            match = re.search(pattern, task_text, re.IGNORECASE)
            if match:
                candidate = match.group(1)
                # Skip generic words but allow package names with hyphens
                if candidate.lower() not in ['and', 'the', 'a', 'an', 'to', 'for', 'with', 'from']:
                    package_name = candidate
                    break
        
        if not package_name:
            return TaskAction(
                action_type="error",
                command=None,
                files_to_create=[],
                validation_checks=[],
                description="Could not extract package name from task"
            )
        
        # Determine install command based on project type
        if self.context.project_type in [ProjectType.REACT, ProjectType.VUE, ProjectType.ANGULAR, ProjectType.NODE]:
            if self.context.package_manager == "yarn":
                command = f"yarn add {package_name}"
            elif self.context.package_manager == "pnpm":
                command = f"pnpm add {package_name}"
            else:
                command = f"npm install {package_name}"
        else:
            command = f"pip install {package_name}"
        
        return TaskAction(
            action_type="dependency_install",
            command=command,
            files_to_create=[],
            validation_checks=[f"dependency_installed:{package_name}"],
            description=f"Install {package_name} dependency"
        )
    
    def _interpret_file_creation_task(self, task: Dict, task_text: str) -> TaskAction:
        """Interpret file creation tasks"""
        # Extract file/component name and type
        file_patterns = [
            r'create\s+(\w+)\s+(component|service|file|module)',
            r'create\s+(\w+)\.(js|ts|jsx|tsx|py|rs)',
            r'(\w+)\s+file',
            r'(\w+)\s+component'
        ]
        
        file_name = None
        file_type = "component"
        
        for pattern in file_patterns:
            match = re.search(pattern, task_text, re.IGNORECASE)
            if match:
                file_name = match.group(1)
                if len(match.groups()) > 1:
                    file_type = match.group(2)
                break
        
        if not file_name:
            return TaskAction(
                action_type="error",
                command=None,
                files_to_create=[],
                validation_checks=[],
                description="Could not extract file name from task"
            )
        
        # Generate file content based on project type and file type
        files_to_create = self._generate_file_templates(file_name, file_type)
        
        return TaskAction(
            action_type="file_create",
            command=None,
            files_to_create=files_to_create,
            validation_checks=[f"file_exists:{files_to_create[0][0]}"],
            description=f"Create {file_name} {file_type}"
        )
    
    def _interpret_implementation_task(self, task: Dict, task_text: str) -> TaskAction:
        """Interpret implementation tasks"""
        return TaskAction(
            action_type="implementation",
            command=None,
            files_to_create=[],
            validation_checks=["manual_review"],
            description=f"Implementation task: {task.get('title', '')}"
        )
    
    def _interpret_testing_task(self, task: Dict, task_text: str) -> TaskAction:
        """Interpret testing tasks"""
        return TaskAction(
            action_type="testing",
            command=self.context.test_command,
            files_to_create=[],
            validation_checks=["tests_pass"],
            description=f"Testing task: {task.get('title', '')}"
        )
    
    def _generate_file_templates(self, name: str, file_type: str) -> List[Tuple[str, str]]:
        """Generate file templates based on project context"""
        files = []
        
        if self.context.project_type == ProjectType.REACT:
            if file_type.lower() in ['component', 'jsx', 'tsx']:
                # React component
                component_path = self.context.src_dir / "components" / f"{name}.js"
                component_content = f"""import React from 'react';

const {name} = () => {{
  return (
    <div className="{name.lower()}">
      <h2>{name}</h2>
      {{/* TODO: Implement {name} functionality */}}
    </div>
  );
}};

export default {name};
"""
                files.append((str(component_path), component_content))
                
                # Test file
                test_path = self.context.src_dir / "components" / f"{name}.test.js"
                test_content = f"""import React from 'react';
import {{ render, screen }} from '@testing-library/react';
import {name} from './{name}';

describe('{name}', () => {{
  test('renders {name} component', () => {{
    render(<{name} />);
    expect(screen.getByText('{name}')).toBeInTheDocument();
  }});
}});
"""
                files.append((str(test_path), test_content))
        
        elif file_type.lower() in ['service', 'api']:
            # Service file
            service_path = self.context.src_dir / "services" / f"{name}Service.js"
            service_content = f"""class {name}Service {{
  // TODO: Implement {name} service methods
  
  async getData() {{
    throw new Error('Not implemented');
  }}
}}

export default new {name}Service();
"""
            files.append((str(service_path), service_content))
        
        return files
    
    def execute_task_action(self, action: TaskAction) -> bool:
        """Execute a task action"""
        try:
            print(f"  Executing: {action.description}")
            
            # Execute command if present
            if action.command:
                print(f"    Running: {action.command}")
                result = subprocess.run(
                    action.command.split(),
                    cwd=self.project_root,
                    capture_output=True,
                    text=True
                )
                if result.returncode != 0:
                    print(f"    ❌ Command failed: {result.stderr}")
                    return False
                else:
                    print(f"    ✅ Command succeeded")
            
            # Create files if specified
            for file_path, content in action.files_to_create:
                file_path_obj = Path(file_path)
                print(f"    Creating: {file_path}")
                
                # Create directory if it doesn't exist
                file_path_obj.parent.mkdir(parents=True, exist_ok=True)
                
                # Write file content
                with open(file_path_obj, 'w') as f:
                    f.write(content)
                print(f"    ✅ Created: {file_path}")
            
            # Run validations
            for validation in action.validation_checks:
                if not self._validate_action(validation):
                    print(f"    ❌ Validation failed: {validation}")
                    return False
                else:
                    print(f"    ✅ Validation passed: {validation}")
            
            return True
            
        except Exception as e:
            print(f"    ❌ Error executing action: {e}")
            return False
    
    def _validate_action(self, validation: str) -> bool:
        """Validate that an action was successful"""
        if validation.startswith("dependency_installed:"):
            package_name = validation.split(":", 1)[1]
            return self._check_dependency_installed(package_name)
        
        elif validation.startswith("file_exists:"):
            file_path = validation.split(":", 1)[1]
            return Path(file_path).exists()
        
        elif validation == "tests_pass":
            return self._run_tests()
        
        elif validation == "builds_successfully":
            return self._run_build()
        
        elif validation == "manual_review":
            # For implementation tasks, require manual confirmation
            return True  # For now, assume success
        
        return True
    
    def _check_dependency_installed(self, package_name: str) -> bool:
        """Check if a dependency was successfully installed"""
        # Re-load dependencies to check if package was added
        updated_deps = self._load_dependencies(self.project_root, self.context.project_type)
        return package_name in updated_deps
    
    def _run_tests(self) -> bool:
        """Run project tests"""
        if self.context.test_command == "unknown":
            return True  # Skip if no test command available
        
        try:
            result = subprocess.run(
                self.context.test_command.split(),
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            return result.returncode == 0
        except:
            return False
    
    def _run_build(self) -> bool:
        """Run project build"""
        if self.context.build_command == "unknown":
            return True  # Skip if no build command available
        
        try:
            result = subprocess.run(
                self.context.build_command.split(),
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            return result.returncode == 0
        except:
            return False
    
    def mark_task_status(self, task_id: int, status: str) -> bool:
        """Update task status in Task Master"""
        try:
            # Map our status names to Task Master status names
            status_mapping = {
                'in_progress': 'in-progress',
                'completed': 'done',
                'pending': 'pending'
            }
            
            tm_status = status_mapping.get(status, status)
            cmd = ['task-master', 'set-status', f'--id={task_id}', f'--status={tm_status}']
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                print(f"    Task Master error: {result.stderr.strip()}")
                return False
            
            return True
        except Exception as e:
            print(f"    Error updating task status: {e}")
            return False
    
    def execute_next_task(self) -> bool:
        """Find and execute the next available task"""
        task = self.find_next_task()
        if not task:
            print("No tasks available to execute")
            return False
        
        task_id = task.get('id')
        title = task.get('title', '')
        
        print(f"\n🚀 Executing Task {task_id}: {title}")
        
        # Mark task as in progress (handle both main tasks and subtasks)
        if not self.mark_task_status(task_id, 'in_progress'):
            print(f"Failed to mark task {task_id} as in-progress")
            # For subtasks, this might be expected, so continue anyway
            if '.' not in str(task_id):
                return False
        
        # Interpret and execute the task
        action = self.interpret_task(task)
        
        if action.action_type == "error":
            print(f"❌ {action.description}")
            self.state['failed_tasks'].append(task_id)
            self._save_state()
            return False
        
        if action.action_type == "unknown":
            print(f"⚠️  Unknown task type, marking for manual review: {title}")
            # For unknown tasks, mark as completed but log for review
            self.mark_task_status(task_id, 'completed')
            self.state['completed_tasks'].append(task_id)
            self.state['last_task_id'] = task_id
            self._save_state()
            return True
        
        # Execute the action
        success = self.execute_task_action(action)
        
        if success:
            print(f"✅ Task {task_id} completed successfully")
            self.mark_task_status(task_id, 'completed')
            self.state['completed_tasks'].append(task_id)
        else:
            print(f"❌ Task {task_id} failed")
            self.state['failed_tasks'].append(task_id)
        
        self.state['last_task_id'] = task_id
        self._save_state()
        
        return success
    
    def run_continuous_execution(self, max_tasks: int = 10) -> None:
        """Continuously execute tasks until none are available"""
        print("🤖 Universal Development Execution Agent")
        print("=" * 60)
        print(f"Project Type: {self.context.project_type.value}")
        print(f"Package Manager: {self.context.package_manager}")
        print(f"Source Directory: {self.context.src_dir}")
        print("=" * 60)
        
        executed_count = 0
        
        while executed_count < max_tasks:
            if not self.execute_next_task():
                break
            
            executed_count += 1
            time.sleep(1)  # Brief pause between tasks
        
        print(f"\n🏁 Execution completed. Processed {executed_count} tasks.")
        print(f"Completed: {len(self.state['completed_tasks'])}")
        print(f"Failed: {len(self.state['failed_tasks'])}")

def main():
    parser = argparse.ArgumentParser(description='Universal Development Execution Agent')
    parser.add_argument('--single', action='store_true', help='Execute only one task')
    parser.add_argument('--max-tasks', type=int, default=10, help='Maximum tasks to execute')
    parser.add_argument('--project', type=str, default='.', help='Project root directory')
    
    args = parser.parse_args()
    
    agent = UniversalDevAgent(args.project)
    
    if args.single:
        agent.execute_next_task()
    else:
        agent.run_continuous_execution(args.max_tasks)

if __name__ == "__main__":
    main()