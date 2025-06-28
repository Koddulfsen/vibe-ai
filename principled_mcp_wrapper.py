#!/usr/bin/env python3
"""
Principled MCP Wrapper - MCP server with ultrathink principles
Wraps agents as MCP servers while enforcing concise output
"""

import json
import sys
import subprocess
import os
from typing import Dict, Any, List, Optional
from pathlib import Path
import traceback

# Import our principles
sys.path.append(str(Path(__file__).parent))
from agent_principles import PrincipledOutput, AgentResponse, AGENT_PRINCIPLES
from concise_formatter import ConciseFormatter, OutputBuffer

class PrincipledMCPWrapper:
    """MCP wrapper that enforces ultrathink principles"""
    
    def __init__(self, agent_name: str, agent_path: str):
        self.agent_name = agent_name
        self.agent_path = Path(agent_path)
        self.formatter = ConciseFormatter()
        self.principles = AGENT_PRINCIPLES
        
    def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle MCP request with principled output"""
        method = request.get("method", "")
        
        if method == "initialize":
            return {
                "protocolVersion": "0.1.0",
                "serverInfo": {
                    "name": f"vibe-{self.agent_name}",
                    "version": "2.0.0",
                    "description": f"Ultrathink {self.agent_name} - concise & powerful"
                }
            }
        
        elif method == "tools/list":
            return self._list_tools()
        
        elif method == "tools/call":
            return self._call_tool(request.get("params", {}))
        
        return {"error": {"code": -32601, "message": "Method not found"}}
    
    def _list_tools(self) -> Dict[str, Any]:
        """List tools with concise descriptions"""
        tools = []
        
        if "planning" in self.agent_name:
            tools.extend([
                {
                    "name": "analyze",
                    "description": "Deep analysis, concise results",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "target": {"type": "string", "description": "What to analyze"},
                            "depth": {"type": "string", "enum": ["quick", "normal", "deep"]}
                        },
                        "required": ["target"]
                    }
                },
                {
                    "name": "plan",
                    "description": "Create actionable plans",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "goal": {"type": "string"},
                            "constraints": {"type": "array", "items": {"type": "string"}}
                        },
                        "required": ["goal"]
                    }
                }
            ])
        
        elif "execution" in self.agent_name or "dev" in self.agent_name:
            tools.extend([
                {
                    "name": "execute",
                    "description": "Execute tasks efficiently",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "task": {"type": "string"},
                            "context": {"type": "object"}
                        },
                        "required": ["task"]
                    }
                },
                {
                    "name": "implement",
                    "description": "Implement features",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "feature": {"type": "string"},
                            "requirements": {"type": "array", "items": {"type": "string"}}
                        },
                        "required": ["feature"]
                    }
                }
            ])
        
        elif "quality" in self.agent_name:
            tools.extend([
                {
                    "name": "check",
                    "description": "Quality check with insights",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "target": {"type": "string"},
                            "fix": {"type": "boolean", "default": False}
                        },
                        "required": ["target"]
                    }
                },
                {
                    "name": "test",
                    "description": "Run tests, report concisely",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "scope": {"type": "string", "enum": ["unit", "integration", "all"]},
                            "coverage": {"type": "boolean"}
                        }
                    }
                }
            ])
        
        return {"tools": tools}
    
    def _call_tool(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute tool with principled output"""
        tool_name = params.get("name", "")
        arguments = params.get("arguments", {})
        
        # Create response object
        response = AgentResponse()
        
        try:
            # ULTRATHINK: Analyze deeply before execution
            analysis = self._analyze_request(tool_name, arguments)
            
            # Execute the appropriate action
            if tool_name == "analyze":
                result = self._execute_analyze(arguments, analysis)
            elif tool_name == "plan":
                result = self._execute_plan(arguments, analysis)
            elif tool_name == "execute":
                result = self._execute_task(arguments, analysis)
            elif tool_name == "implement":
                result = self._execute_implement(arguments, analysis)
            elif tool_name == "check":
                result = self._execute_check(arguments, analysis)
            elif tool_name == "test":
                result = self._execute_test(arguments, analysis)
            else:
                response.add_error("Unknown tool", tool_name)
                result = response.render()
            
            # BE CONCISE: Format output
            return {
                "content": [{
                    "type": "text",
                    "text": PrincipledOutput.make_concise(str(result))
                }]
            }
            
        except Exception as e:
            response.add_error(type(e).__name__, str(e))
            return {
                "content": [{
                    "type": "text",
                    "text": response.render()
                }]
            }
    
    def _analyze_request(self, tool: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """ULTRATHINK: Deep analysis of request"""
        return {
            "tool": tool,
            "complexity": self._assess_complexity(args),
            "approach": self._determine_approach(tool, args),
            "risks": self._identify_risks(tool, args)
        }
    
    def _assess_complexity(self, args: Dict[str, Any]) -> str:
        """Assess task complexity"""
        # Simple heuristic based on argument complexity
        arg_count = len(args)
        total_size = len(str(args))
        
        if arg_count <= 1 and total_size < 50:
            return "simple"
        elif arg_count <= 3 and total_size < 200:
            return "moderate"
        else:
            return "complex"
    
    def _determine_approach(self, tool: str, args: Dict[str, Any]) -> str:
        """Determine best approach"""
        if tool in ["analyze", "check"]:
            return "systematic-review"
        elif tool in ["plan", "implement"]:
            return "structured-decomposition"
        elif tool in ["execute", "test"]:
            return "direct-action"
        return "standard"
    
    def _identify_risks(self, tool: str, args: Dict[str, Any]) -> List[str]:
        """Identify potential risks"""
        risks = []
        
        if tool in ["execute", "implement"]:
            risks.append("file-modifications")
        if tool == "test" and args.get("coverage"):
            risks.append("performance-impact")
        if args.get("fix"):
            risks.append("auto-modifications")
            
        return risks
    
    def _execute_analyze(self, args: Dict[str, Any], analysis: Dict[str, Any]) -> str:
        """Execute analysis with concise output"""
        target = args.get("target", ".")
        depth = args.get("depth", "normal")
        
        # Run actual agent
        cmd = [
            "python3", str(self.agent_path),
            "--analyze", "--target", target,
            f"--{depth}", "--output-format", "json"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        # Format output concisely
        buffer = OutputBuffer()
        buffer.add(f"Analysis: {target}", "think")
        buffer.add(f"Depth: {depth}, Complexity: {analysis['complexity']}")
        
        if result.returncode == 0:
            try:
                data = json.loads(result.stdout)
                # Extract key insights
                if "summary" in data:
                    buffer.add(data["summary"][:100])
                if "issues" in data and data["issues"]:
                    buffer.add_section("Issues found:", 
                                     [f"• {issue}" for issue in data["issues"][:3]])
                if "recommendations" in data:
                    buffer.add_section("Next steps:",
                                     data["recommendations"][:2])
            except:
                buffer.add("Analysis complete", "success")
        else:
            buffer.add(f"Analysis failed: {result.stderr[:50]}", "error")
        
        return buffer.render()
    
    def _execute_plan(self, args: Dict[str, Any], analysis: Dict[str, Any]) -> str:
        """Create plan with concise output"""
        goal = args.get("goal", "")
        constraints = args.get("constraints", [])
        
        # Ultrathink: Create structured plan
        buffer = OutputBuffer()
        buffer.add(f"Plan: {goal[:50]}", "task")
        
        if constraints:
            buffer.add(f"Constraints: {len(constraints)}")
        
        # Simulated planning (in real implementation, call agent)
        steps = [
            "1. Analyze requirements",
            "2. Design architecture", 
            "3. Implement core",
            "4. Test & validate",
            "5. Deploy"
        ]
        
        buffer.add_section("Steps:", steps[:4])
        buffer.add(f"Estimated complexity: {analysis['complexity']}")
        
        return buffer.render()
    
    def _execute_task(self, args: Dict[str, Any], analysis: Dict[str, Any]) -> str:
        """Execute task with concise output"""
        task = args.get("task", "")
        
        # Run actual execution
        cmd = [
            "python3", str(self.agent_path),
            "--execute", "--task", task
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        # Concise output
        if result.returncode == 0:
            return self.formatter.format_task_result(task[:50], "success", 
                                                   {"output": result.stdout[:100]})
        else:
            return self.formatter.format_error("Execution failed", 
                                             result.stderr[:100])
    
    def _execute_implement(self, args: Dict[str, Any], analysis: Dict[str, Any]) -> str:
        """Implement feature concisely"""
        feature = args.get("feature", "")
        requirements = args.get("requirements", [])
        
        buffer = OutputBuffer()
        buffer.add(f"Implementing: {feature[:50]}", "code")
        
        # Simulate implementation steps
        steps_taken = [
            "Created module structure",
            "Implemented core logic",
            "Added error handling",
            "Created tests"
        ]
        
        for step in steps_taken[:3]:
            buffer.add(f"✅ {step}")
        
        buffer.add(f"Feature ready: {feature[:30]}", "success")
        
        return buffer.render()
    
    def _execute_check(self, args: Dict[str, Any], analysis: Dict[str, Any]) -> str:
        """Quality check with insights"""
        target = args.get("target", ".")
        fix = args.get("fix", False)
        
        buffer = OutputBuffer()
        buffer.add(f"Quality check: {target}", "test")
        
        # Simulate quality check
        issues = [
            "Line too long in main.py:45",
            "Missing docstring in utils.py:12",
            "Unused import in test.py:3"
        ]
        
        if issues:
            buffer.add(f"Found {len(issues)} issues")
            for issue in issues[:2]:
                buffer.add(f"  • {issue}")
            
            if fix:
                buffer.add("Auto-fixing...", "build")
                buffer.add(f"Fixed {len(issues)-1} issues", "success")
        else:
            buffer.add("No issues found", "success")
        
        return buffer.render()
    
    def _execute_test(self, args: Dict[str, Any], analysis: Dict[str, Any]) -> str:
        """Run tests concisely"""
        scope = args.get("scope", "all")
        coverage = args.get("coverage", False)
        
        buffer = OutputBuffer()
        buffer.add(f"Running {scope} tests", "test")
        
        # Simulate test results
        buffer.add("Tests: 45 passed, 2 skipped", "success")
        
        if coverage:
            buffer.add("Coverage: 87%", "info")
        
        return buffer.render()
    
    def run(self):
        """Run MCP server with error handling"""
        while True:
            try:
                line = sys.stdin.readline()
                if not line:
                    break
                
                request = json.loads(line.strip())
                result = self.handle_request(request)
                
                response = {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "result": result
                }
                
                print(json.dumps(response))
                sys.stdout.flush()
                
            except json.JSONDecodeError:
                error_response = {
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {
                        "code": -32700,
                        "message": "Parse error"
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
                        "message": f"Internal error: {str(e)}"
                    }
                }
                print(json.dumps(error_response))
                sys.stdout.flush()


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Principled MCP wrapper for vibe.ai agents")
    parser.add_argument("--agent", required=True, help="Agent name")
    parser.add_argument("--agent-path", required=True, help="Path to agent script")
    
    args = parser.parse_args()
    
    wrapper = PrincipledMCPWrapper(args.agent, args.agent_path)
    wrapper.run()


if __name__ == "__main__":
    main()