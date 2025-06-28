#!/usr/bin/env python3
"""
Session Integration for vibe.ai
Integrates session tracking into all vibe.ai tools
"""

import functools
import inspect
import os
import sys
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

# Import session manager
from session_manager import get_session_manager, EventType


class SessionIntegration:
    """Provides decorators and utilities for session integration"""
    
    @staticmethod
    def track_tool_execution(tool_name: str):
        """Decorator to track tool execution"""
        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                session = get_session_manager()
                
                # Track start
                session.add_event(
                    EventType.AGENT_EXECUTED,
                    f"Starting {tool_name}",
                    {
                        "tool": tool_name,
                        "function": func.__name__,
                        "args": str(args)[:200],
                        "kwargs": str(kwargs)[:200]
                    },
                    tags=[tool_name, "tool_execution"]
                )
                
                try:
                    # Execute function
                    result = func(*args, **kwargs)
                    
                    # Track success
                    session.add_event(
                        EventType.AGENT_EXECUTED,
                        f"Completed {tool_name}",
                        {
                            "tool": tool_name,
                            "function": func.__name__,
                            "success": True,
                            "result_type": type(result).__name__
                        }
                    )
                    
                    return result
                    
                except Exception as e:
                    # Track error
                    session.add_event(
                        EventType.ERROR_OCCURRED,
                        f"Error in {tool_name}",
                        {
                            "tool": tool_name,
                            "function": func.__name__,
                            "error": str(e),
                            "error_type": type(e).__name__
                        },
                        tags=[tool_name, "error"]
                    )
                    raise
            
            return wrapper
        return decorator
    
    @staticmethod
    def track_file_operation(operation: str = "modified"):
        """Decorator to track file operations"""
        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                session = get_session_manager()
                
                # Try to extract file path from args
                file_path = None
                sig = inspect.signature(func)
                params = list(sig.parameters.keys())
                
                # Look for common file path parameter names
                for i, param in enumerate(params):
                    if param in ["file_path", "path", "filename"] and i < len(args):
                        file_path = args[i]
                        break
                
                # Also check kwargs
                if not file_path:
                    for key in ["file_path", "path", "filename"]:
                        if key in kwargs:
                            file_path = kwargs[key]
                            break
                
                # Execute function
                result = func(*args, **kwargs)
                
                # Track file operation
                if file_path:
                    session.track_file_modification(str(file_path), operation)
                
                return result
            
            return wrapper
        return decorator
    
    @staticmethod
    def track_command(func: Callable) -> Callable:
        """Decorator to track command execution"""
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            session = get_session_manager()
            
            # Extract command from args
            command = None
            if args:
                command = str(args[0])
            elif "command" in kwargs:
                command = kwargs["command"]
            
            # Execute
            result = func(*args, **kwargs)
            
            # Track command
            if command:
                output = None
                error = None
                return_code = None
                
                # Try to extract from result
                if isinstance(result, dict):
                    output = result.get("output", result.get("stdout"))
                    error = result.get("error", result.get("stderr"))
                    return_code = result.get("return_code", result.get("returncode"))
                elif isinstance(result, tuple) and len(result) >= 2:
                    output, error = result[:2]
                    if len(result) >= 3:
                        return_code = result[2]
                
                session.track_command(command, output, error, return_code)
            
            return result
        
        return wrapper
    
    @staticmethod
    def track_api_call(api_name: str):
        """Decorator to track API calls"""
        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                session = get_session_manager()
                
                # Build endpoint from function name and args
                endpoint = func.__name__
                if args:
                    endpoint += f"/{args[0]}" if len(str(args[0])) < 50 else ""
                
                try:
                    # Execute
                    result = func(*args, **kwargs)
                    
                    # Track API call
                    session.track_api_call(
                        api_name,
                        endpoint,
                        params=kwargs,
                        result=result
                    )
                    
                    return result
                    
                except Exception as e:
                    # Track failed API call
                    session.track_api_call(
                        api_name,
                        endpoint,
                        params=kwargs,
                        error=str(e)
                    )
                    raise
            
            return wrapper
        return decorator
    
    @staticmethod
    def track_decision(decision_type: str):
        """Decorator to track decisions"""
        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                session = get_session_manager()
                
                # Execute function
                result = func(*args, **kwargs)
                
                # Try to extract decision info from result
                if isinstance(result, dict):
                    session.track_decision(
                        decision_type,
                        result.get("description", func.__name__),
                        options=result.get("options"),
                        chosen=result.get("chosen", str(result)),
                        reasoning=result.get("reasoning")
                    )
                else:
                    session.track_decision(
                        decision_type,
                        func.__name__,
                        chosen=str(result)
                    )
                
                return result
            
            return wrapper
        return decorator


def integrate_with_existing_tools():
    """Patch existing vibe.ai tools with session tracking"""
    
    # Import tools
    try:
        import idea_to_solution_engine
        import vibe_perfect
        import enhanced_taskmaster_bridge
        import simple_solution_generator
        import agent_based_solution_engine
        
        # Patch idea_to_solution_engine
        if hasattr(idea_to_solution_engine, 'IdeaToSolutionEngine'):
            engine_class = idea_to_solution_engine.IdeaToSolutionEngine
            
            # Track PRD creation
            original_create_prd = engine_class.create_prd_from_refinement
            @SessionIntegration.track_file_operation("created")
            def patched_create_prd(self, refinement):
                result = original_create_prd(refinement)
                # Also track as PRD event
                get_session_manager().add_event(
                    EventType.PRD_GENERATED,
                    "Generated PRD from refined idea",
                    {"prd_path": result, "idea": refinement.refined_idea},
                    tags=["prd", "generation"]
                )
                return result
            engine_class.create_prd_from_refinement = patched_create_prd
        
        # Patch vibe_perfect
        if hasattr(vibe_perfect, 'VibePerfect'):
            perfect_class = vibe_perfect.VibePerfect
            
            # Track workflow execution
            original_run = perfect_class.run_perfect_workflow
            @SessionIntegration.track_tool_execution("vibe_perfect")
            def patched_run(self, idea):
                get_session_manager().add_context("initial_idea", idea)
                return original_run(idea)
            perfect_class.run_perfect_workflow = patched_run
        
        # Patch enhanced_taskmaster_bridge
        if hasattr(enhanced_taskmaster_bridge, 'EnhancedTaskMasterBridge'):
            bridge_class = enhanced_taskmaster_bridge.EnhancedTaskMasterBridge
            
            # Track task processing
            original_process = bridge_class.process_task
            @SessionIntegration.track_tool_execution("taskmaster")
            def patched_process(self, task_description, additional_context=None, auto_execute=None):
                result = original_process(task_description, additional_context, auto_execute)
                
                # Track task creation
                if isinstance(result, dict) and "prd" in result:
                    get_session_manager().add_event(
                        EventType.TASK_CREATED,
                        "Created tasks from PRD",
                        {"complexity": result.get("complexity_score", 0)},
                        tags=["taskmaster", "task_creation"]
                    )
                
                return result
            bridge_class.process_task = patched_process
        
        print("✅ Session tracking integrated with existing tools")
        
    except ImportError as e:
        print(f"⚠️  Could not integrate with all tools: {e}")


def create_session_aware_wrapper(tool_function: Callable, tool_name: str) -> Callable:
    """Create a session-aware wrapper for any tool function"""
    
    @functools.wraps(tool_function)
    @SessionIntegration.track_tool_execution(tool_name)
    def wrapper(*args, **kwargs):
        return tool_function(*args, **kwargs)
    
    return wrapper


def monkey_patch_subprocess():
    """Monkey patch subprocess to track all commands"""
    import subprocess
    
    # Save original
    original_run = subprocess.run
    original_popen = subprocess.Popen
    
    @SessionIntegration.track_command
    def patched_run(cmd, *args, **kwargs):
        return original_run(cmd, *args, **kwargs)
    
    class PatchedPopen(original_popen):
        def __init__(self, cmd, *args, **kwargs):
            super().__init__(cmd, *args, **kwargs)
            
            # Track command start
            get_session_manager().track_command(
                str(cmd) if isinstance(cmd, list) else cmd,
                output="[Process started]"
            )
    
    # Apply patches
    subprocess.run = patched_run
    subprocess.Popen = PatchedPopen


# Auto-integrate when imported
integrate_with_existing_tools()


if __name__ == "__main__":
    # Test integration
    print("Testing session integration...")
    
    # Create a test function
    @SessionIntegration.track_tool_execution("test_tool")
    @SessionIntegration.track_file_operation("created")
    def test_function(file_path: str):
        with open(file_path, 'w') as f:
            f.write("test content")
        return {"success": True, "file": file_path}
    
    # Run test
    result = test_function("test_session_integration.txt")
    print(f"Test result: {result}")
    
    # Check session
    session = get_session_manager()
    summary = session.get_session_summary()
    print(f"\nSession summary: {summary}")