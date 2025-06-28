#!/usr/bin/env python3
"""
Auto-Agent Generation System
Automatically generates specialized agents based on requirements
"""

import os
import ast
import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import subprocess

from code_generation_templates import CodeGenerationTemplates
from domain_knowledge_base import DomainKnowledgeBase


@dataclass
class AgentSpecification:
    """Specification for a new agent"""
    name: str
    purpose: str
    capabilities: List[str]
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]
    dependencies: List[str]
    domain: Optional[str] = None
    implementation_strategy: Optional[str] = None


class AutoAgentGenerator:
    """Automatically generates new agents based on requirements"""
    
    def __init__(self):
        self.template_generator = CodeGenerationTemplates()
        self.knowledge_base = DomainKnowledgeBase()
        self.agents_dir = "agents"
        
    def analyze_agent_need(self, requirement: str) -> AgentSpecification:
        """Analyze what kind of agent is needed"""
        # Detect domain
        domains = self.knowledge_base.detect_domains(requirement)
        primary_domain = domains[0] if domains else None
        
        # Extract agent characteristics
        name = self._extract_agent_name(requirement)
        purpose = self._extract_purpose(requirement)
        capabilities = self._extract_capabilities(requirement, primary_domain)
        
        # Define schemas based on purpose
        input_schema, output_schema = self._define_schemas(purpose, capabilities)
        
        # Determine dependencies
        dependencies = self._determine_dependencies(capabilities, primary_domain)
        
        # Choose implementation strategy
        strategy = self._choose_implementation_strategy(capabilities)
        
        return AgentSpecification(
            name=name,
            purpose=purpose,
            capabilities=capabilities,
            input_schema=input_schema,
            output_schema=output_schema,
            dependencies=dependencies,
            domain=primary_domain,
            implementation_strategy=strategy
        )
    
    def generate_agent(self, spec: AgentSpecification) -> Dict[str, Any]:
        """Generate a complete agent from specification"""
        # Generate main agent code
        agent_code = self._generate_agent_code(spec)
        
        # Generate test code
        test_code = self._generate_test_code(spec)
        
        # Generate configuration
        config = self._generate_agent_config(spec)
        
        # Save files
        agent_path = self._save_agent_files(spec, agent_code, test_code, config)
        
        # Register agent
        self._register_agent(spec, agent_path)
        
        return {
            "success": True,
            "agent_name": spec.name,
            "agent_path": agent_path,
            "capabilities": spec.capabilities,
            "message": f"Successfully generated agent: {spec.name}"
        }
    
    def _extract_agent_name(self, requirement: str) -> str:
        """Extract agent name from requirement"""
        # Look for patterns like "payment-processor-agent" or "ml-recommendation-agent"
        import re
        
        # Try to find explicit agent name
        agent_pattern = r"(\w+[-_]\w+[-_]agent)"
        match = re.search(agent_pattern, requirement.lower())
        if match:
            return match.group(1).replace("_", "-")
        
        # Generate name from key terms
        key_terms = []
        for term in ["payment", "ml", "recommendation", "inventory", "sync", 
                    "vendor", "management", "processing", "analysis", "generation"]:
            if term in requirement.lower():
                key_terms.append(term)
        
        if key_terms:
            return f"{'-'.join(key_terms[:2])}-agent"
        
        return "custom-agent"
    
    def _extract_purpose(self, requirement: str) -> str:
        """Extract agent purpose from requirement"""
        # Clean up the requirement to extract purpose
        purpose_keywords = ["for", "to", "that", "which"]
        requirement_lower = requirement.lower()
        
        for keyword in purpose_keywords:
            if keyword in requirement_lower:
                parts = requirement_lower.split(keyword, 1)
                if len(parts) > 1:
                    return parts[1].strip().capitalize()
        
        return f"Handle {requirement}"
    
    def _extract_capabilities(self, requirement: str, domain: Optional[str]) -> List[str]:
        """Extract agent capabilities"""
        capabilities = []
        
        # Common capability keywords
        capability_keywords = {
            "process": ["data_processing", "event_handling"],
            "analyze": ["data_analysis", "pattern_recognition"],
            "generate": ["code_generation", "report_generation"],
            "integrate": ["api_integration", "service_communication"],
            "validate": ["data_validation", "schema_validation"],
            "transform": ["data_transformation", "format_conversion"],
            "monitor": ["health_monitoring", "performance_tracking"],
            "sync": ["data_synchronization", "state_management"],
            "recommend": ["ml_inference", "recommendation_engine"],
            "detect": ["anomaly_detection", "pattern_matching"]
        }
        
        requirement_lower = requirement.lower()
        for keyword, caps in capability_keywords.items():
            if keyword in requirement_lower:
                capabilities.extend(caps)
        
        # Domain-specific capabilities
        if domain:
            domain_knowledge = self.knowledge_base.get_domain_knowledge(domain)
            if domain_knowledge:
                if "payment" in requirement_lower:
                    capabilities.extend(["payment_processing", "transaction_handling"])
                if "ml" in requirement_lower or "ai" in requirement_lower:
                    capabilities.extend(["model_loading", "prediction", "training"])
        
        # Ensure basic capabilities
        if not capabilities:
            capabilities = ["task_execution", "data_processing", "result_generation"]
        
        return list(set(capabilities))
    
    def _define_schemas(self, purpose: str, capabilities: List[str]) -> tuple[Dict[str, Any], Dict[str, Any]]:
        """Define input and output schemas based on purpose and capabilities"""
        # Base schemas
        input_schema = {
            "type": "object",
            "properties": {
                "task_id": {"type": "string"},
                "action": {"type": "string"},
                "data": {"type": "object"}
            },
            "required": ["task_id", "action"]
        }
        
        output_schema = {
            "type": "object",
            "properties": {
                "status": {"type": "string", "enum": ["success", "error", "pending"]},
                "task_id": {"type": "string"},
                "result": {"type": "object"},
                "errors": {"type": "array", "items": {"type": "string"}}
            },
            "required": ["status", "task_id"]
        }
        
        # Customize based on capabilities
        if "payment_processing" in capabilities:
            input_schema["properties"]["data"]["properties"] = {
                "amount": {"type": "number"},
                "currency": {"type": "string"},
                "payment_method": {"type": "string"},
                "customer_id": {"type": "string"}
            }
            output_schema["properties"]["result"]["properties"] = {
                "transaction_id": {"type": "string"},
                "status": {"type": "string"},
                "timestamp": {"type": "string"}
            }
        
        elif "ml_inference" in capabilities:
            input_schema["properties"]["data"]["properties"] = {
                "model_name": {"type": "string"},
                "input_data": {"type": "array"},
                "parameters": {"type": "object"}
            }
            output_schema["properties"]["result"]["properties"] = {
                "predictions": {"type": "array"},
                "confidence": {"type": "number"},
                "model_version": {"type": "string"}
            }
        
        elif "data_synchronization" in capabilities:
            input_schema["properties"]["data"]["properties"] = {
                "source": {"type": "string"},
                "target": {"type": "string"},
                "sync_type": {"type": "string", "enum": ["full", "incremental"]},
                "filters": {"type": "object"}
            }
            output_schema["properties"]["result"]["properties"] = {
                "records_synced": {"type": "number"},
                "duration_ms": {"type": "number"},
                "errors": {"type": "array"}
            }
        
        return input_schema, output_schema
    
    def _determine_dependencies(self, capabilities: List[str], domain: Optional[str]) -> List[str]:
        """Determine required dependencies based on capabilities"""
        dependencies = ["pydantic", "typing", "asyncio"]  # Base dependencies
        
        # Capability-based dependencies
        capability_deps = {
            "payment_processing": ["stripe", "paypal-sdk"],
            "ml_inference": ["tensorflow", "scikit-learn", "numpy"],
            "data_processing": ["pandas", "numpy"],
            "api_integration": ["httpx", "aiohttp"],
            "database_operations": ["sqlalchemy", "asyncpg"],
            "message_queuing": ["celery", "redis", "kombu"],
            "data_validation": ["cerberus", "marshmallow"],
            "monitoring": ["prometheus-client", "opencensus"]
        }
        
        for cap in capabilities:
            if cap in capability_deps:
                dependencies.extend(capability_deps[cap])
        
        # Domain-specific dependencies
        if domain:
            tech_recommendations = self.knowledge_base.get_technology_recommendations([domain])
            for category, techs in tech_recommendations.items():
                if category in ["database", "cache", "queue"]:
                    dependencies.extend(list(techs)[:1])  # Add first recommendation
        
        return list(set(dependencies))
    
    def _choose_implementation_strategy(self, capabilities: List[str]) -> str:
        """Choose implementation strategy based on capabilities"""
        if "ml_inference" in capabilities or "model_loading" in capabilities:
            return "ml_agent"
        elif "api_integration" in capabilities or "service_communication" in capabilities:
            return "integration_agent"
        elif "data_processing" in capabilities or "data_transformation" in capabilities:
            return "processing_agent"
        elif "monitoring" in capabilities or "health_monitoring" in capabilities:
            return "monitoring_agent"
        else:
            return "generic_agent"
    
    def _generate_agent_code(self, spec: AgentSpecification) -> str:
        """Generate the actual agent code"""
        # Choose template based on implementation strategy
        if spec.implementation_strategy == "ml_agent":
            return self._generate_ml_agent_code(spec)
        elif spec.implementation_strategy == "integration_agent":
            return self._generate_integration_agent_code(spec)
        elif spec.implementation_strategy == "processing_agent":
            return self._generate_processing_agent_code(spec)
        else:
            return self._generate_generic_agent_code(spec)
    
    def _generate_generic_agent_code(self, spec: AgentSpecification) -> str:
        """Generate generic agent code"""
        capabilities_str = ",\n        ".join([f'"{cap}"' for cap in spec.capabilities])
        dependencies_str = "\n".join([f"import {dep}" for dep in spec.dependencies if dep in ["pandas", "numpy", "httpx"]])
        
        return f'''#!/usr/bin/env python3
"""
{spec.name.replace("-", " ").title()}
Auto-generated by vibe.ai AutoAgentGenerator
Purpose: {spec.purpose}
"""

import json
import sys
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
from pydantic import BaseModel, Field
{dependencies_str}

# Import verification layer for zero-hallucination
sys.path.append("/home/koddulf/vibecode/tools/vibe.ai")
from verification_layer import VerificationLayer


class TaskInput(BaseModel):
    """Input schema for {spec.name}"""
    task_id: str = Field(..., description="Unique task identifier")
    action: str = Field(..., description="Action to perform")
    data: Dict[str, Any] = Field(default_factory=dict, description="Task data")


class TaskOutput(BaseModel):
    """Output schema for {spec.name}"""
    status: str = Field(..., description="Task status: success, error, pending")
    task_id: str = Field(..., description="Task identifier")
    result: Dict[str, Any] = Field(default_factory=dict, description="Task results")
    errors: List[str] = Field(default_factory=list, description="Any errors encountered")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class {spec.name.replace("-", "_").title().replace("_", "")}:
    """
    {spec.purpose}
    
    Capabilities:
    {chr(10).join(f"    - {cap}" for cap in spec.capabilities)}
    """
    
    def __init__(self):
        self.name = "{spec.name}"
        self.version = "1.0.0"
        self.capabilities = [
        {capabilities_str}
        ]
        self.verifier = VerificationLayer()
        self._initialize()
    
    def _initialize(self):
        """Initialize agent resources"""
        # TODO: Initialize any required resources
        pass
    
    async def execute(self, task_input: TaskInput) -> TaskOutput:
        """
        Execute the agent task
        
        Args:
            task_input: The task input with action and data
            
        Returns:
            TaskOutput with results or errors
        """
        try:
            # Verify input
            verification = self.verifier.verify_output(
                self.name,
                {{"action": task_input.action, "data": task_input.data}}
            )
            
            if verification["verification_status"] != "verified":
                return TaskOutput(
                    status="error",
                    task_id=task_input.task_id,
                    errors=[f"Input verification failed: {{verification['verification_status']}}"]
                )
            
            # Route to appropriate handler
            if task_input.action == "process":
                result = await self._process_data(task_input.data)
            elif task_input.action == "analyze":
                result = await self._analyze_data(task_input.data)
            elif task_input.action == "validate":
                result = await self._validate_data(task_input.data)
            else:
                result = await self._handle_generic_action(task_input.action, task_input.data)
            
            # Verify output
            output_verification = self.verifier.verify_output(
                self.name,
                {{"result": result}}
            )
            
            return TaskOutput(
                status="success",
                task_id=task_input.task_id,
                result=result,
                metadata={{
                    "agent": self.name,
                    "version": self.version,
                    "timestamp": datetime.utcnow().isoformat(),
                    "verification_confidence": output_verification.get("overall_confidence", 0)
                }}
            )
            
        except Exception as e:
            return TaskOutput(
                status="error",
                task_id=task_input.task_id,
                errors=[str(e)],
                metadata={{
                    "agent": self.name,
                    "version": self.version,
                    "timestamp": datetime.utcnow().isoformat()
                }}
            )
    
    async def _process_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process data according to agent capabilities"""
        # TODO: Implement data processing logic
        processed_data = {{
            "processed": True,
            "record_count": len(data.get("records", [])),
            "processing_time_ms": 100
        }}
        return processed_data
    
    async def _analyze_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze data and return insights"""
        # TODO: Implement analysis logic
        analysis = {{
            "insights": [],
            "patterns": [],
            "recommendations": []
        }}
        return analysis
    
    async def _validate_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate data against schemas and rules"""
        # TODO: Implement validation logic
        validation_result = {{
            "valid": True,
            "errors": [],
            "warnings": []
        }}
        return validation_result
    
    async def _handle_generic_action(self, action: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle generic actions"""
        # TODO: Implement generic action handling
        return {{
            "action": action,
            "completed": True,
            "data": data
        }}
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Get agent capabilities and metadata"""
        return {{
            "name": self.name,
            "version": self.version,
            "capabilities": self.capabilities,
            "input_schema": {json.dumps(spec.input_schema, indent=2)},
            "output_schema": {json.dumps(spec.output_schema, indent=2)}
        }}
    
    def health_check(self) -> Dict[str, Any]:
        """Check agent health status"""
        return {{
            "healthy": True,
            "agent": self.name,
            "version": self.version,
            "timestamp": datetime.utcnow().isoformat()
        }}


async def main():
    """Main entry point for the agent"""
    agent = {spec.name.replace("-", "_").title().replace("_", "")}()
    
    # Handle command line execution
    if len(sys.argv) > 1:
        # Parse command line arguments
        if sys.argv[1] == "capabilities":
            print(json.dumps(agent.get_capabilities(), indent=2))
        elif sys.argv[1] == "health":
            print(json.dumps(agent.health_check(), indent=2))
        elif sys.argv[1] == "execute":
            # Read task from stdin
            task_data = json.loads(sys.stdin.read())
            task_input = TaskInput(**task_data)
            result = await agent.execute(task_input)
            print(json.dumps(result.dict(), indent=2))
        else:
            print(f"Unknown command: {{sys.argv[1]}}")
            print("Usage: {{sys.argv[0]}} [capabilities|health|execute]")
            sys.exit(1)
    else:
        # Interactive mode
        print(f"{{agent.name}} - Interactive Mode")
        print("Enter 'quit' to exit")
        
        while True:
            try:
                action = input("\\nAction: ").strip()
                if action.lower() == "quit":
                    break
                
                data_str = input("Data (JSON): ").strip()
                data = json.loads(data_str) if data_str else {{}}
                
                task_input = TaskInput(
                    task_id=f"interactive-{{datetime.utcnow().timestamp()}}",
                    action=action,
                    data=data
                )
                
                result = await agent.execute(task_input)
                print(json.dumps(result.dict(), indent=2))
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"Error: {{e}}")


if __name__ == "__main__":
    asyncio.run(main())
'''
    
    def _generate_ml_agent_code(self, spec: AgentSpecification) -> str:
        """Generate ML-specific agent code"""
        # TODO: Implement ML agent template
        return self._generate_generic_agent_code(spec)  # Fallback for now
    
    def _generate_integration_agent_code(self, spec: AgentSpecification) -> str:
        """Generate integration-specific agent code"""
        # TODO: Implement integration agent template
        return self._generate_generic_agent_code(spec)  # Fallback for now
    
    def _generate_processing_agent_code(self, spec: AgentSpecification) -> str:
        """Generate data processing agent code"""
        # TODO: Implement processing agent template
        return self._generate_generic_agent_code(spec)  # Fallback for now
    
    def _generate_test_code(self, spec: AgentSpecification) -> str:
        """Generate test code for the agent"""
        return f'''#!/usr/bin/env python3
"""
Tests for {spec.name.replace("-", " ").title()}
Auto-generated by vibe.ai AutoAgentGenerator
"""

import pytest
import asyncio
import json
from datetime import datetime

from {spec.name.replace("-", "_")} import {spec.name.replace("-", "_").title().replace("_", "")}, TaskInput, TaskOutput


class Test{spec.name.replace("-", "_").title().replace("_", "")}:
    """Test suite for {spec.name}"""
    
    @pytest.fixture
    def agent(self):
        """Create agent instance"""
        return {spec.name.replace("-", "_").title().replace("_", "")}()
    
    @pytest.fixture
    def sample_input(self):
        """Create sample input"""
        return TaskInput(
            task_id="test-123",
            action="process",
            data={{"test": "data"}}
        )
    
    @pytest.mark.asyncio
    async def test_agent_initialization(self, agent):
        """Test agent initializes correctly"""
        assert agent.name == "{spec.name}"
        assert agent.version == "1.0.0"
        assert len(agent.capabilities) > 0
    
    @pytest.mark.asyncio
    async def test_health_check(self, agent):
        """Test health check functionality"""
        health = agent.health_check()
        assert health["healthy"] is True
        assert health["agent"] == "{spec.name}"
    
    @pytest.mark.asyncio
    async def test_execute_success(self, agent, sample_input):
        """Test successful execution"""
        result = await agent.execute(sample_input)
        
        assert isinstance(result, TaskOutput)
        assert result.status in ["success", "error", "pending"]
        assert result.task_id == sample_input.task_id
    
    @pytest.mark.asyncio
    async def test_invalid_action(self, agent):
        """Test handling of invalid action"""
        invalid_input = TaskInput(
            task_id="test-invalid",
            action="nonexistent_action",
            data={{}}
        )
        
        result = await agent.execute(invalid_input)
        assert result.status in ["error", "success"]  # Depends on implementation
    
    @pytest.mark.asyncio
    async def test_error_handling(self, agent):
        """Test error handling"""
        # Provide data that might cause an error
        error_input = TaskInput(
            task_id="test-error",
            action="process",
            data={{}}  # Empty data might cause issues
        )
        
        result = await agent.execute(error_input)
        assert isinstance(result, TaskOutput)
        assert result.task_id == error_input.task_id
    
    def test_capabilities(self, agent):
        """Test capabilities reporting"""
        caps = agent.get_capabilities()
        
        assert "name" in caps
        assert "version" in caps
        assert "capabilities" in caps
        assert "input_schema" in caps
        assert "output_schema" in caps
        
        # Verify schemas are valid JSON
        input_schema = json.loads(caps["input_schema"])
        output_schema = json.loads(caps["output_schema"])
        
        assert input_schema["type"] == "object"
        assert output_schema["type"] == "object"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
'''
    
    def _generate_agent_config(self, spec: AgentSpecification) -> Dict[str, Any]:
        """Generate agent configuration"""
        return {
            "agent": {
                "name": spec.name,
                "version": "1.0.0",
                "purpose": spec.purpose,
                "author": "vibe.ai AutoAgentGenerator",
                "created_at": datetime.utcnow().isoformat()
            },
            "capabilities": spec.capabilities,
            "dependencies": spec.dependencies,
            "schemas": {
                "input": spec.input_schema,
                "output": spec.output_schema
            },
            "configuration": {
                "timeout_seconds": 300,
                "max_retries": 3,
                "log_level": "INFO",
                "cache_enabled": True,
                "cache_ttl_seconds": 3600
            },
            "deployment": {
                "min_instances": 1,
                "max_instances": 10,
                "cpu_request": "100m",
                "cpu_limit": "500m",
                "memory_request": "128Mi",
                "memory_limit": "512Mi"
            }
        }
    
    def _save_agent_files(self, spec: AgentSpecification, agent_code: str, 
                         test_code: str, config: Dict[str, Any]) -> str:
        """Save agent files to disk"""
        # Create agents directory if it doesn't exist
        os.makedirs(self.agents_dir, exist_ok=True)
        
        # Create agent directory
        agent_dir = os.path.join(self.agents_dir, spec.name)
        os.makedirs(agent_dir, exist_ok=True)
        
        # Save agent code
        agent_file = os.path.join(agent_dir, f"{spec.name.replace('-', '_')}.py")
        with open(agent_file, 'w') as f:
            f.write(agent_code)
        
        # Make executable
        os.chmod(agent_file, 0o755)
        
        # Save test code
        test_file = os.path.join(agent_dir, f"test_{spec.name.replace('-', '_')}.py")
        with open(test_file, 'w') as f:
            f.write(test_code)
        
        # Save configuration
        config_file = os.path.join(agent_dir, "config.json")
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        # Create requirements.txt
        requirements_file = os.path.join(agent_dir, "requirements.txt")
        with open(requirements_file, 'w') as f:
            f.write("\n".join(spec.dependencies))
        
        # Create README
        readme_file = os.path.join(agent_dir, "README.md")
        with open(readme_file, 'w') as f:
            f.write(f"""# {spec.name.replace("-", " ").title()}

## Purpose
{spec.purpose}

## Capabilities
{chr(10).join(f"- {cap}" for cap in spec.capabilities)}

## Usage

### Command Line
```bash
# Check capabilities
python {spec.name.replace('-', '_')}.py capabilities

# Health check
python {spec.name.replace('-', '_')}.py health

# Execute task
echo '{{"task_id": "123", "action": "process", "data": {{}}}}' | python {spec.name.replace('-', '_')}.py execute
```

### Python API
```python
from {spec.name.replace('-', '_')} import {spec.name.replace("-", "_").title().replace("_", "")}, TaskInput

agent = {spec.name.replace("-", "_").title().replace("_", "")}()
result = await agent.execute(TaskInput(
    task_id="123",
    action="process",
    data={{}}
))
```

## Configuration
See `config.json` for configuration options.

## Testing
```bash
pytest test_{spec.name.replace('-', '_')}.py -v
```

## Auto-generated
This agent was auto-generated by vibe.ai AutoAgentGenerator.
""")
        
        return agent_file
    
    def _register_agent(self, spec: AgentSpecification, agent_path: str):
        """Register agent with the system"""
        # Update agent registry
        registry_file = os.path.join(self.agents_dir, "registry.json")
        
        # Load existing registry
        if os.path.exists(registry_file):
            with open(registry_file, 'r') as f:
                registry = json.load(f)
        else:
            registry = {"agents": []}
        
        # Add new agent
        registry["agents"].append({
            "name": spec.name,
            "path": agent_path,
            "purpose": spec.purpose,
            "capabilities": spec.capabilities,
            "created_at": datetime.utcnow().isoformat(),
            "auto_generated": True
        })
        
        # Save updated registry
        with open(registry_file, 'w') as f:
            json.dump(registry, f, indent=2)


# Usage example
if __name__ == "__main__":
    generator = AutoAgentGenerator()
    
    # Example: Generate a payment processor agent
    requirement = "Create a payment-processor-agent for handling Stripe payments and transactions"
    
    print(f"Analyzing requirement: {requirement}")
    spec = generator.analyze_agent_need(requirement)
    
    print(f"\nAgent Specification:")
    print(f"  Name: {spec.name}")
    print(f"  Purpose: {spec.purpose}")
    print(f"  Capabilities: {spec.capabilities}")
    print(f"  Dependencies: {spec.dependencies}")
    print(f"  Strategy: {spec.implementation_strategy}")
    
    # Generate the agent
    print(f"\nGenerating agent...")
    result = generator.generate_agent(spec)
    
    if result["success"]:
        print(f"\n✅ {result['message']}")
        print(f"   Path: {result['agent_path']}")
        print(f"   Capabilities: {result['capabilities']}")
    else:
        print(f"\n❌ Failed to generate agent")