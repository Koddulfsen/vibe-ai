#!/usr/bin/env python3
"""
MCP Control Agent
Intelligently manages which MCP tools are relevant for each task/prompt
Handles MCP connection issues and provides fallbacks
"""

import os
import json
import subprocess
from typing import Dict, List, Optional, Any, Set
from pathlib import Path
from datetime import datetime
import time

# Rich terminal UI
try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich import box
    console = Console()
    RICH_AVAILABLE = True
except ImportError:
    console = None
    RICH_AVAILABLE = False


class MCPConfig:
    """MCP server configuration"""
    def __init__(self, name: str, command: str, args: List[str], env: Dict[str, str]):
        self.name = name
        self.command = command
        self.args = args
        self.env = env
        self.available = False
        self.error = None
        self.tools = []


class MCPControlAgent:
    """Controls and manages MCP tool selection based on task requirements"""
    
    # MCP tool categories
    MCP_CATEGORIES = {
        "search": ["brave-search", "perplexity", "google-search"],
        "thinking": ["sequential-thinking", "reasoning", "analysis"],
        "task_management": ["taskmaster-ai", "task-tracker", "project-manager"],
        "code": ["git", "github", "code-analysis"],
        "database": ["postgres", "mysql", "mongodb"],
        "communication": ["slack", "email", "discord"],
        "file_system": ["file-manager", "directory-browser"],
        "web": ["web-browser", "web-scraper", "http-client"],
        "ai_models": ["openai", "anthropic", "gemini"]
    }
    
    # Task type to MCP mapping
    TASK_MCP_MAPPING = {
        "research": ["search", "thinking", "web"],
        "planning": ["thinking", "task_management", "search"],
        "development": ["code", "file_system", "database"],
        "testing": ["code", "web", "thinking"],
        "deployment": ["code", "web", "file_system"],
        "communication": ["communication", "task_management"],
        "analysis": ["thinking", "search", "ai_models"],
        "documentation": ["file_system", "thinking", "search"]
    }
    
    def __init__(self):
        self.console = console
        self.mcp_config_path = Path.home() / ".cursor" / "mcp.json"
        self.available_mcps = {}
        self.active_mcps = set()
        self.mcp_status = {}
        
        # Load and check MCP configurations
        self._load_mcp_config()
        self._check_mcp_availability()
    
    def _load_mcp_config(self):
        """Load MCP configuration from file"""
        if not self.mcp_config_path.exists():
            if self.console:
                self.console.print("[yellow]No MCP configuration found[/yellow]")
            return
        
        try:
            with open(self.mcp_config_path) as f:
                config = json.load(f)
            
            for name, server_config in config.get("mcpServers", {}).items():
                mcp = MCPConfig(
                    name=name,
                    command=server_config.get("command", ""),
                    args=server_config.get("args", []),
                    env=server_config.get("env", {})
                )
                self.available_mcps[name] = mcp
                
        except Exception as e:
            if self.console:
                self.console.print(f"[red]Error loading MCP config: {e}[/red]")
    
    def _check_mcp_availability(self):
        """Check which MCPs are actually available and working"""
        for name, mcp in self.available_mcps.items():
            # Check if required environment variables are set
            missing_env = []
            for env_var, env_value in mcp.env.items():
                if env_value and "API_KEY" in env_var and not os.getenv(env_var):
                    missing_env.append(env_var)
            
            if missing_env:
                mcp.available = False
                mcp.error = f"Missing environment variables: {', '.join(missing_env)}"
            else:
                # Try to verify the MCP is accessible
                mcp.available = self._verify_mcp_connection(mcp)
            
            self.mcp_status[name] = {
                "available": mcp.available,
                "error": mcp.error,
                "category": self._categorize_mcp(name)
            }
    
    def _verify_mcp_connection(self, mcp: MCPConfig) -> bool:
        """Verify MCP server can be started"""
        # For now, we'll do a basic check
        # In production, this would actually test the connection
        if mcp.name == "taskmaster-ai":
            # Check if taskmaster is installed
            try:
                result = subprocess.run(
                    ["npm", "list", "-g", "taskmaster-ai"],
                    capture_output=True,
                    text=True
                )
                return result.returncode == 0
            except:
                return False
        elif mcp.name == "brave-search":
            return bool(os.getenv("BRAVE_API_KEY"))
        elif mcp.name == "sequential-thinking":
            # This is typically built-in
            return True
        else:
            # Default to available if no specific check
            return True
    
    def _categorize_mcp(self, mcp_name: str) -> str:
        """Categorize an MCP based on its name"""
        mcp_lower = mcp_name.lower()
        
        for category, keywords in self.MCP_CATEGORIES.items():
            if any(keyword in mcp_lower for keyword in keywords):
                return category
        
        return "general"
    
    def select_mcps_for_task(self, task_description: str, task_type: Optional[str] = None) -> Dict[str, Any]:
        """Select relevant MCPs for a given task"""
        if self.console:
            self.console.print(f"\n[cyan]🎯 Selecting MCPs for task...[/cyan]")
        
        # Determine task type if not provided
        if not task_type:
            task_type = self._infer_task_type(task_description)
        
        # Get recommended MCP categories
        recommended_categories = self.TASK_MCP_MAPPING.get(task_type, ["general"])
        
        # Select available MCPs from recommended categories
        selected_mcps = {}
        unavailable_mcps = {}
        
        for name, status in self.mcp_status.items():
            if status["category"] in recommended_categories:
                if status["available"]:
                    selected_mcps[name] = {
                        "category": status["category"],
                        "config": self.available_mcps[name]
                    }
                else:
                    unavailable_mcps[name] = status["error"]
        
        # Create selection report
        report = {
            "task_description": task_description,
            "task_type": task_type,
            "recommended_categories": recommended_categories,
            "selected_mcps": list(selected_mcps.keys()),
            "unavailable_mcps": unavailable_mcps,
            "fallback_options": self._get_fallback_options(unavailable_mcps)
        }
        
        if self.console:
            self._display_selection_report(report)
        
        return report
    
    def _infer_task_type(self, task_description: str) -> str:
        """Infer task type from description"""
        task_lower = task_description.lower()
        
        # Check for keywords
        if any(word in task_lower for word in ["research", "find", "search", "discover"]):
            return "research"
        elif any(word in task_lower for word in ["plan", "design", "architect", "strategy"]):
            return "planning"
        elif any(word in task_lower for word in ["build", "implement", "code", "develop"]):
            return "development"
        elif any(word in task_lower for word in ["test", "verify", "validate", "check"]):
            return "testing"
        elif any(word in task_lower for word in ["deploy", "release", "publish", "launch"]):
            return "deployment"
        elif any(word in task_lower for word in ["analyze", "evaluate", "assess", "review"]):
            return "analysis"
        elif any(word in task_lower for word in ["document", "write", "describe", "explain"]):
            return "documentation"
        else:
            return "general"
    
    def _get_fallback_options(self, unavailable_mcps: Dict[str, str]) -> Dict[str, str]:
        """Get fallback options for unavailable MCPs"""
        fallbacks = {}
        
        for mcp_name, error in unavailable_mcps.items():
            if "brave-search" in mcp_name:
                fallbacks[mcp_name] = "Use Perplexity API or web scraping as fallback"
            elif "taskmaster" in mcp_name:
                fallbacks[mcp_name] = "Use CLI commands or manual task creation"
            elif "sequential-thinking" in mcp_name:
                fallbacks[mcp_name] = "Use structured prompting as fallback"
            else:
                fallbacks[mcp_name] = "Use alternative tools or manual process"
        
        return fallbacks
    
    def _display_selection_report(self, report: Dict[str, Any]):
        """Display MCP selection report"""
        if not self.console:
            return
        
        # Task info
        self.console.print(Panel(
            f"[bold]Task:[/bold] {report['task_description']}\n"
            f"[bold]Type:[/bold] {report['task_type']}\n"
            f"[bold]Categories:[/bold] {', '.join(report['recommended_categories'])}",
            title="📋 Task Analysis",
            border_style="blue"
        ))
        
        # Selected MCPs
        if report["selected_mcps"]:
            self.console.print("\n[green]✅ Available MCPs:[/green]")
            for mcp in report["selected_mcps"]:
                self.console.print(f"  • {mcp}")
        
        # Unavailable MCPs
        if report["unavailable_mcps"]:
            self.console.print("\n[yellow]⚠️ Unavailable MCPs:[/yellow]")
            for mcp, error in report["unavailable_mcps"].items():
                self.console.print(f"  • {mcp}: {error}")
        
        # Fallbacks
        if report["fallback_options"]:
            self.console.print("\n[cyan]🔄 Fallback Options:[/cyan]")
            for mcp, fallback in report["fallback_options"].items():
                self.console.print(f"  • {mcp} → {fallback}")
    
    def activate_mcps(self, mcp_names: List[str]) -> Dict[str, bool]:
        """Activate selected MCPs"""
        activation_status = {}
        
        for name in mcp_names:
            if name in self.available_mcps and self.mcp_status[name]["available"]:
                # In production, this would actually start the MCP server
                self.active_mcps.add(name)
                activation_status[name] = True
                
                if self.console:
                    self.console.print(f"[green]✓[/green] Activated: {name}")
            else:
                activation_status[name] = False
                if self.console:
                    self.console.print(f"[red]✗[/red] Failed to activate: {name}")
        
        return activation_status
    
    def deactivate_mcps(self, mcp_names: Optional[List[str]] = None):
        """Deactivate MCPs"""
        if mcp_names is None:
            mcp_names = list(self.active_mcps)
        
        for name in mcp_names:
            if name in self.active_mcps:
                self.active_mcps.remove(name)
                if self.console:
                    self.console.print(f"[yellow]○[/yellow] Deactivated: {name}")
    
    def get_mcp_status_table(self) -> Optional[Table]:
        """Get a table showing MCP status"""
        if not RICH_AVAILABLE:
            return None
        
        table = Table(title="MCP Status", box=box.ROUNDED)
        table.add_column("MCP", style="cyan")
        table.add_column("Category", style="magenta")
        table.add_column("Status", justify="center")
        table.add_column("Error/Notes", style="dim")
        
        for name, status in self.mcp_status.items():
            status_icon = "✅" if status["available"] else "❌"
            error_msg = status.get("error", "Available") if not status["available"] else "Ready"
            
            table.add_row(
                name,
                status["category"],
                status_icon,
                error_msg
            )
        
        return table
    
    def suggest_mcp_configuration(self, task_types: List[str]) -> Dict[str, Any]:
        """Suggest MCP configuration for common task types"""
        suggestions = {
            "required_mcps": set(),
            "recommended_mcps": set(),
            "setup_commands": [],
            "environment_variables": set()
        }
        
        # Collect all needed categories
        needed_categories = set()
        for task_type in task_types:
            categories = self.TASK_MCP_MAPPING.get(task_type, [])
            needed_categories.update(categories)
        
        # Map categories to specific MCPs
        for category in needed_categories:
            if category == "search":
                suggestions["required_mcps"].add("brave-search")
                suggestions["environment_variables"].add("BRAVE_API_KEY")
            elif category == "thinking":
                suggestions["required_mcps"].add("sequential-thinking")
            elif category == "task_management":
                suggestions["required_mcps"].add("taskmaster-ai")
                suggestions["setup_commands"].append("npm install -g taskmaster-ai")
                suggestions["environment_variables"].update([
                    "ANTHROPIC_API_KEY",
                    "PERPLEXITY_API_KEY"
                ])
            elif category == "code":
                suggestions["recommended_mcps"].add("git")
        
        return suggestions
    
    def fix_mcp_issues(self) -> Dict[str, Any]:
        """Attempt to fix common MCP issues"""
        fixes_applied = {
            "config_updates": [],
            "env_vars_needed": [],
            "commands_to_run": [],
            "manual_steps": []
        }
        
        # Check for missing config file
        if not self.mcp_config_path.exists():
            self.mcp_config_path.parent.mkdir(parents=True, exist_ok=True)
            default_config = {
                "mcpServers": {
                    "sequential-thinking": {
                        "command": "node",
                        "args": ["sequential-thinking-server"],
                        "env": {}
                    }
                }
            }
            with open(self.mcp_config_path, 'w') as f:
                json.dump(default_config, f, indent=2)
            fixes_applied["config_updates"].append("Created default MCP config")
        
        # Check for common missing environment variables
        for var in ["ANTHROPIC_API_KEY", "BRAVE_API_KEY", "PERPLEXITY_API_KEY"]:
            if not os.getenv(var):
                fixes_applied["env_vars_needed"].append(var)
        
        # Suggest TaskMaster installation if not found
        if "taskmaster-ai" in self.mcp_status and not self.mcp_status["taskmaster-ai"]["available"]:
            fixes_applied["commands_to_run"].append("npm install -g taskmaster-ai")
        
        # Display fixes
        if self.console and any(fixes_applied.values()):
            self._display_fixes(fixes_applied)
        
        return fixes_applied
    
    def _display_fixes(self, fixes: Dict[str, Any]):
        """Display suggested fixes"""
        self.console.print(Panel(
            "[bold]🔧 MCP Configuration Fixes[/bold]",
            border_style="yellow"
        ))
        
        if fixes["config_updates"]:
            self.console.print("\n[green]✅ Applied:[/green]")
            for update in fixes["config_updates"]:
                self.console.print(f"  • {update}")
        
        if fixes["env_vars_needed"]:
            self.console.print("\n[yellow]⚠️ Environment Variables Needed:[/yellow]")
            for var in fixes["env_vars_needed"]:
                self.console.print(f"  export {var}='your-api-key-here'")
        
        if fixes["commands_to_run"]:
            self.console.print("\n[cyan]💻 Commands to Run:[/cyan]")
            for cmd in fixes["commands_to_run"]:
                self.console.print(f"  $ {cmd}")


def main():
    """Main entry point for testing"""
    control = MCPControlAgent()
    
    if console:
        # Show MCP status
        console.print("\n🔌 MCP Control Agent\n")
        
        status_table = control.get_mcp_status_table()
        if status_table:
            console.print(status_table)
        
        # Test task selection
        test_tasks = [
            "Research best practices for REST API design",
            "Build a user authentication system",
            "Deploy application to production"
        ]
        
        console.print("\n[bold]Testing MCP Selection:[/bold]\n")
        
        for task in test_tasks:
            report = control.select_mcps_for_task(task)
            console.print("\n" + "─" * 50 + "\n")
        
        # Show fix suggestions
        console.print("\n[bold]Checking for Issues:[/bold]\n")
        control.fix_mcp_issues()
        
        # Show configuration suggestions
        console.print("\n[bold]Configuration Suggestions:[/bold]\n")
        suggestions = control.suggest_mcp_configuration(["research", "development", "planning"])
        
        console.print("Required MCPs:")
        for mcp in suggestions["required_mcps"]:
            console.print(f"  • {mcp}")
        
        console.print("\nEnvironment Variables:")
        for var in suggestions["environment_variables"]:
            console.print(f"  • {var}")


if __name__ == "__main__":
    main()