#!/usr/bin/env python3
"""
Fix the agent workflow to use actual agent names
"""

import json
import os

# The workflow mapping in master-agent.py uses generic names
# But the actual agents have specific names. Let's create a mapping file.

agent_mapping = {
    "planning": "planning-analysis-agent",
    "execution": "universal-execution-agent", 
    "quality": "quality-git-agent",
    "coordinator": "agent-coordinator",
    "repo": "repo-manager-agent",
    "complexity": "task-complexity-agent",
    "intelligent": "intelligent-task-agent"
}

# Create a configuration file that master-agent can use
config = {
    "agent_aliases": agent_mapping,
    "workflows": {
        "analyze": ["planning-analysis-agent"],
        "execute": ["universal-execution-agent"],
        "quality": ["quality-git-agent"],
        "full-dev": ["planning-analysis-agent", "universal-execution-agent", "quality-git-agent"],
        "planning": ["planning-analysis-agent", "agent-coordinator"],
        "quick-fix": ["universal-execution-agent", "quality-git-agent"]
    },
    "default_workflow": "full-dev"
}

# Save configuration
config_path = "agent_workflow_config.json"
with open(config_path, 'w') as f:
    json.dump(config, f, indent=2)

print(f"✅ Created agent workflow configuration: {config_path}")
print("\nAgent name mappings:")
for generic, specific in agent_mapping.items():
    print(f"  {generic} → {specific}")

print("\nWorkflow definitions:")
for workflow, agents in config["workflows"].items():
    print(f"  {workflow}: {' → '.join(agents)}")

# Now let's patch the master-agent.py to use this config
print("\n🔧 Next steps to fix master-agent.py:")
print("1. Load agent_workflow_config.json in master-agent.py")
print("2. Map generic names to specific agent names")
print("3. Update run_agent method to resolve aliases")