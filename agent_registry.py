#!/usr/bin/env python3
"""
Dynamic Agent Registry for TaskMaster System
===========================================

Provides dynamic discovery, registration, and management of all agents
including factory-created ones. Integrates seamlessly with master-agent.py
workflow orchestration.

Features:
- Auto-discovery of new agents
- Capability-based agent matching
- Dynamic workflow generation
- Agent metadata management
- Integration with quality assessment
"""

import os
import sys
import json
import importlib.util
import inspect
from pathlib import Path
from typing import Dict, List, Optional, Any, Set, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import subprocess
import time

@dataclass
class AgentCapability:
    """Defines what an agent can do"""
    keywords: List[str]
    outputs: List[str] 
    dependencies: List[str]
    provides_for: List[str]
    thinking_patterns: List[str]
    quality_aspects: List[str]

@dataclass
class AgentMetadata:
    """Complete metadata for an agent"""
    name: str
    type: str  # planning, execution, quality, coordination, custom
    description: str
    file_path: Path
    config_path: Optional[Path]
    capabilities: AgentCapability
    template_source: Optional[str] = None  # If created by factory
    version: str = "1.0"
    status: str = "active"

class AgentRegistry:
    """Central registry for all TaskMaster agents"""
    
    def __init__(self, agents_dir: Optional[Path] = None, config_dir: Optional[Path] = None):
        self.base_dir = Path(__file__).parent
        self.agents_dir = agents_dir or self.base_dir / "agents"
        self.config_dir = config_dir or self.base_dir / "config"
        self.registry_file = self.base_dir / ".taskmaster" / "agent_registry.json"
        
        # Ensure directories exist
        self.agents_dir.mkdir(exist_ok=True)
        self.config_dir.mkdir(exist_ok=True)
        (self.base_dir / ".taskmaster").mkdir(exist_ok=True)
        
        self.agents: Dict[str, AgentMetadata] = {}
        self.load_registry()
    
    def discover_agents(self) -> Dict[str, AgentMetadata]:
        """Auto-discover all agents in the agents directory"""
        discovered = {}
        
        # Scan for Python agent files
        for agent_file in self.agents_dir.glob("*.py"):
            if agent_file.name.startswith("__"):
                continue
                
            agent_name = agent_file.stem
            metadata = self._extract_agent_metadata(agent_file)
            
            if metadata:
                discovered[agent_name] = metadata
                
        return discovered
    
    def _extract_agent_metadata(self, agent_file: Path) -> Optional[AgentMetadata]:
        """Extract metadata from agent file"""
        try:
            # Read agent file to extract metadata
            with open(agent_file, 'r') as f:
                content = f.read()
            
            # Try to determine agent type and capabilities
            agent_name = agent_file.stem
            agent_type = self._infer_agent_type(agent_name, content)
            
            # Extract description from docstring
            description = self._extract_description(content)
            
            # Find config file
            config_file = self.config_dir / f"{agent_name}-config.json"
            config_path = config_file if config_file.exists() else None
            
            # Extract capabilities
            capabilities = self._extract_capabilities(agent_name, content, config_path)
            
            # Check if factory-created
            template_source = self._check_factory_source(content)
            
            return AgentMetadata(
                name=agent_name,
                type=agent_type,
                description=description,
                file_path=agent_file,
                config_path=config_path,
                capabilities=capabilities,
                template_source=template_source
            )
            
        except Exception as e:
            print(f"Warning: Could not extract metadata from {agent_file}: {e}")
            return None
    
    def _infer_agent_type(self, name: str, content: str) -> str:
        """Infer agent type from name and content"""
        name_lower = name.lower()
        content_lower = content.lower()
        
        # Check for explicit type markers
        if "planning" in name_lower or "analysis" in name_lower:
            return "planning"
        elif "execution" in name_lower or "execute" in name_lower:
            return "execution"
        elif "quality" in name_lower or "test" in name_lower:
            return "quality"
        elif "coordinator" in name_lower or "coordination" in name_lower:
            return "coordination"
        elif "repo" in name_lower or "repository" in name_lower:
            return "repository"
        
        # Check content for type indicators
        if any(word in content_lower for word in ["complexity", "analyze_task", "generate_plan"]):
            return "planning"
        elif any(word in content_lower for word in ["execute_task", "run_command", "subprocess"]):
            return "execution"
        elif any(word in content_lower for word in ["assess_quality", "run_tests", "validate"]):
            return "quality"
        elif any(word in content_lower for word in ["coordinate", "orchestrate", "manage_workflow"]):
            return "coordination"
        
        return "custom"
    
    def _extract_description(self, content: str) -> str:
        """Extract description from agent docstring"""
        lines = content.split('\n')
        in_docstring = False
        description_lines = []
        
        for line in lines:
            line = line.strip()
            if line.startswith('"""') and not in_docstring:
                in_docstring = True
                # Get text after opening quotes
                after_quotes = line[3:].strip()
                if after_quotes and not after_quotes.endswith('"""'):
                    description_lines.append(after_quotes)
                elif after_quotes.endswith('"""'):
                    # Single line docstring
                    return after_quotes[:-3].strip()
                continue
            elif line.endswith('"""') and in_docstring:
                # End of docstring
                before_quotes = line[:-3].strip()
                if before_quotes:
                    description_lines.append(before_quotes)
                break
            elif in_docstring and line and not line.startswith('==='):
                description_lines.append(line)
        
        return ' '.join(description_lines).strip() or "Agent description not available"
    
    def _extract_capabilities(self, name: str, content: str, config_path: Optional[Path]) -> AgentCapability:
        """Extract agent capabilities"""
        
        # Default capabilities based on type
        type_defaults = {
            "planning": {
                "keywords": ["analyze", "plan", "complexity", "design"],
                "outputs": ["task_analysis", "complexity_scores", "execution_plan"],
                "dependencies": [],
                "provides_for": ["execution", "quality"],
                "thinking_patterns": ["sequential_analysis", "complexity_scoring"],
                "quality_aspects": ["task_understanding", "plan_completeness"]
            },
            "execution": {
                "keywords": ["implement", "execute", "build", "create"],
                "outputs": ["code", "files", "implementation"],
                "dependencies": ["planning"],
                "provides_for": ["quality"],
                "thinking_patterns": ["implementation_planning", "error_handling"],
                "quality_aspects": ["code_quality", "functionality", "completeness"]
            },
            "quality": {
                "keywords": ["test", "validate", "check", "assess"],
                "outputs": ["test_results", "quality_report", "validation"],
                "dependencies": ["execution"],
                "provides_for": [],
                "thinking_patterns": ["quality_assessment", "test_planning"],
                "quality_aspects": ["test_coverage", "validation_accuracy", "issue_detection"]
            },
            "coordination": {
                "keywords": ["coordinate", "orchestrate", "manage", "workflow"],
                "outputs": ["coordination_plan", "workflow_status"],
                "dependencies": [],
                "provides_for": ["planning", "execution", "quality"],
                "thinking_patterns": ["workflow_planning", "dependency_analysis"],
                "quality_aspects": ["coordination_effectiveness", "workflow_optimization"]
            }
        }
        
        agent_type = self._infer_agent_type(name, content)
        defaults = type_defaults.get(agent_type, type_defaults["execution"])
        
        # Try to extract from config file
        if config_path and config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    config = json.load(f)
                    
                capabilities_config = config.get('capabilities', {})
                
                # Merge with defaults
                for key in defaults:
                    if key in capabilities_config:
                        defaults[key] = capabilities_config[key]
                        
            except Exception:
                pass  # Use defaults
        
        # Extract from code content
        content_lower = content.lower()
        
        # Look for capability indicators in code
        additional_keywords = []
        if "git" in content_lower:
            additional_keywords.append("git")
        if "docker" in content_lower:
            additional_keywords.append("docker")
        if "database" in content_lower:
            additional_keywords.append("database")
        
        defaults["keywords"].extend(additional_keywords)
        
        return AgentCapability(**defaults)
    
    def _check_factory_source(self, content: str) -> Optional[str]:
        """Check if agent was created by factory"""
        if "Generated on:" in content and "Template:" in content:
            lines = content.split('\n')
            for line in lines:
                if "Template:" in line:
                    return line.split("Template:")[-1].strip()
        return None
    
    def register_agent(self, metadata: AgentMetadata) -> None:
        """Register an agent in the registry"""
        self.agents[metadata.name] = metadata
        self.save_registry()
    
    def unregister_agent(self, agent_name: str) -> bool:
        """Remove agent from registry"""
        if agent_name in self.agents:
            del self.agents[agent_name]
            self.save_registry()
            return True
        return False
    
    def get_agent(self, name: str) -> Optional[AgentMetadata]:
        """Get agent metadata by name"""
        return self.agents.get(name)
    
    def get_agents_by_type(self, agent_type: str) -> List[AgentMetadata]:
        """Get all agents of specific type"""
        return [agent for agent in self.agents.values() if agent.type == agent_type]
    
    def get_agents_by_capability(self, capability: str) -> List[AgentMetadata]:
        """Get agents that have specific capability"""
        matching = []
        for agent in self.agents.values():
            if (capability in agent.capabilities.keywords or 
                capability in agent.capabilities.outputs):
                matching.append(agent)
        return matching
    
    def find_agents_for_task(self, task_description: str, task_type: Optional[str] = None) -> List[AgentMetadata]:
        """Find best agents for a given task"""
        task_lower = task_description.lower()
        scored_agents = []
        
        for agent in self.agents.values():
            score = 0
            
            # Type match
            if task_type and agent.type == task_type:
                score += 10
            
            # Keyword matches
            for keyword in agent.capabilities.keywords:
                if keyword in task_lower:
                    score += 5
            
            # Output relevance
            for output in agent.capabilities.outputs:
                if output.replace('_', ' ') in task_lower:
                    score += 3
            
            if score > 0:
                scored_agents.append((score, agent))
        
        # Sort by score and return agents
        scored_agents.sort(reverse=True, key=lambda x: x[0])
        return [agent for score, agent in scored_agents]
    
    def get_workflow_agents(self, workflow_type: str) -> List[AgentMetadata]:
        """Get agents needed for specific workflow type"""
        workflows = {
            "analyze": ["planning"],
            "execute": ["execution"],
            "quality": ["quality"],
            "full-dev": ["planning", "execution", "quality"],
            "planning": ["planning", "coordination"],
            "quick-fix": ["execution", "quality"]
        }
        
        needed_types = workflows.get(workflow_type, [])
        workflow_agents = []
        
        for agent_type in needed_types:
            agents = self.get_agents_by_type(agent_type)
            if agents:
                # Get the primary agent for this type (could be enhanced with selection logic)
                workflow_agents.append(agents[0])
        
        return workflow_agents
    
    def refresh_registry(self) -> Dict[str, AgentMetadata]:
        """Refresh registry by re-discovering all agents"""
        discovered = self.discover_agents()
        
        # Update existing agents and add new ones
        for name, metadata in discovered.items():
            self.agents[name] = metadata
        
        # Remove agents that no longer exist
        existing_names = set(self.agents.keys())
        discovered_names = set(discovered.keys())
        removed_agents = existing_names - discovered_names
        
        for removed in removed_agents:
            # Check if the file actually exists before removing
            agent = self.agents[removed]
            if not agent.file_path.exists():
                del self.agents[removed]
        
        self.save_registry()
        return discovered
    
    def save_registry(self) -> None:
        """Save registry to disk"""
        registry_data = {
            "version": "1.0",
            "updated": time.time(),
            "agents": {
                name: {
                    **asdict(metadata),
                    "file_path": str(metadata.file_path),
                    "config_path": str(metadata.config_path) if metadata.config_path else None
                }
                for name, metadata in self.agents.items()
            }
        }
        
        with open(self.registry_file, 'w') as f:
            json.dump(registry_data, f, indent=2)
    
    def load_registry(self) -> None:
        """Load registry from disk"""
        if not self.registry_file.exists():
            # First time - discover all agents
            self.refresh_registry()
            return
        
        try:
            with open(self.registry_file, 'r') as f:
                registry_data = json.load(f)
            
            agents_data = registry_data.get("agents", {})
            
            for name, data in agents_data.items():
                # Convert paths back to Path objects
                data["file_path"] = Path(data["file_path"])
                if data["config_path"]:
                    data["config_path"] = Path(data["config_path"])
                
                # Convert capabilities dict back to AgentCapability
                caps_data = data["capabilities"]
                data["capabilities"] = AgentCapability(**caps_data)
                
                # Create AgentMetadata object
                metadata = AgentMetadata(**data)
                self.agents[name] = metadata
                
        except Exception as e:
            print(f"Warning: Could not load agent registry: {e}")
            # Fallback to discovery
            self.refresh_registry()
    
    def get_registry_status(self) -> Dict[str, Any]:
        """Get status information about the registry"""
        total_agents = len(self.agents)
        agents_by_type = {}
        factory_created = 0
        
        for agent in self.agents.values():
            agent_type = agent.type
            agents_by_type[agent_type] = agents_by_type.get(agent_type, 0) + 1
            
            if agent.template_source:
                factory_created += 1
        
        return {
            "total_agents": total_agents,
            "agents_by_type": agents_by_type,
            "factory_created": factory_created,
            "registry_file": str(self.registry_file),
            "last_updated": self.registry_file.stat().st_mtime if self.registry_file.exists() else None
        }
    
    def list_agents(self, verbose: bool = False) -> None:
        """List all registered agents"""
        if not self.agents:
            print("No agents registered. Run 'refresh' to discover agents.")
            return
        
        print(f"📋 Registered Agents ({len(self.agents)} total)")
        print("=" * 60)
        
        agents_by_type = {}
        for agent in self.agents.values():
            if agent.type not in agents_by_type:
                agents_by_type[agent.type] = []
            agents_by_type[agent.type].append(agent)
        
        for agent_type, agents in agents_by_type.items():
            print(f"\n🤖 {agent_type.upper()} AGENTS ({len(agents)})")
            print("-" * 40)
            
            for agent in agents:
                print(f"   📄 {agent.name}")
                if verbose:
                    print(f"      Description: {agent.description}")
                    print(f"      Keywords: {', '.join(agent.capabilities.keywords)}")
                    print(f"      File: {agent.file_path}")
                    if agent.template_source:
                        print(f"      Template: {agent.template_source}")

def main():
    """CLI interface for agent registry"""
    parser = argparse.ArgumentParser(description="TaskMaster Agent Registry")
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List all agents')
    list_parser.add_argument('--verbose', action='store_true', help='Verbose output')
    
    # Refresh command
    refresh_parser = subparsers.add_parser('refresh', help='Refresh agent registry')
    
    # Status command
    status_parser = subparsers.add_parser('status', help='Show registry status')
    
    # Find command
    find_parser = subparsers.add_parser('find', help='Find agents for task')
    find_parser.add_argument('task', help='Task description')
    find_parser.add_argument('--type', help='Preferred agent type')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    registry = AgentRegistry()
    
    if args.command == 'list':
        registry.list_agents(args.verbose)
        
    elif args.command == 'refresh':
        print("🔄 Refreshing agent registry...")
        discovered = registry.refresh_registry()
        print(f"✅ Discovered {len(discovered)} agents")
        registry.list_agents()
        
    elif args.command == 'status':
        status = registry.get_registry_status()
        print("📊 Agent Registry Status")
        print("=" * 30)
        print(f"Total Agents: {status['total_agents']}")
        print(f"Factory Created: {status['factory_created']}")
        print("Agents by Type:")
        for agent_type, count in status['agents_by_type'].items():
            print(f"  {agent_type}: {count}")
        
    elif args.command == 'find':
        agents = registry.find_agents_for_task(args.task, args.type)
        print(f"🔍 Found {len(agents)} agents for task: {args.task}")
        for i, agent in enumerate(agents[:5], 1):  # Show top 5
            print(f"  {i}. {agent.name} ({agent.type})")
            print(f"     {agent.description}")

if __name__ == "__main__":
    main()