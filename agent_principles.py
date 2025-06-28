#!/usr/bin/env python3
"""
Agent Principles - Core principles for all vibe.ai agents
ULTRATHINK: Deep analysis, concise expression
BE CONCISE: Maximum impact, minimum words
NO BLOAT: If it doesn't help, it hurts
"""

from typing import Any, List, Dict, Optional
import textwrap

# Core principles that guide all agents
AGENT_PRINCIPLES = {
    "ULTRATHINK": "Analyze deeply, consider all angles, but express concisely",
    "BE_CONCISE": "Maximum impact, minimum words. Every line must add value",
    "NO_BLOAT": "Remove redundancy. If it doesn't help, it hurts"
}

# Output limits
OUTPUT_LIMITS = {
    "max_lines": 20,           # Maximum lines for standard output
    "max_line_length": 80,     # Maximum characters per line
    "max_bullet_points": 7,    # Maximum bullet points in lists
    "max_description": 100,    # Maximum characters for descriptions
}

# Concise output templates
TEMPLATES = {
    "task_analysis": "• {task_type} | Complexity: {score}/10 | Time: {time}",
    "file_operation": "✅ {action}: {filename}",
    "error": "❌ {error_type}: {message}",
    "success": "✅ {action} complete",
    "progress": "⏳ {step}/{total}: {action}",
    "decision": "🎯 {decision} (confidence: {confidence}%)",
    "insight": "💡 {insight}",
}


class PrincipledOutput:
    """Enforces agent principles in all outputs"""
    
    @staticmethod
    def think_deeply(analysis_func):
        """Decorator: Think deeply but output concisely"""
        def wrapper(*args, **kwargs):
            # Perform deep analysis
            result = analysis_func(*args, **kwargs)
            
            # Ensure concise output
            if isinstance(result, str):
                return PrincipledOutput.make_concise(result)
            elif isinstance(result, dict):
                return PrincipledOutput.make_dict_concise(result)
            elif isinstance(result, list):
                return PrincipledOutput.make_list_concise(result)
            return result
        return wrapper
    
    @staticmethod
    def make_concise(text: str, max_length: Optional[int] = None) -> str:
        """Make text concise while preserving meaning"""
        if not text:
            return ""
        
        max_length = max_length or OUTPUT_LIMITS["max_line_length"] * OUTPUT_LIMITS["max_lines"]
        
        # Remove redundant whitespace
        text = " ".join(text.split())
        
        # Truncate if needed
        if len(text) > max_length:
            text = text[:max_length-3] + "..."
        
        return text
    
    @staticmethod
    def make_dict_concise(data: Dict[str, Any]) -> Dict[str, Any]:
        """Make dictionary output concise"""
        concise = {}
        for key, value in data.items():
            if value is None or value == "" or value == []:
                continue  # Skip empty values (NO BLOAT)
            
            if isinstance(value, str):
                concise[key] = PrincipledOutput.make_concise(value)
            elif isinstance(value, list):
                concise[key] = PrincipledOutput.make_list_concise(value)
            elif isinstance(value, dict):
                concise[key] = PrincipledOutput.make_dict_concise(value)
            else:
                concise[key] = value
        
        return concise
    
    @staticmethod
    def make_list_concise(items: List[Any], max_items: Optional[int] = None) -> List[Any]:
        """Make list output concise"""
        max_items = max_items or OUTPUT_LIMITS["max_bullet_points"]
        
        # Filter out empty/None items
        items = [item for item in items if item]
        
        # Limit number of items
        if len(items) > max_items:
            items = items[:max_items-1] + [f"...and {len(items)-max_items+1} more"]
        
        # Make each item concise
        return [PrincipledOutput.make_concise(str(item)) if isinstance(item, str) else item 
                for item in items]
    
    @staticmethod
    def format_output(template_key: str, **kwargs) -> str:
        """Format output using templates"""
        template = TEMPLATES.get(template_key, "{message}")
        try:
            return template.format(**kwargs)
        except:
            return str(kwargs)
    
    @staticmethod
    def bullet_list(items: List[str], prefix: str = "•") -> str:
        """Create concise bullet list"""
        items = PrincipledOutput.make_list_concise(items)
        return "\n".join(f"{prefix} {item}" for item in items)
    
    @staticmethod
    def summary_first(full_text: str, summary: str) -> str:
        """Put summary first, details only if needed"""
        if len(full_text) < OUTPUT_LIMITS["max_line_length"]:
            return full_text
        return f"{summary}\n[Details: {len(full_text)} chars]"


class AgentResponse:
    """Structured response that enforces principles"""
    
    def __init__(self):
        self.summary = ""
        self.details = []
        self.actions = []
        self.errors = []
        
    def add_summary(self, text: str):
        """Add concise summary"""
        self.summary = PrincipledOutput.make_concise(text, OUTPUT_LIMITS["max_description"])
        
    def add_detail(self, detail: str):
        """Add detail (will be filtered if not important)"""
        if detail and len(self.details) < OUTPUT_LIMITS["max_bullet_points"]:
            self.details.append(PrincipledOutput.make_concise(detail))
    
    def add_action(self, action: str):
        """Add action taken"""
        if action:
            self.actions.append(PrincipledOutput.format_output("success", action=action))
    
    def add_error(self, error_type: str, message: str):
        """Add error"""
        self.errors.append(PrincipledOutput.format_output("error", 
                                                         error_type=error_type, 
                                                         message=PrincipledOutput.make_concise(message)))
    
    def render(self) -> str:
        """Render concise output"""
        output_parts = []
        
        # Summary always first
        if self.summary:
            output_parts.append(self.summary)
        
        # Errors are critical
        if self.errors:
            output_parts.append(PrincipledOutput.bullet_list(self.errors))
        
        # Actions show what was done
        if self.actions:
            output_parts.append(PrincipledOutput.bullet_list(self.actions[:3]))
        
        # Details only if space allows
        remaining_lines = OUTPUT_LIMITS["max_lines"] - len(output_parts) - 2
        if remaining_lines > 0 and self.details:
            output_parts.append(PrincipledOutput.bullet_list(self.details[:remaining_lines]))
        
        return "\n".join(output_parts)


def apply_principles(agent_class):
    """Class decorator to apply principles to an agent"""
    
    # Add principles as class attribute
    agent_class.PRINCIPLES = AGENT_PRINCIPLES
    agent_class.OUTPUT_LIMITS = OUTPUT_LIMITS
    
    # Wrap output methods
    if hasattr(agent_class, 'output'):
        original_output = agent_class.output
        def principled_output(self, *args, **kwargs):
            result = original_output(self, *args, **kwargs)
            return PrincipledOutput.make_concise(str(result))
        agent_class.output = principled_output
    
    # Add helper methods
    agent_class.concise = PrincipledOutput.make_concise
    agent_class.format = PrincipledOutput.format_output
    agent_class.bullets = PrincipledOutput.bullet_list
    
    return agent_class


# Example usage
if __name__ == "__main__":
    # Test principles
    response = AgentResponse()
    response.add_summary("Task analysis complete")
    response.add_detail("Found 15 Python files")
    response.add_detail("Identified 3 main components")
    response.add_detail("No critical issues")
    response.add_action("Analyzed project structure")
    
    print("=== Principled Output ===")
    print(response.render())
    
    # Test concise formatting
    print("\n=== Concise Formatting ===")
    long_text = "This is a very long text that contains way too much information and should be made more concise according to our principles"
    print(f"Original: {len(long_text)} chars")
    print(f"Concise: {PrincipledOutput.make_concise(long_text)}")
    
    # Test templates
    print("\n=== Template Examples ===")
    print(PrincipledOutput.format_output("task_analysis", 
                                       task_type="API Development",
                                       score=7,
                                       time="2-3 hours"))
    print(PrincipledOutput.format_output("file_operation",
                                       action="Created",
                                       filename="user_service.py"))