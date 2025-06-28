#!/usr/bin/env python3
"""
Smart Dependency Manager
=======================

Automatically detects and installs required packages and tools for the Task Master system.
Makes setup as simple and fast as possible for users.
"""

import os
import sys
import subprocess
import json
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass
from enum import Enum
import tempfile
import platform

class DependencyType(Enum):
    """Types of dependencies that can be managed"""
    PYTHON_PACKAGE = "python_package"
    SYSTEM_PACKAGE = "system_package"
    NODE_PACKAGE = "node_package"
    BINARY_TOOL = "binary_tool"
    API_KEY = "api_key"

@dataclass
class Dependency:
    """Represents a dependency requirement"""
    name: str
    type: DependencyType
    version: Optional[str] = None
    install_command: Optional[str] = None
    check_command: Optional[str] = None
    required_for: List[str] = None
    description: str = ""
    auto_install: bool = True

class DependencyDetector:
    """Detects what dependencies are needed based on project analysis"""
    
    def __init__(self, project_root: Path = None):
        self.project_root = project_root or Path.cwd()
        
    def detect_project_dependencies(self) -> List[Dependency]:
        """Analyze project and detect required dependencies"""
        dependencies = []
        
        # Always needed: Basic Python packages
        dependencies.extend(self._get_core_dependencies())
        
        # Detect based on project files
        dependencies.extend(self._detect_from_project_files())
        
        # Detect based on git repository
        if (self.project_root / ".git").exists():
            dependencies.extend(self._get_git_dependencies())
        
        # Detect Node.js dependencies
        if (self.project_root / "package.json").exists():
            dependencies.extend(self._get_nodejs_dependencies())
        
        # Detect Python dependencies
        if any((self.project_root / name).exists() for name in ["requirements.txt", "setup.py", "pyproject.toml"]):
            dependencies.extend(self._get_python_dependencies())
        
        return dependencies
    
    def _get_core_dependencies(self) -> List[Dependency]:
        """Get core dependencies always needed"""
        return [
            Dependency(
                name="git",
                type=DependencyType.BINARY_TOOL,
                check_command="git --version",
                install_command=self._get_git_install_command(),
                required_for=["git-agent", "repository-manager"],
                description="Version control system",
                auto_install=False  # Usually pre-installed
            ),
            Dependency(
                name="python3",
                type=DependencyType.BINARY_TOOL,
                check_command="python3 --version",
                required_for=["all-agents"],
                description="Python interpreter",
                auto_install=False  # Usually pre-installed
            )
        ]
    
    def _detect_from_project_files(self) -> List[Dependency]:
        """Detect dependencies from project file analysis"""
        dependencies = []
        
        # Scan Python files for imports
        python_files = list(self.project_root.glob("**/*.py"))
        if python_files:
            imports = self._extract_python_imports(python_files)
            dependencies.extend(self._convert_imports_to_dependencies(imports))
        
        # Scan for configuration files
        config_files = [
            "requirements.txt", "setup.py", "pyproject.toml", "Pipfile",
            "package.json", "yarn.lock", "Gemfile", "go.mod"
        ]
        
        for config_file in config_files:
            if (self.project_root / config_file).exists():
                dependencies.extend(self._parse_config_file(config_file))
        
        return dependencies
    
    def _get_git_dependencies(self) -> List[Dependency]:
        """Get git-related dependencies"""
        return [
            Dependency(
                name="gh",
                type=DependencyType.BINARY_TOOL,
                check_command="gh --version",
                install_command="curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg && echo 'deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main' | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null && sudo apt update && sudo apt install gh",
                required_for=["quality-git-agent"],
                description="GitHub CLI for repository operations",
                auto_install=True
            )
        ]
    
    def _get_nodejs_dependencies(self) -> List[Dependency]:
        """Get Node.js related dependencies"""
        return [
            Dependency(
                name="node",
                type=DependencyType.BINARY_TOOL,
                check_command="node --version",
                install_command=self._get_nodejs_install_command(),
                required_for=["execution-agent"],
                description="Node.js runtime",
                auto_install=True
            ),
            Dependency(
                name="npm",
                type=DependencyType.BINARY_TOOL,
                check_command="npm --version",
                required_for=["execution-agent"],
                description="Node package manager",
                auto_install=False  # Comes with Node.js
            )
        ]
    
    def _get_python_dependencies(self) -> List[Dependency]:
        """Get Python-specific dependencies"""
        deps = []
        
        # Read requirements.txt if it exists
        req_file = self.project_root / "requirements.txt"
        if req_file.exists():
            with open(req_file) as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        pkg_name = line.split('==')[0].split('>=')[0].split('<=')[0]
                        deps.append(Dependency(
                            name=pkg_name,
                            type=DependencyType.PYTHON_PACKAGE,
                            install_command=f"pip install {line}",
                            check_command=f"python -c 'import {pkg_name}'",
                            description=f"Python package: {pkg_name}",
                            auto_install=True
                        ))
        
        return deps
    
    def _extract_python_imports(self, files: List[Path]) -> Set[str]:
        """Extract import statements from Python files"""
        imports = set()
        
        for file in files[:20]:  # Limit to avoid performance issues
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Extract import statements
                import re
                import_patterns = [
                    r'^import\s+(\w+)',
                    r'^from\s+(\w+)\s+import',
                ]
                
                for pattern in import_patterns:
                    matches = re.findall(pattern, content, re.MULTILINE)
                    imports.update(matches)
                    
            except Exception:
                continue  # Skip files that can't be read
        
        return imports
    
    def _convert_imports_to_dependencies(self, imports: Set[str]) -> List[Dependency]:
        """Convert Python imports to dependency objects"""
        # Common packages that might need installation
        known_packages = {
            'requests': 'requests',
            'flask': 'flask',
            'django': 'django',
            'numpy': 'numpy',
            'pandas': 'pandas',
            'pytest': 'pytest',
            'click': 'click',
            'rich': 'rich',
            'colorama': 'colorama',
            'pyyaml': 'pyyaml',
            'psutil': 'psutil',
            'aiohttp': 'aiohttp'
        }
        
        dependencies = []
        for imp in imports:
            if imp in known_packages:
                dependencies.append(Dependency(
                    name=known_packages[imp],
                    type=DependencyType.PYTHON_PACKAGE,
                    install_command=f"pip install {known_packages[imp]}",
                    check_command=f"python -c 'import {imp}'",
                    description=f"Python package: {known_packages[imp]}",
                    auto_install=True
                ))
        
        return dependencies
    
    def _parse_config_file(self, filename: str) -> List[Dependency]:
        """Parse configuration files for dependencies"""
        # Simplified parsing - could be expanded
        return []
    
    def _get_git_install_command(self) -> str:
        """Get appropriate git installation command"""
        system = platform.system().lower()
        if system == "linux":
            return "sudo apt-get update && sudo apt-get install -y git"
        elif system == "darwin":
            return "brew install git"
        elif system == "windows":
            return "winget install Git.Git"
        return "echo 'Please install git manually'"
    
    def _get_nodejs_install_command(self) -> str:
        """Get appropriate Node.js installation command"""
        system = platform.system().lower()
        if system == "linux":
            return "curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash - && sudo apt-get install -y nodejs"
        elif system == "darwin":
            return "brew install node"
        elif system == "windows":
            return "winget install OpenJS.NodeJS"
        return "echo 'Please install Node.js manually'"

class DependencyInstaller:
    """Handles automatic installation of dependencies"""
    
    def __init__(self, auto_confirm: bool = False):
        self.auto_confirm = auto_confirm
        self.installation_log = []
    
    def install_dependencies(self, dependencies: List[Dependency]) -> Dict[str, bool]:
        """Install all dependencies with user confirmation"""
        results = {}
        
        # Group dependencies by type for efficient installation
        grouped = self._group_dependencies(dependencies)
        
        print("🔍 Checking dependencies...")
        
        # Check what's already installed
        missing_deps = []
        for dep in dependencies:
            if not self._is_installed(dep):
                missing_deps.append(dep)
            else:
                results[dep.name] = True
                print(f"✅ {dep.name} - already installed")
        
        if not missing_deps:
            print("🎉 All dependencies are already installed!")
            return results
        
        print(f"\n📦 Found {len(missing_deps)} missing dependencies:")
        for dep in missing_deps:
            print(f"   - {dep.name}: {dep.description}")
        
        if not self.auto_confirm:
            response = input(f"\n🤔 Install {len(missing_deps)} missing dependencies? (Y/n): ").strip().lower()
            if response and response != 'y' and response != 'yes':
                print("⏭️  Skipping dependency installation")
                return results
        
        # Install missing dependencies
        print("\n🚀 Installing dependencies...")
        for dep in missing_deps:
            if dep.auto_install:
                results[dep.name] = self._install_dependency(dep)
            else:
                print(f"⚠️  {dep.name} requires manual installation: {dep.install_command or 'See documentation'}")
                results[dep.name] = False
        
        return results
    
    def _group_dependencies(self, dependencies: List[Dependency]) -> Dict[DependencyType, List[Dependency]]:
        """Group dependencies by type for batch installation"""
        grouped = {}
        for dep in dependencies:
            if dep.type not in grouped:
                grouped[dep.type] = []
            grouped[dep.type].append(dep)
        return grouped
    
    def _is_installed(self, dependency: Dependency) -> bool:
        """Check if a dependency is already installed"""
        if dependency.check_command:
            try:
                result = subprocess.run(
                    dependency.check_command.split(),
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                return result.returncode == 0
            except Exception:
                return False
        
        # Default checks based on type
        if dependency.type == DependencyType.PYTHON_PACKAGE:
            try:
                subprocess.run([sys.executable, "-c", f"import {dependency.name}"], 
                             check=True, capture_output=True)
                return True
            except subprocess.CalledProcessError:
                return False
        
        elif dependency.type == DependencyType.BINARY_TOOL:
            return shutil.which(dependency.name) is not None
        
        return False
    
    def _install_dependency(self, dependency: Dependency) -> bool:
        """Install a single dependency"""
        print(f"📥 Installing {dependency.name}...")
        
        if not dependency.install_command:
            print(f"   ❌ No installation command available for {dependency.name}")
            return False
        
        try:
            # Execute installation command
            if dependency.type == DependencyType.PYTHON_PACKAGE:
                # Use current Python interpreter for package installation
                cmd = dependency.install_command.replace("pip", f"{sys.executable} -m pip")
            else:
                cmd = dependency.install_command
            
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            if result.returncode == 0:
                print(f"   ✅ {dependency.name} installed successfully")
                self.installation_log.append(f"✅ {dependency.name}: SUCCESS")
                
                # Verify installation
                if self._is_installed(dependency):
                    return True
                else:
                    print(f"   ⚠️  {dependency.name} installation completed but verification failed")
                    return False
            else:
                print(f"   ❌ {dependency.name} installation failed: {result.stderr}")
                self.installation_log.append(f"❌ {dependency.name}: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print(f"   ⏰ {dependency.name} installation timed out")
            return False
        except Exception as e:
            print(f"   ❌ {dependency.name} installation error: {e}")
            self.installation_log.append(f"❌ {dependency.name}: {str(e)}")
            return False
    
    def get_installation_summary(self) -> str:
        """Get a summary of installation results"""
        if not self.installation_log:
            return "No installations performed"
        
        return "\n".join(self.installation_log)

class SmartDependencyManager:
    """Main class that combines detection and installation"""
    
    def __init__(self, project_root: Path = None, auto_confirm: bool = False):
        self.project_root = project_root or Path.cwd()
        self.detector = DependencyDetector(project_root)
        self.installer = DependencyInstaller(auto_confirm)
    
    def setup_project(self) -> bool:
        """Complete dependency setup for the project"""
        print("🎯 Task Master Agent System - Smart Setup")
        print("=" * 50)
        print(f"📁 Project: {self.project_root}")
        print()
        
        # Detect dependencies
        dependencies = self.detector.detect_project_dependencies()
        
        if not dependencies:
            print("🎉 No additional dependencies needed!")
            return True
        
        # Install dependencies
        results = self.installer.install_dependencies(dependencies)
        
        # Summary
        total = len(results)
        successful = sum(1 for success in results.values() if success)
        failed = total - successful
        
        print(f"\n📊 Setup Summary:")
        print(f"   Total dependencies: {total}")
        print(f"   ✅ Successful: {successful}")
        if failed > 0:
            print(f"   ❌ Failed: {failed}")
        
        if failed == 0:
            print("\n🎉 All dependencies installed successfully!")
            print("   You're ready to use Task Master Agent System!")
            return True
        else:
            print(f"\n⚠️  Some dependencies failed to install.")
            print("   You may need to install them manually.")
            return False
    
    def quick_check(self) -> Dict[str, bool]:
        """Quick check of essential dependencies"""
        essential_deps = [
            Dependency("python3", DependencyType.BINARY_TOOL, check_command="python3 --version"),
            Dependency("git", DependencyType.BINARY_TOOL, check_command="git --version"),
        ]
        
        results = {}
        for dep in essential_deps:
            results[dep.name] = self.installer._is_installed(dep)
        
        return results