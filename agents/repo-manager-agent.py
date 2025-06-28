#!/usr/bin/env python3
"""
Repository Manager Agent

Handles GitHub repository creation, configuration, and setup within the agent system.
Integrates with Quality & Git Agent for comprehensive repository management.
"""

import json
import subprocess
import sys
import os
import requests
import getpass
from pathlib import Path
from typing import Dict, List, Optional, Any
import argparse

class GitHubRepoManager:
    """GitHub repository management agent"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.config_file = self.project_root / ".git" / "github_config.json"
        self.config = self._load_config()
        
    def _load_config(self) -> Dict[str, Any]:
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
    
    def _save_config(self):
        """Save GitHub configuration"""
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def setup_github_auth(self) -> bool:
        """Setup GitHub authentication"""
        print("🔐 GitHub Authentication Setup")
        print("=" * 40)
        
        # Get username
        if not self.config.get("username"):
            username = input("GitHub username: ").strip()
            if not username:
                print("❌ Username is required")
                return False
            self.config["username"] = username
        
        # Get token
        if not self.config.get("token"):
            print("\n📋 You need a GitHub Personal Access Token")
            print("1. Go to: https://github.com/settings/tokens")
            print("2. Click 'Generate new token (classic)'")
            print("3. Select scopes: 'repo' (for private repos)")
            print("4. Copy the token and paste it here:")
            print()
            
            token = getpass.getpass("GitHub Token (hidden): ").strip()
            if not token:
                print("❌ Token is required")
                return False
            self.config["token"] = token
        
        # Test authentication
        if self._test_github_auth():
            self._save_config()
            print("✅ GitHub authentication successful!")
            return True
        else:
            print("❌ GitHub authentication failed")
            # Clear invalid token
            self.config["token"] = ""
            return False
    
    def _test_github_auth(self) -> bool:
        """Test GitHub authentication"""
        try:
            headers = {
                "Authorization": f"token {self.config['token']}",
                "Accept": "application/vnd.github.v3+json"
            }
            
            response = requests.get("https://api.github.com/user", headers=headers)
            if response.status_code == 200:
                user_data = response.json()
                display_name = user_data.get('name') or user_data.get('login') or 'GitHub User'
                print(f"👋 Hello {display_name}!")
                return True
            
        except Exception as e:
            print(f"❌ Auth test failed: {e}")
        
        return False
    
    def update_token(self) -> bool:
        """Update GitHub token only"""
        print("🔄 Update GitHub Token")
        print("=" * 30)
        
        # Show current username
        current_username = self.config.get("username", "Not set")
        print(f"📝 Current username: {current_username}")
        
        # Show token status
        current_token = self.config.get("token", "")
        if current_token:
            token_preview = current_token[:8] + "..." + current_token[-4:] if len(current_token) > 12 else "***"
            print(f"🔑 Current token: {token_preview}")
        else:
            print("🔑 Current token: Not set")
        
        print("\n📋 To create a new token:")
        print("1. Go to: https://github.com/settings/tokens")
        print("2. Delete old token (if any)")
        print("3. Click 'Generate new token (classic)'")
        print("4. Name: 'Sana Dev Automation - Full Repo Access'")
        print("5. Select scopes:")
        print("   ✅ repo (Full control of private repositories)")
        print("   ✅ workflow (Update GitHub Action workflows)")
        print("6. Copy the token and paste it here:")
        print()
        
        # Get new token
        new_token = getpass.getpass("New GitHub Token (hidden): ").strip()
        if not new_token:
            print("❌ No token provided - keeping existing token")
            return False
        
        # Update token
        old_token = self.config.get("token", "")
        self.config["token"] = new_token
        
        # Test new token
        print("🧪 Testing new token...")
        if self._test_github_auth():
            self._save_config()
            print("✅ Token updated and verified successfully!")
            return True
        else:
            # Restore old token on failure
            self.config["token"] = old_token
            print("❌ New token verification failed - keeping old token")
            return False
    
    def show_auth_status(self) -> bool:
        """Show current authentication status"""
        print("🔐 GitHub Authentication Status")
        print("=" * 35)
        
        username = self.config.get("username", "Not set")
        token = self.config.get("token", "")
        
        print(f"📝 Username: {username}")
        
        if token:
            token_preview = token[:8] + "..." + token[-4:] if len(token) > 12 else "***"
            print(f"🔑 Token: {token_preview}")
            
            # Test current authentication
            print("🧪 Testing authentication...")
            if self._test_github_auth():
                print("✅ Authentication working!")
                return True
            else:
                print("❌ Authentication failed!")
                print("💡 Use --update-token to fix")
                return False
        else:
            print("🔑 Token: Not set")
            print("💡 Use --setup-auth or --update-token to configure")
            return False
    
    def setup_complete_git_workflow(self) -> bool:
        """Complete git setup from scratch to GitHub"""
        print("🚀 Complete Git Workflow Setup")
        print("=" * 40)
        print("This will set up everything needed for git automation:")
        print("• Initialize git repository (if needed)")
        print("• Configure git user settings")
        print("• Set up GitHub authentication")
        print("• Create GitHub repository")
        print("• Make initial commit and push")
        print("• Configure for agent automation")
        print()
        
        # Step 1: Initialize git repository
        if not self._ensure_git_initialized():
            return False
        
        # Step 2: Configure git user settings
        if not self._setup_git_config():
            return False
        
        # Step 3: Ensure GitHub authentication
        if not self._ensure_github_auth():
            return False
        
        # Step 4: Create GitHub repository
        repo_info = self._create_repository_interactive()
        if not repo_info:
            return False
        
        # Step 5: Set up remote and push
        if not self._setup_remote_and_push(repo_info):
            return False
        
        # Step 6: Configure for automation
        self._setup_automation_config()
        
        print("🎉 Complete git workflow setup successful!")
        print(f"🔗 Repository: {repo_info.get('html_url', 'N/A')}")
        print("💡 Your repository is now ready for automated git workflows!")
        
        return True
    
    def _ensure_git_initialized(self) -> bool:
        """Ensure git repository is initialized"""
        git_dir = self.project_root / ".git"
        
        if git_dir.exists():
            print("✅ Git repository already initialized")
            return True
        
        print("🔧 Initializing git repository...")
        try:
            result = subprocess.run(
                ["git", "init"],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                print("✅ Git repository initialized")
                return True
            else:
                print(f"❌ Failed to initialize git: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Error initializing git: {e}")
            return False
    
    def _setup_git_config(self) -> bool:
        """Set up git user configuration"""
        print("🔧 Configuring git user settings...")
        
        try:
            # Check current git config
            name_result = subprocess.run(
                ["git", "config", "user.name"],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            
            email_result = subprocess.run(
                ["git", "config", "user.email"],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            
            current_name = name_result.stdout.strip() if name_result.returncode == 0 else ""
            current_email = email_result.stdout.strip() if email_result.returncode == 0 else ""
            
            # Use existing config or prompt for new
            if current_name and current_email:
                print(f"✅ Git config already set: {current_name} <{current_email}>")
                return True
            
            # Set from stored GitHub username if available
            username = self.config.get("username", "")
            if username and not current_name:
                subprocess.run(
                    ["git", "config", "user.name", username],
                    cwd=self.project_root
                )
                print(f"✅ Set git user.name: {username}")
            
            # Prompt for email if not set
            if not current_email:
                email = input("📧 Git email address: ").strip()
                if email:
                    subprocess.run(
                        ["git", "config", "user.email", email],
                        cwd=self.project_root
                    )
                    print(f"✅ Set git user.email: {email}")
                else:
                    print("⚠️  No email provided - you may need to set this later")
            
            return True
            
        except Exception as e:
            print(f"❌ Error configuring git: {e}")
            return False
    
    def _ensure_github_auth(self) -> bool:
        """Ensure GitHub authentication is working"""
        print("🔧 Checking GitHub authentication...")
        
        # Test current auth
        if self.config.get("token") and self._test_github_auth():
            print("✅ GitHub authentication already working")
            return True
        
        # Need to set up auth
        print("⚠️  GitHub authentication needed")
        return self.setup_github_auth()
    
    def _create_repository_interactive(self) -> Optional[Dict[str, Any]]:
        """Create repository with smart defaults"""
        print("🔧 Creating GitHub repository...")
        
        # Suggest repository name
        suggested_name = self.suggest_repo_name()
        repo_name = input(f"Repository name [{suggested_name}]: ").strip() or suggested_name
        
        # Suggest description
        suggested_desc = self.generate_description()
        description = input(f"Description [{suggested_desc}]: ").strip() or suggested_desc
        
        # Default to private
        is_private = True
        privacy_input = input("Private repository? [Y/n]: ").strip().lower()
        if privacy_input in ['n', 'no', 'false']:
            is_private = False
        
        print(f"🚀 Creating '{repo_name}' ({'private' if is_private else 'public'})...")
        
        return self.create_repository(repo_name, description, is_private)
    
    def _setup_remote_and_push(self, repo_info: Dict[str, Any]) -> bool:
        """Set up git remote and make initial push"""
        if not repo_info or not repo_info.get('success'):
            return False
        
        clone_url = repo_info.get('clone_url', '')
        if not clone_url:
            print("❌ No repository URL available")
            return False
        
        print("🔧 Setting up git remote and pushing...")
        
        try:
            # Add remote origin
            subprocess.run(
                ["git", "remote", "add", "origin", clone_url],
                cwd=self.project_root,
                capture_output=True
            )
            
            # Stage all files
            subprocess.run(
                ["git", "add", "."],
                cwd=self.project_root
            )
            
            # Make initial commit
            commit_result = subprocess.run(
                ["git", "commit", "-m", "Initial commit - agent system setup"],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            
            if commit_result.returncode != 0:
                print("ℹ️  No changes to commit")
            
            # Push to repository
            push_result = subprocess.run(
                ["git", "push", "-u", "origin", "main"],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            
            if push_result.returncode == 0:
                print("✅ Successfully pushed to GitHub!")
                return True
            else:
                # Try master branch if main fails
                push_result = subprocess.run(
                    ["git", "push", "-u", "origin", "master"],
                    cwd=self.project_root,
                    capture_output=True,
                    text=True
                )
                
                if push_result.returncode == 0:
                    print("✅ Successfully pushed to GitHub!")
                    return True
                else:
                    print(f"❌ Failed to push: {push_result.stderr}")
                    return False
                    
        except Exception as e:
            print(f"❌ Error setting up remote: {e}")
            return False
    
    def _setup_automation_config(self):
        """Set up configuration for complete agent automation"""
        print("🔧 Configuring complete agent automation...")
        
        # Create comprehensive automation config
        automation_config = {
            "git_automation": True,
            "auto_commit": True,
            "conventional_commits": True,
            "auto_branch": True,
            "agent_coordination": True,
            "dynamic_workflows": True,
            "setup_date": "2024-12-27",
            "repository_url": "",
            "agent_system": {
                "planning_analysis_agent": "agents/planning-analysis-agent.py",
                "universal_execution_agent": "agents/universal-execution-agent.py", 
                "quality_git_agent": "agents/quality-git-agent.py",
                "agent_coordinator": "agents/agent-coordinator.py",
                "repo_manager": "agents/repo-manager-agent.py",
                "agent_interface": "agents/agent-interface.py"
            },
            "features": {
                "pristine_improvement_prompts": True,
                "dynamic_data_generation": True,
                "light_user_experience": True,
                "github_integration": True,
                "git_workflow_automation": True,
                "task_coordination": True,
                "quality_gates": True,
                "sequential_thinking": True,
                "advanced_reasoning": True,
                "context_aware_decisions": True
            }
        }
        
        # Try to get current remote URL
        try:
            result = subprocess.run(
                ["git", "remote", "get-url", "origin"],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                automation_config["repository_url"] = result.stdout.strip()
        except:
            pass
        
        # Create .taskmaster directory structure
        config_dir = self.project_root / ".taskmaster"
        config_dir.mkdir(exist_ok=True)
        
        # Create subdirectories for agent coordination
        for subdir in ["tasks", "agent_sync", "coordination"]:
            (config_dir / subdir).mkdir(exist_ok=True)
        
        # Save comprehensive config
        config_file = config_dir / "git_automation.json"
        with open(config_file, 'w') as f:
            json.dump(automation_config, f, indent=2)
        
        # Create agent system documentation
        self._create_system_documentation()
        
        print("✅ Complete agent automation configured")
        print("📋 Created .taskmaster/ directory structure")
        print("📚 Generated system documentation")
    
    def _create_system_documentation(self):
        """Create documentation for the agent system"""
        docs_content = """# Universal Development Automation Agent System

## Quick Start

### Single Command Setup
```bash
python3 agents/repo-manager-agent.py --setup-complete
```

### Run Complete Workflow
```bash
python3 agents/agent-coordinator.py --workflow --tag agents --verbose
```

### Natural Language Interface
```bash
python3 agents/agent-interface.py
```

## Agent System Components

### 1. Planning & Analysis Agent
- Task complexity analysis
- Dynamic subtask generation  
- Pristine improvement suggestions
- Git workflow planning

### 2. Universal Execution Agent
- Dynamic task execution
- Automatic git branch creation
- Conventional commit messages
- File/dependency management

### 3. Quality & Git Agent
- Quality checks and testing
- GitHub repository management
- Git workflow coordination
- Documentation updates

### 4. Agent Coordinator
- Cross-agent synchronization
- Quality gate enforcement
- Git workflow coordination
- Error recovery

### 5. Repository Manager Agent
- Complete git setup automation
- GitHub authentication
- Repository creation and configuration
- Token management

### 6. Agent Interface
- Light user experience
- Natural language processing
- Intent analysis and routing

## Features

✅ **Dynamic Data Generation** - No hardcoded examples
✅ **Git Workflow Automation** - Automatic branching and commits  
✅ **Agent Coordination** - Synchronized multi-agent workflows
✅ **Quality Gates** - Automated testing and validation
✅ **GitHub Integration** - Repository management and automation
✅ **Light UX** - Natural language input → automated output
✅ **Sequential Thinking** - Advanced reasoning for complex problems
✅ **Context-Aware Decisions** - Smart adaptation to project patterns

## Usage Examples

### Update GitHub Token
```bash
python3 agents/repo-manager-agent.py --update-token
```

### Check System Status  
```bash
python3 agents/repo-manager-agent.py --status
```

### Run Individual Agents
```bash
python3 agents/planning-analysis-agent.py --tag agents
python3 agents/universal-execution-agent.py --tag agents  
python3 agents/quality-git-agent.py --tag agents
```

### Create New Repository
```bash
python3 agents/repo-manager-agent.py --repo-name "my-project"
```

Generated by Universal Development Automation Agent System
"""
        
        readme_file = self.project_root / "AGENT_SYSTEM.md"
        with open(readme_file, 'w') as f:
            f.write(docs_content)
    
    def run_agent_system_test(self) -> bool:
        """Run a comprehensive test of the agent system"""
        print("🧪 Running Agent System Integration Test")
        print("=" * 45)
        
        # Test 1: Check all agent files exist
        print("📁 Checking agent files...")
        agent_files = [
            "agents/planning-analysis-agent.py",
            "agents/universal-execution-agent.py", 
            "agents/quality-git-agent.py",
            "agents/agent-coordinator.py",
            "agents/repo-manager-agent.py",
            "agents/agent-interface.py"
        ]
        
        missing_files = []
        for agent_file in agent_files:
            if not (self.project_root / agent_file).exists():
                missing_files.append(agent_file)
        
        if missing_files:
            print(f"❌ Missing agent files: {missing_files}")
            return False
        else:
            print("✅ All agent files present")
        
        # Test 2: Check GitHub authentication
        print("🔑 Testing GitHub authentication...")
        if not self._test_github_auth():
            print("❌ GitHub authentication failed")
            return False
        else:
            print("✅ GitHub authentication working")
        
        # Test 3: Check git configuration
        print("🔧 Checking git configuration...")
        try:
            name_result = subprocess.run(
                ["git", "config", "user.name"],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            email_result = subprocess.run(
                ["git", "config", "user.email"], 
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            
            if name_result.returncode == 0 and email_result.returncode == 0:
                print(f"✅ Git configured: {name_result.stdout.strip()} <{email_result.stdout.strip()}>")
            else:
                print("⚠️  Git configuration incomplete")
        except:
            print("❌ Git configuration check failed")
            return False
        
        # Test 4: Check .taskmaster structure
        print("📋 Checking .taskmaster structure...")
        taskmaster_dir = self.project_root / ".taskmaster"
        required_dirs = ["tasks", "agent_sync", "coordination"]
        
        for dir_name in required_dirs:
            if not (taskmaster_dir / dir_name).exists():
                print(f"⚠️  Missing directory: .taskmaster/{dir_name}")
                (taskmaster_dir / dir_name).mkdir(parents=True, exist_ok=True)
                print(f"✅ Created: .taskmaster/{dir_name}")
            else:
                print(f"✅ Found: .taskmaster/{dir_name}")
        
        # Test 5: Test agent coordination capabilities
        print("🤝 Testing agent coordination...")
        try:
            coordinator_test = subprocess.run(
                ["python3", "agents/agent-coordinator.py", "--help"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if coordinator_test.returncode == 0:
                print("✅ Agent Coordinator responsive")
            else:
                print("⚠️  Agent Coordinator issues detected")
        except:
            print("❌ Agent Coordinator test failed")
        
        print("\n🎉 Agent System Integration Test Complete!")
        print("💡 System is ready for automated development workflows")
        return True
    
    def create_repository(self, repo_name: str, description: str = "", private: bool = True) -> Dict[str, Any]:
        """Create a new GitHub repository"""
        print(f"🚀 Creating repository: {repo_name}")
        
        # Ensure authentication
        if not self.config.get("token") or not self._test_github_auth():
            if not self.setup_github_auth():
                return {"success": False, "error": "Authentication failed"}
        
        # Create repository via GitHub API
        repo_data = {
            "name": repo_name,
            "description": description,
            "private": private,
            "auto_init": False  # We already have files
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
                print(f"✅ Repository created: {repo_info['html_url']}")
                
                # Setup local git remote
                remote_setup = self._setup_git_remote(repo_info)
                
                return {
                    "success": True,
                    "repo_url": repo_info["html_url"],
                    "clone_url": repo_info["clone_url"],
                    "ssh_url": repo_info["ssh_url"],
                    "remote_setup": remote_setup
                }
            
            else:
                error_msg = response.json().get("message", "Unknown error")
                print(f"❌ Failed to create repository: {error_msg}")
                return {"success": False, "error": error_msg}
                
        except Exception as e:
            print(f"❌ Error creating repository: {e}")
            return {"success": False, "error": str(e)}
    
    def _setup_git_remote(self, repo_info: Dict[str, Any]) -> Dict[str, Any]:
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
                print("📝 Remote 'origin' already exists, updating...")
                subprocess.run(
                    ["git", "remote", "set-url", "origin", repo_info["clone_url"]],
                    cwd=self.project_root,
                    check=True
                )
            else:
                print("🔗 Adding remote 'origin'...")
                subprocess.run(
                    ["git", "remote", "add", "origin", repo_info["clone_url"]],
                    cwd=self.project_root,
                    check=True
                )
            
            # Push to repository
            print("📤 Pushing to repository...")
            push_result = subprocess.run(
                ["git", "push", "-u", "origin", "main"],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            
            if push_result.returncode == 0:
                print("✅ Successfully pushed to repository!")
                return {"success": True, "output": push_result.stdout}
            else:
                print(f"❌ Push failed: {push_result.stderr}")
                return {"success": False, "error": push_result.stderr}
                
        except Exception as e:
            print(f"❌ Error setting up remote: {e}")
            return {"success": False, "error": str(e)}
    
    def suggest_repo_name(self) -> str:
        """Suggest a repository name based on project"""
        # Try to determine project name from directory or files
        project_name = self.project_root.name
        
        # Check for specific files that might indicate project type
        if (self.project_root / "agents").exists():
            return f"{project_name}-dev-automation"
        elif (self.project_root / "package.json").exists():
            try:
                with open(self.project_root / "package.json", 'r') as f:
                    data = json.load(f)
                    return data.get("name", project_name)
            except:
                pass
        
        return project_name
    
    def generate_description(self) -> str:
        """Generate repository description based on project content"""
        descriptions = []
        
        # Check for agent system
        if (self.project_root / "agents").exists():
            descriptions.append("Universal Development Automation Agent System")
        
        # Check for specific frameworks
        if (self.project_root / "package.json").exists():
            descriptions.append("JavaScript/Node.js project")
        
        if (self.project_root / "requirements.txt").exists():
            descriptions.append("Python project")
        
        # Check for README content
        readme_files = ["README.md", "readme.md", "README.txt"]
        for readme in readme_files:
            readme_path = self.project_root / readme
            if readme_path.exists():
                try:
                    with open(readme_path, 'r') as f:
                        content = f.read()[:200]  # First 200 chars
                        if content.strip():
                            return content.strip().replace('\n', ' ')
                except:
                    pass
        
        if descriptions:
            return " - ".join(descriptions)
        else:
            return "Development project with automated tooling"

def main():
    """Main repository manager function"""
    parser = argparse.ArgumentParser(description='Repository Manager Agent')
    parser.add_argument('--project-root', type=str, default='.', help='Project root directory')
    parser.add_argument('--repo-name', type=str, help='Repository name')
    parser.add_argument('--description', type=str, help='Repository description')
    parser.add_argument('--public', action='store_true', help='Make repository public (default: private)')
    parser.add_argument('--setup-auth', action='store_true', help='Setup GitHub authentication')
    parser.add_argument('--update-token', action='store_true', help='Update GitHub token only')
    parser.add_argument('--status', action='store_true', help='Show authentication status')
    parser.add_argument('--setup-complete', action='store_true', help='Complete git workflow setup (recommended)')
    parser.add_argument('--test-system', action='store_true', help='Run comprehensive agent system test')
    parser.add_argument('--interactive', '-i', action='store_true', help='Interactive mode')
    # Common agent arguments for master agent compatibility
    parser.add_argument('--verbose', action='store_true', help='Verbose output')
    parser.add_argument('--action', type=str, help='Action to perform (for master agent compatibility)')
    
    args = parser.parse_args()
    
    manager = GitHubRepoManager(args.project_root)
    
    print("🔧 Repository Manager Agent")
    print("=" * 30)
    
    if args.setup_complete:
        manager.setup_complete_git_workflow()
        return
    
    if args.setup_auth:
        manager.setup_github_auth()
        return
    
    if args.update_token:
        manager.update_token()
        return
    
    if args.status:
        manager.show_auth_status()
        return
    
    if args.test_system:
        manager.run_agent_system_test()
        return
    
    if args.interactive or not args.repo_name:
        # Interactive mode
        print(f"📁 Project: {manager.project_root.absolute()}")
        print()
        
        # Suggest repository name
        suggested_name = manager.suggest_repo_name()
        repo_name = input(f"Repository name [{suggested_name}]: ").strip() or suggested_name
        
        # Suggest description
        suggested_desc = manager.generate_description()
        description = input(f"Description [{suggested_desc}]: ").strip() or suggested_desc
        
        # Ask about privacy
        is_private = not args.public
        privacy_input = input(f"Private repository? [{'Y' if is_private else 'N'}]: ").strip().lower()
        if privacy_input in ['n', 'no', 'false']:
            is_private = False
        elif privacy_input in ['y', 'yes', 'true']:
            is_private = True
        
        print()
        print(f"Creating repository '{repo_name}':")
        print(f"  Description: {description}")
        print(f"  Private: {is_private}")
        print()
        
        confirm = input("Proceed? [Y/n]: ").strip().lower()
        if confirm in ['n', 'no']:
            print("❌ Cancelled")
            return
    
    else:
        # Use command line arguments
        repo_name = args.repo_name
        description = args.description or manager.generate_description()
        is_private = not args.public
    
    # Create repository
    result = manager.create_repository(repo_name, description, is_private)
    
    if result["success"]:
        print()
        print("🎉 Repository Setup Complete!")
        print(f"🔗 URL: {result['repo_url']}")
        
        if result.get("remote_setup", {}).get("success"):
            print("✅ Code pushed successfully")
        else:
            print("⚠️  Repository created but push failed")
            print("   You may need to push manually or check authentication")
    
    else:
        print(f"❌ Failed to create repository: {result['error']}")
        sys.exit(1)

if __name__ == "__main__":
    main()