#!/usr/bin/env python3
"""
Testing & Synchronization Agent

Runs after each subtask completion to:
1. Execute relevant tests
2. Update shared project state
3. Synchronize all agents with current reality
4. Enforce quality gates
"""

import json
import subprocess
import os
import time
from pathlib import Path
from typing import Dict, List, Optional, Set
from dataclasses import dataclass, asdict
from enum import Enum

class TestResult(Enum):
    PASS = "pass"
    FAIL = "fail"
    SKIP = "skip"
    ERROR = "error"

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

@dataclass
class TestExecution:
    """Result of test execution"""
    test_type: str
    result: TestResult
    output: str
    duration: float
    files_tested: List[str]

class TestSyncAgent:
    """
    Agent that maintains project quality and synchronizes agent states
    """
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.state_file = self.project_root / ".taskmaster" / "project_state.json"
        self.agent_sync_dir = self.project_root / ".taskmaster" / "agent_sync"
        
        # Ensure sync directory exists
        self.agent_sync_dir.mkdir(parents=True, exist_ok=True)
        
        # Load or initialize project state
        self.project_state = self._load_project_state()
        
        # Initialize test strategies based on project type
        self.test_strategies = self._init_test_strategies()
    
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
                    errors=data.get('errors', [])
                )
            except:
                pass
        
        # Initialize default state
        return ProjectState(
            installed_dependencies=set(),
            created_files=set(),
            completed_subtasks=set(),
            test_results={},
            build_status='unknown',
            last_updated='',
            project_type=self._detect_project_type(),
            errors=[]
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
            'errors': self.project_state.errors
        }
        state_dict['last_updated'] = time.strftime('%Y-%m-%d %H:%M:%S')
        
        with open(self.state_file, 'w') as f:
            json.dump(state_dict, f, indent=2)
    
    def _detect_project_type(self) -> str:
        """Detect project type"""
        if (self.project_root / "package.json").exists():
            return "react"  # or node/vue/angular - could be more specific
        elif (self.project_root / "requirements.txt").exists():
            return "python"
        elif (self.project_root / "Cargo.toml").exists():
            return "rust"
        return "unknown"
    
    def _init_test_strategies(self) -> Dict[str, List[str]]:
        """Initialize test strategies based on project type"""
        strategies = {
            "react": [
                "npm test -- --watchAll=false --coverage=false",
                "npm run build",
                "npm run lint"
            ],
            "python": [
                "python -m pytest",
                "python -m flake8",
                "python -m mypy ."
            ],
            "rust": [
                "cargo test",
                "cargo build",
                "cargo clippy"
            ]
        }
        
        return strategies.get(self.project_state.project_type, ["echo 'No tests configured'"])
    
    def scan_current_state(self) -> None:
        """Scan current project state and update tracking"""
        print("🔍 Scanning current project state...")
        
        # Scan dependencies
        self._scan_dependencies()
        
        # Scan created files
        self._scan_files()
        
        # Scan completed tasks
        self._scan_completed_tasks()
        
        print(f"   📦 Dependencies: {len(self.project_state.installed_dependencies)}")
        print(f"   📁 Files: {len(self.project_state.created_files)}")
        print(f"   ✅ Completed subtasks: {len(self.project_state.completed_subtasks)}")
    
    def _scan_dependencies(self):
        """Scan for installed dependencies"""
        if self.project_state.project_type == "react":
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
    
    def _scan_files(self):
        """Scan for created files"""
        created_files = set()
        
        # Scan src directory and other common locations
        for pattern in ["src/**/*", "components/**/*", "services/**/*", "utils/**/*"]:
            for file_path in self.project_root.glob(pattern):
                if file_path.is_file():
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
                
                # Handle Task Master format
                if isinstance(data, dict) and 'master' in data:
                    tasks = data['master']['tasks']
                elif isinstance(data, dict) and 'tasks' in data:
                    tasks = data['tasks']
                else:
                    tasks = data if isinstance(data, list) else []
                
                for task in tasks:
                    if task.get('status') == 'done':
                        completed.add(f"task_{task['id']}")
                    
                    # Check subtasks
                    for subtask in task.get('subtasks', []):
                        if subtask.get('status') == 'done':
                            completed.add(f"subtask_{task['id']}.{subtask['id']}")
                
                self.project_state.completed_subtasks = completed
        except:
            pass
    
    def run_tests_for_subtask(self, subtask_id: str, subtask_type: str) -> List[TestExecution]:
        """Run appropriate tests for a completed subtask"""
        print(f"🧪 Running tests for subtask {subtask_id} ({subtask_type})")
        
        test_executions = []
        
        # Determine which tests to run based on subtask type
        tests_to_run = self._select_tests_for_subtask_type(subtask_type)
        
        for test_command in tests_to_run:
            execution = self._execute_test(test_command, subtask_id)
            test_executions.append(execution)
            
            # Store result in project state
            self.project_state.test_results[f"{subtask_id}_{execution.test_type}"] = execution.result.value
        
        return test_executions
    
    def _select_tests_for_subtask_type(self, subtask_type: str) -> List[str]:
        """Select appropriate tests based on subtask type"""
        if "dependency" in subtask_type.lower():
            return ["npm test -- --watchAll=false --passWithNoTests"]
        elif "file" in subtask_type.lower() or "component" in subtask_type.lower():
            return ["npm test -- --watchAll=false", "npm run build"]
        elif "implement" in subtask_type.lower():
            return ["npm test -- --watchAll=false", "npm run build"]
        else:
            return ["npm test -- --watchAll=false --passWithNoTests"]
    
    def _execute_test(self, command: str, context: str) -> TestExecution:
        """Execute a single test command"""
        start_time = time.time()
        
        try:
            print(f"   Running: {command}")
            result = subprocess.run(
                command.split(),
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=120  # 2 minute timeout
            )
            
            duration = time.time() - start_time
            
            if result.returncode == 0:
                test_result = TestResult.PASS
                print(f"   ✅ PASS ({duration:.1f}s)")
            else:
                test_result = TestResult.FAIL
                print(f"   ❌ FAIL ({duration:.1f}s)")
                # Add error to project state
                self.project_state.errors.append(f"{context}: {result.stderr[:200]}")
            
            return TestExecution(
                test_type=command.split()[0],
                result=test_result,
                output=result.stdout if result.returncode == 0 else result.stderr,
                duration=duration,
                files_tested=[]
            )
            
        except subprocess.TimeoutExpired:
            duration = time.time() - start_time
            print(f"   ⏰ TIMEOUT ({duration:.1f}s)")
            return TestExecution(
                test_type=command.split()[0],
                result=TestResult.ERROR,
                output="Test timed out",
                duration=duration,
                files_tested=[]
            )
        except Exception as e:
            duration = time.time() - start_time
            print(f"   💥 ERROR ({duration:.1f}s): {e}")
            return TestExecution(
                test_type=command.split()[0],
                result=TestResult.ERROR,
                output=str(e),
                duration=duration,
                files_tested=[]
            )
    
    def check_quality_gates(self) -> bool:
        """Check if quality gates pass for progression"""
        print("🚦 Checking quality gates...")
        
        # Gate 1: No recent test failures
        recent_failures = [k for k, v in self.project_state.test_results.items() 
                          if v == TestResult.FAIL.value]
        
        if recent_failures:
            print(f"   ❌ Quality gate failed: {len(recent_failures)} test failures")
            return False
        
        # Gate 2: Build succeeds
        if self.project_state.build_status == "failed":
            print("   ❌ Quality gate failed: Build failing")
            return False
        
        # Gate 3: No critical errors
        critical_errors = [e for e in self.project_state.errors if "error" in e.lower()]
        if critical_errors:
            print(f"   ❌ Quality gate failed: {len(critical_errors)} critical errors")
            return False
        
        print("   ✅ All quality gates passed")
        return True
    
    def sync_agents(self) -> None:
        """Synchronize all agents with current project state"""
        print("🔄 Synchronizing agents...")
        
        # Create sync files for each agent
        sync_data = {
            "project_state": {
                'installed_dependencies': list(self.project_state.installed_dependencies),
                'created_files': list(self.project_state.created_files),
                'completed_subtasks': list(self.project_state.completed_subtasks),
                'test_results': self.project_state.test_results,
                'build_status': self.project_state.build_status,
                'project_type': self.project_state.project_type,
                'errors': self.project_state.errors
            },
            "sync_timestamp": time.time(),
            "quality_gates_passing": self.check_quality_gates()
        }
        
        # Universal Dev Agent sync
        universal_sync_file = self.agent_sync_dir / "universal_dev_agent.json"
        with open(universal_sync_file, 'w') as f:
            json.dump({
                **sync_data,
                "skip_dependencies": list(self.project_state.installed_dependencies),
                "skip_files": list(self.project_state.created_files)
            }, f, indent=2)
        
        # Intelligent Task Agent sync
        intelligent_sync_file = self.agent_sync_dir / "intelligent_task_agent.json"
        with open(intelligent_sync_file, 'w') as f:
            json.dump({
                **sync_data,
                "completed_subtasks": list(self.project_state.completed_subtasks),
                "project_dependencies": list(self.project_state.installed_dependencies)
            }, f, indent=2)
        
        # Complexity Agent sync
        complexity_sync_file = self.agent_sync_dir / "complexity_agent.json"
        with open(complexity_sync_file, 'w') as f:
            json.dump({
                **sync_data,
                "project_complexity_factors": {
                    "file_count": len(self.project_state.created_files),
                    "dependency_count": len(self.project_state.installed_dependencies),
                    "test_coverage": self._calculate_test_coverage()
                }
            }, f, indent=2)
        
        print(f"   📡 Synced {len(os.listdir(self.agent_sync_dir))} agents")
    
    def _calculate_test_coverage(self) -> float:
        """Calculate rough test coverage based on test results"""
        if not self.project_state.test_results:
            return 0.0
        
        passing_tests = sum(1 for result in self.project_state.test_results.values() 
                           if result == TestResult.PASS.value)
        total_tests = len(self.project_state.test_results)
        
        return passing_tests / total_tests if total_tests > 0 else 0.0
    
    def process_completed_subtask(self, subtask_id: str, subtask_title: str) -> bool:
        """Main method: process a completed subtask"""
        print(f"\n🔄 Processing completed subtask: {subtask_id} - {subtask_title}")
        
        # 1. Update project state
        self.scan_current_state()
        
        # 2. Determine subtask type and run appropriate tests
        subtask_type = self._classify_subtask(subtask_title)
        test_results = self.run_tests_for_subtask(subtask_id, subtask_type)
        
        # 3. Update build status
        build_success = all(t.result in [TestResult.PASS, TestResult.SKIP] for t in test_results)
        self.project_state.build_status = "passed" if build_success else "failed"
        
        # 4. Save updated state
        self._save_project_state()
        
        # 5. Sync all agents
        self.sync_agents()
        
        # 6. Check quality gates
        quality_passed = self.check_quality_gates()
        
        print(f"✅ Subtask {subtask_id} processed - Quality gates: {'PASS' if quality_passed else 'FAIL'}")
        
        return quality_passed
    
    def _classify_subtask(self, title: str) -> str:
        """Classify subtask type for appropriate testing"""
        title_lower = title.lower()
        
        if "install" in title_lower and "dependency" in title_lower:
            return "dependency_install"
        elif "create" in title_lower and "file" in title_lower:
            return "file_creation"
        elif "implement" in title_lower:
            return "implementation"
        elif "test" in title_lower:
            return "testing"
        else:
            return "unknown"
    
    def generate_status_report(self) -> str:
        """Generate a comprehensive status report"""
        report = f"""
🤖 Testing & Sync Agent Status Report
=====================================

📊 Project State:
  • Type: {self.project_state.project_type}
  • Dependencies: {len(self.project_state.installed_dependencies)}
  • Files: {len(self.project_state.created_files)}
  • Completed Subtasks: {len(self.project_state.completed_subtasks)}
  • Build Status: {self.project_state.build_status}

🧪 Test Results:
  • Total Tests Run: {len(self.project_state.test_results)}
  • Passing: {sum(1 for r in self.project_state.test_results.values() if r == 'pass')}
  • Failing: {sum(1 for r in self.project_state.test_results.values() if r == 'fail')}
  • Test Coverage: {self._calculate_test_coverage():.1%}

🚦 Quality Gates: {'✅ PASSING' if self.check_quality_gates() else '❌ FAILING'}

⚠️  Recent Errors: {len(self.project_state.errors)}

🔄 Last Updated: {self.project_state.last_updated}
"""
        return report

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Testing & Synchronization Agent')
    parser.add_argument('--scan', action='store_true', help='Scan current project state')
    parser.add_argument('--test-subtask', type=str, help='Test specific subtask ID')
    parser.add_argument('--sync', action='store_true', help='Sync all agents')
    parser.add_argument('--status', action='store_true', help='Show status report')
    parser.add_argument('--project', type=str, default='.', help='Project directory')
    
    args = parser.parse_args()
    
    agent = TestSyncAgent(args.project)
    
    if args.scan:
        agent.scan_current_state()
        agent._save_project_state()
    
    elif args.test_subtask:
        agent.process_completed_subtask(args.test_subtask, "Manual test")
    
    elif args.sync:
        agent.scan_current_state()
        agent.sync_agents()
    
    elif args.status:
        print(agent.generate_status_report())
    
    else:
        # Default: scan and sync
        agent.scan_current_state()
        agent.sync_agents()
        print(agent.generate_status_report())

if __name__ == "__main__":
    main()