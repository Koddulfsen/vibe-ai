#!/usr/bin/env python3
"""
Task Master Agent System - Interactive Launcher
==============================================

Super simple, menu-driven interface for the Task Master Agent System.
Automatically handles dependencies and guides users through everything.

Usage: python3 start.py
"""

import os
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Any
import subprocess

# Add agents directory to path
AGENT_DIR = Path(__file__).parent / "agents"
sys.path.insert(0, str(AGENT_DIR))

try:
    from dependency_manager import SmartDependencyManager
    DEPENDENCY_MANAGER_AVAILABLE = True
except ImportError:
    DEPENDENCY_MANAGER_AVAILABLE = False

try:
    from service_integrator import ServiceIntegrator
    SERVICE_INTEGRATOR_AVAILABLE = True
except ImportError:
    SERVICE_INTEGRATOR_AVAILABLE = False

# Import master agent
sys.path.insert(0, str(Path(__file__).parent))
try:
    # Simple subprocess approach - more reliable
    import subprocess
    test_result = subprocess.run(
        ["python3", str(Path(__file__).parent / "master-agent.py"), "status"],
        capture_output=True,
        text=True,
        timeout=10
    )
    MASTER_AGENT_AVAILABLE = test_result.returncode == 0
    MasterAgent = None  # Will use subprocess calls
    WorkflowType = None
except:
    MASTER_AGENT_AVAILABLE = False
    MasterAgent = None
    WorkflowType = None

class InteractiveLauncher:
    """Interactive menu-driven interface for Task Master Agent System"""
    
    def __init__(self):
        self.project_root = Path.cwd()
        self.master_agent = None
        self.dependency_manager = None
        self.service_integrator = None
        self.setup_complete = False
        
    def start(self):
        """Main entry point for the interactive launcher"""
        self.show_welcome()
        
        # Quick dependency check
        if DEPENDENCY_MANAGER_AVAILABLE:
            self.dependency_manager = SmartDependencyManager(self.project_root)
            self.check_basic_dependencies()
        
        # Initialize master agent (using subprocess approach)
        if MASTER_AGENT_AVAILABLE:
            self.master_agent = None  # Will use subprocess calls directly
        
        # Initialize service integrator
        if SERVICE_INTEGRATOR_AVAILABLE:
            self.service_integrator = ServiceIntegrator()
        
        # Main menu loop
        while True:
            try:
                choice = self.show_main_menu()
                if not self.handle_menu_choice(choice):
                    break
            except KeyboardInterrupt:
                self.show_goodbye()
                break
            except Exception as e:
                print(f"\n❌ An error occurred: {e}")
                input("Press Enter to continue...")
    
    def show_welcome(self):
        """Show welcome screen"""
        os.system('clear' if os.name == 'posix' else 'cls')
        print("🚀 " + "=" * 60)
        print("   TASK MASTER AGENT SYSTEM - Interactive Launcher")
        print("   Intelligent automation made simple")
        print("=" * 62)
        print()
        print(f"📁 Project: {self.project_root}")
        print(f"🐍 Python: {sys.version.split()[0]}")
        print()
    
    def check_basic_dependencies(self):
        """Quick check and setup of basic dependencies"""
        print("🔍 Checking system requirements...")
        
        if self.dependency_manager:
            essential = self.dependency_manager.quick_check()
            missing = [name for name, installed in essential.items() if not installed]
            
            if missing:
                print(f"⚠️  Missing: {', '.join(missing)}")
                print("🛠️  Running quick setup...")
                self.dependency_manager.setup_project()
            else:
                print("✅ System requirements OK")
        
        time.sleep(1)
    
    def run_master_agent_command(self, command: str, args: List[str] = None) -> bool:
        """Execute master agent command via subprocess"""
        if not MASTER_AGENT_AVAILABLE:
            print("❌ Master agent not available")
            return False
        
        cmd = ["python3", str(Path(__file__).parent / "master-agent.py"), command]
        if args:
            cmd.extend(args)
        
        try:
            result = subprocess.run(cmd, capture_output=False, text=True)
            return result.returncode == 0
        except Exception as e:
            print(f"❌ Command failed: {e}")
            return False
    
    def show_main_menu(self) -> str:
        """Show main menu and get user choice"""
        print("\n" + "=" * 70)
        print("🎯 TASK MASTER - CENTRAL DEVELOPMENT HUB")
        print("=" * 70)
        print()
        print("🏗️  PROJECT CREATION & SETUP")
        print("   1) 🎨 Create New Project       - Full-stack project with integrations")
        print("   2) 🔌 Service Integrations     - Connect GitHub, cloud services, APIs")
        print("   3) 🚀 Deploy Existing Project  - Push current project to production")
        print()
        print("📋 ANALYSIS & PLANNING")
        print("   4) 🔍 Analyze Project          - Understand tasks & complexity")
        print("   5) 📊 Project Complexity       - Detailed complexity analysis")
        print("   6) 🎯 Planning Session         - Interactive planning workshop")
        print()
        print("⚡ EXECUTION & DEVELOPMENT")
        print("   7) 🚀 Quick Development        - Auto-detect and execute tasks")
        print("   8) 🎪 Full Workflow           - Complete analysis → execution → quality")
        print("   9) 🛠️  Custom Execution        - Choose specific tasks to run")
        print()
        print("✅ QUALITY & TESTING")
        print("   a) 🧪 Quality Check           - Run tests and quality analysis")
        print("   b) 🔧 Fix Issues              - Auto-fix quality issues")
        print("   c) 📝 Generate Reports        - Create quality and progress reports")
        print()
        print("⚙️  SYSTEM & SETUP")
        print("   s) 🔧 System Setup            - Install dependencies & configure")
        print("   m) ⚙️  Manage Configuration    - System and service settings")
        print("   h) ❓ Help & Documentation    - Learn how to use the system")
        print("   q) 👋 Quit                    - Exit the application")
        print()
        
        while True:
            choice = input("🤔 Choose an option (1-9, a-c, s/m/h/q): ").strip().lower()
            if choice in ['1', '2', '3', '4', '5', '6', '7', '8', '9', 'a', 'b', 'c', 's', 'm', 'h', 'q']:
                return choice
            print("❌ Invalid choice. Please enter 1-9, a-c, s, m, h, or q")
    
    def handle_menu_choice(self, choice: str) -> bool:
        """Handle user menu choice. Returns False to exit."""
        
        if choice == 'q':
            self.show_goodbye()
            return False
        
        elif choice == '1':
            self.create_new_project()
        
        elif choice == '2':
            self.service_integrations()
        
        elif choice == '3':
            self.deploy_existing_project()
        
        elif choice == '4':
            self.analyze_project()
        
        elif choice == '5':
            self.complexity_analysis()
        
        elif choice == '6':
            self.planning_session()
        
        elif choice == '7':
            self.quick_development()
        
        elif choice == '8':
            self.full_workflow()
        
        elif choice == '9':
            self.custom_execution()
        
        elif choice == 'a':
            self.quality_check()
        
        elif choice == 'b':
            self.fix_issues()
        
        elif choice == 'c':
            self.generate_reports()
        
        elif choice == 's':
            self.system_setup()
        
        elif choice == 'm':
            self.configuration()
        
        elif choice == 'h':
            self.show_help()
        
        input("\n📋 Press Enter to continue...")
        return True
    
    def create_new_project(self):
        """Create a new project with full integrations"""
        print("\n🎨 CREATE NEW PROJECT")
        print("=" * 40)
        
        print("🏗️  Choose project type:")
        print("   1) React App (Frontend)")
        print("   2) Python API (Backend)")
        print("   3) Full-Stack App (React + Python)")
        print("   4) Static Website")
        print("   5) Node.js Application")
        
        project_type = input("\nChoose type (1-5): ").strip()
        
        if project_type == '1':
            self._create_react_project()
        elif project_type == '2':
            self._create_python_api()
        elif project_type == '3':
            self._create_fullstack_project()
        elif project_type == '4':
            self._create_static_website()
        elif project_type == '5':
            self._create_nodejs_app()
        else:
            print("❌ Invalid choice")
    
    def service_integrations(self):
        """Manage service integrations"""
        print("\n🔌 SERVICE INTEGRATIONS")
        print("=" * 40)
        
        if not self.service_integrator:
            print("❌ Service integrator not available")
            return
        
        while True:
            choice = self.service_integrator.show_integration_menu()
            
            if choice == 'c':
                self._configure_new_service()
            elif choice == 's':
                self.service_integrator.show_configured_services()
                input("\nPress Enter to continue...")
            elif choice == 'r':
                self._remove_service()
            elif choice == 'b':
                break
            else:
                print("❌ Invalid choice")
    
    def deploy_existing_project(self):
        """Deploy the current project"""
        print("\n🚀 DEPLOY EXISTING PROJECT")
        print("=" * 40)
        
        if not self.service_integrator:
            print("❌ Service integrator not available")
            return
        
        print("🎯 Choose deployment target:")
        print("   1) Vercel (Frontend/Static)")
        print("   2) Heroku (Full-Stack)")
        print("   3) AWS (Advanced)")
        print("   4) GitHub Pages (Static)")
        
        choice = input("\nChoose target (1-4): ").strip()
        
        if choice == '1':
            self._deploy_to_vercel()
        elif choice == '2':
            self._deploy_to_heroku()
        elif choice == '3':
            self._deploy_to_aws()
        elif choice == '4':
            self._deploy_to_github_pages()
        else:
            print("❌ Invalid choice")
    
    def _create_react_project(self):
        """Create a React project with full setup"""
        print("\n🎨 Creating React Project")
        print("-" * 30)
        
        project_name = input("📝 Project name: ").strip()
        if not project_name:
            print("❌ Project name required")
            return
        
        print(f"\n🚀 Creating React app: {project_name}")
        print("   This will:")
        print("   📁 Create React project structure")
        print("   🐙 Set up GitHub repository (if configured)")
        print("   🚀 Configure deployment (if services available)")
        print("   📦 Install dependencies")
        
        confirm = input("\n🤔 Proceed? (Y/n): ").strip().lower()
        if confirm and confirm != 'y' and confirm != 'yes':
            print("⏭️  Project creation cancelled")
            return
        
        target_dir = self.project_root / project_name
        
        if self.service_integrator:
            success = self.service_integrator.create_full_project('react', project_name, target_dir)
            if success:
                print(f"\n✅ React project '{project_name}' created successfully!")
                print(f"📁 Location: {target_dir}")
                print("\n💡 Next steps:")
                print(f"   cd {project_name}")
                print("   npm start")
            else:
                print("❌ Project creation failed")
        else:
            print("❌ Service integrator not available")
    
    def _create_python_api(self):
        """Create a Python API project"""
        print("\n🐍 Creating Python API Project")
        print("-" * 30)
        print("🚧 Python API template coming soon!")
        print("   Will include: FastAPI, database setup, authentication")
    
    def _create_fullstack_project(self):
        """Create a full-stack project"""
        print("\n🌟 Creating Full-Stack Project")
        print("-" * 30)
        print("🚧 Full-stack template coming soon!")
        print("   Will include: React frontend + Python/Node backend")
    
    def _create_static_website(self):
        """Create a static website"""
        print("\n📄 Creating Static Website")
        print("-" * 30)
        print("🚧 Static website template coming soon!")
        print("   Will include: HTML/CSS/JS with modern build tools")
    
    def _create_nodejs_app(self):
        """Create a Node.js application"""
        print("\n💚 Creating Node.js Application")
        print("-" * 30)
        print("🚧 Node.js template coming soon!")
        print("   Will include: Express.js, database, API setup")
    
    def _configure_new_service(self):
        """Configure a new service"""
        print("\n🔧 Configure New Service")
        print("-" * 30)
        
        print("Available services:")
        print("   1) GitHub - Repository management")
        print("   2) Vercel - Frontend deployment")
        print("   3) Heroku - Full-stack deployment")
        print("   4) AWS - Cloud infrastructure")
        
        choice = input("\nChoose service (1-4): ").strip()
        
        if choice == '1':
            self.service_integrator.configure_service('github')
        elif choice == '2':
            self.service_integrator.configure_service('vercel')
        elif choice == '3':
            print("🚧 Heroku integration coming soon!")
        elif choice == '4':
            print("🚧 AWS integration coming soon!")
        else:
            print("❌ Invalid choice")
    
    def _remove_service(self):
        """Remove a configured service"""
        services = self.service_integrator.credential_manager.list_credentials()
        
        if not services:
            print("📭 No configured services to remove")
            return
        
        print("\n🗑️  Remove Service")
        print("-" * 20)
        
        for i, service in enumerate(services, 1):
            print(f"   {i}) {service}")
        
        try:
            choice = int(input(f"\nChoose service to remove (1-{len(services)}): ").strip())
            if 1 <= choice <= len(services):
                service_name = services[choice - 1]
                confirm = input(f"🤔 Remove {service_name}? (y/N): ").strip().lower()
                if confirm == 'y':
                    if self.service_integrator.credential_manager.delete_credential(service_name):
                        print(f"✅ {service_name} removed")
                    else:
                        print(f"❌ Failed to remove {service_name}")
                else:
                    print("⏭️  Removal cancelled")
            else:
                print("❌ Invalid choice")
        except ValueError:
            print("❌ Please enter a number")
    
    def _deploy_to_vercel(self):
        """Deploy to Vercel"""
        if not self.service_integrator:
            return
        
        if 'vercel' not in self.service_integrator.credential_manager.list_credentials():
            print("⚠️  Vercel not configured. Setting up now...")
            if not self.service_integrator.configure_service('vercel'):
                print("❌ Vercel setup failed")
                return
        
        print("🚀 Deploying to Vercel...")
        success = self.service_integrator.cloud.deploy_to_vercel(self.project_root)
        
        if success:
            print("✅ Deployment successful!")
        else:
            print("❌ Deployment failed")
    
    def _deploy_to_heroku(self):
        """Deploy to Heroku"""
        print("🚧 Heroku deployment coming soon!")
    
    def _deploy_to_aws(self):
        """Deploy to AWS"""
        print("🚧 AWS deployment coming soon!")
    
    def _deploy_to_github_pages(self):
        """Deploy to GitHub Pages"""
        print("🚧 GitHub Pages deployment coming soon!")
    
    def analyze_project(self):
        """Run project analysis"""
        print("\n🔍 PROJECT ANALYSIS")
        print("=" * 40)
        
        # Get project tag
        tag = self._get_project_tag()
        
        print(f"\n🚀 Analyzing project with tag: '{tag}'")
        print("   This will examine your project structure and identify tasks...")
        
        # Use subprocess to run analysis
        args = ["--tag", tag, "--complexity"]
        self.run_master_agent_command("analyze", args)
    
    def complexity_analysis(self):
        """Run detailed complexity analysis"""
        print("\n📊 COMPLEXITY ANALYSIS")
        print("=" * 40)
        
        tag = self._get_project_tag()
        
        print(f"\n🧮 Running detailed complexity analysis for: '{tag}'")
        print("   This will provide in-depth scoring and recommendations...")
        
        if self.master_agent:
            try:
                # Run with focus on complexity
                results = self.master_agent.run_smart_workflow('analyze', {
                    'tag': tag, 
                    'complexity': True,
                    'detailed': True
                })
                self.master_agent.print_enhanced_results(results)
                
                # Show detailed quality reports if available
                for result in results:
                    if result.quality_report:
                        self.master_agent.show_detailed_quality_report(result)
                
            except Exception as e:
                print(f"❌ Complexity analysis failed: {e}")
        else:
            print("❌ Master agent not available")
    
    def planning_session(self):
        """Interactive planning session"""
        print("\n🎯 PLANNING SESSION")
        print("=" * 40)
        
        print("🤔 Let's plan your project step by step...")
        print()
        
        # Gather project information
        project_goal = input("What is your main project goal? ").strip()
        if not project_goal:
            project_goal = "general development"
        
        timeline = input("What's your timeline? (days/weeks) ").strip()
        if not timeline:
            timeline = "flexible"
        
        complexity = input("Expected complexity? (simple/medium/complex) ").strip().lower()
        if complexity not in ['simple', 'medium', 'complex']:
            complexity = 'medium'
        
        print(f"\n📋 Planning for: {project_goal}")
        print(f"⏰ Timeline: {timeline}")
        print(f"🎚️  Complexity: {complexity}")
        
        if self.master_agent:
            try:
                results = self.master_agent.run_smart_workflow('workflow', {
                    'type': 'planning',
                    'goal': project_goal,
                    'timeline': timeline,
                    'complexity': complexity
                })
                self.master_agent.print_enhanced_results(results)
            except Exception as e:
                print(f"❌ Planning session failed: {e}")
    
    def quick_development(self):
        """Quick development workflow"""
        print("\n🚀 QUICK DEVELOPMENT")
        print("=" * 40)
        
        print("🎪 Auto-detecting your project and running optimal workflow...")
        
        # Auto-detect project type and tasks
        tag = self._auto_detect_tag()
        
        print(f"📂 Detected project type: {tag}")
        print("🔄 Running: Analysis → Execution → Quality Check")
        
        if self.master_agent:
            try:
                results = self.master_agent.run_smart_workflow('workflow', {
                    'type': 'full-dev',
                    'tag': tag,
                    'auto': True
                })
                self.master_agent.print_enhanced_results(results)
            except Exception as e:
                print(f"❌ Quick development failed: {e}")
    
    def full_workflow(self):
        """Complete development workflow"""
        print("\n🎪 FULL WORKFLOW")
        print("=" * 40)
        
        tag = self._get_project_tag()
        
        print(f"🌟 Running complete workflow for: '{tag}'")
        print("   📋 Phase 1: Analysis & Planning")
        print("   ⚡ Phase 2: Task Execution")
        print("   ✅ Phase 3: Quality Control")
        print("   📂 Phase 4: Repository Management")
        
        confirm = input("\n🤔 Proceed with full workflow? (Y/n): ").strip().lower()
        if confirm and confirm != 'y' and confirm != 'yes':
            print("⏭️  Workflow cancelled")
            return
        
        if self.master_agent:
            try:
                results = self.master_agent.run_smart_workflow('workflow', {
                    'type': 'full-dev',
                    'tag': tag,
                    'auto': False,
                    'fix': True
                })
                self.master_agent.print_enhanced_results(results)
            except Exception as e:
                print(f"❌ Full workflow failed: {e}")
    
    def custom_execution(self):
        """Custom task execution"""
        print("\n🛠️  CUSTOM EXECUTION")
        print("=" * 40)
        
        print("🎯 Choose what you want to execute:")
        print("   1) Specific Task ID")
        print("   2) Task Category/Tag")
        print("   3) Custom Agent")
        
        choice = input("Choose (1-3): ").strip()
        
        if choice == '1':
            task_id = input("Enter Task ID (e.g., 1.2): ").strip()
            if task_id and self.master_agent:
                try:
                    results = self.master_agent.run_smart_workflow('execute', {
                        'task_id': task_id,
                        'auto': False
                    })
                    self.master_agent.print_enhanced_results(results)
                except Exception as e:
                    print(f"❌ Task execution failed: {e}")
        
        elif choice == '2':
            tag = self._get_project_tag()
            if self.master_agent:
                try:
                    results = self.master_agent.run_smart_workflow('execute', {
                        'tag': tag,
                        'auto': False
                    })
                    self.master_agent.print_enhanced_results(results)
                except Exception as e:
                    print(f"❌ Execution failed: {e}")
        
        elif choice == '3':
            self._run_custom_agent()
    
    def quality_check(self):
        """Run quality checks"""
        print("\n🧪 QUALITY CHECK")
        print("=" * 40)
        
        print("🔍 Running comprehensive quality analysis...")
        
        if self.master_agent:
            try:
                results = self.master_agent.run_smart_workflow('quality', {
                    'fix': False,
                    'comprehensive': True
                })
                self.master_agent.print_enhanced_results(results)
            except Exception as e:
                print(f"❌ Quality check failed: {e}")
    
    def fix_issues(self):
        """Auto-fix quality issues"""
        print("\n🔧 FIX ISSUES")
        print("=" * 40)
        
        print("🛠️  Running quality check with auto-fix enabled...")
        print("   This will attempt to automatically fix found issues.")
        
        confirm = input("🤔 Proceed with auto-fix? (Y/n): ").strip().lower()
        if confirm and confirm != 'y' and confirm != 'yes':
            print("⏭️  Auto-fix cancelled")
            return
        
        if self.master_agent:
            try:
                results = self.master_agent.run_smart_workflow('quality', {
                    'fix': True,
                    'auto': True
                })
                self.master_agent.print_enhanced_results(results)
            except Exception as e:
                print(f"❌ Auto-fix failed: {e}")
    
    def generate_reports(self):
        """Generate quality and progress reports"""
        print("\n📝 GENERATE REPORTS")
        print("=" * 40)
        
        print("📊 Generating comprehensive project reports...")
        
        # This would integrate with reporting functionality
        print("🚧 Report generation feature coming soon!")
        print("   For now, run quality checks to see detailed assessments.")
    
    def system_setup(self):
        """System setup and dependency management"""
        print("\n🔧 SYSTEM SETUP")
        print("=" * 40)
        
        if self.dependency_manager:
            print("🔍 Analyzing project dependencies...")
            success = self.dependency_manager.setup_project()
            
            if success:
                print("✅ System setup complete!")
                self.setup_complete = True
            else:
                print("⚠️  Setup completed with some issues")
        else:
            print("❌ Dependency manager not available")
    
    def configuration(self):
        """System configuration"""
        print("\n⚙️  CONFIGURATION")
        print("=" * 40)
        
        print("🛠️  Configuration options:")
        print("   1) View current settings")
        print("   2) Set API keys")
        print("   3) Configure agents")
        print("   4) Reset to defaults")
        
        choice = input("Choose (1-4): ").strip()
        
        if choice == '1':
            self._show_current_config()
        elif choice == '2':
            self._configure_api_keys()
        elif choice == '3':
            self._configure_agents()
        elif choice == '4':
            self._reset_config()
    
    def show_help(self):
        """Show help and documentation"""
        print("\n❓ HELP & DOCUMENTATION")
        print("=" * 40)
        
        print("📚 Task Master Agent System Help")
        print()
        print("🎯 PURPOSE:")
        print("   Intelligent automation for development workflows")
        print("   Analyzes, executes, and quality-checks your projects")
        print()
        print("🚀 QUICK START:")
        print("   1) Choose 'Analyze Project' to understand your codebase")
        print("   2) Use 'Quick Development' for automatic workflows")
        print("   3) Run 'Quality Check' to validate your work")
        print()
        print("💡 TIPS:")
        print("   • Start with project analysis to understand what's possible")
        print("   • Use tags to organize and filter tasks")
        print("   • Quality checks provide detailed improvement suggestions")
        print("   • Full workflow runs end-to-end automation")
        print()
        print("🔧 SETUP:")
        print("   • System automatically detects and installs dependencies")
        print("   • Configure API keys in Configuration menu if needed")
        print("   • All settings are saved automatically")
    
    def show_goodbye(self):
        """Show goodbye message"""
        print("\n👋 " + "=" * 50)
        print("   Thanks for using Task Master Agent System!")
        print("   Happy coding! 🚀")
        print("=" * 52)
    
    # Helper methods
    
    def _get_project_tag(self) -> str:
        """Get project tag from user input with smart defaults"""
        suggestions = self._get_tag_suggestions()
        
        if suggestions:
            print(f"\n💡 Suggested tags: {', '.join(suggestions)}")
        
        tag = input("Enter project tag (or press Enter for auto-detect): ").strip()
        
        if not tag:
            tag = self._auto_detect_tag()
            print(f"🤖 Auto-detected tag: '{tag}'")
        
        return tag
    
    def _auto_detect_tag(self) -> str:
        """Auto-detect appropriate project tag"""
        # Simple detection based on project files
        if (self.project_root / "package.json").exists():
            return "javascript"
        elif any((self.project_root / f).exists() for f in ["requirements.txt", "setup.py", "pyproject.toml"]):
            return "python"
        elif (self.project_root / "agents").exists():
            return "agents"
        elif (self.project_root / ".git").exists():
            return "development"
        else:
            return "general"
    
    def _get_tag_suggestions(self) -> List[str]:
        """Get tag suggestions based on project analysis"""
        suggestions = []
        
        # Check for common project types
        if (self.project_root / "agents").exists():
            suggestions.append("agents")
        if (self.project_root / "package.json").exists():
            suggestions.append("javascript")
        if any((self.project_root / f).exists() for f in ["requirements.txt", "setup.py"]):
            suggestions.append("python")
        if (self.project_root / ".git").exists():
            suggestions.append("git")
        
        return suggestions[:3]  # Limit to top 3
    
    def _run_custom_agent(self):
        """Run a specific agent"""
        print("\n🤖 Available Agents:")
        agents = ['planning', 'execution', 'quality', 'coordinator', 'repo']
        
        for i, agent in enumerate(agents, 1):
            print(f"   {i}) {agent.title()} Agent")
        
        try:
            choice = int(input("\nChoose agent (1-5): ").strip())
            if 1 <= choice <= len(agents):
                agent_name = agents[choice - 1]
                print(f"\n🚀 Running {agent_name} agent...")
                
                if self.master_agent:
                    result = self.master_agent.run_agent_enhanced(agent_name, ["--verbose"])
                    self.master_agent.print_enhanced_results([result])
            else:
                print("❌ Invalid choice")
        except ValueError:
            print("❌ Please enter a number")
    
    def _show_current_config(self):
        """Show current configuration"""
        print("\n📋 Current Configuration:")
        print(f"   Project Root: {self.project_root}")
        print(f"   Setup Complete: {self.setup_complete}")
        
        if self.master_agent:
            status = self.master_agent.show_status()
            print(f"   Available Agents: {len(status['agents'])}")
        
    def _configure_api_keys(self):
        """Configure API keys"""
        print("\n🔑 API Key Configuration:")
        print("   This would configure API keys for external services")
        print("   (Implementation would securely handle API key storage)")
    
    def _configure_agents(self):
        """Configure individual agents"""
        print("\n🤖 Agent Configuration:")
        print("   This would allow customizing individual agent behavior")
        print("   (Implementation would provide agent-specific settings)")
    
    def _reset_config(self):
        """Reset configuration to defaults"""
        confirm = input("🤔 Reset all settings to defaults? (y/N): ").strip().lower()
        if confirm == 'y' or confirm == 'yes':
            print("🔄 Configuration reset to defaults")
            self.setup_complete = False
        else:
            print("⏭️  Reset cancelled")
    
    # Non-interactive mode methods
    def run_non_interactive_analyze(self, tag: str):
        """Run analysis in non-interactive mode"""
        print(f"\n🔍 Running analysis for tag: {tag}")
        
        if MASTER_AGENT_AVAILABLE:
            try:
                result = subprocess.run(
                    ["python3", str(Path(__file__).parent / "master-agent.py"), "analyze", "--tag", tag],
                    cwd=Path.cwd(),
                    text=True
                )
                if result.returncode != 0:
                    print("❌ Analysis failed")
                    sys.exit(1)
            except Exception as e:
                print(f"❌ Analysis failed: {e}")
                sys.exit(1)
        else:
            print("❌ Master agent not available")
            sys.exit(1)
    
    def run_non_interactive_execute(self, tag: str):
        """Run execution in non-interactive mode"""
        print(f"\n⚡ Running execution for tag: {tag}")
        
        if self.master_agent:
            try:
                results = self.master_agent.run_smart_workflow('execute', {
                    'tag': tag,
                    'auto': True
                })
                self.master_agent.print_enhanced_results(results)
            except Exception as e:
                print(f"❌ Execution failed: {e}")
                sys.exit(1)
        else:
            print("❌ Master agent not available")
            sys.exit(1)
    
    def run_non_interactive_quality(self):
        """Run quality checks in non-interactive mode"""
        print("\n🧪 Running quality checks...")
        
        if self.master_agent:
            try:
                results = self.master_agent.run_smart_workflow('quality', {
                    'fix': False,
                    'comprehensive': True
                })
                self.master_agent.print_enhanced_results(results)
            except Exception as e:
                print(f"❌ Quality check failed: {e}")
                sys.exit(1)
        else:
            print("❌ Master agent not available")
            sys.exit(1)
    
    def run_non_interactive_workflow(self, workflow_type: str):
        """Run workflow in non-interactive mode"""
        print(f"\n🎪 Running {workflow_type} workflow...")
        
        valid_types = ['analyze', 'execute', 'quality', 'full-dev', 'planning']
        if workflow_type not in valid_types:
            print(f"❌ Invalid workflow type: {workflow_type}")
            print(f"   Valid types: {', '.join(valid_types)}")
            sys.exit(1)
        
        if self.master_agent:
            try:
                if workflow_type == 'full-dev':
                    tag = self._auto_detect_tag()
                    results = self.master_agent.run_smart_workflow('workflow', {
                        'type': 'full-dev',
                        'tag': tag,
                        'auto': True
                    })
                elif workflow_type == 'analyze':
                    tag = self._auto_detect_tag()
                    results = self.master_agent.run_smart_workflow('analyze', {
                        'tag': tag,
                        'complexity': True
                    })
                elif workflow_type == 'execute':
                    tag = self._auto_detect_tag()
                    results = self.master_agent.run_smart_workflow('execute', {
                        'tag': tag,
                        'auto': True
                    })
                elif workflow_type == 'quality':
                    results = self.master_agent.run_smart_workflow('quality', {
                        'fix': False,
                        'comprehensive': True
                    })
                elif workflow_type == 'planning':
                    results = self.master_agent.run_smart_workflow('workflow', {
                        'type': 'planning',
                        'goal': 'general development',
                        'timeline': 'flexible',
                        'complexity': 'medium'
                    })
                
                self.master_agent.print_enhanced_results(results)
            except Exception as e:
                print(f"❌ Workflow failed: {e}")
                sys.exit(1)
        else:
            print("❌ Master agent not available")
            sys.exit(1)

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Task Master Agent System')
    parser.add_argument('--non-interactive', action='store_true', 
                       help='Run in non-interactive mode (for automated environments)')
    parser.add_argument('--analyze', type=str, metavar='TAG',
                       help='Run analysis with specified tag')
    parser.add_argument('--execute', type=str, metavar='TAG',
                       help='Run execution with specified tag')
    parser.add_argument('--quality', action='store_true',
                       help='Run quality checks')
    parser.add_argument('--workflow', type=str, metavar='TYPE',
                       help='Run workflow (analyze, execute, quality, full-dev)')
    
    args = parser.parse_args()
    
    launcher = InteractiveLauncher()
    
    # Handle non-interactive modes
    if args.non_interactive:
        print("🤖 Running in non-interactive mode")
        if args.analyze:
            launcher.run_non_interactive_analyze(args.analyze)
        elif args.execute:
            launcher.run_non_interactive_execute(args.execute)
        elif args.quality:
            launcher.run_non_interactive_quality()
        elif args.workflow:
            launcher.run_non_interactive_workflow(args.workflow)
        else:
            print("❌ Non-interactive mode requires --analyze, --execute, --quality, or --workflow")
            sys.exit(1)
    else:
        # Interactive mode
        launcher.start()

if __name__ == "__main__":
    main()