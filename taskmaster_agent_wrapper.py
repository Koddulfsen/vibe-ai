#!/usr/bin/env python3
"""
TaskMaster Agent Wrapper
Provides integration between vibe.ai agents and TaskMaster system
"""

import os
import sys
import json
import argparse
from typing import Dict, Any, Optional

class TaskMasterAgentWrapper:
    """Wrapper to make agents work with TaskMaster"""
    
    def __init__(self):
        self.taskmaster_dir = os.path.join(os.path.dirname(__file__), ".taskmaster")
        self.tasks_file = os.path.join(self.taskmaster_dir, "tasks", "tasks.json")
    
    def get_task_context(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get task context from TaskMaster"""
        if not os.path.exists(self.tasks_file):
            return None
        
        try:
            with open(self.tasks_file, 'r') as f:
                tasks_data = json.load(f)
            
            for task in tasks_data.get("tasks", []):
                if task["id"] == task_id:
                    return task
            
            return None
        except Exception as e:
            print(f"Error reading task: {e}", file=sys.stderr)
            return None
    
    def create_agent_input(self, task: Dict[str, Any], agent_type: str) -> Dict[str, Any]:
        """Create appropriate input for agent based on task"""
        agent_input = {
            "task_id": task["id"],
            "description": task["description"],
            "title": task["title"],
            "type": agent_type,
            "context": task.get("analysis", {})
        }
        
        # Add agent-specific context
        if agent_type == "planning":
            agent_input["action"] = "analyze"
            agent_input["requirements"] = task.get("requirements", [])
        elif agent_type == "execution":
            agent_input["action"] = "implement"
            agent_input["architecture"] = task.get("architecture", "monolithic")
        elif agent_type == "quality":
            agent_input["action"] = "verify"
            agent_input["test_strategy"] = task.get("testStrategy", "unit and integration tests")
        
        return agent_input
    
    def wrap_agent_call(self, agent_name: str, task_id: Optional[str] = None) -> int:
        """Wrap agent call with TaskMaster context"""
        # Get task context if provided
        task_context = None
        if task_id:
            task_context = self.get_task_context(task_id)
            if not task_context:
                print(f"Warning: Task {task_id} not found in TaskMaster")
        
        # Determine agent type
        agent_type = "execution"  # default
        if "planning" in agent_name or "analysis" in agent_name:
            agent_type = "planning"
        elif "quality" in agent_name or "test" in agent_name:
            agent_type = "quality"
        
        # Create agent input
        if task_context:
            agent_input = self.create_agent_input(task_context, agent_type)
            # Set environment variable for agent
            os.environ["TASKMASTER_CONTEXT"] = json.dumps(agent_input)
            os.environ["TASKMASTER_TASK_ID"] = task_id
        
        # Import and run the agent
        agent_module = agent_name.replace("-", "_").replace(".py", "")
        
        try:
            # Add agents directory to path
            agents_dir = os.path.join(os.path.dirname(__file__), "agents")
            if agents_dir not in sys.path:
                sys.path.insert(0, agents_dir)
            
            # Dynamic import
            agent = __import__(agent_module)
            
            # Check if agent has a main function
            if hasattr(agent, 'main'):
                return agent.main()
            else:
                print(f"Agent {agent_name} does not have a main() function")
                return 1
                
        except ImportError as e:
            print(f"Error importing agent {agent_name}: {e}")
            return 1
        except Exception as e:
            print(f"Error running agent {agent_name}: {e}")
            return 1

def main():
    """Main entry point for wrapper"""
    parser = argparse.ArgumentParser(description="TaskMaster Agent Wrapper")
    parser.add_argument("agent", help="Agent name to run")
    parser.add_argument("--task-id", help="TaskMaster task ID")
    parser.add_argument("--debug", action="store_true", help="Enable debug output")
    
    args = parser.parse_args()
    
    wrapper = TaskMasterAgentWrapper()
    
    if args.debug:
        print(f"Running agent: {args.agent}")
        print(f"Task ID: {args.task_id}")
    
    return wrapper.wrap_agent_call(args.agent, args.task_id)

if __name__ == "__main__":
    sys.exit(main())