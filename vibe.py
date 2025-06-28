#!/usr/bin/env python3
"""
vibe - The intuitive interface to vibe.ai

A user-first experience that makes AI-powered development simple and delightful.
Just tell vibe what you want to build, and watch the magic happen.
"""

import os
import sys
import argparse
import json
from typing import Optional, Dict, Any, List
from datetime import datetime
import subprocess
from pathlib import Path

# Try to import rich for better UI
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from rich.table import Table
    from rich.markdown import Markdown
    from rich.prompt import Prompt, Confirm
    from rich import print as rprint
    RICH_AVAILABLE = True
    console = Console()
except ImportError:
    RICH_AVAILABLE = False
    console = None

# Import session tracking
try:
    from session_manager import get_session_manager, EventType
    from session_integration import integrate_with_existing_tools
    SESSION_TRACKING = True
    # Initialize session
    session = get_session_manager()
    session.add_context("vibe_startup", datetime.now().isoformat())
except ImportError:
    SESSION_TRACKING = False
    session = None


class VibeInterface:
    """The main vibe interface focused on user experience"""
    
    def __init__(self):
        self.vibe_dir = Path(__file__).parent
        self.agent_based_engine = self.vibe_dir / "agent_based_solution_engine.py"
        self.master_agent = self.vibe_dir / "master-agent.py"
        self.start_script = self.vibe_dir / "start.py"
        self.non_interactive = not sys.stdin.isatty()
        
    def run(self):
        """Main entry point with smart context detection"""
        # Check if any command line arguments
        if len(sys.argv) > 1:
            self.handle_command()
        else:
            self.interactive_mode()
    
    def interactive_mode(self):
        """Beautiful interactive mode when no arguments provided"""
        if self.non_interactive:
            if RICH_AVAILABLE:
                console.print("[yellow]Non-interactive mode detected. Please provide a command.[/yellow]")
                console.print("Usage: vibe.py [command] [options]")
                console.print("Try: vibe.py --help")
            else:
                print("Non-interactive mode detected. Please provide a command.")
                print("Usage: vibe.py [command] [options]")
                print("Try: vibe.py --help")
            sys.exit(1)
            
        self.show_welcome()
        
        # Keep running until user exits
        while True:
            try:
                self.show_main_menu()
                    
            except KeyboardInterrupt:
                if RICH_AVAILABLE:
                    console.print("\n[yellow]Exiting vibe.ai. Thanks for using![/yellow]")
                else:
                    print("\nExiting vibe.ai. Thanks for using!")
                break
            except EOFError:
                # Handle Ctrl+D
                if RICH_AVAILABLE:
                    console.print("\n[yellow]Goodbye![/yellow]")
                else:
                    print("\nGoodbye!")
                break
    
    def show_main_menu(self):
        """Show the main menu with clear options"""
        if RICH_AVAILABLE:
            console.print("\n[bold green]What do you want to do?[/bold green]\n")
            console.print("[bold cyan]1[/bold cyan] → Make something new")
            console.print("[bold cyan]2[/bold cyan] → Exit\n")
            
            choice = Prompt.ask("Type 1 or 2", choices=["1", "2"], default="1")
        else:
            print("\nWhat do you want to do?\n")
            print("1 → Make something new")
            print("2 → Exit\n")
            
            choice = input("Type 1 or 2: ").strip()
        
        # Handle menu choices
        if choice == "1":
            self.build_new_project()
        elif choice == "2":
            if RICH_AVAILABLE:
                console.print("\n[green]Bye bye! 👋[/green]")
            else:
                print("\nBye bye! 👋")
            sys.exit(0)
        else:
            if RICH_AVAILABLE:
                console.print("[yellow]Just type 1 or 2 😊[/yellow]")
            else:
                print("Just type 1 or 2 😊")
    
    def build_new_project(self):
        """Start with Oracle consultation, then deep philosophical conversation"""
        if RICH_AVAILABLE:
            console.print("\n[bold magenta]✨ Let's explore your idea deeply! ✨[/bold magenta]\n")
            console.print("[dim]First, I'll consult the Oracle to understand the true essence...[/dim]")
            console.print("[dim]Then we'll have a philosophical conversation about your vision.[/dim]\n")
            
            project_idea = Prompt.ask("[cyan]What vision calls to you?[/cyan]")
        else:
            print("\n✨ Let's explore your idea deeply! ✨\n")
            print("First, I'll consult the Oracle to understand the true essence...")
            print("Then we'll have a philosophical conversation about your vision.\n")
            
            project_idea = input("What vision calls to you? ")
        
        # First, consult the Oracle
        from prompting_oracle_agent import PromptingInterface
        oracle_interface = PromptingInterface()
        
        if RICH_AVAILABLE:
            console.print("\n[purple]🔮 Consulting the Prompting Oracle...[/purple]\n")
        else:
            print("\n🔮 Consulting the Prompting Oracle...\n")
        
        oracle_result = oracle_interface.consult_oracle(project_idea)
        oracle_interface.display_oracle_wisdom(oracle_result)
        
        # Wait for user to absorb Oracle's wisdom
        if RICH_AVAILABLE:
            console.print("\n[dim]Press Enter to begin the deep conversation with enhanced consciousness...[/dim]")
        else:
            print("\nPress Enter to begin the deep conversation with enhanced consciousness...")
        input()
        
        # Start deep conversation with Oracle enhancement
        import asyncio
        from deep_planner_agent import DeepConversationInterface
        
        # Set Brave API key if available
        os.environ["BRAVE_API_KEY"] = "BSArXZ987KsjfuUmJRTvpXPjuYVP7-I"
        
        interface = DeepConversationInterface()
        # Pass Oracle results to enhance the conversation
        interface.oracle_wisdom = oracle_result
        asyncio.run(interface.start_conversation(project_idea))
        
        # After conversation, ask if they want to build it
        if RICH_AVAILABLE:
            console.print("\n[yellow]The PRD has been created from our deep dialogue.[/yellow]")
            if Confirm.ask("Would you like me to build this vision now?"):
                # Extract folder name from idea
                folder_name = project_idea.lower().replace(" ", "-")
                folder_name = ''.join(c if c.isalnum() or c == '-' else '-' for c in folder_name)
                folder_name = folder_name.strip('-') or "transcendent-project"
                
                self.execute_task(project_idea, folder_name)
        else:
            print("\nThe PRD has been created from our deep dialogue.")
            build_now = input("Would you like me to build this vision now? (y/n): ").lower()
            if build_now == 'y':
                folder_name = project_idea.lower().replace(" ", "-")
                folder_name = ''.join(c if c.isalnum() or c == '-' else '-' for c in folder_name)
                folder_name = folder_name.strip('-') or "transcendent-project"
                
                self.execute_task(project_idea, folder_name)
    
    
    def show_welcome(self):
        """Display a beautiful welcome message"""
        if RICH_AVAILABLE:
            console.print("\n[bold magenta]🌟 Hi! I'm vibe! 🌟[/bold magenta]")
            console.print("[yellow]I can make cool things for you![/yellow]\n")
        else:
            print("\n🌟 Hi! I'm vibe! 🌟")
            print("I can make cool things for you!\n")
    
    def analyze_context(self) -> Dict[str, Any]:
        """Analyze the current directory context"""
        context = {
            "in_project": False,
            "project_type": None,
            "has_git": False,
            "languages": [],
            "frameworks": [],
            "suggestions": []
        }
        
        # Check for common project files
        current_dir = Path.cwd()
        
        # Git check
        if (current_dir / ".git").exists():
            context["has_git"] = True
            context["in_project"] = True
        
        # Language detection
        if (current_dir / "package.json").exists():
            context["languages"].append("JavaScript/Node.js")
            context["in_project"] = True
            # Check for frameworks
            try:
                with open(current_dir / "package.json") as f:
                    pkg = json.load(f)
                    deps = pkg.get("dependencies", {})
                    if "react" in deps:
                        context["frameworks"].append("React")
                    if "vue" in deps:
                        context["frameworks"].append("Vue")
                    if "express" in deps:
                        context["frameworks"].append("Express")
            except:
                pass
        
        if (current_dir / "requirements.txt").exists() or (current_dir / "setup.py").exists():
            context["languages"].append("Python")
            context["in_project"] = True
        
        if (current_dir / "go.mod").exists():
            context["languages"].append("Go")
            context["in_project"] = True
        
        if (current_dir / "Cargo.toml").exists():
            context["languages"].append("Rust")
            context["in_project"] = True
        
        # Generate smart suggestions based on context
        if context["in_project"]:
            if "Python" in context["languages"]:
                context["suggestions"].extend([
                    "Add REST API endpoints",
                    "Create unit tests",
                    "Add database models",
                    "Generate documentation"
                ])
            if "JavaScript/Node.js" in context["languages"]:
                if "React" in context["frameworks"]:
                    context["suggestions"].extend([
                        "Add new React component",
                        "Create custom hook",
                        "Add state management"
                    ])
                else:
                    context["suggestions"].extend([
                        "Create Express API",
                        "Add authentication",
                        "Setup database connection"
                    ])
        
        return context
    
    def show_project_options(self, context: Dict[str, Any]):
        """Show options for existing project"""
        if RICH_AVAILABLE:
            # Show project info
            info = Table(title="📁 Current Project", show_header=False)
            info.add_column("Property", style="cyan")
            info.add_column("Value", style="green")
            
            info.add_row("Languages", ", ".join(context["languages"]) or "Unknown")
            info.add_row("Frameworks", ", ".join(context["frameworks"]) or "None detected")
            info.add_row("Git", "✓" if context["has_git"] else "✗")
            
            console.print(info)
            console.print()
            
            # Show suggestions
            if context["suggestions"]:
                console.print("[bold]Suggested actions:[/bold]")
                for i, suggestion in enumerate(context["suggestions"], 1):
                    console.print(f"  {i}. {suggestion}")
                console.print(f"  {len(context['suggestions']) + 1}. Something else...")
                console.print(f"  {len(context['suggestions']) + 2}. Exit")
                console.print()
            
            choice = Prompt.ask("What would you like to do?", default="1")
        else:
            print("\n📁 Current Project Detected")
            print(f"Languages: {', '.join(context['languages']) or 'Unknown'}")
            print(f"Frameworks: {', '.join(context['frameworks']) or 'None detected'}")
            print()
            
            if context["suggestions"]:
                print("Suggested actions:")
                for i, suggestion in enumerate(context["suggestions"], 1):
                    print(f"  {i}. {suggestion}")
                print(f"  {len(context['suggestions']) + 1}. Something else...")
                print(f"  {len(context['suggestions']) + 2}. Exit")
            
            choice = input("\nWhat would you like to do? (number or description): ")
        
        # Process choice
        try:
            choice_idx = int(choice) - 1
            if 0 <= choice_idx < len(context["suggestions"]):
                self.execute_task(context["suggestions"][choice_idx])
            elif choice_idx == len(context["suggestions"]):
                # "Something else" option
                self.get_custom_task()
            elif choice_idx == len(context["suggestions"]) + 1:
                # Exit option
                if RICH_AVAILABLE:
                    console.print("[yellow]Thanks for using vibe.ai![/yellow]")
                else:
                    print("Thanks for using vibe.ai!")
                sys.exit(0)
            else:
                self.get_custom_task()
        except ValueError:
            # Check if user typed "exit" or "quit"
            if choice.lower() in ["exit", "quit", "q"]:
                if RICH_AVAILABLE:
                    console.print("[yellow]Thanks for using vibe.ai![/yellow]")
                else:
                    print("Thanks for using vibe.ai!")
                sys.exit(0)
            # User entered custom description
            self.execute_task(choice)
    
    def show_new_project_options(self):
        """Show options for creating new project"""
        if RICH_AVAILABLE:
            options = [
                "Build a REST API",
                "Create a web application", 
                "Build a CLI tool",
                "Create a microservice",
                "Build a data pipeline",
                "Something custom..."
            ]
            
            console.print("[bold]What would you like to build?[/bold]")
            for i, option in enumerate(options, 1):
                console.print(f"  {i}. {option}")
            
            choice = Prompt.ask("\nYour choice", default="6")
        else:
            print("\nWhat would you like to build?")
            options = [
                "Build a REST API",
                "Create a web application",
                "Build a CLI tool", 
                "Create a microservice",
                "Build a data pipeline",
                "Something custom..."
            ]
            for i, option in enumerate(options, 1):
                print(f"  {i}. {option}")
            
            choice = input("\nYour choice (number or description): ")
        
        # Process choice
        try:
            choice_idx = int(choice) - 1
            if 0 <= choice_idx < len(options) - 1:
                self.execute_task(options[choice_idx])
            else:
                self.get_custom_task()
        except ValueError:
            self.execute_task(choice)
    
    def get_custom_task(self):
        """Get custom task from user"""
        if RICH_AVAILABLE:
            task = Prompt.ask("\n[cyan]Describe what you want to build[/cyan]")
        else:
            task = input("\nDescribe what you want to build: ")
        
        self.execute_task(task)
    
    def execute_task(self, description: str, output_dir: Optional[str] = None):
        """Execute the task with beautiful progress display"""
        # Track task execution
        if SESSION_TRACKING and session:
            session.add_event(
                EventType.CONTEXT_ADDED,
                f"Starting task: {description}",
                {"task_description": description},
                tags=["vibe", "task_start"]
            )
            session.track_decision(
                "task_execution",
                f"User requested: {description}",
                chosen=description
            )
        
        # Handle non-interactive mode
        if self.non_interactive:
            if not output_dir:
                output_dir = "vibe-solution"
            if RICH_AVAILABLE:
                console.print(f"\n[bold green]🎯 Got it![/bold green] Let me create: [cyan]{description}[/cyan]")
                console.print(f"[dim]Output directory: {output_dir}[/dim]\n")
            else:
                print(f"\n🎯 Got it! Let me create: {description}")
                print(f"Output directory: {output_dir}\n")
            self.run_with_progress(description, output_dir)
            return
        
        if RICH_AVAILABLE:
            console.print(f"\n[bold green]🎯 Got it![/bold green] Let me create: [cyan]{description}[/cyan]\n")
            
            # Ask for confirmation
            if not output_dir:
                output_dir = Prompt.ask("Output directory", default="vibe-solution")
            
            if Confirm.ask(f"Create solution in [cyan]{output_dir}[/cyan]?"):
                self.run_with_progress(description, output_dir)
            else:
                console.print("[yellow]Cancelled[/yellow]")
                if SESSION_TRACKING and session:
                    session.add_event(EventType.CONTEXT_ADDED, "Task cancelled by user")
        else:
            print(f"\n🎯 Got it! Let me create: {description}")
            if not output_dir:
                output_dir = input("Output directory (default: vibe-solution): ").strip() or "vibe-solution"
            
            confirm = input(f"Create solution in {output_dir}? (y/n): ").lower()
            if confirm == 'y':
                self.run_with_progress(description, output_dir)
            else:
                print("Cancelled")
                if SESSION_TRACKING and session:
                    session.add_event(EventType.CONTEXT_ADDED, "Task cancelled by user")
    
    def run_with_progress(self, description: str, output_dir: str):
        """Run the solution engine with progress display"""
        # Track solution creation
        if SESSION_TRACKING and session:
            session.add_event(
                EventType.AGENT_EXECUTED,
                f"Creating solution in {output_dir}",
                {"description": description, "output_dir": output_dir},
                tags=["vibe", "solution_creation"]
            )
        
        # Use the UltraDeep Agent Engine for better results
        try:
            from ultradeep_agent_engine import UltraDeepAgentEngine
            engine = UltraDeepAgentEngine()
            result = engine.create_complete_solution(description, output_dir)
        except ImportError:
            # Fallback to original engine
            from agent_based_solution_engine import AgentBasedSolutionEngine
            engine = AgentBasedSolutionEngine()
            result = engine.create_complete_solution(description, output_dir)
        
        if result.get("success"):
            self.show_success(output_dir)
            if SESSION_TRACKING and session:
                session.add_event(
                    EventType.CONTEXT_ADDED,
                    f"Solution created successfully in {output_dir}",
                    {"files_created": result.get("files_created", [])},
                    tags=["vibe", "success"]
                )
        else:
            if SESSION_TRACKING and session:
                session.add_event(
                    EventType.ERROR_OCCURRED,
                    f"Solution creation failed",
                    {"error": result.get("error", "Unknown error")},
                    tags=["vibe", "error"]
                )
    
    def show_success(self, output_dir: str):
        """Show success message with next steps"""
        if RICH_AVAILABLE:
            success_msg = f"""
# 🎉 Success!

Your solution has been created in: [bold cyan]{output_dir}[/bold cyan]

## Next Steps:
1. `cd {output_dir}`
2. Review the generated files
3. Follow the README.md instructions

[dim]Generated by vibe.ai - Making development delightful[/dim]
"""
            console.print(Panel(Markdown(success_msg), border_style="green"))
        else:
            print("\n🎉 Success!")
            print(f"Your solution has been created in: {output_dir}")
            print("\nNext Steps:")
            print(f"1. cd {output_dir}")
            print("2. Review the generated files")
            print("3. Follow the README.md instructions")
    
    def handle_command(self):
        """Handle command line arguments"""
        parser = argparse.ArgumentParser(
            description="vibe - AI-powered development made simple",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  vibe                          # Interactive mode
  vibe "build a chat app"       # Create solution directly
  vibe demo                     # Show interactive demo
  vibe gallery                  # Browse solution templates
  vibe explain <task>          # Explain how vibe would approach a task
            """
        )
        
        parser.add_argument("command", nargs="?", help="Command or task description")
        parser.add_argument("-o", "--output", default="vibe-solution", help="Output directory")
        parser.add_argument("--preview", action="store_true", help="Preview what would be created")
        parser.add_argument("--explain", action="store_true", help="Explain the approach")
        
        args = parser.parse_args()
        
        if not args.command:
            self.interactive_mode()
        elif args.command == "demo":
            self.show_demo()
        elif args.command == "gallery":
            self.show_gallery()
        elif args.command == "help":
            parser.print_help()
        else:
            # Treat as task description
            if args.preview:
                self.preview_solution(args.command)
            elif args.explain:
                self.explain_approach(args.command)
            else:
                self.execute_task(args.command, args.output)
    
    def show_demo(self):
        """Show interactive demo"""
        # Import and run the showcase engine
        from demo.showcase_engine import ShowcaseEngine
        engine = ShowcaseEngine()
        engine.run_interactive_demo()
    
    def show_gallery(self):
        """Show solution gallery"""
        # Import and run the gallery
        from gallery.solution_templates import SolutionGallery
        gallery = SolutionGallery()
        gallery.browse_gallery()
    
    def preview_solution(self, task: str):
        """Preview what would be created"""
        # Import and run the preview engine
        from preview.solution_previewer import SolutionPreviewer
        previewer = SolutionPreviewer()
        previewer.show_preview(task)
    
    def explain_approach(self, task: str):
        """Explain how vibe would approach the task"""
        # Import and run the explanation engine
        from explain.reasoning_engine import ExplanationEngine
        engine = ExplanationEngine()
        engine.explain_task(task)


def main():
    """Main entry point"""
    vibe = VibeInterface()
    vibe.run()


if __name__ == "__main__":
    main()