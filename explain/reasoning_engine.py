#!/usr/bin/env python3
"""
Explanation Engine for vibe.ai
Shows users how vibe.ai thinks and makes decisions
"""

import os
import sys
import json
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass
from pathlib import Path

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.tree import Tree
    from rich.markdown import Markdown
    from rich.table import Table
    from rich.syntax import Syntax
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from rich import box
    RICH_AVAILABLE = True
    console = Console()
except ImportError:
    RICH_AVAILABLE = False
    console = None


@dataclass
class ReasoningStep:
    """Represents a step in the reasoning process"""
    phase: str
    agent: str
    thought: str
    decision: str
    rationale: str
    confidence: float
    alternatives: List[str] = None


class ExplanationEngine:
    """Explains how vibe.ai approaches and solves problems"""
    
    def __init__(self):
        self.reasoning_steps = []
        self.task_analysis = {}
        self.decision_tree = {}
        
    def explain_task(self, task_description: str):
        """Main method to explain how vibe.ai would approach a task"""
        if RICH_AVAILABLE:
            self._rich_explain(task_description)
        else:
            self._simple_explain(task_description)
    
    def _rich_explain(self, task_description: str):
        """Rich explanation with beautiful visualizations"""
        console.clear()
        
        # Header
        header = f"""
# 🧠 vibe.ai Reasoning Engine

Let me explain how I would approach your task:
[cyan]{task_description}[/cyan]

I'll show you my thought process, decision-making, and the agents that would work together.
"""
        console.print(Panel(Markdown(header), border_style="cyan"))
        
        # Analyze the task
        with console.status("Analyzing your request...", spinner="dots"):
            self._analyze_task(task_description)
        
        # Show analysis results
        self._show_task_analysis()
        
        # Show reasoning process
        self._show_reasoning_process()
        
        # Show decision tree
        self._show_decision_tree()
        
        # Show agent collaboration
        self._show_agent_collaboration()
        
        # Show expected outcome
        self._show_expected_outcome()
    
    def _analyze_task(self, task_description: str):
        """Analyze the task and generate reasoning steps"""
        # Simulate task analysis
        task_lower = task_description.lower()
        
        # Detect task type and complexity
        self.task_analysis = {
            "description": task_description,
            "detected_type": self._detect_task_type(task_lower),
            "complexity_score": self._calculate_complexity(task_lower),
            "key_requirements": self._extract_requirements(task_lower),
            "suggested_tech": self._suggest_technologies(task_lower),
            "estimated_agents": self._estimate_agents(task_lower)
        }
        
        # Generate reasoning steps
        self.reasoning_steps = self._generate_reasoning_steps(self.task_analysis)
        
        # Build decision tree
        self.decision_tree = self._build_decision_tree(self.task_analysis)
    
    def _detect_task_type(self, task_lower: str) -> str:
        """Detect the type of task"""
        if any(word in task_lower for word in ["api", "rest", "endpoint", "backend"]):
            return "Backend API Development"
        elif any(word in task_lower for word in ["react", "vue", "frontend", "ui", "dashboard"]):
            return "Frontend Application"
        elif any(word in task_lower for word in ["full stack", "complete app", "saas"]):
            return "Full Stack Application"
        elif any(word in task_lower for word in ["cli", "command", "terminal"]):
            return "CLI Tool"
        elif any(word in task_lower for word in ["ml", "machine learning", "ai", "model"]):
            return "Machine Learning Application"
        else:
            return "General Application"
    
    def _calculate_complexity(self, task_lower: str) -> int:
        """Calculate task complexity score"""
        score = 5  # Base score
        
        # Complexity indicators
        complex_indicators = [
            ("auth", 2), ("database", 2), ("real-time", 3), ("microservice", 4),
            ("kubernetes", 4), ("machine learning", 3), ("payment", 3),
            ("multi-tenant", 4), ("scalable", 2), ("production", 2)
        ]
        
        for indicator, points in complex_indicators:
            if indicator in task_lower:
                score += points
        
        return min(score, 10)  # Cap at 10
    
    def _extract_requirements(self, task_lower: str) -> List[str]:
        """Extract key requirements from task description"""
        requirements = []
        
        requirement_patterns = {
            "authentication": ["auth", "login", "jwt", "oauth"],
            "database": ["database", "postgresql", "mysql", "mongodb"],
            "real-time": ["real-time", "realtime", "websocket", "live"],
            "testing": ["test", "testing", "coverage", "tdd"],
            "docker": ["docker", "container", "kubernetes"],
            "api": ["api", "rest", "graphql", "endpoint"],
            "frontend": ["react", "vue", "angular", "frontend"],
            "payments": ["payment", "stripe", "billing", "subscription"]
        }
        
        for req_name, patterns in requirement_patterns.items():
            if any(pattern in task_lower for pattern in patterns):
                requirements.append(req_name)
        
        return requirements
    
    def _suggest_technologies(self, task_lower: str) -> List[str]:
        """Suggest technologies based on task"""
        tech_stack = []
        
        # Backend suggestions
        if "python" in task_lower or "api" in task_lower:
            tech_stack.append("FastAPI")
        if "node" in task_lower or "javascript" in task_lower:
            tech_stack.append("Express.js")
        
        # Frontend suggestions
        if "react" in task_lower:
            tech_stack.append("React")
        elif "vue" in task_lower:
            tech_stack.append("Vue.js")
        elif "dashboard" in task_lower or "ui" in task_lower:
            tech_stack.append("React")  # Default
        
        # Database suggestions
        if "database" in task_lower:
            if "nosql" in task_lower or "mongodb" in task_lower:
                tech_stack.append("MongoDB")
            else:
                tech_stack.append("PostgreSQL")  # Default
        
        # Additional tech
        if "real-time" in task_lower:
            tech_stack.append("WebSockets")
        if "docker" in task_lower:
            tech_stack.append("Docker")
        if "test" in task_lower:
            tech_stack.append("pytest" if "python" in task_lower else "Jest")
        
        return tech_stack
    
    def _estimate_agents(self, task_lower: str) -> List[str]:
        """Estimate which agents would be involved"""
        agents = ["planning-analysis-agent", "task-complexity-agent"]  # Always involved
        
        if "api" in task_lower or "backend" in task_lower:
            agents.append("api-development-agent")
        if "frontend" in task_lower or "ui" in task_lower:
            agents.append("frontend-development-agent")
        if "database" in task_lower:
            agents.append("database-design-agent")
        if "test" in task_lower:
            agents.append("testing-agent")
        if "docker" in task_lower or "deploy" in task_lower:
            agents.append("devops-agent")
        
        agents.append("quality-assessment-agent")  # Always at the end
        
        return agents
    
    def _generate_reasoning_steps(self, analysis: Dict) -> List[ReasoningStep]:
        """Generate detailed reasoning steps"""
        steps = []
        
        # Phase 1: Understanding
        steps.append(ReasoningStep(
            phase="Understanding Requirements",
            agent="planning-analysis-agent",
            thought="I need to understand what the user wants to build",
            decision=f"This is a {analysis['detected_type']} project",
            rationale=f"Based on keywords and context, this appears to be focused on {analysis['detected_type'].lower()}",
            confidence=0.9,
            alternatives=["Could also be interpreted as a microservice", "Might need clarification on scope"]
        ))
        
        # Phase 2: Complexity Assessment
        steps.append(ReasoningStep(
            phase="Assessing Complexity",
            agent="task-complexity-agent",
            thought="How complex is this project?",
            decision=f"Complexity score: {analysis['complexity_score']}/10",
            rationale=f"Found {len(analysis['key_requirements'])} key requirements that increase complexity",
            confidence=0.85,
            alternatives=["Could be simpler with different architecture", "Might be more complex if scale is considered"]
        ))
        
        # Phase 3: Technology Selection
        if analysis['suggested_tech']:
            steps.append(ReasoningStep(
                phase="Technology Selection",
                agent="tech-stack-agent",
                thought="What technologies should we use?",
                decision=f"Recommended stack: {', '.join(analysis['suggested_tech'])}",
                rationale="These technologies best match the requirements and provide good developer experience",
                confidence=0.8,
                alternatives=["Alternative: Use Next.js for full-stack", "Could use Go for better performance"]
            ))
        
        # Phase 4: Architecture Planning
        steps.append(ReasoningStep(
            phase="Architecture Planning",
            agent="architect-agent",
            thought="How should we structure this application?",
            decision="Monolithic architecture with modular design",
            rationale="Given the complexity and requirements, a well-structured monolith is optimal",
            confidence=0.75,
            alternatives=["Microservices if expecting high scale", "Serverless for cost optimization"]
        ))
        
        # Phase 5: Implementation Strategy
        steps.append(ReasoningStep(
            phase="Implementation Strategy",
            agent="execution-planning-agent",
            thought="What's the best order to build this?",
            decision="Start with core API, then auth, then frontend",
            rationale="This allows for incremental testing and validation",
            confidence=0.9,
            alternatives=["Could start with frontend mockups", "Parallel development possible with team"]
        ))
        
        return steps
    
    def _build_decision_tree(self, analysis: Dict) -> Dict:
        """Build a decision tree for the task"""
        tree = {
            "root": "Analyze Task",
            "branches": [
                {
                    "condition": "Is it a web application?",
                    "yes": {
                        "action": "Determine frontend/backend split",
                        "branches": [
                            {
                                "condition": "Need real-time features?",
                                "yes": "Add WebSocket support",
                                "no": "Use REST API"
                            }
                        ]
                    },
                    "no": {
                        "action": "Check if CLI or desktop app",
                        "branches": []
                    }
                },
                {
                    "condition": "Requires authentication?",
                    "yes": {
                        "action": "Implement JWT-based auth",
                        "branches": [
                            {
                                "condition": "Need social login?",
                                "yes": "Add OAuth providers",
                                "no": "Email/password only"
                            }
                        ]
                    },
                    "no": "Skip auth implementation"
                }
            ]
        }
        return tree
    
    def _show_task_analysis(self):
        """Display task analysis results"""
        console.print("\n[bold]📊 Task Analysis[/bold]\n")
        
        table = Table(show_header=False, box=box.ROUNDED)
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="green")
        
        table.add_row("Task Type", self.task_analysis['detected_type'])
        table.add_row("Complexity", f"{self.task_analysis['complexity_score']}/10")
        table.add_row("Key Requirements", ", ".join(self.task_analysis['key_requirements']) or "None detected")
        table.add_row("Suggested Tech", ", ".join(self.task_analysis['suggested_tech']) or "To be determined")
        table.add_row("Agents Needed", str(len(self.task_analysis['estimated_agents'])))
        
        console.print(table)
    
    def _show_reasoning_process(self):
        """Display the reasoning process"""
        console.print("\n[bold]🤔 Reasoning Process[/bold]\n")
        
        for i, step in enumerate(self.reasoning_steps, 1):
            # Create step panel
            content = f"""
[yellow]Agent:[/yellow] {step.agent}
[yellow]Thinking:[/yellow] {step.thought}
[yellow]Decision:[/yellow] [bold]{step.decision}[/bold]
[yellow]Rationale:[/yellow] {step.rationale}
[yellow]Confidence:[/yellow] {step.confidence * 100:.0f}%
"""
            
            if step.alternatives:
                content += f"\n[dim]Alternatives considered:[/dim]"
                for alt in step.alternatives:
                    content += f"\n  • {alt}"
            
            console.print(Panel(
                content.strip(),
                title=f"Step {i}: {step.phase}",
                border_style="blue"
            ))
    
    def _show_decision_tree(self):
        """Display decision tree visualization"""
        console.print("\n[bold]🌳 Decision Tree[/bold]\n")
        
        tree = Tree("🎯 Analyze Task")
        
        # Build tree visualization
        for branch in self.decision_tree.get("branches", []):
            self._add_tree_branch(tree, branch)
        
        console.print(tree)
    
    def _add_tree_branch(self, parent: Tree, branch: Dict):
        """Recursively add branches to tree"""
        condition = branch.get("condition", "")
        
        if "yes" in branch:
            yes_branch = parent.add(f"❓ {condition}")
            if isinstance(branch["yes"], dict):
                yes_node = yes_branch.add("✅ Yes")
                action_node = yes_node.add(f"→ {branch['yes']['action']}")
                for sub_branch in branch["yes"].get("branches", []):
                    self._add_tree_branch(action_node, sub_branch)
            else:
                yes_branch.add(f"✅ Yes → {branch['yes']}")
            
            if "no" in branch:
                yes_branch.add(f"❌ No → {branch['no']}")
    
    def _show_agent_collaboration(self):
        """Show how agents would collaborate"""
        console.print("\n[bold]🤝 Agent Collaboration[/bold]\n")
        
        # Create collaboration flow
        agents = self.task_analysis['estimated_agents']
        
        for i, agent in enumerate(agents):
            if i == 0:
                console.print(f"1️⃣ [cyan]{agent}[/cyan]")
                console.print("   └─→ Analyzes requirements and creates initial plan")
            elif i == len(agents) - 1:
                console.print(f"{i+1}️⃣ [cyan]{agent}[/cyan]")
                console.print("   └─→ Reviews all work and ensures quality standards")
            else:
                console.print(f"{i+1}️⃣ [cyan]{agent}[/cyan]")
                console.print(f"   └─→ Implements specific features based on plan")
            
            if i < len(agents) - 1:
                console.print("   ↓")
    
    def _show_expected_outcome(self):
        """Show what the expected outcome would be"""
        console.print("\n[bold]📦 Expected Outcome[/bold]\n")
        
        outcome = f"""
Based on my analysis, vibe.ai would create:

• A complete project structure with all necessary files
• Production-ready code following best practices
• Comprehensive documentation and README
• Testing setup with example tests
• Docker configuration for easy deployment
• CI/CD pipeline configuration

The solution would be:
- **Functional**: Everything works out of the box
- **Scalable**: Designed for growth
- **Maintainable**: Clean, documented code
- **Secure**: Following security best practices

[dim]Total estimated time: ~10-15 minutes[/dim]
"""
        console.print(Panel(Markdown(outcome), border_style="green"))
    
    def _simple_explain(self, task_description: str):
        """Simple explanation for non-rich terminals"""
        print("\n🧠 vibe.ai Reasoning Engine")
        print("=" * 50)
        print(f"\nAnalyzing: {task_description}")
        
        # Analyze
        self._analyze_task(task_description)
        
        print("\n📊 Task Analysis:")
        print(f"  Type: {self.task_analysis['detected_type']}")
        print(f"  Complexity: {self.task_analysis['complexity_score']}/10")
        print(f"  Requirements: {', '.join(self.task_analysis['key_requirements'])}")
        
        print("\n🤔 Reasoning Process:")
        for i, step in enumerate(self.reasoning_steps, 1):
            print(f"\n{i}. {step.phase}")
            print(f"   Agent: {step.agent}")
            print(f"   Decision: {step.decision}")
            print(f"   Confidence: {step.confidence * 100:.0f}%")
        
        print("\n🤝 Agent Collaboration:")
        for i, agent in enumerate(self.task_analysis['estimated_agents'], 1):
            print(f"  {i}. {agent}")
        
        print("\n📦 Expected Outcome:")
        print("  - Complete project structure")
        print("  - Production-ready code")
        print("  - Documentation and tests")
        print("  - Docker configuration")
    
    def generate_explanation_report(self, task_description: str) -> Dict[str, Any]:
        """Generate a detailed explanation report"""
        self._analyze_task(task_description)
        
        return {
            "task": task_description,
            "analysis": self.task_analysis,
            "reasoning_steps": [
                {
                    "phase": step.phase,
                    "agent": step.agent,
                    "decision": step.decision,
                    "confidence": step.confidence
                }
                for step in self.reasoning_steps
            ],
            "estimated_time": "10-15 minutes",
            "success_probability": 0.95
        }


def main():
    """Main entry point for explanation engine"""
    import sys
    
    if len(sys.argv) > 1:
        task = " ".join(sys.argv[1:])
    else:
        task = "Build a REST API with authentication and database"
    
    engine = ExplanationEngine()
    engine.explain_task(task)


if __name__ == "__main__":
    main()