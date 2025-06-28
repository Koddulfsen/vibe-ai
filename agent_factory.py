#!/usr/bin/env python3
"""
Agent Factory - Simple Agent Creation System
=============================================

Creates new agents with standardized structure and integrated thinking capabilities.
Provides templates and generators for consistent agent development.

Usage:
    python3 agent_factory.py create --name my-agent --type execution
    python3 agent_factory.py list-templates
    python3 agent_factory.py scaffold --name custom-agent --interactive
"""

import os
import sys
import json
import argparse
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime

@dataclass
class AgentTemplate:
    """Represents an agent template configuration"""
    name: str
    type: str  # planning, execution, quality, coordination, custom
    description: str
    base_capabilities: List[str]
    thinking_patterns: List[str]
    required_methods: List[str]
    config_schema: Dict[str, Any]

class AgentFactory:
    """Factory for creating new agents with standardized structure"""
    
    def __init__(self, agents_dir: Optional[Path] = None):
        self.base_dir = Path(__file__).parent
        self.agents_dir = agents_dir or self.base_dir / "agents"
        self.templates_dir = self.base_dir / "templates"
        self.config_dir = self.base_dir / "config"
        
        # Ensure directories exist
        self.agents_dir.mkdir(exist_ok=True)
        self.templates_dir.mkdir(exist_ok=True)
        self.config_dir.mkdir(exist_ok=True)
        
        self.templates = self._load_templates()
        
        # Initialize agent registry for integration
        try:
            from agent_registry import AgentRegistry
            self.registry = AgentRegistry(self.agents_dir, self.config_dir)
        except ImportError:
            self.registry = None
    
    def _load_templates(self) -> Dict[str, AgentTemplate]:
        """Load available agent templates"""
        return {
            "planning": AgentTemplate(
                name="planning",
                type="planning",
                description="Agent that analyzes tasks and creates execution plans",
                base_capabilities=["task_analysis", "complexity_assessment", "subtask_generation"],
                thinking_patterns=["sequential_analysis", "complexity_scoring", "requirement_analysis"],
                required_methods=["analyze_task", "generate_plan", "assess_complexity"],
                config_schema={
                    "max_complexity_score": 100,
                    "max_subtasks": 10,
                    "thinking_depth": 3
                }
            ),
            "execution": AgentTemplate(
                name="execution",
                type="execution", 
                description="Agent that executes development tasks",
                base_capabilities=["code_generation", "file_operations", "command_execution"],
                thinking_patterns=["implementation_planning", "error_handling", "optimization"],
                required_methods=["execute_task", "validate_execution", "handle_errors"],
                config_schema={
                    "timeout_seconds": 300,
                    "retry_count": 3,
                    "safety_checks": True
                }
            ),
            "quality": AgentTemplate(
                name="quality",
                type="quality",
                description="Agent that performs quality assurance and testing",
                base_capabilities=["code_analysis", "test_execution", "quality_scoring"],
                thinking_patterns=["quality_assessment", "test_planning", "risk_analysis"],
                required_methods=["assess_quality", "run_tests", "generate_report"],
                config_schema={
                    "quality_threshold": 0.8,
                    "test_types": ["unit", "integration"],
                    "auto_fix": False
                }
            ),
            "coordination": AgentTemplate(
                name="coordination",
                type="coordination",
                description="Agent that coordinates multi-agent workflows",
                base_capabilities=["agent_management", "workflow_orchestration", "state_synchronization"],
                thinking_patterns=["workflow_planning", "dependency_analysis", "coordination_strategy"],
                required_methods=["coordinate_agents", "manage_workflow", "sync_state"],
                config_schema={
                    "max_parallel_agents": 3,
                    "coordination_timeout": 600,
                    "state_persistence": True
                }
            ),
            "custom": AgentTemplate(
                name="custom",
                type="custom",
                description="Customizable agent template",
                base_capabilities=["base_functionality"],
                thinking_patterns=["custom_thinking"],
                required_methods=["process_task"],
                config_schema={
                    "custom_config": True
                }
            )
        }
    
    def create_agent(self, name: str, template_type: str, description: str = None, 
                    interactive: bool = False) -> Path:
        """Create a new agent from template"""
        
        if template_type not in self.templates:
            raise ValueError(f"Unknown template type: {template_type}")
        
        template = self.templates[template_type]
        agent_name = self._sanitize_name(name)
        agent_file = self.agents_dir / f"{agent_name}.py"
        
        if agent_file.exists():
            raise FileExistsError(f"Agent already exists: {agent_file}")
        
        # Generate agent code
        agent_code = self._generate_agent_code(
            agent_name, template, description, interactive
        )
        
        # Write agent file
        with open(agent_file, 'w') as f:
            f.write(agent_code)
        
        # Make executable
        os.chmod(agent_file, 0o755)
        
        # Create configuration file
        config_file = self.config_dir / f"{agent_name}-config.json"
        with open(config_file, 'w') as f:
            json.dump(template.config_schema, f, indent=2)
        
        print(f"✅ Created agent: {agent_file}")
        print(f"✅ Created config: {config_file}")
        
        # Auto-register with TaskMaster workflow system
        if self.registry:
            try:
                self.registry.refresh_registry()
                agent_metadata = self.registry.get_agent(agent_name)
                if agent_metadata:
                    print(f"✅ Registered with TaskMaster workflow system")
                    print(f"🔧 Agent type: {agent_metadata.type}")
                    print(f"🎯 Capabilities: {', '.join(agent_metadata.capabilities.keywords)}")
                    
                    # Show workflow integration info
                    print(f"\n🤖 TaskMaster Integration:")
                    print(f"   Master Agent: ./master-agent.py agent {agent_name} [args...]")
                    print(f"   Workflow: ./master-agent.py workflow --type {template.type}")
                    
            except Exception as e:
                print(f"⚠️  Registry registration failed: {e}")
        
        return agent_file
    
    def _sanitize_name(self, name: str) -> str:
        """Sanitize agent name for filename"""
        return name.lower().replace(' ', '-').replace('_', '-')
    
    def _generate_agent_code(self, name: str, template: AgentTemplate, 
                           description: str = None, interactive: bool = False) -> str:
        """Generate agent code from template"""
        
        class_name = ''.join(word.capitalize() for word in name.replace('-', ' ').split())
        
        if interactive:
            description = description or input(f"Enter description for {name}: ")
            # Could add more interactive customization here
        
        final_description = description or template.description
        config_dict_str = json.dumps(template.config_schema, indent=12)
        
        # Generate template parts
        thinking_patterns_code = self._generate_thinking_patterns(template)
        required_methods_code = self._generate_required_methods(template)
        
        # Build the agent code using string concatenation to avoid f-string issues
        return self._build_agent_template(
            class_name, name, template, final_description, 
            thinking_patterns_code, required_methods_code, config_dict_str
        )
        
    def _build_agent_template(self, class_name: str, name: str, template: AgentTemplate,
                            description: str, thinking_code: str, methods_code: str,
                            config_dict_str: str) -> str:
        """Build agent template without f-string complications"""
        
        # Build the complete agent code  
        agent_code = f'''#!/usr/bin/env python3
"""
{class_name} Agent

{description}

Generated on: {datetime.now().isoformat()}
Template: {template.name}
Agent Type: {template.type}
Capabilities: {', '.join(template.base_capabilities)}
Thinking Patterns: {', '.join(template.thinking_patterns)}

TaskMaster Integration: This agent is automatically registered with the TaskMaster
workflow system and can be used in orchestrated workflows via master-agent.py
"""

import json
import subprocess
import argparse
import sys
import os
import time
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path

@dataclass
class AgentResult:
    """Standard result structure for all agents"""
    success: bool
    data: Dict[str, Any]
    messages: List[str]
    execution_time: float
    confidence_score: float = 0.0
    thinking_trace: List[Dict[str, Any]] = None

@dataclass
class ThinkingStep:
    """Represents a step in the thinking process"""
    step: int
    question: str
    analysis: str
    conclusion: str
    confidence: float

class {class_name}Agent:
    """
    {description}
    
    Capabilities: {', '.join(template.base_capabilities)}
    Thinking Patterns: {', '.join(template.thinking_patterns)}
    """
    
    def __init__(self, config_path: Optional[str] = None):
        self.agent_name = "{name}"
        self.agent_type = "{template.type}"
        self.config = self._load_config(config_path)
        self.thinking_trace = []
    
    def _load_config(self, config_path: Optional[str] = None) -> Dict[str, Any]:
        """Load agent configuration"""
        if config_path is None:
            config_path = Path(__file__).parent.parent / "config" / f"{name}-config.json"
        
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            # Return default config  
            return {config_dict_str}
    
    def think_through_task(self, task_data: Dict[str, Any]) -> List[ThinkingStep]:
        """Perform sequential thinking about the task"""
        thinking_steps = []
        
        # Template-specific thinking patterns
{thinking_code}
        
        self.thinking_trace = thinking_steps
        return thinking_steps
    
{methods_code}
    
    def process_task(self, task_data: Dict[str, Any]) -> AgentResult:
        """Main entry point for task processing"""
        start_time = time.time()
        
        try:
            # Perform thinking
            thinking_steps = self.think_through_task(task_data)
            
            # Execute main logic
            result_data = self._execute_main_logic(task_data, thinking_steps)
            
            return AgentResult(
                success=True,
                data=result_data,
                messages=[f"{{self.agent_name}} completed successfully"],
                execution_time=time.time() - start_time,
                confidence_score=self._calculate_confidence(result_data),
                thinking_trace=[asdict(step) for step in thinking_steps]
            )
            
        except Exception as e:
            return AgentResult(
                success=False,
                data={{"error": str(e)}},
                messages=[f"Error in {{self.agent_name}}: {{str(e)}}"],
                execution_time=time.time() - start_time,
                confidence_score=0.0,
                thinking_trace=[asdict(step) for step in self.thinking_trace]
            )
    
    def _execute_main_logic(self, task_data: Dict[str, Any], 
                          thinking_steps: List[ThinkingStep]) -> Dict[str, Any]:
        """Execute the main agent logic - override in subclasses"""
        # TODO: Implement agent-specific logic
        return {{
            "status": "completed", 
            "agent": self.agent_name,
            "task_summary": task_data.get("description", "No description"),
            "thinking_summary": f"Performed {{len(thinking_steps)}} thinking steps"
        }}
    
    def _calculate_confidence(self, result_data: Dict[str, Any]) -> float:
        """Calculate confidence score for the result"""
        # Basic confidence calculation - can be enhanced
        if result_data.get("error"):
            return 0.0
        return 0.8  # Default confidence
    
    def get_capabilities(self) -> List[str]:
        """Return list of agent capabilities"""
        return {template.base_capabilities}
    
    def get_thinking_patterns(self) -> List[str]:
        """Return list of thinking patterns"""
        return {template.thinking_patterns}

def main():
    """CLI interface for the agent"""
    parser = argparse.ArgumentParser(description=f"{class_name} Agent")
    parser.add_argument("--task", required=True, help="Task description")
    parser.add_argument("--config", help="Configuration file path")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    # Create agent
    agent = {class_name}Agent(args.config)
    
    # Process task
    task_data = {{"description": args.task}}
    result = agent.process_task(task_data)
    
    # Output results
    if args.verbose:
        print(json.dumps(asdict(result), indent=2))
    else:
        print(f"Success: {{result.success}}")
        print(f"Messages: {{', '.join(result.messages)}}")

if __name__ == "__main__":
    main()
'''
        
        return agent_code
    
    def _generate_thinking_patterns(self, template: AgentTemplate) -> str:
        """Generate thinking pattern code based on template"""
        patterns = {
            "planning": """
        # Planning-specific thinking
        questions = [
            "What is the complexity of this task?",
            "What subtasks are needed?",
            "What dependencies exist?",
            "What risks should be considered?"
        ]""",
            "execution": """
        # Execution-specific thinking  
        questions = [
            "What steps are needed to implement this?",
            "What tools and resources are required?",
            "What could go wrong during execution?",
            "How can we validate the results?"
        ]""",
            "quality": """
        # Quality-specific thinking
        questions = [
            "What quality criteria apply?",
            "What tests should be performed?",
            "What are the potential quality risks?",
            "How can quality be measured?"
        ]""",
            "coordination": """
        # Coordination-specific thinking
        questions = [
            "Which agents need to be coordinated?",
            "What is the optimal workflow sequence?",
            "What dependencies exist between agents?",
            "How should failures be handled?"
        ]""",
            "custom": """
        # Custom thinking patterns
        questions = [
            "What is the goal of this task?",
            "What approach should be taken?",
            "What considerations are important?",
            "How can success be measured?"
        ]"""
        }
        
        base_pattern = patterns.get(template.type, patterns["custom"])
        
        return f'''{base_pattern}
        
        for i, question in enumerate(questions, 1):
            analysis = f"Analyzing: {{question}}"
            conclusion = f"Step {{i}} analysis complete"
            confidence = 0.8  # Default confidence
            
            thinking_steps.append(ThinkingStep(
                step=i,
                question=question,
                analysis=analysis,
                conclusion=conclusion,
                confidence=confidence
            ))'''
    
    def _generate_required_methods(self, template: AgentTemplate) -> str:
        """Generate required method stubs"""
        methods = []
        
        for method in template.required_methods:
            if method == "analyze_task":
                methods.append('''
    def analyze_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze the given task"""
        # TODO: Implement task analysis logic
        return {"analysis": "Task analyzed", "complexity": "moderate"}''')
            
            elif method == "generate_plan":
                methods.append('''
    def generate_plan(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate execution plan for the task"""
        # TODO: Implement plan generation logic
        return {"plan": "Execution plan generated", "steps": []}''')
            
            elif method == "execute_task":
                methods.append('''
    def execute_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the given task"""
        # TODO: Implement task execution logic
        return {"execution": "Task executed", "result": "completed"}''')
            
            elif method == "assess_quality":
                methods.append('''
    def assess_quality(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess quality of task results"""
        # TODO: Implement quality assessment logic
        return {"quality": "Quality assessed", "score": 0.8}''')
            
            else:
                # Generic method stub
                method_name = method.replace("_", " ").title().replace(" ", "")
                methods.append(f'''
    def {method}(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """{method_name} method"""
        # TODO: Implement {method} logic
        return {{"{method}": "Method executed"}}''')
        
        return '\n'.join(methods)
    
    def list_templates(self) -> None:
        """List available agent templates"""
        print("📋 Available Agent Templates:")
        print("=" * 50)
        
        for name, template in self.templates.items():
            print(f"\n🤖 {name.upper()}")
            print(f"   Description: {template.description}")
            print(f"   Capabilities: {', '.join(template.base_capabilities)}")
            print(f"   Thinking: {', '.join(template.thinking_patterns)}")
    
    def scaffold_interactive(self, name: str) -> Path:
        """Create agent with interactive customization"""
        print(f"🏗️  Creating agent: {name}")
        print("=" * 50)
        
        # Choose template
        self.list_templates()
        template_type = input("\nSelect template type: ").strip().lower()
        
        if template_type not in self.templates:
            print(f"❌ Invalid template: {template_type}")
            return None
        
        # Get description
        description = input("Enter agent description: ").strip()
        
        # Create agent
        return self.create_agent(name, template_type, description, interactive=True)

def main():
    """CLI interface for agent factory"""
    parser = argparse.ArgumentParser(description="Agent Factory - Create new agents")
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Create command
    create_parser = subparsers.add_parser('create', help='Create new agent')
    create_parser.add_argument('--name', required=True, help='Agent name')
    create_parser.add_argument('--type', required=True, help='Agent template type')
    create_parser.add_argument('--description', help='Agent description')
    create_parser.add_argument('--interactive', action='store_true', help='Interactive creation')
    
    # List templates command
    list_parser = subparsers.add_parser('list-templates', help='List available templates')
    
    # Scaffold command
    scaffold_parser = subparsers.add_parser('scaffold', help='Interactive agent creation')
    scaffold_parser.add_argument('--name', required=True, help='Agent name')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    factory = AgentFactory()
    
    try:
        if args.command == 'create':
            agent_file = factory.create_agent(
                args.name, args.type, args.description, args.interactive
            )
            print(f"\n🎉 Agent created successfully!")
            print(f"📁 Location: {agent_file}")
            print(f"\n🚀 To test your agent:")
            print(f"   python3 {agent_file} --task 'test task'")
            
        elif args.command == 'list-templates':
            factory.list_templates()
            
        elif args.command == 'scaffold':
            agent_file = factory.scaffold_interactive(args.name)
            if agent_file:
                print(f"\n🎉 Agent scaffolded successfully!")
                print(f"📁 Location: {agent_file}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()