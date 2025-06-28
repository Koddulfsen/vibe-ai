#!/usr/bin/env python3
"""
Intelligent Task Discovery and Expansion Agent

Analyzes codebase, task descriptions, and project structure to intelligently
discover missing tasks and break down complex ones - no hardcoded templates!
"""

import json
import subprocess
import argparse
import sys
import os
import re
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass

@dataclass
class TaskAnalysis:
    """Analysis results for a task"""
    missing_files: List[str]
    missing_dependencies: List[str]
    missing_tests: List[str]
    implementation_gaps: List[str]
    discovered_subtasks: List[Dict]
    complexity_score: int

class IntelligentTaskAgent:
    """
    Intelligently analyzes tasks and codebase to discover real work that needs to be done
    """
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.src_dir = self.project_root / "src"
        self.package_json = self.project_root / "package.json"
        
        # Initialize analysis patterns
        self.file_patterns = self._get_file_patterns()
        self.dependency_patterns = self._get_dependency_patterns()
        self.implementation_patterns = self._get_implementation_patterns()
    
    def _get_file_patterns(self) -> Dict[str, List[str]]:
        """Patterns to identify what files should exist for different task types"""
        return {
            'component': [
                'src/components/{name}.js',
                'src/components/{name}.css',
                'src/components/{name}.test.js'
            ],
            'service': [
                'src/services/{name}.js',
                'src/services/{name}.test.js'
            ],
            'api': [
                'src/services/{name}API.js',
                'src/services/{name}API.test.js',
                'src/types/{name}Types.js'
            ],
            'hook': [
                'src/hooks/use{name}.js',
                'src/hooks/use{name}.test.js'
            ],
            'util': [
                'src/utils/{name}.js',
                'src/utils/{name}.test.js'
            ]
        }
    
    def _get_dependency_patterns(self) -> Dict[str, List[str]]:
        """Patterns to identify missing dependencies"""
        return {
            'barcode_scanning': ['html5-qrcode', 'quagga'],
            'api_client': ['axios', 'fetch'],
            'testing': ['@testing-library/react', '@testing-library/jest-dom'],
            'pwa': ['workbox-*'],
            'offline_storage': ['dexie', 'idb'],
            'state_management': ['redux', 'zustand', 'context'],
            'ui_components': ['react-modal', 'react-spinner']
        }
    
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
            'testing_setup': [
                'unit tests',
                'integration tests',
                'mock setup',
                'test utilities',
                'coverage configuration'
            ],
            'performance': [
                'code splitting',
                'lazy loading',
                'memoization',
                'bundle optimization'
            ]
        }
    
    def scan_existing_files(self) -> Set[str]:
        """Scan existing files in the project"""
        existing_files = set()
        
        for root, dirs, files in os.walk(self.src_dir):
            # Skip node_modules and other common directories
            dirs[:] = [d for d in dirs if d not in ['.git', 'node_modules', '.next', 'build', 'dist']]
            
            for file in files:
                rel_path = os.path.relpath(os.path.join(root, file), self.project_root)
                existing_files.add(rel_path)
        
        return existing_files
    
    def scan_package_dependencies(self) -> Set[str]:
        """Scan package.json for existing dependencies"""
        if not self.package_json.exists():
            return set()
        
        try:
            with open(self.package_json) as f:
                package_data = json.load(f)
            
            deps = set()
            deps.update(package_data.get('dependencies', {}).keys())
            deps.update(package_data.get('devDependencies', {}).keys())
            return deps
        except:
            return set()
    
    def scan_todo_comments(self) -> List[Tuple[str, str]]:
        """Scan for TODO, FIXME, etc. comments in code"""
        todos = []
        todo_patterns = [
            re.compile(r'//\s*(TODO|FIXME|HACK|NOTE):\s*(.+)', re.IGNORECASE),
            re.compile(r'/\*\s*(TODO|FIXME|HACK|NOTE):\s*(.+?)\s*\*/', re.IGNORECASE),
            re.compile(r'#\s*(TODO|FIXME|HACK|NOTE):\s*(.+)', re.IGNORECASE)
        ]
        
        for root, dirs, files in os.walk(self.src_dir):
            dirs[:] = [d for d in dirs if d not in ['.git', 'node_modules', '.next', 'build', 'dist']]
            
            for file in files:
                if file.endswith(('.js', '.jsx', '.ts', '.tsx', '.py', '.md')):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                            
                        for pattern in todo_patterns:
                            for match in pattern.finditer(content):
                                rel_path = os.path.relpath(file_path, self.project_root)
                                todos.append((rel_path, match.group(2).strip()))
                    except:
                        continue
        
        return todos
    
    def analyze_task_requirements(self, task: Dict) -> TaskAnalysis:
        """Analyze what a task actually needs based on its description"""
        title = task.get('title', '').lower()
        description = task.get('description', '').lower()
        details = task.get('details', '') or ''
        all_text = f"{title} {description} {details}".lower()
        
        analysis = TaskAnalysis(
            missing_files=[],
            missing_dependencies=[],
            missing_tests=[],
            implementation_gaps=[],
            discovered_subtasks=[],
            complexity_score=0
        )
        
        # Scan existing project state
        existing_files = self.scan_existing_files()
        existing_deps = self.scan_package_dependencies()
        todos = self.scan_todo_comments()
        
        # Analyze what files should exist
        analysis.missing_files = self._find_missing_files(all_text, existing_files)
        
        # Analyze what dependencies are needed
        analysis.missing_dependencies = self._find_missing_dependencies(all_text, existing_deps)
        
        # Analyze implementation gaps
        analysis.implementation_gaps = self._find_implementation_gaps(all_text, existing_files)
        
        # Find relevant TODOs
        relevant_todos = self._find_relevant_todos(all_text, todos)
        
        # Generate intelligent subtasks based on analysis
        analysis.discovered_subtasks = self._generate_intelligent_subtasks(
            task, analysis, relevant_todos
        )
        
        # Calculate complexity based on actual requirements
        analysis.complexity_score = len(analysis.missing_files) * 2 + \
                                  len(analysis.missing_dependencies) * 3 + \
                                  len(analysis.implementation_gaps) * 2 + \
                                  len(relevant_todos)
        
        return analysis
    
    def _find_missing_files(self, task_text: str, existing_files: Set[str]) -> List[str]:
        """Find files that should exist but don't"""
        missing = []
        
        # Extract component names from task
        component_matches = re.findall(r'(\w+)(?:component|scanner|modal|button)', task_text)
        for component in component_matches:
            component_name = component.capitalize()
            expected_files = [
                f'src/components/{component_name}.js',
                f'src/components/{component_name}.test.js'
            ]
            for file in expected_files:
                if file not in existing_files:
                    missing.append(file)
        
        # Extract service names
        if 'api' in task_text or 'service' in task_text:
            service_matches = re.findall(r'(\w+)(?:api|service)', task_text)
            for service in service_matches:
                service_name = service.capitalize()
                expected_files = [
                    f'src/services/{service_name}API.js',
                    f'src/services/{service_name}API.test.js'
                ]
                for file in expected_files:
                    if file not in existing_files:
                        missing.append(file)
        
        # Check for utility files
        if 'util' in task_text or 'helper' in task_text:
            util_matches = re.findall(r'(\w+)(?:util|helper)', task_text)
            for util in util_matches:
                util_name = util.lower()
                expected_file = f'src/utils/{util_name}.js'
                if expected_file not in existing_files:
                    missing.append(expected_file)
        
        return missing
    
    def _find_missing_dependencies(self, task_text: str, existing_deps: Set[str]) -> List[str]:
        """Find dependencies that should be installed but aren't"""
        missing = []
        
        # Check for barcode scanning
        if any(word in task_text for word in ['barcode', 'scanner', 'camera']):
            if not any(dep in existing_deps for dep in ['html5-qrcode', 'quagga']):
                missing.append('html5-qrcode')
        
        # Check for API client
        if 'api' in task_text and not any(dep in existing_deps for dep in ['axios', 'fetch']):
            missing.append('axios')
        
        # Check for offline storage
        if 'offline' in task_text or 'cache' in task_text:
            if not any(dep in existing_deps for dep in ['dexie', 'idb']):
                missing.append('dexie')
        
        # Check for testing
        if 'test' in task_text:
            if '@testing-library/react' not in existing_deps:
                missing.append('@testing-library/react')
        
        return missing
    
    def _find_implementation_gaps(self, task_text: str, existing_files: Set[str]) -> List[str]:
        """Find implementation aspects that are missing"""
        gaps = []
        
        # Error handling
        if 'error' in task_text or 'handling' in task_text:
            gaps.append('Error handling implementation')
        
        # Testing
        if any(keyword in task_text for keyword in ['test', 'testing']):
            if not any('test' in f for f in existing_files):
                gaps.append('Test setup and implementation')
        
        # Performance
        if any(keyword in task_text for keyword in ['performance', 'optimize']):
            gaps.append('Performance monitoring setup')
            gaps.append('Optimization implementation')
        
        # Accessibility
        if 'interface' in task_text or 'ui' in task_text:
            gaps.append('Accessibility implementation')
        
        # Mobile/PWA
        if any(keyword in task_text for keyword in ['mobile', 'pwa', 'responsive']):
            gaps.append('Mobile optimization')
            gaps.append('PWA compliance checks')
        
        return gaps
    
    def _find_relevant_todos(self, task_text: str, todos: List[Tuple[str, str]]) -> List[str]:
        """Find TODO comments relevant to this task"""
        relevant = []
        task_keywords = set(task_text.split())
        
        for file_path, todo_text in todos:
            todo_keywords = set(todo_text.lower().split())
            # Check for keyword overlap
            if task_keywords.intersection(todo_keywords):
                relevant.append(f"{file_path}: {todo_text}")
        
        return relevant
    
    def _generate_intelligent_subtasks(self, task: Dict, analysis: TaskAnalysis, todos: List[str]) -> List[Dict]:
        """Generate subtasks based on actual analysis, not templates"""
        subtasks = []
        subtask_id = 1
        
        # Subtasks for missing dependencies
        for dep in analysis.missing_dependencies:
            subtasks.append({
                'id': subtask_id,
                'title': f"Install {dep} dependency",
                'description': f"Add {dep} to package.json and configure for use",
                'dependencies': [],
                'details': f"Run npm install {dep} and set up initial configuration",
                'testStrategy': f"Verify {dep} is properly installed and importable"
            })
            subtask_id += 1
        
        # Subtasks for missing files
        for file in analysis.missing_files:
            file_name = Path(file).stem
            subtasks.append({
                'id': subtask_id,
                'title': f"Create {file_name} file",
                'description': f"Implement {file} with required functionality",
                'dependencies': [],
                'details': f"Create {file} with proper structure and exports",
                'testStrategy': f"Ensure {file} can be imported and used correctly"
            })
            subtask_id += 1
        
        # Subtasks for implementation gaps
        for gap in analysis.implementation_gaps:
            subtasks.append({
                'id': subtask_id,
                'title': f"Implement {gap}",
                'description': f"Add {gap} to meet task requirements",
                'dependencies': [],
                'details': f"Research and implement {gap} following best practices",
                'testStrategy': f"Test {gap} functionality thoroughly"
            })
            subtask_id += 1
        
        # Subtasks for TODO items
        for todo in todos:
            subtasks.append({
                'id': subtask_id,
                'title': f"Address TODO: {todo[:50]}...",
                'description': f"Resolve TODO comment found in codebase",
                'dependencies': [],
                'details': todo,
                'testStrategy': "Verify TODO item is properly resolved"
            })
            subtask_id += 1
        
        # Add integration and testing subtasks if we have multiple components
        if len(analysis.missing_files) > 1:
            subtasks.append({
                'id': subtask_id,
                'title': "Integration testing",
                'description': "Test integration between all components",
                'dependencies': list(range(1, subtask_id)),
                'details': "Create integration tests to verify all components work together",
                'testStrategy': "End-to-end testing of complete functionality"
            })
            subtask_id += 1
        
        return subtasks
    
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
    
    def analyze_all_tasks(self) -> Dict[int, TaskAnalysis]:
        """Analyze all tasks and return intelligent recommendations"""
        tasks = self.get_taskmaster_tasks()
        analyses = {}
        
        print(f"🔍 Scanning project: {self.project_root}")
        print(f"📁 Found {len(list(self.scan_existing_files()))} files")
        print(f"📦 Found {len(self.scan_package_dependencies())} dependencies")
        print(f"📝 Found {len(self.scan_todo_comments())} TODO comments")
        print()
        
        for task in tasks:
            if task.get('subtasks') and len(task['subtasks']) > 0:
                continue  # Skip tasks that already have subtasks
                
            analysis = self.analyze_task_requirements(task)
            analyses[task['id']] = analysis
        
        return analyses
    
    def create_subtasks_for_task(self, task_id: int, analysis: TaskAnalysis, dry_run: bool = True) -> bool:
        """Create subtasks using task-master add-subtask commands"""
        if not analysis.discovered_subtasks:
            print(f"  No subtasks needed for task {task_id}")
            return True
        
        if dry_run:
            print(f"  Would create {len(analysis.discovered_subtasks)} subtasks:")
            for subtask in analysis.discovered_subtasks:
                print(f"    {subtask['id']}. {subtask['title']}")
            return True
        
        print(f"  Creating {len(analysis.discovered_subtasks)} subtasks...")
        for subtask in analysis.discovered_subtasks:
            try:
                cmd = [
                    'task-master', 'add-subtask',
                    f'--parent={task_id}',
                    f'--title={subtask["title"]}',
                    f'--description={subtask["description"]}',
                    f'--details={subtask["details"]}'
                ]
                
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode == 0:
                    print(f"    ✅ {subtask['title']}")
                else:
                    print(f"    ❌ Failed: {subtask['title']}")
                    return False
            except Exception as e:
                print(f"    ❌ Error creating subtask: {e}")
                return False
        
        return True
    
    def run_intelligent_analysis(self, task_ids: Optional[List[int]] = None, dry_run: bool = True):
        """Run intelligent analysis and create subtasks"""
        print("🤖 Intelligent Task Discovery and Expansion Agent")
        print("=" * 60)
        
        analyses = self.analyze_all_tasks()
        
        if not analyses:
            print("No tasks found or all tasks already have subtasks!")
            return
        
        if task_ids:
            analyses = {tid: analysis for tid, analysis in analyses.items() if tid in task_ids}
        
        print(f"{'🔍 DRY RUN: ' if dry_run else '🚀 EXECUTING: '}Intelligent Task Analysis")
        print("-" * 60)
        
        tasks = {t['id']: t for t in self.get_taskmaster_tasks()}
        
        for task_id, analysis in analyses.items():
            task = tasks.get(task_id, {})
            title = task.get('title', f'Task {task_id}')
            
            print(f"\n📋 Task {task_id}: {title}")
            print(f"   Complexity Score: {analysis.complexity_score}")
            
            if analysis.missing_dependencies:
                print(f"   Missing Dependencies: {', '.join(analysis.missing_dependencies)}")
            
            if analysis.missing_files:
                print(f"   Missing Files: {len(analysis.missing_files)} files")
            
            if analysis.implementation_gaps:
                print(f"   Implementation Gaps: {len(analysis.implementation_gaps)} gaps")
            
            if analysis.discovered_subtasks:
                print(f"   Discovered Subtasks: {len(analysis.discovered_subtasks)}")
                self.create_subtasks_for_task(task_id, analysis, dry_run)
            else:
                print("   No additional work discovered - task appears simple")

def main():
    parser = argparse.ArgumentParser(description='Intelligent Task Discovery Agent')
    parser.add_argument('--execute', action='store_true', help='Actually create subtasks (default: dry run)')
    parser.add_argument('--tasks', type=str, help='Comma-separated task IDs to analyze (default: all)')
    parser.add_argument('--project', type=str, default='.', help='Project root directory')
    
    args = parser.parse_args()
    
    task_ids = None
    if args.tasks:
        try:
            task_ids = [int(x.strip()) for x in args.tasks.split(',')]
        except ValueError:
            print("Invalid task IDs format. Use: --tasks=1,2,3")
            sys.exit(1)
    
    agent = IntelligentTaskAgent(args.project)
    agent.run_intelligent_analysis(task_ids=task_ids, dry_run=not args.execute)

if __name__ == "__main__":
    main()