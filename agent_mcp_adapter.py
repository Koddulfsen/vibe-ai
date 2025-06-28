#!/usr/bin/env python3
"""
Agent MCP Adapter - Add MCP support to any agent class
"""

import json
import sys
from typing import Dict, Any, Callable, List

class MCPAdapter:
    """Add MCP protocol support to any agent"""
    
    def __init__(self, agent_instance, tool_mappings: Dict[str, Callable]):
        self.agent = agent_instance
        self.tool_mappings = tool_mappings
        
    def create_tool_definition(self, name: str, description: str, 
                             parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Create MCP tool definition"""
        return {
            "name": name,
            "description": description,
            "inputSchema": {
                "type": "object",
                "properties": parameters,
                "required": list(parameters.keys())
            }
        }
    
    def run_mcp_server(self):
        """Run as MCP server"""
        while True:
            try:
                line = sys.stdin.readline()
                if not line:
                    break
                    
                request = json.loads(line.strip())
                method = request.get("method", "")
                
                if method == "initialize":
                    response = {
                        "protocolVersion": "0.1.0",
                        "serverInfo": {
                            "name": self.agent.__class__.__name__,
                            "version": "1.0.0"
                        }
                    }
                
                elif method == "tools/list":
                    tools = []
                    for tool_name, (func, description, params) in self.tool_mappings.items():
                        tools.append(self.create_tool_definition(tool_name, description, params))
                    response = {"tools": tools}
                
                elif method == "tools/call":
                    tool_name = request["params"]["name"]
                    arguments = request["params"]["arguments"]
                    
                    if tool_name in self.tool_mappings:
                        func, _, _ = self.tool_mappings[tool_name]
                        result = func(**arguments)
                        response = {
                            "content": [{
                                "type": "text",
                                "text": str(result)
                            }]
                        }
                    else:
                        response = {"error": {"code": -32602, "message": "Unknown tool"}}
                
                else:
                    response = {"error": {"code": -32601, "message": "Method not found"}}
                
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
                    "id": request.get("id") if 'request' in locals() else None,
                    "error": {
                        "code": -32603,
                        "message": str(e)
                    }
                }))
                sys.stdout.flush()


# Example usage:
if __name__ == "__main__":
    # Example agent class
    class MyAgent:
        def analyze(self, code: str) -> str:
            return f"Analysis complete: {len(code)} characters"
        
        def execute(self, task: str) -> str:
            return f"Executed: {task}"
    
    # Create agent instance
    agent = MyAgent()
    
    # Define tool mappings
    tools = {
        "analyze_code": (
            agent.analyze,
            "Analyze code for issues",
            {"code": {"type": "string", "description": "Code to analyze"}}
        ),
        "execute_task": (
            agent.execute,
            "Execute a development task",
            {"task": {"type": "string", "description": "Task description"}}
        )
    }
    
    # Run as MCP server
    adapter = MCPAdapter(agent, tools)
    adapter.run_mcp_server()