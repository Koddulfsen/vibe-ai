#!/usr/bin/env python3
"""
Example MCP Server - Custom Sub-Agent for Claude Code
This shows how to create a custom agent that Claude can use
"""

import json
import sys
from typing import Dict, Any

class CustomMCPAgent:
    """A simple MCP server that acts as a sub-agent"""
    
    def __init__(self):
        self.name = "custom-agent"
        self.capabilities = ["analyze", "plan", "execute"]
    
    def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle incoming requests from Claude"""
        method = request.get("method", "")
        
        if method == "tools/list":
            return {
                "tools": [
                    {
                        "name": "analyze_task",
                        "description": "Analyze a task and provide insights",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "task": {"type": "string"}
                            }
                        }
                    },
                    {
                        "name": "create_plan", 
                        "description": "Create an execution plan",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "requirements": {"type": "string"}
                            }
                        }
                    }
                ]
            }
        
        elif method == "tools/call":
            tool_name = request.get("params", {}).get("name", "")
            arguments = request.get("params", {}).get("arguments", {})
            
            if tool_name == "analyze_task":
                return self.analyze_task(arguments.get("task", ""))
            elif tool_name == "create_plan":
                return self.create_plan(arguments.get("requirements", ""))
        
        return {"error": "Unknown method"}
    
    def analyze_task(self, task: str) -> Dict[str, Any]:
        """Analyze a task - ultrathink, be concise, no bloat"""
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"Task Analysis:\n• Type: Development\n• Complexity: Medium\n• Time: 2-3 hours"
                }
            ]
        }
    
    def create_plan(self, requirements: str) -> Dict[str, Any]:
        """Create execution plan - concise and actionable"""
        return {
            "content": [
                {
                    "type": "text", 
                    "text": f"Execution Plan:\n1. Setup environment\n2. Implement core logic\n3. Add tests\n4. Deploy"
                }
            ]
        }
    
    def run(self):
        """Run the MCP server"""
        while True:
            try:
                line = sys.stdin.readline()
                if not line:
                    break
                
                request = json.loads(line)
                response = self.handle_request(request)
                
                # Send response
                print(json.dumps({
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "result": response
                }))
                sys.stdout.flush()
                
            except Exception as e:
                print(json.dumps({
                    "jsonrpc": "2.0",
                    "id": request.get("id", 0),
                    "error": {
                        "code": -32603,
                        "message": str(e)
                    }
                }))
                sys.stdout.flush()

if __name__ == "__main__":
    agent = CustomMCPAgent()
    agent.run()