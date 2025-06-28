#!/usr/bin/env python3
"""
Progress Visualizer for vibe.ai
Creates beautiful, real-time progress displays for agent activities
"""

import time
import sys
from typing import Dict, List, Any, Optional
from datetime import datetime
from threading import Thread, Event
import queue

try:
    from rich.console import Console
    from rich.layout import Layout
    from rich.panel import Panel
    from rich.progress import Progress, BarColumn, TextColumn, TimeRemainingColumn, SpinnerColumn
    from rich.table import Table
    from rich.live import Live
    from rich.text import Text
    from rich.columns import Columns
    from rich import box
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False


class AgentActivity:
    """Represents an agent's current activity"""
    def __init__(self, agent_name: str, status: str = "idle", task: str = ""):
        self.agent_name = agent_name
        self.status = status  # idle, thinking, executing, completed, error
        self.task = task
        self.start_time = datetime.now()
        self.progress = 0
        self.sub_tasks = []
        self.output_preview = ""


class ProgressVisualizer:
    """Creates beautiful progress displays for vibe.ai operations"""
    
    def __init__(self):
        self.console = Console() if RICH_AVAILABLE else None
        self.agents = {}
        self.overall_progress = 0
        self.current_phase = "Initializing"
        self.message_queue = queue.Queue()
        self.stop_event = Event()
        
    def create_layout(self) -> Layout:
        """Create the main layout for progress display"""
        layout = Layout()
        
        layout.split(
            Layout(name="header", size=3),
            Layout(name="main"),
            Layout(name="footer", size=3)
        )
        
        layout["main"].split_row(
            Layout(name="agents", ratio=2),
            Layout(name="activity", ratio=3)
        )
        
        return layout
    
    def create_header(self) -> Panel:
        """Create header panel"""
        header_text = Text()
        header_text.append("🚀 vibe.ai ", style="bold cyan")
        header_text.append(f"| Phase: {self.current_phase} ", style="yellow")
        header_text.append(f"| Progress: {self.overall_progress}%", style="green")
        
        return Panel(header_text, box=box.ROUNDED)
    
    def create_agents_panel(self) -> Panel:
        """Create panel showing agent statuses"""
        table = Table(show_header=True, header_style="bold cyan", box=box.SIMPLE)
        table.add_column("Agent", style="cyan", width=20)
        table.add_column("Status", width=10)
        table.add_column("Task", width=30)
        
        status_colors = {
            "idle": "dim white",
            "thinking": "yellow",
            "executing": "green",
            "completed": "bold green",
            "error": "red"
        }
        
        for agent_name, activity in self.agents.items():
            status_style = status_colors.get(activity.status, "white")
            
            # Add status emoji
            status_emoji = {
                "idle": "⏸️",
                "thinking": "🤔",
                "executing": "⚙️",
                "completed": "✅",
                "error": "❌"
            }.get(activity.status, "")
            
            table.add_row(
                agent_name,
                Text(f"{status_emoji} {activity.status}", style=status_style),
                Text(activity.task, overflow="ellipsis")
            )
        
        return Panel(table, title="Active Agents", border_style="cyan")
    
    def create_activity_panel(self) -> Panel:
        """Create panel showing current activity details"""
        content_lines = []
        
        # Show recent activities
        recent_activities = list(self.agents.values())[-5:]
        for activity in recent_activities:
            if activity.status == "executing" and activity.sub_tasks:
                content_lines.append(f"\n[bold cyan]{activity.agent_name}:[/bold cyan]")
                for subtask in activity.sub_tasks[-3:]:  # Show last 3 subtasks
                    content_lines.append(f"  [dim]• {subtask}[/dim]")
                
                if activity.output_preview:
                    content_lines.append(f"\n  [dim italic]Preview: {activity.output_preview[:100]}...[/dim italic]")
        
        if not content_lines:
            content_lines.append("[dim]Waiting for agent activity...[/dim]")
        
        content_text = "\n".join(content_lines)
        
        return Panel(
            content_text,
            title="Current Activity",
            border_style="green"
        )
    
    def create_footer(self) -> Panel:
        """Create footer panel"""
        tips = [
            "💡 Tip: Use 'vibe explain' to understand the solution approach",
            "💡 Tip: Try 'vibe preview' to see what will be created",
            "💡 Tip: Use 'vibe gallery' to browse pre-built solutions",
            "💡 Tip: Press Ctrl+C to cancel at any time"
        ]
        
        # Rotate through tips
        tip_index = int(time.time() / 5) % len(tips)
        
        return Panel(
            Text(tips[tip_index], style="dim italic"),
            box=box.ROUNDED,
            border_style="dim"
        )
    
    def update_display(self, layout: Layout):
        """Update the display with current state"""
        layout["header"].update(self.create_header())
        layout["agents"].update(self.create_agents_panel())
        layout["activity"].update(self.create_activity_panel())
        layout["footer"].update(self.create_footer())
    
    def add_agent(self, agent_name: str):
        """Add an agent to track"""
        self.agents[agent_name] = AgentActivity(agent_name)
    
    def update_agent(self, agent_name: str, status: str, task: str = "", 
                    progress: int = 0, output_preview: str = ""):
        """Update agent status"""
        if agent_name not in self.agents:
            self.add_agent(agent_name)
        
        agent = self.agents[agent_name]
        agent.status = status
        agent.task = task
        agent.progress = progress
        if output_preview:
            agent.output_preview = output_preview
    
    def add_subtask(self, agent_name: str, subtask: str):
        """Add a subtask to an agent"""
        if agent_name in self.agents:
            self.agents[agent_name].sub_tasks.append(subtask)
    
    def set_phase(self, phase: str):
        """Set the current phase"""
        self.current_phase = phase
    
    def set_progress(self, progress: int):
        """Set overall progress"""
        self.overall_progress = min(100, max(0, progress))
    
    def start_live_display(self):
        """Start the live progress display"""
        if not RICH_AVAILABLE:
            return
        
        layout = self.create_layout()
        
        with Live(layout, console=self.console, refresh_per_second=4) as live:
            while not self.stop_event.is_set():
                self.update_display(layout)
                time.sleep(0.25)
    
    def stop(self):
        """Stop the live display"""
        self.stop_event.set()


class SimpleProgressBar:
    """Fallback progress bar for when rich is not available"""
    
    def __init__(self, total: int = 100):
        self.total = total
        self.current = 0
        self.width = 50
    
    def update(self, current: int, message: str = ""):
        """Update progress bar"""
        self.current = min(current, self.total)
        filled = int(self.width * self.current / self.total)
        bar = "█" * filled + "░" * (self.width - filled)
        percent = int(100 * self.current / self.total)
        
        sys.stdout.write(f"\r[{bar}] {percent}% {message}")
        sys.stdout.flush()
    
    def finish(self, message: str = "Complete!"):
        """Finish the progress bar"""
        self.update(self.total, message)
        print()  # New line


def demo_progress():
    """Demo the progress visualizer"""
    if RICH_AVAILABLE:
        visualizer = ProgressVisualizer()
        
        # Start live display in background
        display_thread = Thread(target=visualizer.start_live_display)
        display_thread.start()
        
        try:
            # Simulate agent activities
            phases = [
                ("Analyzing Requirements", [
                    ("planning-agent", "thinking", "Understanding user intent"),
                    ("complexity-agent", "thinking", "Assessing project complexity"),
                ]),
                ("Planning Architecture", [
                    ("architect-agent", "executing", "Designing system architecture"),
                    ("tech-stack-agent", "executing", "Selecting technologies"),
                ]),
                ("Generating Solution", [
                    ("code-generator", "executing", "Creating project structure"),
                    ("api-agent", "executing", "Building REST endpoints"),
                    ("database-agent", "executing", "Setting up data models"),
                ]),
                ("Quality Assurance", [
                    ("test-agent", "executing", "Writing unit tests"),
                    ("quality-agent", "executing", "Reviewing code quality"),
                ])
            ]
            
            total_steps = sum(len(agents) for _, agents in phases)
            completed = 0
            
            for phase_name, agents in phases:
                visualizer.set_phase(phase_name)
                
                for agent_name, status, task in agents:
                    visualizer.update_agent(agent_name, status, task)
                    
                    # Simulate work
                    for i in range(3):
                        time.sleep(0.5)
                        visualizer.add_subtask(agent_name, f"Step {i+1} of {task}")
                    
                    visualizer.update_agent(agent_name, "completed", task)
                    completed += 1
                    visualizer.set_progress(int(100 * completed / total_steps))
                
                time.sleep(1)
            
            visualizer.set_phase("Complete!")
            visualizer.set_progress(100)
            time.sleep(2)
            
        finally:
            visualizer.stop()
            display_thread.join()
            print("\n✅ Demo complete!")
    
    else:
        # Fallback demo
        print("🚀 vibe.ai Progress Demo (install 'rich' for better display)")
        bar = SimpleProgressBar(100)
        
        for i in range(101):
            bar.update(i, f"Processing... ({i}%)")
            time.sleep(0.02)
        
        bar.finish("✅ Complete!")


if __name__ == "__main__":
    demo_progress()