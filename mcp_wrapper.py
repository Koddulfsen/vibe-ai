#!/usr/bin/env python3
"""
MCP Wrapper - Convert any Python agent to an MCP server
This wraps existing vibe.ai agents to work as MCP servers
"""

import json
import sys
import subprocess
import os
from typing import Dict, Any, List
from pathlib import Path

class MCPAgentWrapper:
    """Wraps existing Python agents as MCP servers"""
    
    def __init__(self, agent_name: str, agent_path: str):
        self.agent_name = agent_name
        self.agent_path = Path(agent_path)
        self.agent_dir = self.agent_path.parent
        
    def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle MCP protocol requests"""
        method = request.get("method", "")
        
        if method == "initialize":
            return {
                "protocolVersion": "0.1.0",
                "serverInfo": {
                    "name": f"vibe-{self.agent_name}",
                    "version": "1.0.0"
                }
            }
        
        elif method == "tools/list":
            return self.list_tools()
        
        elif method == "tools/call":
            return self.call_tool(request.get("params", {}))
        
        return {"error": {"code": -32601, "message": "Method not found"}}
    
    def list_tools(self) -> Dict[str, Any]:
        """List available tools based on agent type"""
        tools = []
        
        if "planning" in self.agent_name:
            tools.extend([
                {
                    "name": "analyze_project",
                    "description": "Analyze project complexity and structure",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "path": {"type": "string", "description": "Project path"},
                            "deep": {"type": "boolean", "description": "Deep analysis"}
                        },
                        "required": ["path"]
                    }
                },
                {
                    "name": "create_tasks",
                    "description": "Generate tasks from requirements",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "requirements": {"type": "string"},
                            "complexity_threshold": {"type": "number"}
                        },
                        "required": ["requirements"]
                    }
                }
            ])
        
        elif "execution" in self.agent_name or "dev" in self.agent_name:
            tools.extend([
                {
                    "name": "execute_task",
                    "description": "Execute a development task",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "task_id": {"type": "string"},
                            "task_description": {"type": "string"}
                        },
                        "required": ["task_description"]
                    }
                },
                {
                    "name": "create_file",
                    "description": "Create a new file with content",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "path": {"type": "string"},
                            "content": {"type": "string"},
                            "file_type": {"type": "string"}
                        },
                        "required": ["path", "content"]
                    }
                }
            ])
        
        elif "quality" in self.agent_name:
            tools.extend([
                {
                    "name": "run_tests",
                    "description": "Run project tests",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "test_type": {"type": "string", "enum": ["unit", "integration", "all"]},
                            "coverage": {"type": "boolean"}
                        }
                    }
                },
                {
                    "name": "check_quality",
                    "description": "Check code quality",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "path": {"type": "string"},
                            "fix": {"type": "boolean"}
                        }
                    }
                }
            ])
        
        return {"tools": tools}
    
    def call_tool(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute tool by calling underlying agent"""
        tool_name = params.get("name", "")
        arguments = params.get("arguments", {})
        
        try:
            # Map tool calls to agent commands
            if tool_name == "analyze_project":
                cmd = [
                    "python3", str(self.agent_path),
                    "--analyze",
                    "--path", arguments.get("path", "."),
                    "--output-format", "json"
                ]
                if arguments.get("deep"):
                    cmd.append("--deep")
            
            elif tool_name == "execute_task":
                cmd = [
                    "python3", str(self.agent_path),
                    "--execute",
                    "--task", arguments.get("task_description", ""),
                    "--output-format", "json"
                ]
            
            elif tool_name == "create_file":
                # Direct implementation for file creation
                path = Path(arguments["path"])
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(arguments["content"])
                return {
                    "content": [{
                        "type": "text",
                        "text": f"✅ Created {path}"
                    }]
                }
            
            else:
                return {
                    "error": {
                        "code": -32602,
                        "message": f"Unknown tool: {tool_name}"
                    }
                }
            
            # Execute command
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=self.agent_dir
            )
            
            # Format response
            output = result.stdout if result.returncode == 0 else result.stderr
            
            # Try to parse as JSON first
            try:
                data = json.loads(output)
                return {
                    "content": [{
                        "type": "text",
                        "text": json.dumps(data, indent=2)
                    }]
                }
            except:
                # Return as plain text
                return {
                    "content": [{
                        "type": "text",
                        "text": output
                    }]
                }
            
        except Exception as e:
            return {
                "error": {
                    "code": -32603,
                    "message": f"Execution error: {str(e)}"
                }
            }
    
    def run(self):
        """Run the MCP server loop"""
        while True:
            try:
                line = sys.stdin.readline()
                if not line:
                    break
                
                # Parse JSON-RPC request
                request = json.loads(line.strip())
                
                # Handle request
                result = self.handle_request(request)
                
                # Send response
                response = {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "result": result
                }
                
                print(json.dumps(response))
                sys.stdout.flush()
                
            except json.JSONDecodeError as e:
                error_response = {
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {
                        "code": -32700,
                        "message": "Parse error",
                        "data": str(e)
                    }
                }
                print(json.dumps(error_response))
                sys.stdout.flush()
            
            except Exception as e:
                error_response = {
                    "jsonrpc": "2.0",
                    "id": request.get("id") if 'request' in locals() else None,
                    "error": {
                        "code": -32603,
                        "message": "Internal error",
                        "data": str(e)
                    }
                }
                print(json.dumps(error_response))
                sys.stdout.flush()


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="MCP wrapper for vibe.ai agents")
    parser.add_argument("--agent", required=True, help="Agent name (planning, execution, quality)")
    parser.add_argument("--agent-path", required=True, help="Path to agent Python script")
    
    args = parser.parse_args()
    
    wrapper = MCPAgentWrapper(args.agent, args.agent_path)
    wrapper.run()


if __name__ == "__main__":
    main()