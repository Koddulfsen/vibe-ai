#!/usr/bin/env python3
"""
Interactive Demo and Showcase Engine for vibe.ai
Shows users the power of vibe.ai through interactive demonstrations
"""

import os
import sys
import time
import json
from typing import Dict, List, Any, Optional
from pathlib import Path
import subprocess
import tempfile

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.syntax import Syntax
    from rich.markdown import Markdown
    from rich.prompt import Prompt, Confirm
    from rich.table import Table
    from rich import print as rprint
    RICH_AVAILABLE = True
    console = Console()
except ImportError:
    RICH_AVAILABLE = False
    console = None


class ShowcaseDemo:
    """Represents a demo scenario"""
    def __init__(self, name: str, description: str, prompt: str, 
                 features: List[str], complexity: int = 5):
        self.name = name
        self.description = description
        self.prompt = prompt
        self.features = features
        self.complexity = complexity
        self.files_created = []
        self.technologies = []


class ShowcaseEngine:
    """Interactive demonstration engine for vibe.ai"""
    
    def __init__(self):
        self.demos = self._load_demos()
        self.vibe_dir = Path(__file__).parent.parent
        self.agent_engine = self.vibe_dir / "agent_based_solution_engine.py"
        
    def _load_demos(self) -> List[ShowcaseDemo]:
        """Load available demos"""
        demos = [
            ShowcaseDemo(
                name="REST API Demo",
                description="Build a production-ready REST API with authentication",
                prompt="Create a task management REST API with JWT authentication, PostgreSQL database, and comprehensive testing",
                features=[
                    "FastAPI framework",
                    "JWT authentication", 
                    "PostgreSQL integration",
                    "Automated testing",
                    "Docker configuration",
                    "API documentation"
                ],
                complexity=7
            ),
            ShowcaseDemo(
                name="React Dashboard",
                description="Create a modern React dashboard application",
                prompt="Build a React dashboard with charts, real-time updates, and responsive design using TypeScript and Material-UI",
                features=[
                    "React with TypeScript",
                    "Material-UI components",
                    "Real-time WebSocket updates",
                    "Interactive charts",
                    "Responsive design",
                    "State management"
                ],
                complexity=8
            ),
            ShowcaseDemo(
                name="Microservices Demo",
                description="Build a microservices architecture with multiple services",
                prompt="Create a microservices e-commerce system with user service, product service, and order service using Docker and Kubernetes",
                features=[
                    "Multiple microservices",
                    "Service mesh communication",
                    "Docker containers",
                    "Kubernetes deployment",
                    "API Gateway",
                    "Message queue integration"
                ],
                complexity=9
            ),
            ShowcaseDemo(
                name="CLI Tool Demo",
                description="Create a powerful command-line tool",
                prompt="Build a CLI tool for file organization with multiple commands, configuration support, and progress tracking",
                features=[
                    "Multi-command CLI",
                    "Configuration files",
                    "Progress bars",
                    "File system operations",
                    "Plugin system",
                    "Comprehensive help"
                ],
                complexity=6
            ),
            ShowcaseDemo(
                name="Machine Learning API",
                description="Build an ML-powered API service",
                prompt="Create a sentiment analysis API with model training, inference endpoints, and performance monitoring",
                features=[
                    "ML model integration",
                    "Training pipeline",
                    "Inference API",
                    "Model versioning",
                    "Performance metrics",
                    "Caching layer"
                ],
                complexity=8
            )
        ]
        return demos
    
    def run_interactive_demo(self):
        """Run the interactive demo experience"""
        # Check if we're in non-interactive mode
        if not sys.stdin.isatty():
            if RICH_AVAILABLE:
                console.print("[yellow]Demo mode requires interactive terminal.[/yellow]")
                console.print("\nAvailable demos:")
                for i, demo in enumerate(self.demos, 1):
                    console.print(f"  {i}. {demo.name}: {demo.description}")
            else:
                print("Demo mode requires interactive terminal.")
                print("\nAvailable demos:")
                for i, demo in enumerate(self.demos, 1):
                    print(f"  {i}. {demo.name}: {demo.description}")
            return
            
        if RICH_AVAILABLE:
            self._rich_demo()
        else:
            self._simple_demo()
    
    def _rich_demo(self):
        """Rich interactive demo with beautiful UI"""
        # Welcome screen
        welcome = """
# 🎭 vibe.ai Interactive Demo

Welcome to the vibe.ai showcase! Watch as our AI agents collaborate to build 
complete, production-ready solutions right before your eyes.

**What you'll see:**
- 🧠 Intelligent requirement analysis
- 🏗️ Automatic architecture planning
- ⚡ Real-time code generation
- ✅ Quality assurance and testing
- 📦 Complete project delivery

Let's explore what vibe.ai can build for you!
"""
        console.print(Panel(Markdown(welcome), border_style="cyan", title="Welcome"))
        
        # Show demo options
        self._show_demo_menu()
    
    def _show_demo_menu(self):
        """Show interactive demo menu"""
        console.print("\n[bold cyan]Available Demos:[/bold cyan]\n")
        
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("№", style="cyan", width=3)
        table.add_column("Demo", style="green", width=25)
        table.add_column("Description", width=50)
        table.add_column("Complexity", justify="center", width=10)
        
        for i, demo in enumerate(self.demos, 1):
            complexity_bar = "🟢" * (demo.complexity // 3) + "⚪" * (3 - demo.complexity // 3)
            table.add_row(
                str(i),
                demo.name,
                demo.description,
                complexity_bar
            )
        
        console.print(table)
        console.print()
        
        # Get user choice
        choice = Prompt.ask(
            "[cyan]Select a demo to watch[/cyan]",
            choices=[str(i) for i in range(1, len(self.demos) + 1)],
            default="1"
        )
        
        selected_demo = self.demos[int(choice) - 1]
        self._run_demo(selected_demo)
    
    def _run_demo(self, demo: ShowcaseDemo):
        """Run a specific demo"""
        console.clear()
        
        # Show demo details
        console.print(Panel(
            f"[bold]{demo.name}[/bold]\n\n{demo.description}",
            title="📋 Demo Details",
            border_style="green"
        ))
        
        console.print("\n[bold]This demo will create:[/bold]")
        for feature in demo.features:
            console.print(f"  ✓ {feature}")
        
        console.print(f"\n[dim]Prompt: {demo.prompt}[/dim]\n")
        
        if not Confirm.ask("Ready to see vibe.ai in action?"):
            return
        
        # Create temporary directory for demo
        with tempfile.TemporaryDirectory(prefix="vibe-demo-") as temp_dir:
            output_dir = Path(temp_dir) / "demo-output"
            
            # Show what's happening
            console.print("\n[bold cyan]🚀 Starting vibe.ai...[/bold cyan]\n")
            
            # Simulate the phases with explanations
            phases = [
                ("🧠 Understanding Requirements", self._explain_requirements, demo),
                ("📐 Planning Architecture", self._explain_architecture, demo),
                ("⚙️ Generating Code", self._explain_generation, demo),
                ("✅ Quality Assurance", self._explain_quality, demo)
            ]
            
            for phase_name, explain_func, demo_obj in phases:
                console.print(f"\n[bold yellow]{phase_name}[/bold yellow]")
                explain_func(demo_obj)
                time.sleep(1)  # Dramatic pause
            
            # Actually run the engine (optional, or simulate)
            console.print("\n[bold green]✨ Demo Complete![/bold green]\n")
            
            # Show generated structure
            self._show_generated_structure(demo)
            
            # Show sample code
            self._show_sample_code(demo)
            
            # Offer to create it for real
            console.print("\n[bold]Impressed?[/bold] This was just a simulation!")
            if Confirm.ask("Would you like vibe.ai to actually build this?"):
                self._build_for_real(demo)
    
    def _explain_requirements(self, demo: ShowcaseDemo):
        """Explain requirements analysis phase"""
        explanations = {
            "REST API Demo": [
                "• Detecting need for web framework → Choosing FastAPI",
                "• Authentication mentioned → Adding JWT implementation",
                "• Database required → Configuring PostgreSQL with migrations",
                "• Testing emphasized → Setting up pytest with coverage"
            ],
            "React Dashboard": [
                "• Frontend framework needed → React with TypeScript",
                "• UI components required → Integrating Material-UI",
                "• Real-time updates → Adding WebSocket support",
                "• Data visualization → Including chart libraries"
            ]
        }
        
        for line in explanations.get(demo.name, ["• Analyzing project requirements..."]):
            console.print(f"[dim]{line}[/dim]")
            time.sleep(0.3)
    
    def _explain_architecture(self, demo: ShowcaseDemo):
        """Explain architecture planning phase"""
        console.print("[dim]• Designing project structure[/dim]")
        time.sleep(0.3)
        console.print("[dim]• Planning component relationships[/dim]")
        time.sleep(0.3)
        console.print("[dim]• Optimizing for scalability[/dim]")
        time.sleep(0.3)
    
    def _explain_generation(self, demo: ShowcaseDemo):
        """Explain code generation phase"""
        console.print("[dim]• Creating project scaffold[/dim]")
        time.sleep(0.3)
        console.print("[dim]• Generating production-ready code[/dim]")
        time.sleep(0.3)
        console.print("[dim]• Adding configuration files[/dim]")
        time.sleep(0.3)
        console.print("[dim]• Setting up development environment[/dim]")
        time.sleep(0.3)
    
    def _explain_quality(self, demo: ShowcaseDemo):
        """Explain quality assurance phase"""
        console.print("[dim]• Reviewing generated code[/dim]")
        time.sleep(0.3)
        console.print("[dim]• Adding error handling[/dim]")
        time.sleep(0.3)
        console.print("[dim]• Ensuring best practices[/dim]")
        time.sleep(0.3)
    
    def _show_generated_structure(self, demo: ShowcaseDemo):
        """Show what would be generated"""
        structures = {
            "REST API Demo": """
📁 task-management-api/
├── 📁 src/
│   ├── 📄 main.py          # FastAPI application
│   ├── 📄 models.py        # Database models
│   ├── 📄 auth.py          # JWT authentication
│   ├── 📄 routes/          # API endpoints
│   └── 📄 database.py      # DB configuration
├── 📁 tests/
│   ├── 📄 test_api.py      # API tests
│   └── 📄 test_auth.py     # Auth tests
├── 📄 docker-compose.yml    # Docker setup
├── 📄 requirements.txt      # Dependencies
└── 📄 README.md            # Documentation
""",
            "React Dashboard": """
📁 react-dashboard/
├── 📁 src/
│   ├── 📁 components/      # React components
│   ├── 📁 hooks/           # Custom hooks
│   ├── 📁 services/        # API services
│   ├── 📄 App.tsx          # Main app
│   └── 📄 index.tsx        # Entry point
├── 📁 public/              # Static assets
├── 📄 package.json         # Dependencies
├── 📄 tsconfig.json        # TypeScript config
└── 📄 README.md           # Documentation
"""
        }
        
        structure = structures.get(demo.name, "📁 Generated project structure...")
        console.print(Panel(structure, title="Generated Structure", border_style="green"))
    
    def _show_sample_code(self, demo: ShowcaseDemo):
        """Show sample generated code"""
        code_samples = {
            "REST API Demo": '''
# src/main.py
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from . import models, auth, database

app = FastAPI(title="Task Management API")
security = HTTPBearer()

@app.post("/tasks", response_model=models.TaskResponse)
async def create_task(
    task: models.TaskCreate,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(database.get_db)
):
    """Create a new task with authentication"""
    new_task = models.Task(**task.dict(), user_id=current_user.id)
    db.add(new_task)
    db.commit()
    return new_task
''',
            "React Dashboard": '''
// src/components/Dashboard.tsx
import React, { useEffect, useState } from 'react';
import { Grid, Paper, Typography } from '@mui/material';
import { LineChart, Line, XAxis, YAxis, CartesianGrid } from 'recharts';
import { useWebSocket } from '../hooks/useWebSocket';

export const Dashboard: React.FC = () => {
  const [data, setData] = useState<ChartData[]>([]);
  const { messages } = useWebSocket('ws://localhost:8000/ws');
  
  useEffect(() => {
    // Update chart with real-time data
    if (messages.length > 0) {
      const latestData = messages[messages.length - 1];
      setData(prev => [...prev, latestData].slice(-20));
    }
  }, [messages]);
  
  return (
    <Grid container spacing={3}>
      <Grid item xs={12}>
        <Paper elevation={3} sx={{ p: 2 }}>
          <Typography variant="h5">Real-time Analytics</Typography>
          <LineChart width={600} height={300} data={data}>
            <Line type="monotone" dataKey="value" stroke="#8884d8" />
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="time" />
            <YAxis />
          </LineChart>
        </Paper>
      </Grid>
    </Grid>
  );
};
'''
        }
        
        code = code_samples.get(demo.name, "# Generated code...")
        syntax = Syntax(code, "python" if "API" in demo.name else "typescript", 
                       theme="monokai", line_numbers=True)
        console.print("\n[bold]Sample Generated Code:[/bold]")
        console.print(Panel(syntax, border_style="blue"))
    
    def _build_for_real(self, demo: ShowcaseDemo):
        """Actually build the demo project"""
        output_dir = f"vibe-demo-{demo.name.lower().replace(' ', '-')}"
        console.print(f"\n[bold green]Building {demo.name} in ./{output_dir}...[/bold green]\n")
        
        # Run the actual agent engine
        cmd = [
            sys.executable,
            str(self.agent_engine),
            demo.prompt,
            "-o", output_dir
        ]
        
        subprocess.run(cmd)
        console.print(f"\n[bold green]✅ Project created in {output_dir}![/bold green]")
    
    def _simple_demo(self):
        """Simple demo for when rich is not available"""
        print("\n🎭 vibe.ai Interactive Demo")
        print("=" * 50)
        print("\nAvailable Demos:")
        
        for i, demo in enumerate(self.demos, 1):
            print(f"{i}. {demo.name} - {demo.description}")
        
        choice = input("\nSelect a demo (1-5): ")
        
        try:
            selected = self.demos[int(choice) - 1]
            print(f"\n{selected.name}")
            print("-" * len(selected.name))
            print(f"Prompt: {selected.prompt}")
            print("\nThis would create:")
            for feature in selected.features:
                print(f"  • {feature}")
            
            confirm = input("\nBuild this project? (y/n): ")
            if confirm.lower() == 'y':
                self._build_for_real(selected)
        except (ValueError, IndexError):
            print("Invalid choice")


def main():
    """Main entry point for showcase"""
    engine = ShowcaseEngine()
    engine.run_interactive_demo()


if __name__ == "__main__":
    main()