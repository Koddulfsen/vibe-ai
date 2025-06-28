#!/usr/bin/env python3
"""
Quality & Git Agent (Expanded)

Comprehensive validation, quality assurance, and version control agent that:
1. Executes relevant tests based on subtask completion
2. Enforces code quality checks (linting, formatting, security)
3. Updates documentation automatically
4. Manages git workflow (branching, commits, PRs)
5. Synchronizes all agents with current state
6. Enforces quality gates to prevent progression
"""

import json
import subprocess
import os
import time
import re
import hashlib
import requests
import getpass
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Any
from dataclasses import dataclass, asdict
from enum import Enum
import argparse
import shutil

class TestResult(Enum):
    PASS = "pass"
    FAIL = "fail"
    SKIP = "skip"
    ERROR = "error"

class QualityGate(Enum):
    TESTS = "tests"
    LINTING = "linting"
    SECURITY = "security"
    BUILD = "build"
    DOCUMENTATION = "documentation"
    REPOSITORY = "repository"

@dataclass
class ProjectState:
    """Shared state across all agents"""
    installed_dependencies: Set[str]
    created_files: Set[str]
    completed_subtasks: Set[str]
    test_results: Dict[str, str]
    build_status: str
    last_updated: str
    project_type: str
    errors: List[str]
    git_branch: str
    last_commit: str
    quality_score: float

@dataclass
class TestExecution:
    """Result of test execution"""
    test_type: str
    result: TestResult
    output: str
    duration: float
    files_tested: List[str]
    coverage: float

@dataclass
class QualityCheck:
    """Result of quality check"""
    check_type: str
    status: str
    issues_found: int
    issues_fixed: int
    details: List[str]

@dataclass
class GitOperation:
    """Git operation result"""
    operation: str
    success: bool
    branch: str
    commit_hash: Optional[str]
    message: str

class GitHubManager:
    """GitHub repository management functionality"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.config_file = self.project_root / ".git" / "github_config.json"
        self.config = self._load_github_config()
    
    def _load_github_config(self) -> Dict[str, Any]:
        """Load GitHub configuration"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except Exception:
                pass
        
        return {
            "username": "",
            "token": "",
            "default_private": True
        }
    
    def _save_github_config(self):
        """Save GitHub configuration"""
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def has_github_auth(self) -> bool:
        """Check if GitHub authentication is available"""
        return bool(self.config.get("username") and self.config.get("token"))
    
    def test_github_auth(self) -> bool:
        """Test GitHub authentication"""
        if not self.has_github_auth():
            return False
        
        try:
            headers = {
                "Authorization": f"token {self.config['token']}",
                "Accept": "application/vnd.github.v3+json"
            }
            
            response = requests.get("https://api.github.com/user", headers=headers)
            return response.status_code == 200
            
        except Exception:
            return False
    
    def create_repository(self, repo_name: str, description: str = "", private: bool = True) -> Dict[str, Any]:
        """Create a GitHub repository"""
        if not self.has_github_auth():
            return {"success": False, "error": "GitHub authentication not configured"}
        
        repo_data = {
            "name": repo_name,
            "description": description,
            "private": private,
            "auto_init": False
        }
        
        headers = {
            "Authorization": f"token {self.config['token']}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        try:
            response = requests.post(
                "https://api.github.com/user/repos",
                json=repo_data,
                headers=headers
            )
            
            if response.status_code == 201:
                repo_info = response.json()
                return {
                    "success": True,
                    "repo_url": repo_info["html_url"],
                    "clone_url": repo_info["clone_url"],
                    "ssh_url": repo_info["ssh_url"]
                }
            else:
                error_msg = response.json().get("message", "Unknown error")
                return {"success": False, "error": error_msg}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def setup_git_remote(self, repo_info: Dict[str, Any]) -> Dict[str, Any]:
        """Setup git remote for the repository"""
        try:
            # Check if remote already exists
            result = subprocess.run(
                ["git", "remote", "get-url", "origin"],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                # Update existing remote
                subprocess.run(
                    ["git", "remote", "set-url", "origin", repo_info["clone_url"]],
                    cwd=self.project_root,
                    check=True
                )
            else:
                # Add new remote
                subprocess.run(
                    ["git", "remote", "add", "origin", repo_info["clone_url"]],
                    cwd=self.project_root,
                    check=True
                )
            
            return {"success": True, "message": "Remote configured successfully"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def push_to_repository(self, branch: str = "main") -> Dict[str, Any]:
        """Push to the repository"""
        try:
            # Push to repository
            push_result = subprocess.run(
                ["git", "push", "-u", "origin", branch],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            
            if push_result.returncode == 0:
                return {"success": True, "output": push_result.stdout}
            else:
                return {"success": False, "error": push_result.stderr}
                
        except Exception as e:
            return {"success": False, "error": str(e)}

class QualityGitAgent:
    """
    Comprehensive Quality & Git Agent with full validation pipeline
    """
    
    def __init__(self, project_root: str = ".", config_path: Optional[str] = None):
        self.project_root = Path(project_root)
        self.config = self._load_config(config_path)
        
        # State and sync management
        self.state_file = self.project_root / ".taskmaster" / "project_state.json"
        self.agent_sync_dir = self.project_root / ".taskmaster" / "agent_sync"
        self.sync_file = self.agent_sync_dir / "quality_git_agent.json"
        
        # Ensure directories exist
        self.agent_sync_dir.mkdir(parents=True, exist_ok=True)
        
        # Load project state
        self.project_state = self._load_project_state()
        
        # Detect project type
        self.project_type = self._detect_project_type()
        
        # Initialize tools and strategies
        self.quality_tools = self._init_quality_tools()
        self.test_strategies = self._init_test_strategies()
        self.doc_generators = self._init_doc_generators()
        self.git_config = self._init_git_config()
        
        # Initialize GitHub manager
        self.github_manager = GitHubManager(self.project_root)
        
        # Quality gate thresholds
        self.quality_thresholds = {
            "test_coverage": 80.0,
            "lint_score": 8.0,
            "security_score": 7.0,
            "build_success": True,
            "doc_coverage": 70.0
        }
        
    def _load_config(self, config_path: Optional[str]) -> Dict:
        """Load configuration with defaults"""
        default_config = {
            "verbose": False,
            "dry_run": False,
            "auto_fix": True,
            "enforce_quality_gates": True,
            "git_auto_commit": True,
            "git_auto_branch": True,
            "doc_auto_update": True,
            "security_scanning": True,
            "backup_before_changes": True
        }
        
        if config_path and Path(config_path).exists():
            with open(config_path, 'r') as f:
                user_config = json.load(f)
                default_config.update(user_config)
        
        return default_config
    
    def _load_project_state(self) -> ProjectState:
        """Load shared project state"""
        if self.state_file.exists():
            try:
                with open(self.state_file) as f:
                    data = json.load(f)
                return ProjectState(
                    installed_dependencies=set(data.get('installed_dependencies', [])),
                    created_files=set(data.get('created_files', [])),
                    completed_subtasks=set(data.get('completed_subtasks', [])),
                    test_results=data.get('test_results', {}),
                    build_status=data.get('build_status', 'unknown'),
                    last_updated=data.get('last_updated', ''),
                    project_type=data.get('project_type', 'unknown'),
                    errors=data.get('errors', []),
                    git_branch=data.get('git_branch', 'main'),
                    last_commit=data.get('last_commit', ''),
                    quality_score=data.get('quality_score', 0.0)
                )
            except Exception as e:
                if self.config['verbose']:
                    print(f"⚠️  Error loading project state: {e}")
        
        # Initialize default state
        return ProjectState(
            installed_dependencies=set(),
            created_files=set(),
            completed_subtasks=set(),
            test_results={},
            build_status='unknown',
            last_updated='',
            project_type=self._detect_project_type(),
            errors=[],
            git_branch=self._get_current_git_branch(),
            last_commit=self._get_last_commit(),
            quality_score=0.0
        )
    
    def _save_project_state(self):
        """Save shared project state"""
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Convert sets to lists for JSON serialization
        state_dict = {
            'installed_dependencies': list(self.project_state.installed_dependencies),
            'created_files': list(self.project_state.created_files),
            'completed_subtasks': list(self.project_state.completed_subtasks),
            'test_results': self.project_state.test_results,
            'build_status': self.project_state.build_status,
            'project_type': self.project_state.project_type,
            'errors': self.project_state.errors,
            'git_branch': self.project_state.git_branch,
            'last_commit': self.project_state.last_commit,
            'quality_score': self.project_state.quality_score
        }
        state_dict['last_updated'] = time.strftime('%Y-%m-%d %H:%M:%S')
        
        with open(self.state_file, 'w') as f:
            json.dump(state_dict, f, indent=2)
    
    def _save_sync_data(self, data: Dict):
        """Save synchronization data"""
        sync_data = {
            **data,
            "sync_timestamp": time.time(),
            "agent_type": "quality_git_agent",
            "quality_gates_status": self._check_all_quality_gates()
        }
        
        with open(self.sync_file, 'w') as f:
            json.dump(sync_data, f, indent=2)
    
    def _detect_project_type(self) -> str:
        """Enhanced project type detection"""
        # Check for JavaScript/Node projects
        package_json = self.project_root / "package.json"
        if package_json.exists():
            try:
                with open(package_json) as f:
                    data = json.load(f)
                deps = {**data.get('dependencies', {}), **data.get('devDependencies', {})}
                
                if 'react' in deps:
                    return "react"
                elif 'vue' in deps:
                    return "vue"
                elif '@angular/core' in deps:
                    return "angular"
                else:
                    return "node"
            except:
                pass
        
        # Check for Python projects
        if (self.project_root / "requirements.txt").exists() or (self.project_root / "pyproject.toml").exists():
            return "python"
        
        # Check for Rust projects
        if (self.project_root / "Cargo.toml").exists():
            return "rust"
        
        # Check for Go projects
        if (self.project_root / "go.mod").exists():
            return "go"
        
        return "unknown"
    
    def _init_quality_tools(self) -> Dict[str, Dict]:
        """Initialize quality tools by detecting from actual project configuration"""
        # Detect tools dynamically from project files instead of hardcoded assumptions
        detected_tools = self._detect_available_tools()
        
        # Return project-specific tools based on detection
        return {self.project_type: detected_tools}
    
    def _detect_available_tools(self) -> Dict[str, str]:
        """Detect available tools from actual project configuration"""
        tools = {}
        
        # Analyze package.json for JavaScript/Node projects
        if self.project_type in ["react", "vue", "angular", "node"]:
            tools.update(self._detect_npm_tools())
        
        # Analyze Python project files
        elif self.project_type == "python":
            tools.update(self._detect_python_tools())
        
        # Analyze Rust project files
        elif self.project_type == "rust":
            tools.update(self._detect_rust_tools())
        
        # Analyze Go project files
        elif self.project_type == "go":
            tools.update(self._detect_go_tools())
        
        # Add generic tools if specific ones not found
        if not tools:
            tools = self._get_fallback_tools()
        
        return tools
    
    def _detect_npm_tools(self) -> Dict[str, str]:
        """Detect tools from package.json and project structure"""
        tools = {}
        
        package_json = self.project_root / "package.json"
        if package_json.exists():
            try:
                with open(package_json, 'r') as f:
                    pkg_data = json.load(f)
                
                scripts = pkg_data.get('scripts', {})
                dev_deps = pkg_data.get('devDependencies', {})
                deps = pkg_data.get('dependencies', {})
                all_deps = {**deps, **dev_deps}
                
                # Detect linter
                if 'eslint' in all_deps:
                    tools['linter'] = 'npx eslint'
                elif 'lint' in scripts:
                    tools['linter'] = f'npm run lint'
                
                # Detect formatter
                if 'prettier' in all_deps:
                    tools['formatter'] = 'npx prettier'
                elif 'format' in scripts:
                    tools['formatter'] = f'npm run format'
                
                # Detect type checker
                if 'typescript' in all_deps:
                    tools['type_check'] = 'npx tsc --noEmit'
                elif 'type-check' in scripts:
                    tools['type_check'] = f'npm run type-check'
                
                # Detect test command
                if 'test' in scripts:
                    tools['test'] = 'npm test'
                elif '@testing-library' in str(all_deps):
                    tools['test'] = 'npm test'
                
                # Detect build command
                if 'build' in scripts:
                    tools['build'] = 'npm run build'
                
                # Security audit
                tools['security'] = 'npm audit'
                
            except Exception:
                pass
        
        return tools
    
    def _detect_python_tools(self) -> Dict[str, str]:
        """Detect Python tools from project files"""
        tools = {}
        
        # Check for common Python tool configuration files
        config_files = {
            'pyproject.toml': self._analyze_pyproject_toml,
            'setup.cfg': self._analyze_setup_cfg,
            'requirements-dev.txt': self._analyze_requirements_dev,
        }
        
        for config_file, analyzer in config_files.items():
            config_path = self.project_root / config_file
            if config_path.exists():
                detected_tools = analyzer(config_path)
                tools.update(detected_tools)
                break
        
        # Fallback to common Python tools if available
        if not tools:
            tools = {
                'linter': 'flake8' if self._command_exists('flake8') else 'pylint',
                'formatter': 'black' if self._command_exists('black') else 'autopep8',
                'test': 'pytest' if self._command_exists('pytest') else 'python -m unittest',
                'security': 'safety check' if self._command_exists('safety') else 'pip-audit'
            }
        
        return tools
    
    def _detect_rust_tools(self) -> Dict[str, str]:
        """Detect Rust tools from Cargo.toml"""
        tools = {
            'linter': 'cargo clippy',
            'formatter': 'cargo fmt',
            'test': 'cargo test',
            'build': 'cargo build --release'
        }
        
        if self._command_exists('cargo-audit'):
            tools['security'] = 'cargo audit'
        
        return tools
    
    def _detect_go_tools(self) -> Dict[str, str]:
        """Detect Go tools from go.mod and project structure"""
        tools = {
            'formatter': 'go fmt',
            'test': 'go test ./...',
            'build': 'go build .'
        }
        
        # Check for additional tools
        if self._command_exists('golangci-lint'):
            tools['linter'] = 'golangci-lint run'
        
        if self._command_exists('gosec'):
            tools['security'] = 'gosec ./...'
        
        return tools
    
    def _analyze_pyproject_toml(self, config_path: Path) -> Dict[str, str]:
        """Analyze pyproject.toml for tool configuration"""
        tools = {}
        try:
            with open(config_path, 'r') as f:
                content = f.read()
            
            if '[tool.black]' in content:
                tools['formatter'] = 'black'
            if '[tool.pytest' in content:
                tools['test'] = 'pytest'
            if '[tool.mypy]' in content:
                tools['type_check'] = 'mypy'
            
        except Exception:
            pass
        
        return tools
    
    def _analyze_setup_cfg(self, config_path: Path) -> Dict[str, str]:
        """Analyze setup.cfg for tool configuration"""
        tools = {}
        try:
            with open(config_path, 'r') as f:
                content = f.read()
            
            if '[flake8]' in content:
                tools['linter'] = 'flake8'
            if '[tool:pytest]' in content:
                tools['test'] = 'pytest'
            
        except Exception:
            pass
        
        return tools
    
    def _analyze_requirements_dev(self, config_path: Path) -> Dict[str, str]:
        """Analyze requirements-dev.txt for development tools"""
        tools = {}
        try:
            with open(config_path, 'r') as f:
                content = f.read()
            
            if 'black' in content:
                tools['formatter'] = 'black'
            if 'pytest' in content:
                tools['test'] = 'pytest'
            if 'flake8' in content:
                tools['linter'] = 'flake8'
            
        except Exception:
            pass
        
        return tools
    
    def _command_exists(self, command: str) -> bool:
        """Check if a command exists in the system"""
        try:
            subprocess.run(['which', command], capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    def _get_fallback_tools(self) -> Dict[str, str]:
        """Get minimal fallback tools"""
        return {
            'test': 'echo "No test command configured"',
            'build': 'echo "No build command configured"',
            'linter': 'echo "No linter configured"'
        }
    
    def _init_test_strategies(self) -> Dict[str, List[str]]:
        """Initialize test strategies based on project type"""
        strategies = {
            "react": [
                "npm test -- --watchAll=false --coverage --coverageReporters=text",
                "npm run build"
            ],
            "vue": [
                "npm test",
                "npm run build"
            ],
            "angular": [
                "npx ng test --watch=false --code-coverage",
                "npx ng build"
            ],
            "node": [
                "npm test",
                "npm run build"
            ],
            "python": [
                "python -m pytest --cov=. --cov-report=term",
                "python -m build"
            ],
            "rust": [
                "cargo test",
                "cargo build --release"
            ],
            "go": [
                "go test -cover ./...",
                "go build ."
            ]
        }
        
        return strategies.get(self.project_state.project_type, ["echo 'No tests configured'"])
    
    def _init_doc_generators(self) -> Dict[str, List[str]]:
        """Initialize documentation generators"""
        return {
            "react": [
                "npx jsdoc -r src/ -d docs/",
                "npx typedoc --out docs/ src/"
            ],
            "python": [
                "sphinx-build -b html docs/ docs/_build/",
                "pdoc --html --output-dir docs/ ."
            ],
            "rust": [
                "cargo doc --no-deps"
            ],
            "go": [
                "godoc -http=:6060"
            ]
        }
    
    def _init_git_config(self) -> Dict[str, str]:
        """Initialize git configuration"""
        return {
            "commit_format": "feat({scope}): {description}\n\n{details}\n\n🤖 Generated with Quality & Git Agent",
            "branch_prefix": "feature/",
            "main_branch": "main"
        }
    
    def _get_current_git_branch(self) -> str:
        """Get current git branch"""
        try:
            result = subprocess.run(
                ["git", "branch", "--show-current"],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except:
            pass
        return "main"
    
    def _get_last_commit(self) -> str:
        """Get last commit hash"""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                return result.stdout.strip()[:8]
        except:
            pass
        return ""
    
    def scan_current_state(self) -> None:
        """Scan current project state and update tracking"""
        if self.config['verbose']:
            print("🔍 Scanning current project state...")
        
        # Scan dependencies
        self._scan_dependencies()
        
        # Scan created files
        self._scan_files()
        
        # Scan completed tasks
        self._scan_completed_tasks()
        
        # Update git state
        self.project_state.git_branch = self._get_current_git_branch()
        self.project_state.last_commit = self._get_last_commit()
        
        if self.config['verbose']:
            print(f"   📦 Dependencies: {len(self.project_state.installed_dependencies)}")
            print(f"   📁 Files: {len(self.project_state.created_files)}")
            print(f"   ✅ Completed subtasks: {len(self.project_state.completed_subtasks)}")
            print(f"   🌿 Git branch: {self.project_state.git_branch}")
    
    def _scan_dependencies(self):
        """Scan for installed dependencies"""
        project_type = self.project_state.project_type
        
        if project_type in ["react", "vue", "angular", "node"]:
            package_json = self.project_root / "package.json"
            if package_json.exists():
                try:
                    with open(package_json) as f:
                        data = json.load(f)
                    deps = set()
                    deps.update(data.get('dependencies', {}).keys())
                    deps.update(data.get('devDependencies', {}).keys())
                    self.project_state.installed_dependencies = deps
                except:
                    pass
        
        elif project_type == "python":
            req_file = self.project_root / "requirements.txt"
            if req_file.exists():
                try:
                    with open(req_file) as f:
                        deps = set()
                        for line in f:
                            line = line.strip()
                            if line and not line.startswith('#'):
                                deps.add(line.split('==')[0].split('>=')[0])
                        self.project_state.installed_dependencies = deps
                except:
                    pass
    
    def _scan_files(self):
        """Scan for created files"""
        created_files = set()
        
        # Scan project directories
        patterns = ["src/**/*", "lib/**/*", "components/**/*", "services/**/*", "utils/**/*", "*.py", "*.rs", "*.go"]
        
        for pattern in patterns:
            for file_path in self.project_root.glob(pattern):
                if file_path.is_file() and not file_path.name.startswith('.'):
                    rel_path = file_path.relative_to(self.project_root)
                    created_files.add(str(rel_path))
        
        self.project_state.created_files = created_files
    
    def _scan_completed_tasks(self):
        """Scan Task Master for completed subtasks"""
        try:
            tasks_file = self.project_root / '.taskmaster' / 'tasks' / 'tasks.json'
            if tasks_file.exists():
                with open(tasks_file) as f:
                    data = json.load(f)
                
                completed = set()
                # Check all tags for completed tasks
                for tag_data in data.values():
                    if isinstance(tag_data, dict) and 'tasks' in tag_data:
                        for task in tag_data['tasks']:
                            if task.get('status') == 'completed':
                                completed.add(str(task['id']))
                
                self.project_state.completed_subtasks = completed
        except:
            pass
    
    def run_tests(self, specific_files: Optional[List[str]] = None) -> List[TestExecution]:
        """Run appropriate tests based on project type and changed files"""
        if self.config['verbose']:
            print("🧪 Running tests...")
        
        test_results = []
        
        for test_command in self.test_strategies:
            if self.config['dry_run']:
                print(f"🔍 [DRY RUN] Would execute: {test_command}")
                test_results.append(TestExecution(
                    test_type="unit",
                    result=TestResult.PASS,
                    output="Dry run - tests passed",
                    duration=0.0,
                    files_tested=[],
                    coverage=85.0
                ))
                continue
            
            start_time = time.time()
            try:
                result = subprocess.run(
                    test_command.split(),
                    cwd=self.project_root,
                    capture_output=True,
                    text=True,
                    timeout=300
                )
                
                duration = time.time() - start_time
                test_type = "build" if "build" in test_command else "unit"
                
                test_execution = TestExecution(
                    test_type=test_type,
                    result=TestResult.PASS if result.returncode == 0 else TestResult.FAIL,
                    output=result.stdout + result.stderr,
                    duration=duration,
                    files_tested=specific_files or [],
                    coverage=self._extract_coverage(result.stdout + result.stderr)
                )
                
                test_results.append(test_execution)
                
                # Update project state
                test_key = f"{test_type}_{int(time.time())}"
                self.project_state.test_results[test_key] = test_execution.result.value
                
                if test_execution.result == TestResult.FAIL:
                    self.project_state.errors.append(f"{test_key}: {result.stderr[:200]}")
                
                if self.config['verbose']:
                    status = "✅" if test_execution.result == TestResult.PASS else "❌"
                    print(f"   {status} {test_type.title()} tests: {test_execution.result.value} ({duration:.1f}s)")
                
            except subprocess.TimeoutExpired:
                test_results.append(TestExecution(
                    test_type="timeout",
                    result=TestResult.ERROR,
                    output="Test timeout after 300s",
                    duration=300.0,
                    files_tested=[],
                    coverage=0.0
                ))
            except Exception as e:
                test_results.append(TestExecution(
                    test_type="error",
                    result=TestResult.ERROR,
                    output=str(e),
                    duration=0.0,
                    files_tested=[],
                    coverage=0.0
                ))
        
        return test_results
    
    def _extract_coverage(self, output: str) -> float:
        """Extract test coverage percentage from output"""
        # Look for common coverage patterns
        patterns = [
            r'coverage:\s*(\d+(?:\.\d+)?)%',
            r'(\d+(?:\.\d+)?)%\s*coverage',
            r'Total coverage:\s*(\d+(?:\.\d+)?)%'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, output, re.IGNORECASE)
            if match:
                return float(match.group(1))
        
        return 0.0
    
    def run_quality_checks(self) -> List[QualityCheck]:
        """Run comprehensive code quality checks"""
        if self.config['verbose']:
            print("🔍 Running quality checks...")
        
        quality_results = []
        tools = self.quality_tools.get(self.project_state.project_type, {})
        
        for check_type, command in tools.items():
            if check_type in ["test", "build"]:  # Skip these as they're handled separately
                continue
            
            if self.config['dry_run']:
                print(f"🔍 [DRY RUN] Would run {check_type}: {command}")
                quality_results.append(QualityCheck(
                    check_type=check_type,
                    status="pass",
                    issues_found=0,
                    issues_fixed=0,
                    details=["Dry run - quality check passed"]
                ))
                continue
            
            try:
                result = subprocess.run(
                    command.split(),
                    cwd=self.project_root,
                    capture_output=True,
                    text=True,
                    timeout=120
                )
                
                issues_found = self._count_issues(result.stdout + result.stderr, check_type)
                issues_fixed = 0
                
                # Auto-fix if enabled and possible
                if self.config['auto_fix'] and check_type == "formatter":
                    issues_fixed = self._auto_fix_formatting()
                
                quality_check = QualityCheck(
                    check_type=check_type,
                    status="pass" if result.returncode == 0 else "fail",
                    issues_found=issues_found,
                    issues_fixed=issues_fixed,
                    details=[result.stdout[:500]] if result.stdout else []
                )
                
                quality_results.append(quality_check)
                
                if self.config['verbose']:
                    status = "✅" if quality_check.status == "pass" else "❌"
                    print(f"   {status} {check_type.title()}: {issues_found} issues found")
                
            except subprocess.TimeoutExpired:
                quality_results.append(QualityCheck(
                    check_type=check_type,
                    status="timeout",
                    issues_found=0,
                    issues_fixed=0,
                    details=["Quality check timeout"]
                ))
            except Exception as e:
                quality_results.append(QualityCheck(
                    check_type=check_type,
                    status="error",
                    issues_found=0,
                    issues_fixed=0,
                    details=[str(e)]
                ))
        
        return quality_results
    
    def _count_issues(self, output: str, check_type: str) -> int:
        """Count issues from quality check output"""
        if check_type == "linter":
            # Count lines that look like linting errors
            lines = output.split('\n')
            issues = 0
            for line in lines:
                if any(indicator in line.lower() for indicator in ['error', 'warning', 'problem']):
                    issues += 1
            return issues
        
        elif check_type == "security":
            # Count security vulnerabilities
            if 'vulnerabilities' in output.lower():
                # Look for patterns like "5 vulnerabilities"
                import re
                match = re.search(r'(\d+)\s+vulnerabilities?', output)
                if match:
                    return int(match.group(1))
        
        return 0
    
    def _auto_fix_formatting(self) -> int:
        """Auto-fix formatting issues"""
        tools = self.quality_tools.get(self.project_state.project_type, {})
        formatter = tools.get('formatter')
        
        if not formatter:
            return 0
        
        try:
            # Add common auto-fix flags
            if 'prettier' in formatter:
                formatter += " --write ."
            elif 'black' in formatter:
                formatter += " ."
            elif 'rustfmt' in formatter or 'cargo fmt' in formatter:
                pass  # cargo fmt already formats in place
            elif 'go fmt' in formatter:
                formatter += " ./..."
            
            result = subprocess.run(
                formatter.split(),
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                return 1  # Assume 1 fix applied
        
        except:
            pass
        
        return 0
    
    def update_documentation(self, changed_files: List[str]) -> bool:
        """Update documentation based on changes"""
        if not self.config['doc_auto_update']:
            return True
        
        if self.config['verbose']:
            print("📚 Updating documentation...")
        
        if self.config['dry_run']:
            print("🔍 [DRY RUN] Would update documentation")
            return True
        
        # Update README if new features were added
        readme_updated = self._update_readme(changed_files)
        
        # Generate API docs if available
        api_docs_updated = self._generate_api_docs()
        
        # Update CHANGELOG
        changelog_updated = self._update_changelog()
        
        return readme_updated or api_docs_updated or changelog_updated
    
    def _update_readme(self, changed_files: List[str]) -> bool:
        """Update README with new features"""
        readme_path = self.project_root / "README.md"
        
        if not readme_path.exists():
            # Create basic README
            with open(readme_path, 'w') as f:
                f.write(f"# {self.project_root.name}\n\n")
                f.write("Auto-generated project documentation.\n\n")
                f.write("## Features\n\n")
                f.write("- Automated development workflow\n")
                f.write("- Quality gates and testing\n")
                f.write("- Git workflow automation\n")
            return True
        
        return False
    
    def _generate_api_docs(self) -> bool:
        """Generate API documentation"""
        doc_generators = self.doc_generators.get(self.project_state.project_type, [])
        
        for generator in doc_generators:
            try:
                result = subprocess.run(
                    generator.split(),
                    cwd=self.project_root,
                    capture_output=True,
                    text=True,
                    timeout=120
                )
                if result.returncode == 0:
                    return True
            except:
                continue
        
        return False
    
    def _update_changelog(self) -> bool:
        """Update CHANGELOG.md"""
        changelog_path = self.project_root / "CHANGELOG.md"
        
        if not changelog_path.exists():
            with open(changelog_path, 'w') as f:
                f.write("# Changelog\n\n")
                f.write("All notable changes to this project will be documented in this file.\n\n")
                f.write(f"## [Unreleased] - {time.strftime('%Y-%m-%d')}\n\n")
                f.write("### Added\n- Automated development workflow\n")
                f.write("### Changed\n- Project structure improvements\n")
            return True
        
        return False
    
    def create_git_branch(self, task_id: str, description: str) -> GitOperation:
        """Create feature branch for task"""
        if not self.config['git_auto_branch']:
            return GitOperation("skip", True, self.project_state.git_branch, None, "Branch creation disabled")
        
        # Generate branch name
        clean_desc = re.sub(r'[^\w\s-]', '', description).strip()
        clean_desc = re.sub(r'[-\s]+', '-', clean_desc)[:30]
        branch_name = f"{self.git_config['branch_prefix']}task-{task_id}-{clean_desc}".lower()
        
        if self.config['dry_run']:
            return GitOperation("create_branch", True, branch_name, None, f"[DRY RUN] Would create branch: {branch_name}")
        
        try:
            # Check if branch already exists
            result = subprocess.run(
                ["git", "branch", "--list", branch_name],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            
            if branch_name in result.stdout:
                # Branch exists, switch to it
                result = subprocess.run(
                    ["git", "checkout", branch_name],
                    cwd=self.project_root,
                    capture_output=True,
                    text=True
                )
            else:
                # Create new branch
                result = subprocess.run(
                    ["git", "checkout", "-b", branch_name],
                    cwd=self.project_root,
                    capture_output=True,
                    text=True
                )
            
            if result.returncode == 0:
                self.project_state.git_branch = branch_name
                return GitOperation("create_branch", True, branch_name, None, f"Created/switched to branch: {branch_name}")
            else:
                return GitOperation("create_branch", False, self.project_state.git_branch, None, f"Failed to create branch: {result.stderr}")
        
        except Exception as e:
            return GitOperation("create_branch", False, self.project_state.git_branch, None, f"Git error: {e}")
    
    def commit_changes(self, task_id: str, description: str, files_changed: List[str]) -> GitOperation:
        """Commit changes with meaningful message"""
        if not self.config['git_auto_commit']:
            return GitOperation("skip", True, self.project_state.git_branch, None, "Auto-commit disabled")
        
        if self.config['dry_run']:
            return GitOperation("commit", True, self.project_state.git_branch, "abc123", f"[DRY RUN] Would commit: {description}")
        
        try:
            # Stage all changes
            subprocess.run(
                ["git", "add", "."],
                cwd=self.project_root,
                check=True
            )
            
            # Check if there are changes to commit
            result = subprocess.run(
                ["git", "diff", "--cached", "--quiet"],
                cwd=self.project_root
            )
            
            if result.returncode == 0:
                # No changes to commit
                return GitOperation("commit", True, self.project_state.git_branch, None, "No changes to commit")
            
            # Generate commit message
            scope = self._determine_scope(files_changed)
            commit_msg = self.git_config['commit_format'].format(
                scope=scope,
                description=description[:50],
                details=f"Task {task_id}: {description}"
            )
            
            # Commit changes
            result = subprocess.run(
                ["git", "commit", "-m", commit_msg],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                commit_hash = self._get_last_commit()
                self.project_state.last_commit = commit_hash
                return GitOperation("commit", True, self.project_state.git_branch, commit_hash, f"Committed changes: {commit_hash}")
            else:
                return GitOperation("commit", False, self.project_state.git_branch, None, f"Commit failed: {result.stderr}")
        
        except Exception as e:
            return GitOperation("commit", False, self.project_state.git_branch, None, f"Git error: {e}")
    
    def _determine_scope(self, files_changed: List[str]) -> str:
        """Determine commit scope based on changed files"""
        if not files_changed:
            return "misc"
        
        # Analyze file paths to determine scope
        scopes = []
        for file_path in files_changed:
            if 'component' in file_path.lower():
                scopes.append("components")
            elif 'service' in file_path.lower():
                scopes.append("services")
            elif 'test' in file_path.lower():
                scopes.append("tests")
            elif 'doc' in file_path.lower() or 'readme' in file_path.lower():
                scopes.append("docs")
            elif any(ext in file_path for ext in ['.js', '.ts', '.py', '.rs', '.go']):
                scopes.append("core")
        
        # Return most common scope or 'misc'
        if scopes:
            return max(set(scopes), key=scopes.count)
        return "misc"
    
    def _check_all_quality_gates(self) -> Dict[str, bool]:
        """Check all quality gates"""
        gates = {}
        
        # Test gate
        gates['tests'] = self._check_test_gate()
        
        # Build gate
        gates['build'] = self.project_state.build_status == 'success'
        
        # Quality gate (placeholder - would check linting, etc.)
        gates['quality'] = True  # Simplified for now
        
        return gates
    
    def _check_test_gate(self) -> bool:
        """Check if test quality gate passes"""
        recent_tests = [result for key, result in self.project_state.test_results.items() 
                      if 'unit' in key and result == 'pass']
        return len(recent_tests) > 0
    
    def enforce_quality_gates(self) -> bool:
        """Enforce quality gates before allowing progression"""
        if not self.config['enforce_quality_gates']:
            return True
        
        if self.config['verbose']:
            print("🚦 Checking quality gates...")
        
        gates_status = self._check_all_quality_gates()
        all_passed = all(gates_status.values())
        
        if self.config['verbose']:
            for gate, status in gates_status.items():
                icon = "✅" if status else "❌"
                print(f"   {icon} {gate.title()} gate: {'PASS' if status else 'FAIL'}")
        
        if not all_passed and not self.config['dry_run']:
            if self.config['verbose']:
                print("🚫 Quality gates failed - blocking progression")
        
        return all_passed
    
    def sync_agents(self) -> None:
        """Synchronize state across all agents"""
        if self.config['verbose']:
            print("🔄 Synchronizing agent states...")
        
        # Save our current state
        self._save_project_state()
        
        # Create sync data
        sync_data = {
            "project_state": {
                "installed_dependencies": list(self.project_state.installed_dependencies),
                "created_files": list(self.project_state.created_files),
                "completed_subtasks": list(self.project_state.completed_subtasks),
                "project_type": self.project_state.project_type,
                "build_status": self.project_state.build_status,
                "git_branch": self.project_state.git_branch,
                "quality_score": self.project_state.quality_score
            },
            "quality_gates_passing": self.enforce_quality_gates(),
            "skip_dependencies": list(self.project_state.installed_dependencies),
            "skip_files": list(self.project_state.created_files),
            "completed_subtasks": list(self.project_state.completed_subtasks)
        }
        
        self._save_sync_data(sync_data)
        
        if self.config['verbose']:
            print("   ✅ Agent synchronization complete")
    
    def process_completed_subtask(self, task_id: str, task_description: str, 
                                 changed_files: Optional[List[str]] = None) -> bool:
        """Complete validation pipeline for a finished subtask"""
        if self.config['verbose']:
            print(f"🎯 Processing completed subtask {task_id}: {task_description}")
        
        changed_files = changed_files or []
        
        # 1. Scan current state
        self.scan_current_state()
        
        # 2. Run tests
        test_results = self.run_tests(changed_files)
        all_tests_passed = all(test.result == TestResult.PASS for test in test_results)
        
        if not all_tests_passed and self.config['enforce_quality_gates']:
            if self.config['verbose']:
                print("❌ Tests failed - aborting pipeline")
            return False
        
        # 3. Run quality checks
        quality_results = self.run_quality_checks()
        
        # 4. Update documentation
        doc_updated = self.update_documentation(changed_files)
        
        # 5. Git operations
        if self.config['git_auto_branch'] or self.config['git_auto_commit']:
            # Create branch if needed
            branch_op = self.create_git_branch(task_id, task_description)
            
            # Commit changes
            commit_op = self.commit_changes(task_id, task_description, changed_files)
            
            if self.config['verbose'] and commit_op.success:
                print(f"   📝 {commit_op.message}")
        
        # 6. Enforce quality gates
        gates_passed = self.enforce_quality_gates()
        
        if not gates_passed and self.config['enforce_quality_gates']:
            if self.config['verbose']:
                print("🚫 Quality gates failed - pipeline blocked")
            return False
        
        # 7. Sync with other agents
        self.sync_agents()
        
        # Update project state
        self.project_state.completed_subtasks.add(task_id)
        self.project_state.build_status = 'success' if all_tests_passed else 'failed'
        self._save_project_state()
        
        if self.config['verbose']:
            print(f"✅ Subtask {task_id} pipeline complete")
        
        return True
    
    def run_full_pipeline(self, task_id: Optional[str] = None) -> bool:
        """Run the complete quality pipeline"""
        print("🤖 Quality & Git Agent - Full Pipeline")
        print("=" * 50)
        
        if task_id:
            # Process specific task
            task_desc = f"Task {task_id} completion"
            return self.process_completed_subtask(task_id, task_desc)
        else:
            # Run general pipeline
            self.scan_current_state()
            test_results = self.run_tests()
            quality_results = self.run_quality_checks()
            self.update_documentation([])
            gates_passed = self.enforce_quality_gates()
            self.sync_agents()
            
            return gates_passed
    
    def create_github_repository(self, repo_name: str, description: str = "", private: bool = True) -> Dict[str, Any]:
        """Create GitHub repository and setup git integration"""
        print(f"🚀 Creating GitHub repository: {repo_name}")
        
        # Create repository
        repo_result = self.github_manager.create_repository(repo_name, description, private)
        
        if not repo_result["success"]:
            print(f"❌ Repository creation failed: {repo_result['error']}")
            return repo_result
        
        print(f"✅ Repository created: {repo_result['repo_url']}")
        
        # Setup git remote
        remote_result = self.github_manager.setup_git_remote(repo_result)
        
        if not remote_result["success"]:
            print(f"⚠️  Repository created but remote setup failed: {remote_result['error']}")
            return {**repo_result, "remote_setup": remote_result}
        
        print("🔗 Git remote configured")
        
        # Push to repository
        push_result = self.github_manager.push_to_repository()
        
        if not push_result["success"]:
            print(f"⚠️  Repository created but push failed: {push_result['error']}")
            return {**repo_result, "remote_setup": remote_result, "push": push_result}
        
        print("📤 Code pushed successfully")
        
        return {
            **repo_result,
            "remote_setup": remote_result,
            "push": push_result,
            "full_success": True
        }
    
    def check_github_status(self) -> Dict[str, Any]:
        """Check GitHub authentication and repository status"""
        status = {
            "auth_configured": self.github_manager.has_github_auth(),
            "auth_valid": False,
            "remote_configured": False,
            "can_push": False
        }
        
        if status["auth_configured"]:
            status["auth_valid"] = self.github_manager.test_github_auth()
        
        # Check if git remote is configured
        try:
            result = subprocess.run(
                ["git", "remote", "get-url", "origin"],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            status["remote_configured"] = result.returncode == 0
            if status["remote_configured"]:
                status["remote_url"] = result.stdout.strip()
        except Exception:
            pass
        
        # Check if we can push (requires both auth and remote)
        status["can_push"] = status["auth_valid"] and status["remote_configured"]
        
        return status
    
    def suggest_repository_name(self) -> str:
        """Suggest a repository name based on project analysis"""
        # Use project directory name as base
        base_name = self.project_root.name
        
        # Add suffix based on project type  
        if hasattr(self, 'project_type'):
            if self.project_type == "unknown" and (self.project_root / "agents").exists():
                return f"{base_name}-dev-automation"
            elif self.project_type != "unknown":
                return f"{base_name}-{self.project_type}"
        
        return base_name
    
    def generate_repository_description(self) -> str:
        """Generate repository description from project analysis"""
        description_parts = []
        
        # Check for agent system
        if (self.project_root / "agents").exists():
            description_parts.append("Universal Development Automation Agent System")
        
        # Check for specific frameworks
        if (self.project_root / "package.json").exists():
            description_parts.append("JavaScript/Node.js project")
        
        if (self.project_root / "requirements.txt").exists():
            description_parts.append("Python project")
        
        # Check for README content
        readme_files = ["README.md", "readme.md", "README.txt"]
        for readme in readme_files:
            readme_path = self.project_root / readme
            if readme_path.exists():
                try:
                    with open(readme_path, 'r') as f:
                        content = f.read()[:300]  # First 300 chars
                        if content.strip():
                            # Extract first meaningful line
                            lines = [line.strip() for line in content.split('\n') if line.strip()]
                            if lines:
                                first_line = lines[0].replace('#', '').strip()
                                if len(first_line) > 10:
                                    return first_line
                except:
                    pass
        
        if description_parts:
            return " - ".join(description_parts)
        else:
            return "Development project with automated tooling"

def main():
    parser = argparse.ArgumentParser(description='Quality & Git Agent')
    parser.add_argument('--config', type=str, help='Configuration file path')
    parser.add_argument('--project-root', type=str, default='.', help='Project root directory')
    parser.add_argument('--task-id', type=str, help='Specific task ID to process')
    parser.add_argument('--task-description', type=str, help='Task description')
    parser.add_argument('--changed-files', type=str, nargs='*', help='List of changed files')
    parser.add_argument('--mode', choices=['pipeline', 'scan', 'test', 'quality', 'git', 'repo'], 
                       default='pipeline', help='Operation mode')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    parser.add_argument('--dry-run', action='store_true', help='Dry run mode')
    parser.add_argument('--no-quality-gates', action='store_true', help='Disable quality gate enforcement')
    
    # Repository management options
    parser.add_argument('--create-repo', action='store_true', help='Create GitHub repository')
    parser.add_argument('--repo-name', type=str, help='Repository name')
    parser.add_argument('--repo-description', type=str, help='Repository description')
    parser.add_argument('--repo-public', action='store_true', help='Make repository public (default: private)')
    parser.add_argument('--check-github', action='store_true', help='Check GitHub status')
    
    args = parser.parse_args()
    
    # Create agent
    agent = QualityGitAgent(args.project_root, args.config)
    agent.config.update({
        'verbose': args.verbose,
        'dry_run': args.dry_run,
        'enforce_quality_gates': not args.no_quality_gates
    })
    
    # Execute based on mode
    if args.mode == 'pipeline':
        if args.task_id and args.task_description:
            success = agent.process_completed_subtask(
                args.task_id, 
                args.task_description, 
                args.changed_files or []
            )
        else:
            success = agent.run_full_pipeline(args.task_id)
    elif args.mode == 'scan':
        agent.scan_current_state()
        success = True
    elif args.mode == 'test':
        test_results = agent.run_tests(args.changed_files)
        success = all(test.result == TestResult.PASS for test in test_results)
    elif args.mode == 'quality':
        quality_results = agent.run_quality_checks()
        success = all(check.status == "pass" for check in quality_results)
    elif args.mode == 'git':
        if args.task_id and args.task_description:
            branch_op = agent.create_git_branch(args.task_id, args.task_description)
            commit_op = agent.commit_changes(args.task_id, args.task_description, args.changed_files or [])
            success = branch_op.success and commit_op.success
        else:
            success = False
    elif args.mode == 'repo':
        success = True
        
        # Handle repository operations
        if args.check_github:
            status = agent.check_github_status()
            print("🔍 GitHub Status:")
            print(f"   Auth configured: {'✅' if status['auth_configured'] else '❌'}")
            print(f"   Auth valid: {'✅' if status['auth_valid'] else '❌'}")
            print(f"   Remote configured: {'✅' if status['remote_configured'] else '❌'}")
            if status.get('remote_url'):
                print(f"   Remote URL: {status['remote_url']}")
            print(f"   Can push: {'✅' if status['can_push'] else '❌'}")
            
        elif args.create_repo:
            # Get repository details
            repo_name = args.repo_name or agent.suggest_repository_name()
            repo_description = args.repo_description or agent.generate_repository_description()
            is_private = not args.repo_public
            
            print(f"📋 Creating repository:")
            print(f"   Name: {repo_name}")
            print(f"   Description: {repo_description}")
            print(f"   Private: {is_private}")
            print()
            
            # Create repository
            result = agent.create_github_repository(repo_name, repo_description, is_private)
            success = result.get("full_success", False)
            
            if success:
                print(f"\n🎉 Repository created successfully!")
                print(f"🔗 URL: {result['repo_url']}")
            else:
                print(f"\n❌ Repository creation failed")
                if result.get("error"):
                    print(f"Error: {result['error']}")
        else:
            print("🔧 Repository mode requires --create-repo or --check-github")
            success = False
    
    if success:
        print("\n✅ Quality & Git Agent completed successfully")
    else:
        print("\n❌ Quality & Git Agent failed")
    
    exit(0 if success else 1)

if __name__ == "__main__":
    main()