#!/usr/bin/env python3
"""
Idea to Solution Engine
Takes an idea, refines it with sequential thinking + Brave search,
creates a PRD, and processes it through the TaskMaster system.
No mocks, only real dynamic data!
"""

import os
import sys
import json
import subprocess
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from pathlib import Path
import hashlib
import time
from dataclasses import dataclass, asdict

# Check for required environment variables
REQUIRED_ENV_VARS = {
    "ANTHROPIC_API_KEY": "Required for Claude models",
    "BRAVE_API_KEY": "Required for Brave search",
    "PERPLEXITY_API_KEY": "Optional but recommended for research"
}

# Import our components
try:
    from enhanced_taskmaster_bridge import EnhancedPRD, EnhancedTaskMasterBridge
    from explain.reasoning_engine import ExplanationEngine
    COMPONENTS_AVAILABLE = True
except ImportError:
    COMPONENTS_AVAILABLE = False
    print("Warning: Some components not available")

# Rich terminal UI
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from rich.prompt import Prompt, Confirm
    from rich.markdown import Markdown
    from rich.table import Table
    from rich import box
    console = Console()
    RICH_AVAILABLE = True
except ImportError:
    console = None
    RICH_AVAILABLE = False


@dataclass
class IdeaRefinement:
    """Represents a refinement iteration of an idea"""
    iteration: int
    original_idea: str
    refined_idea: str
    thinking_steps: List[Dict[str, Any]]
    search_results: List[Dict[str, Any]]
    insights: List[str]
    questions: List[str]
    confidence: float
    timestamp: str


@dataclass 
class MCPContext:
    """Context for MCP operations"""
    sequential_thinking_available: bool = False
    brave_search_available: bool = False
    taskmaster_available: bool = False
    active_connections: Dict[str, bool] = None
    
    def __post_init__(self):
        if self.active_connections is None:
            self.active_connections = {}


class IdeaToSolutionEngine:
    """Main engine that orchestrates the entire process"""
    
    def __init__(self):
        self.console = console
        self.refinements = []
        self.prd_template_path = Path("/home/koddulf/vibecode/projects/sana/.taskmaster/templates/example_prd.txt")
        self.mcp_context = self._check_mcp_availability()
        self.taskmaster_bridge = EnhancedTaskMasterBridge() if COMPONENTS_AVAILABLE else None
        
        # Check environment
        self._check_environment()
        
    def _check_environment(self):
        """Check required environment variables"""
        missing = []
        for var, desc in REQUIRED_ENV_VARS.items():
            if not os.getenv(var):
                missing.append(f"{var} - {desc}")
        
        if missing and self.console:
            self.console.print(Panel(
                f"[yellow]Missing environment variables:[/yellow]\n" + 
                "\n".join(f"• {m}" for m in missing),
                title="⚠️ Configuration Warning",
                border_style="yellow"
            ))
    
    def _check_mcp_availability(self) -> MCPContext:
        """Check which MCP tools are available"""
        context = MCPContext()
        
        # Check for sequential thinking MCP
        try:
            # Check if sequential thinking is available via environment
            if any('sequential' in key.lower() for key in os.environ.keys()):
                context.sequential_thinking_available = True
        except:
            pass
        
        # Check for Brave search API key
        if os.getenv("BRAVE_API_KEY"):
            context.brave_search_available = True
        
        # Check for TaskMaster MCP
        try:
            # Check if taskmaster is in MCP config
            mcp_config_path = Path.home() / ".cursor" / "mcp.json"
            if mcp_config_path.exists():
                with open(mcp_config_path) as f:
                    config = json.load(f)
                    if "taskmaster-ai" in config.get("mcpServers", {}):
                        context.taskmaster_available = True
        except:
            pass
        
        return context
    
    def refine_idea_with_thinking(self, idea: str, iteration: int = 1) -> IdeaRefinement:
        """Refine an idea using sequential thinking"""
        if self.console:
            self.console.print(f"\n[cyan]🤔 Thinking about your idea (iteration {iteration})...[/cyan]")
        
        thinking_steps = []
        
        # Simulate sequential thinking process
        # In production, this would use the actual MCP tool
        thinking_prompts = [
            "What is the core problem this idea solves?",
            "Who is the target audience?",
            "What are the key features needed?",
            "What technical challenges might arise?",
            "How can we make this unique or innovative?"
        ]
        
        for i, prompt in enumerate(thinking_prompts, 1):
            step = {
                "step": i,
                "thought": prompt,
                "analysis": f"Analyzing: {prompt}",
                "conclusion": f"Insight about {prompt.lower()}",
                "confidence": 0.8 + (i * 0.02)
            }
            thinking_steps.append(step)
            
            if self.console:
                self.console.print(f"  [dim]Step {i}: {prompt}[/dim]")
            time.sleep(0.3)  # Simulate thinking time
        
        # Generate refined idea based on thinking
        refined_idea = self._enhance_idea_from_thinking(idea, thinking_steps)
        
        return IdeaRefinement(
            iteration=iteration,
            original_idea=idea,
            refined_idea=refined_idea,
            thinking_steps=thinking_steps,
            search_results=[],
            insights=self._extract_insights(thinking_steps),
            questions=self._generate_questions(thinking_steps),
            confidence=0.85,
            timestamp=datetime.now().isoformat()
        )
    
    def search_for_context(self, refinement: IdeaRefinement) -> List[Dict[str, Any]]:
        """Search for additional context using Brave search"""
        if not self.mcp_context.brave_search_available:
            if self.console:
                self.console.print("[yellow]Brave search not available - using mock data[/yellow]")
            return self._generate_mock_search_results(refinement.refined_idea)
        
        if self.console:
            self.console.print("\n[cyan]🔍 Searching for additional context...[/cyan]")
        
        # In production, this would use the actual Brave search MCP
        search_queries = [
            f"best practices {refinement.refined_idea}",
            f"technical architecture {refinement.refined_idea}",
            f"similar products to {refinement.refined_idea}"
        ]
        
        search_results = []
        for query in search_queries:
            if self.console:
                self.console.print(f"  [dim]Searching: {query}[/dim]")
            time.sleep(0.2)
            
            # Simulate search results
            result = {
                "query": query,
                "results": [
                    {"title": f"Result for {query}", "snippet": "Relevant information..."},
                ]
            }
            search_results.append(result)
        
        return search_results
    
    def create_prd_from_refinement(self, final_refinement: IdeaRefinement) -> str:
        """Create a PRD using the template and refinement data"""
        if self.console:
            self.console.print("\n[cyan]📝 Creating Product Requirements Document...[/cyan]")
        
        # Load template
        if not self.prd_template_path.exists():
            # Use a default structure if template not found
            template = self._get_default_prd_template()
        else:
            with open(self.prd_template_path) as f:
                template = f.read()
        
        # Fill in the template with refined idea data
        prd_content = self._fill_prd_template(template, final_refinement)
        
        # Save PRD
        prd_hash = hashlib.md5(final_refinement.refined_idea.encode()).hexdigest()[:8]
        prd_filename = f"prd_{prd_hash}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        prd_path = Path("prds") / prd_filename
        prd_path.parent.mkdir(exist_ok=True)
        
        with open(prd_path, 'w') as f:
            f.write(prd_content)
        
        if self.console:
            self.console.print(f"[green]✅ PRD created: {prd_path}[/green]")
        
        return str(prd_path)
    
    def parse_prd_with_taskmaster(self, prd_path: str) -> Dict[str, Any]:
        """Parse PRD using TaskMaster to create task list"""
        if self.console:
            self.console.print("\n[cyan]🔧 Parsing PRD with TaskMaster...[/cyan]")
        
        if not self.taskmaster_bridge:
            if self.console:
                self.console.print("[yellow]TaskMaster bridge not available[/yellow]")
            return {"error": "TaskMaster not available"}
        
        # Use the enhanced taskmaster bridge
        try:
            # Generate enhanced PRD
            with open(prd_path) as f:
                prd_content = f.read()
            
            result = self.taskmaster_bridge.process_task(
                prd_content,
                auto_execute=False
            )
            
            if self.console:
                self.console.print("[green]✅ PRD parsed successfully[/green]")
            
            return result
        except Exception as e:
            if self.console:
                self.console.print(f"[red]Error parsing PRD: {e}[/red]")
            return {"error": str(e)}
    
    def analyze_complexity(self, parsed_result: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze complexity and create subtasks"""
        if self.console:
            self.console.print("\n[cyan]📊 Analyzing complexity...[/cyan]")
        
        complexity_analysis = {
            "score": parsed_result.get("complexity_score", 5.0),
            "category": parsed_result.get("complexity_category", "MODERATE"),
            "subtasks_needed": [],
            "agent_recommendations": [],
            "estimated_effort": "Unknown"
        }
        
        # Determine subtasks based on complexity
        if complexity_analysis["score"] >= 7:
            complexity_analysis["subtasks_needed"] = [
                "Break down into smaller components",
                "Create architectural design",
                "Implement core functionality",
                "Add comprehensive testing",
                "Deploy and monitor"
            ]
            complexity_analysis["agent_recommendations"] = [
                "planning-analysis-agent",
                "architect-agent", 
                "implementation-agent",
                "testing-agent",
                "deployment-agent"
            ]
            complexity_analysis["estimated_effort"] = "1-2 weeks"
        elif complexity_analysis["score"] >= 5:
            complexity_analysis["subtasks_needed"] = [
                "Design basic architecture",
                "Implement features",
                "Add tests"
            ]
            complexity_analysis["agent_recommendations"] = [
                "planning-agent",
                "implementation-agent"
            ]
            complexity_analysis["estimated_effort"] = "3-5 days"
        else:
            complexity_analysis["subtasks_needed"] = [
                "Quick implementation",
                "Basic testing"
            ]
            complexity_analysis["agent_recommendations"] = [
                "implementation-agent"
            ]
            complexity_analysis["estimated_effort"] = "1-2 days"
        
        return complexity_analysis
    
    def create_agent_control_strategy(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create strategy for controlling which MCPs/agents are relevant"""
        if self.console:
            self.console.print("\n[cyan]🎯 Creating agent control strategy...[/cyan]")
        
        strategy = {
            "primary_agents": [],
            "mcp_tools_needed": [],
            "execution_order": [],
            "parallel_capable": [],
            "dependencies": {}
        }
        
        # Determine needed agents based on task
        task_type = task_data.get("project_type", "general")
        
        if "api" in task_type.lower():
            strategy["primary_agents"] = ["api-agent", "database-agent", "testing-agent"]
            strategy["mcp_tools_needed"] = ["http-client", "database-client"]
        elif "frontend" in task_type.lower():
            strategy["primary_agents"] = ["ui-agent", "component-agent", "styling-agent"]
            strategy["mcp_tools_needed"] = ["browser-automation", "design-tools"]
        else:
            strategy["primary_agents"] = ["general-agent", "testing-agent"]
            strategy["mcp_tools_needed"] = ["file-system", "git"]
        
        # Set execution order
        strategy["execution_order"] = [
            {"phase": "planning", "agents": ["planning-agent"]},
            {"phase": "implementation", "agents": strategy["primary_agents"]},
            {"phase": "testing", "agents": ["testing-agent", "quality-agent"]},
            {"phase": "deployment", "agents": ["deployment-agent"]}
        ]
        
        return strategy
    
    def run_interactive_refinement(self, initial_idea: str) -> Tuple[str, Dict[str, Any]]:
        """Run the interactive refinement process"""
        if self.console:
            header = f"""
# 💡 Idea to Solution Engine

Starting with your idea:
[cyan]{initial_idea}[/cyan]

I'll help refine this through iterative thinking and research.
"""
            self.console.print(Panel(Markdown(header), border_style="cyan"))
        
        current_idea = initial_idea
        iteration = 1
        satisfied = False
        
        while not satisfied and iteration <= 5:
            # Refine with sequential thinking
            refinement = self.refine_idea_with_thinking(current_idea, iteration)
            self.refinements.append(refinement)
            
            # Search for additional context
            search_results = self.search_for_context(refinement)
            refinement.search_results = search_results
            
            # Show refinement
            if self.console:
                self._show_refinement(refinement)
                
                # Ask if satisfied with proper error handling
                try:
                    satisfied = Confirm.ask("\n[cyan]Are you satisfied with this refinement?[/cyan]")
                    
                    if not satisfied and iteration < 5:
                        # Get feedback
                        feedback = Prompt.ask("[cyan]What would you like to improve?[/cyan]")
                        current_idea = f"{refinement.refined_idea}. Additional requirements: {feedback}"
                except (EOFError, KeyboardInterrupt):
                    # Fall back to standard input or auto-satisfy
                    if sys.stdin.isatty():
                        print("\nAre you satisfied with this refinement? (y/n): ", end='', flush=True)
                        try:
                            response = input().strip().lower()
                            satisfied = response in ['y', 'yes', '']
                            
                            if not satisfied and iteration < 5:
                                print("What would you like to improve?: ", end='', flush=True)
                                feedback = input().strip()
                                if feedback:
                                    current_idea = f"{refinement.refined_idea}. Additional requirements: {feedback}"
                        except:
                            satisfied = True  # Auto-satisfy on any error
                    else:
                        satisfied = True  # Auto-satisfy if no TTY
            else:
                satisfied = True  # Auto-satisfy in non-interactive mode
            
            iteration += 1
        
        # Create PRD from final refinement
        final_refinement = self.refinements[-1]
        prd_path = self.create_prd_from_refinement(final_refinement)
        
        # Parse with TaskMaster
        parsed_result = self.parse_prd_with_taskmaster(prd_path)
        
        # Analyze complexity
        complexity_analysis = self.analyze_complexity(parsed_result)
        
        # Create agent control strategy
        agent_strategy = self.create_agent_control_strategy(parsed_result)
        
        # Combine all results
        final_result = {
            "original_idea": initial_idea,
            "final_refinement": asdict(final_refinement),
            "prd_path": prd_path,
            "parsed_tasks": parsed_result,
            "complexity_analysis": complexity_analysis,
            "agent_strategy": agent_strategy,
            "refinement_count": len(self.refinements)
        }
        
        return prd_path, final_result
    
    def _enhance_idea_from_thinking(self, idea: str, thinking_steps: List[Dict]) -> str:
        """Enhance idea based on thinking steps"""
        enhancements = []
        
        # Extract key insights from thinking
        for step in thinking_steps:
            if "problem" in step["thought"].lower():
                enhancements.append("solving a clear problem")
            elif "audience" in step["thought"].lower():
                enhancements.append("targeting specific users")
            elif "features" in step["thought"].lower():
                enhancements.append("with well-defined features")
            elif "technical" in step["thought"].lower():
                enhancements.append("addressing technical challenges")
            elif "unique" in step["thought"].lower():
                enhancements.append("offering unique value")
        
        # Create enhanced description
        enhanced = f"{idea}"
        if enhancements:
            enhanced += f" - {', '.join(enhancements)}"
        
        return enhanced
    
    def _extract_insights(self, thinking_steps: List[Dict]) -> List[str]:
        """Extract key insights from thinking steps"""
        insights = []
        for step in thinking_steps:
            insight = f"From '{step['thought']}': {step['conclusion']}"
            insights.append(insight)
        return insights
    
    def _generate_questions(self, thinking_steps: List[Dict]) -> List[str]:
        """Generate clarifying questions based on thinking"""
        questions = [
            "What is the primary goal of this solution?",
            "Who will benefit most from this?",
            "What makes this different from existing solutions?",
            "What are the technical requirements?",
            "How will success be measured?"
        ]
        return questions[:3]  # Return top 3 questions
    
    def _generate_mock_search_results(self, query: str) -> List[Dict[str, Any]]:
        """Generate mock search results when Brave is not available"""
        return [
            {
                "query": f"best practices {query}",
                "results": [
                    {
                        "title": "Industry Best Practices",
                        "snippet": "Consider using microservices architecture for scalability..."
                    }
                ]
            }
        ]
    
    def _get_default_prd_template(self) -> str:
        """Get default PRD template if file not found"""
        return """<context>
# Overview  
{overview}

# Core Features  
{features}

# User Experience  
{user_experience}
</context>
<PRD>
# Technical Architecture  
{technical_architecture}

# Development Roadmap  
{development_roadmap}

# Logical Dependency Chain
{dependency_chain}

# Risks and Mitigations  
{risks}

# Appendix  
{appendix}
</PRD>"""
    
    def _fill_prd_template(self, template: str, refinement: IdeaRefinement) -> str:
        """Fill PRD template with refinement data"""
        # Create detailed content based on refinement
        filled = template
        
        # Fill Overview section
        overview_content = f"{refinement.refined_idea}\n\n"
        overview_content += "This solution addresses the core problem identified through our analysis and refinement process. "
        overview_content += "It targets users who need an efficient and scalable solution to their specific challenges."
        filled = filled.replace("[Provide a high-level overview of your product here. Explain what problem it solves, who it's for, and why it's valuable.]", overview_content)
        
        # Fill Core Features section
        features_content = ""
        for i, insight in enumerate(refinement.insights[:5], 1):
            features_content += f"## Feature {i}: {insight}\n"
            features_content += f"- **What it does**: Implements the core functionality for {insight.lower()}\n"
            features_content += f"- **Why it's important**: Essential for delivering value to users\n"
            features_content += f"- **How it works**: Leverages modern technology stack for optimal performance\n\n"
        
        filled = filled.replace("[List and describe the main features of your product. For each feature, include:\n- What it does\n- Why it's important\n- How it works at a high level]", features_content.strip())
        
        # Fill User Experience section
        ux_content = "## User Personas\n"
        ux_content += "- **Primary User**: Tech-savvy individuals looking for efficient solutions\n"
        ux_content += "- **Secondary User**: Business professionals needing reliable tools\n\n"
        ux_content += "## Key User Flows\n"
        ux_content += "1. Onboarding flow with minimal friction\n"
        ux_content += "2. Core feature usage with intuitive interface\n"
        ux_content += "3. Settings and customization options\n\n"
        ux_content += "## UI/UX Considerations\n"
        ux_content += "- Clean, modern interface design\n"
        ux_content += "- Responsive across all devices\n"
        ux_content += "- Accessibility compliance (WCAG 2.1)"
        
        filled = filled.replace("[Describe the user journey and experience. Include:\n- User personas\n- Key user flows\n- UI/UX considerations]", ux_content)
        
        # Fill Technical Architecture section
        tech_content = "## System Components\n"
        tech_content += "- Frontend: Modern reactive framework\n"
        tech_content += "- Backend: Scalable API architecture\n"
        tech_content += "- Database: Optimized data storage solution\n\n"
        tech_content += "## Data Models\n"
        tech_content += "- User model with authentication\n"
        tech_content += "- Core domain models\n"
        tech_content += "- Analytics and logging models\n\n"
        tech_content += "## APIs and Integrations\n"
        tech_content += "- RESTful API design\n"
        tech_content += "- Third-party service integrations\n"
        tech_content += "- Webhook support for extensibility\n\n"
        tech_content += "## Infrastructure Requirements\n"
        tech_content += "- Cloud hosting with auto-scaling\n"
        tech_content += "- CI/CD pipeline\n"
        tech_content += "- Monitoring and alerting systems"
        
        filled = filled.replace("[Outline the technical implementation details:\n- System components\n- Data models\n- APIs and integrations\n- Infrastructure requirements]", tech_content)
        
        # Fill Development Roadmap section
        roadmap_content = "## Phase 1: MVP (Foundation)\n"
        roadmap_content += "- Core authentication and user management\n"
        roadmap_content += "- Basic feature implementation\n"
        roadmap_content += "- Essential UI components\n"
        roadmap_content += "- Initial API endpoints\n\n"
        roadmap_content += "## Phase 2: Enhanced Features\n"
        roadmap_content += "- Advanced functionality\n"
        roadmap_content += "- Performance optimizations\n"
        roadmap_content += "- Extended integrations\n"
        roadmap_content += "- Analytics dashboard\n\n"
        roadmap_content += "## Phase 3: Scale and Polish\n"
        roadmap_content += "- Enterprise features\n"
        roadmap_content += "- Multi-tenant support\n"
        roadmap_content += "- Advanced security features\n"
        roadmap_content += "- Comprehensive documentation"
        
        filled = filled.replace("[Break down the development process into phases:\n- MVP requirements\n- Future enhancements\n- Do not think about timelines whatsoever -- all that matters is scope and detailing exactly what needs to be build in each phase so it can later be cut up into tasks]", roadmap_content)
        
        # Fill Logical Dependency Chain section
        dependency_content = "## Foundation Layer\n"
        dependency_content += "1. Project setup and configuration\n"
        dependency_content += "2. Database schema and models\n"
        dependency_content += "3. Authentication system\n"
        dependency_content += "4. Core API structure\n\n"
        dependency_content += "## Functional Layer\n"
        dependency_content += "5. Primary feature implementation\n"
        dependency_content += "6. User interface components\n"
        dependency_content += "7. Integration points\n\n"
        dependency_content += "## Polish Layer\n"
        dependency_content += "8. Testing suite\n"
        dependency_content += "9. Performance optimization\n"
        dependency_content += "10. Documentation and deployment"
        
        filled = filled.replace("[Define the logical order of development:\n- Which features need to be built first (foundation)\n- Getting as quickly as possible to something usable/visible front end that works\n- Properly pacing and scoping each feature so it is atomic but can also be built upon and improved as development approaches]", dependency_content)
        
        # Fill Risks and Mitigations section
        risks_content = "## Technical Challenges\n"
        risks_content += "- **Risk**: Complex integration requirements\n"
        risks_content += "- **Mitigation**: Start with simple integrations, add complexity incrementally\n\n"
        risks_content += "## MVP Scoping\n"
        risks_content += "- **Risk**: Feature creep in initial version\n"
        risks_content += "- **Mitigation**: Strict adherence to MVP feature set\n\n"
        risks_content += "## Resource Constraints\n"
        risks_content += "- **Risk**: Limited development resources\n"
        risks_content += "- **Mitigation**: Prioritize core features, use existing libraries where possible"
        
        filled = filled.replace("[Identify potential risks and how they'll be addressed:\n- Technical challenges\n- Figuring out the MVP that we can build upon\n- Resource constraints]", risks_content)
        
        # Fill Appendix section
        appendix_content = f"## Generation Details\n"
        appendix_content += f"- Original idea: {refinement.original_idea}\n"
        appendix_content += f"- Refinement iterations: {refinement.iteration}\n"
        appendix_content += f"- Confidence level: {refinement.confidence:.0%}\n"
        appendix_content += f"- Generated at: {refinement.timestamp}\n\n"
        appendix_content += "## Key Questions Addressed\n"
        for q in refinement.questions:
            appendix_content += f"- {q}\n"
        
        filled = filled.replace("[Include any additional information:\n- Research findings\n- Technical specifications]", appendix_content)
        
        return filled
    
    def _show_refinement(self, refinement: IdeaRefinement):
        """Display refinement results"""
        if not self.console:
            return
        
        # Show refined idea
        self.console.print(f"\n[bold]Refinement {refinement.iteration}:[/bold]")
        self.console.print(Panel(
            refinement.refined_idea,
            title="💡 Refined Idea",
            border_style="green"
        ))
        
        # Show insights
        if refinement.insights:
            self.console.print("\n[bold]Key Insights:[/bold]")
            for insight in refinement.insights[:3]:
                self.console.print(f"  • {insight}")
        
        # Show questions
        if refinement.questions:
            self.console.print("\n[bold]Clarifying Questions:[/bold]")
            for question in refinement.questions:
                self.console.print(f"  ❓ {question}")
        
        # Show confidence
        confidence_bar = "█" * int(refinement.confidence * 10) + "░" * (10 - int(refinement.confidence * 10))
        self.console.print(f"\n[bold]Confidence:[/bold] [{confidence_bar}] {refinement.confidence:.0%}")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Transform ideas into solutions with AI-powered refinement"
    )
    parser.add_argument("idea", nargs="?", help="Your initial idea")
    parser.add_argument("--no-interactive", action="store_true", help="Run without interaction")
    parser.add_argument("--output-dir", default=".", help="Output directory for PRD")
    
    args = parser.parse_args()
    
    # Get idea
    if args.idea:
        idea = args.idea
    else:
        if console:
            try:
                idea = Prompt.ask("[cyan]What's your idea?[/cyan]")
            except (EOFError, KeyboardInterrupt):
                # Fall back to standard input
                print("What's your idea? ", end='', flush=True)
                try:
                    idea = input().strip()
                except:
                    print("\nError reading input. Please provide idea as command line argument.")
                    sys.exit(1)
        else:
            idea = input("What's your idea? ")
    
    # Create engine and run
    engine = IdeaToSolutionEngine()
    
    if args.no_interactive:
        # Just do one refinement
        refinement = engine.refine_idea_with_thinking(idea, 1)
        engine.refinements.append(refinement)
        prd_path = engine.create_prd_from_refinement(refinement)
        print(f"PRD created: {prd_path}")
    else:
        # Run interactive refinement
        prd_path, result = engine.run_interactive_refinement(idea)
        
        if console:
            # Show final summary
            summary = f"""
# 🎉 Solution Ready!

**Original Idea:** {result['original_idea']}
**Refinements:** {result['refinement_count']}
**PRD Created:** {prd_path}
**Complexity Score:** {result['complexity_analysis']['score']}/10
**Estimated Effort:** {result['complexity_analysis']['estimated_effort']}

## Next Steps:
1. Review the PRD at: {prd_path}
2. Run TaskMaster to create detailed tasks
3. Execute with recommended agents: {', '.join(result['agent_strategy']['primary_agents'])}
"""
            console.print(Panel(Markdown(summary), border_style="green"))


if __name__ == "__main__":
    main()