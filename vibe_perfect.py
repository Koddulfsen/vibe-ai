#!/usr/bin/env python3
"""
vibe Perfect - The Complete Idea to Solution System
Integrates all components for a seamless, bullshit-free development experience
"""

import os
import sys
import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

# Add vibe.ai to path
sys.path.insert(0, str(Path(__file__).parent))

# Import all our components
from idea_to_solution_engine import IdeaToSolutionEngine, IdeaRefinement
from mcp_control_agent import MCPControlAgent
from bullshit_filter import BullshitFilter
from enhanced_taskmaster_bridge import EnhancedTaskMasterBridge

# Rich UI
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.markdown import Markdown
    from rich.prompt import Prompt, Confirm
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from rich.table import Table
    from rich import box
    console = Console()
    RICH_AVAILABLE = True
except ImportError:
    console = None
    RICH_AVAILABLE = False


class VibePerfect:
    """The perfect vibe.ai system - no mocks, no hallucinations, only results"""
    
    def __init__(self):
        self.console = console
        self.mcp_control = MCPControlAgent()
        self.bullshit_filter = BullshitFilter()
        self.idea_engine = IdeaToSolutionEngine()
        self.taskmaster_bridge = None
        
        # Try to initialize TaskMaster bridge
        try:
            self.taskmaster_bridge = EnhancedTaskMasterBridge()
        except Exception as e:
            if self.console:
                self.console.print(f"[yellow]Warning: TaskMaster bridge not available: {e}[/yellow]")
        
        # Check system status
        self._check_system_status()
    
    def _check_system_status(self):
        """Check and display system status"""
        if not self.console:
            return
        
        status = {
            "mcp_available": len(self.mcp_control.available_mcps) > 0,
            "taskmaster_available": self.taskmaster_bridge is not None,
            "sequential_thinking": self.mcp_control.mcp_status.get("sequential-thinking", {}).get("available", False),
            "brave_search": self.mcp_control.mcp_status.get("brave-search", {}).get("available", False),
            "env_vars": {
                "ANTHROPIC_API_KEY": bool(os.getenv("ANTHROPIC_API_KEY")),
                "BRAVE_API_KEY": bool(os.getenv("BRAVE_API_KEY")),
                "PERPLEXITY_API_KEY": bool(os.getenv("PERPLEXITY_API_KEY"))
            }
        }
        
        # Display status
        self.console.print(Panel(
            self._format_status(status),
            title="🚀 vibe Perfect System Status",
            border_style="cyan"
        ))
        
        # Show MCP status table if available
        mcp_table = self.mcp_control.get_mcp_status_table()
        if mcp_table:
            self.console.print("\n")
            self.console.print(mcp_table)
        
        # Check for issues and suggest fixes
        if not all(status["env_vars"].values()) or not status["mcp_available"]:
            self.console.print("\n[yellow]⚠️ Some components need configuration[/yellow]")
            self.mcp_control.fix_mcp_issues()
    
    def _format_status(self, status: Dict[str, Any]) -> str:
        """Format status for display"""
        lines = []
        
        # Core components
        lines.append("[bold]Core Components:[/bold]")
        lines.append(f"  • MCP System: {'✅' if status['mcp_available'] else '❌'}")
        lines.append(f"  • TaskMaster: {'✅' if status['taskmaster_available'] else '❌'}")
        lines.append(f"  • Bullshit Filter: ✅")
        
        # MCP Tools
        lines.append("\n[bold]MCP Tools:[/bold]")
        lines.append(f"  • Sequential Thinking: {'✅' if status['sequential_thinking'] else '❌'}")
        lines.append(f"  • Brave Search: {'✅' if status['brave_search'] else '❌'}")
        
        # Environment
        lines.append("\n[bold]API Keys:[/bold]")
        for key, available in status["env_vars"].items():
            lines.append(f"  • {key}: {'✅' if available else '❌'}")
        
        return "\n".join(lines)
    
    def run_perfect_workflow(self, initial_idea: str):
        """Run the complete perfect workflow"""
        if self.console:
            self.console.print(Panel(
                f"[bold]💡 Starting Perfect Workflow[/bold]\n\n"
                f"Initial Idea: [cyan]{initial_idea}[/cyan]\n\n"
                f"I'll refine this idea using sequential thinking and verified research,\n"
                f"then create a complete solution with no bullshit!",
                title="🚀 vibe Perfect",
                border_style="cyan"
            ))
        
        # Step 1: Select relevant MCPs for the task
        self._select_mcps_for_idea(initial_idea)
        
        # Step 2: Run iterative refinement with thinking and search
        refined_idea, refinement_data = self._refine_idea_perfectly(initial_idea)
        
        # Step 3: Create PRD from refined idea
        prd_path = self._create_perfect_prd(refined_idea, refinement_data)
        
        # Step 4: Parse PRD and create tasks
        task_result = self._process_with_taskmaster(prd_path)
        
        # Step 5: Analyze complexity and create execution plan
        execution_plan = self._create_execution_plan(task_result)
        
        # Step 6: Show final summary
        self._show_final_summary(initial_idea, refined_idea, prd_path, execution_plan)
    
    def _select_mcps_for_idea(self, idea: str):
        """Select and activate relevant MCPs"""
        if self.console:
            self.console.print("\n[cyan]🎯 Selecting optimal MCP tools...[/cyan]")
        
        # Analyze task and select MCPs
        mcp_selection = self.mcp_control.select_mcps_for_task(idea, "planning")
        
        # Activate selected MCPs
        if mcp_selection["selected_mcps"]:
            self.mcp_control.activate_mcps(mcp_selection["selected_mcps"])
    
    def _refine_idea_perfectly(self, initial_idea: str) -> tuple:
        """Refine idea with perfect integration of thinking and search"""
        if self.console:
            self.console.print("\n[cyan]🧠 Refining idea with AI thinking...[/cyan]")
        
        current_idea = initial_idea
        all_refinements = []
        iteration = 1
        max_iterations = 3
        
        while iteration <= max_iterations:
            # Use sequential thinking
            refinement = self.idea_engine.refine_idea_with_thinking(current_idea, iteration)
            
            # Search for context (with bullshit filter)
            if self.mcp_control.mcp_status.get("brave-search", {}).get("available"):
                search_results = self.idea_engine.search_for_context(refinement)
                
                # Filter bullshit from search results
                if search_results:
                    filtered = self.bullshit_filter.filter_search_results(search_results)
                    refinement.search_results = filtered["filtered_results"]
            
            all_refinements.append(refinement)
            
            # Check if we're satisfied
            if self.console and iteration < max_iterations:
                self.idea_engine._show_refinement(refinement)
                
                try:
                    if Confirm.ask("\n[cyan]Refine further?[/cyan]"):
                        feedback = Prompt.ask("[cyan]What aspect needs improvement?[/cyan]")
                        current_idea = f"{refinement.refined_idea}. Focus on: {feedback}"
                        iteration += 1
                    else:
                        break
                except (EOFError, KeyboardInterrupt):
                    # Auto-complete on EOFError
                    break
            else:
                break
        
        final_refinement = all_refinements[-1]
        return final_refinement.refined_idea, {
            "refinements": all_refinements,
            "final_confidence": final_refinement.confidence,
            "iterations": len(all_refinements)
        }
    
    def _create_perfect_prd(self, refined_idea: str, refinement_data: Dict[str, Any]) -> str:
        """Create a perfect PRD with all insights"""
        if self.console:
            self.console.print("\n[cyan]📝 Creating comprehensive PRD...[/cyan]")
        
        # Use the idea engine to create PRD
        final_refinement = refinement_data["refinements"][-1]
        prd_path = self.idea_engine.create_prd_from_refinement(final_refinement)
        
        return prd_path
    
    def _process_with_taskmaster(self, prd_path: str) -> Dict[str, Any]:
        """Process PRD with TaskMaster"""
        if not self.taskmaster_bridge:
            if self.console:
                self.console.print("[yellow]TaskMaster not available - skipping task generation[/yellow]")
            return {"error": "TaskMaster not available"}
        
        if self.console:
            self.console.print("\n[cyan]🔧 Processing with TaskMaster...[/cyan]")
        
        # Read PRD content
        with open(prd_path) as f:
            prd_content = f.read()
        
        # Process with enhanced bridge
        result = self.taskmaster_bridge.process_task(
            prd_content,
            auto_execute=False
        )
        
        return result
    
    def _create_execution_plan(self, task_result: Dict[str, Any]) -> Dict[str, Any]:
        """Create detailed execution plan"""
        if self.console:
            self.console.print("\n[cyan]📋 Creating execution plan...[/cyan]")
        
        # Analyze complexity
        complexity_analysis = self.idea_engine.analyze_complexity(task_result)
        
        # Create agent strategy
        agent_strategy = self.idea_engine.create_agent_control_strategy(task_result)
        
        # Combine into execution plan
        execution_plan = {
            "complexity": complexity_analysis,
            "agent_strategy": agent_strategy,
            "phases": self._create_execution_phases(complexity_analysis, agent_strategy),
            "estimated_timeline": complexity_analysis.get("estimated_effort", "Unknown")
        }
        
        return execution_plan
    
    def _create_execution_phases(self, complexity: Dict[str, Any], strategy: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create execution phases"""
        phases = []
        
        for order in strategy.get("execution_order", []):
            phase = {
                "name": order["phase"],
                "agents": order["agents"],
                "tasks": [],
                "duration": "TBD"
            }
            
            # Add tasks based on complexity
            if order["phase"] == "planning":
                phase["tasks"] = ["Requirements analysis", "Architecture design", "Tech stack selection"]
            elif order["phase"] == "implementation":
                phase["tasks"] = complexity.get("subtasks_needed", ["Implement features"])
            elif order["phase"] == "testing":
                phase["tasks"] = ["Unit tests", "Integration tests", "Quality checks"]
            elif order["phase"] == "deployment":
                phase["tasks"] = ["Setup CI/CD", "Deploy to staging", "Production release"]
            
            phases.append(phase)
        
        return phases
    
    def _show_final_summary(self, initial_idea: str, refined_idea: str, 
                           prd_path: str, execution_plan: Dict[str, Any]):
        """Show final summary of the perfect workflow"""
        if not self.console:
            return
        
        summary = f"""
# 🎉 Perfect Solution Ready!

## Journey Summary

**Original Idea:**
{initial_idea}

**Refined Concept:**
{refined_idea}

**Deliverables Created:**
- PRD Document: {prd_path}
- Complexity Score: {execution_plan['complexity']['score']}/10
- Estimated Effort: {execution_plan['estimated_timeline']}

## Execution Plan

**Recommended Agents:**
{self._format_agent_list(execution_plan['agent_strategy']['primary_agents'])}

**Development Phases:**
{self._format_phases(execution_plan['phases'])}

## Next Steps

1. Review the PRD at: `{prd_path}`
2. Run TaskMaster to generate detailed tasks
3. Execute with vibe.ai agents
4. Monitor progress with visual tools

Ready to build something amazing! 🚀
"""
        
        self.console.print(Panel(
            Markdown(summary),
            title="✨ vibe Perfect Complete",
            border_style="green"
        ))
    
    def _format_agent_list(self, agents: List[str]) -> str:
        """Format agent list for display"""
        return "\n".join(f"- {agent}" for agent in agents)
    
    def _format_phases(self, phases: List[Dict[str, Any]]) -> str:
        """Format phases for display"""
        lines = []
        for i, phase in enumerate(phases, 1):
            lines.append(f"\n**Phase {i}: {phase['name'].title()}**")
            lines.append(f"Agents: {', '.join(phase['agents'])}")
            if phase['tasks']:
                lines.append("Tasks:")
                for task in phase['tasks']:
                    lines.append(f"  - {task}")
        return "\n".join(lines)


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="vibe Perfect - Transform ideas into perfect solutions"
    )
    parser.add_argument("idea", nargs="?", help="Your initial idea")
    parser.add_argument("--check-status", action="store_true", help="Check system status only")
    parser.add_argument("--fix-issues", action="store_true", help="Attempt to fix configuration issues")
    
    args = parser.parse_args()
    
    # Create perfect system
    vibe = VibePerfect()
    
    if args.check_status:
        # Just show status
        return
    
    if args.fix_issues:
        # Fix issues
        vibe.mcp_control.fix_mcp_issues()
        return
    
    # Get idea
    if args.idea:
        idea = args.idea
    else:
        if console:
            idea = Prompt.ask("[cyan]💡 What's your idea?[/cyan]")
        else:
            idea = input("What's your idea? ")
    
    # Run perfect workflow
    vibe.run_perfect_workflow(idea)


if __name__ == "__main__":
    main()