#!/usr/bin/env python3
"""
Concise Formatter - Output formatting for ultrathink agents
Ensures all agent outputs are concise, clear, and valuable
"""

import json
import re
from typing import Any, Dict, List, Optional, Union
from datetime import datetime
from pathlib import Path

class ConciseFormatter:
    """Format agent outputs to be concise and impactful"""
    
    # Icons for different message types (use sparingly)
    ICONS = {
        "success": "✅",
        "error": "❌",
        "warning": "⚠️",
        "info": "ℹ️",
        "task": "📋",
        "file": "📄",
        "folder": "📁",
        "code": "💻",
        "test": "🧪",
        "build": "🔨",
        "deploy": "🚀",
        "think": "🤔",
        "decision": "🎯",
        "time": "⏱️",
    }
    
    @staticmethod
    def format_task_result(task: str, status: str, details: Optional[Dict] = None) -> str:
        """Format task execution result concisely"""
        icon = ConciseFormatter.ICONS.get(status, "")
        result = f"{icon} {task}"
        
        if details:
            # Add only essential details
            if "time" in details:
                result += f" ({details['time']})"
            if "error" in details:
                result += f"\n  Error: {details['error'][:50]}..."
        
        return result
    
    @staticmethod
    def format_file_list(files: List[str], max_files: int = 5) -> str:
        """Format file list concisely"""
        if not files:
            return "No files"
        
        # Group by extension
        by_ext = {}
        for file in files:
            ext = Path(file).suffix or "no-ext"
            by_ext.setdefault(ext, []).append(Path(file).name)
        
        # Format output
        lines = []
        shown = 0
        for ext, names in sorted(by_ext.items()):
            if shown >= max_files:
                lines.append(f"...+{len(files)-shown} more")
                break
            
            if len(names) == 1:
                lines.append(f"• {names[0]}")
                shown += 1
            else:
                count = min(len(names), max_files - shown)
                lines.append(f"• {count} {ext} files")
                shown += count
        
        return "\n".join(lines)
    
    @staticmethod
    def format_analysis(analysis: Dict[str, Any]) -> str:
        """Format analysis results concisely"""
        lines = []
        
        # Priority order for analysis keys
        priority_keys = ["summary", "complexity", "issues", "recommendations"]
        
        for key in priority_keys:
            if key in analysis:
                value = analysis[key]
                if isinstance(value, list):
                    if value:  # Only show if not empty
                        lines.append(f"{key.title()}: {len(value)} items")
                elif isinstance(value, dict):
                    if "score" in value:
                        lines.append(f"{key.title()}: {value['score']}/10")
                    else:
                        lines.append(f"{key.title()}: {len(value)} properties")
                else:
                    lines.append(f"{key.title()}: {str(value)[:50]}")
        
        return "\n".join(lines) if lines else "No analysis data"
    
    @staticmethod
    def format_progress(current: int, total: int, action: str) -> str:
        """Format progress update"""
        percent = (current / total * 100) if total > 0 else 0
        bar_length = 10
        filled = int(bar_length * current / total) if total > 0 else 0
        bar = "█" * filled + "░" * (bar_length - filled)
        
        return f"[{bar}] {percent:.0f}% - {action}"
    
    @staticmethod
    def format_decision(decision: str, options: List[str], chosen: str, 
                       confidence: float) -> str:
        """Format decision concisely"""
        icon = ConciseFormatter.ICONS["decision"]
        return f"{icon} {decision}: {chosen} ({confidence:.0f}% confident)"
    
    @staticmethod
    def format_error(error_type: str, message: str, suggestion: Optional[str] = None) -> str:
        """Format error message concisely"""
        icon = ConciseFormatter.ICONS["error"]
        output = f"{icon} {error_type}: {message[:100]}"
        
        if suggestion:
            output += f"\n  Fix: {suggestion[:80]}"
        
        return output
    
    @staticmethod
    def format_json_output(data: Dict[str, Any], max_depth: int = 2) -> str:
        """Format JSON data concisely"""
        def truncate_value(value: Any, depth: int = 0) -> Any:
            if depth >= max_depth:
                return "..."
            
            if isinstance(value, str) and len(value) > 50:
                return value[:47] + "..."
            elif isinstance(value, list):
                if len(value) > 3:
                    return [truncate_value(v, depth+1) for v in value[:2]] + [f"...+{len(value)-2}"]
                return [truncate_value(v, depth+1) for v in value]
            elif isinstance(value, dict):
                if len(value) > 3:
                    result = {}
                    for i, (k, v) in enumerate(value.items()):
                        if i < 3:
                            result[k] = truncate_value(v, depth+1)
                        else:
                            result["..."] = f"+{len(value)-3} more"
                            break
                    return result
                return {k: truncate_value(v, depth+1) for k, v in value.items()}
            return value
        
        truncated = truncate_value(data)
        return json.dumps(truncated, indent=2, ensure_ascii=False)
    
    @staticmethod
    def create_summary(title: str, items: List[str], max_items: int = 5) -> str:
        """Create a concise summary with bullet points"""
        lines = [title]
        
        for i, item in enumerate(items[:max_items]):
            lines.append(f"• {item}")
        
        if len(items) > max_items:
            lines.append(f"• ...+{len(items) - max_items} more")
        
        return "\n".join(lines)
    
    @staticmethod
    def strip_decorations(text: str) -> str:
        """Remove unnecessary decorations from text"""
        # Remove excessive newlines
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        # Remove decorative separators
        text = re.sub(r'^[=-]{3,}$', '', text, flags=re.MULTILINE)
        
        # Remove excessive whitespace
        text = re.sub(r' {2,}', ' ', text)
        
        return text.strip()


class OutputBuffer:
    """Collect and format outputs efficiently"""
    
    def __init__(self, max_lines: int = 20):
        self.lines = []
        self.max_lines = max_lines
        self.formatter = ConciseFormatter()
    
    def add(self, text: str, icon: Optional[str] = None):
        """Add line to buffer"""
        if len(self.lines) >= self.max_lines:
            return  # Ignore if buffer full
        
        if icon:
            text = f"{ConciseFormatter.ICONS.get(icon, '')} {text}"
        
        self.lines.append(text)
    
    def add_section(self, title: str, items: List[str]):
        """Add a section with items"""
        if len(self.lines) + len(items) + 1 > self.max_lines:
            # Truncate to fit
            available = self.max_lines - len(self.lines) - 1
            if available > 0:
                items = items[:available-1] + [f"...+{len(items)-available+1} more"]
        
        self.lines.append(title)
        for item in items:
            self.lines.append(f"  {item}")
    
    def render(self) -> str:
        """Render buffer as string"""
        return "\n".join(self.lines)


# Test the formatter
if __name__ == "__main__":
    formatter = ConciseFormatter()
    
    # Test task result
    print("=== Task Result ===")
    print(formatter.format_task_result("API endpoint created", "success", {"time": "1.2s"}))
    
    # Test file list
    print("\n=== File List ===")
    files = ["src/main.py", "src/utils.py", "src/api.py", "tests/test_main.py", 
             "tests/test_utils.py", "README.md", "setup.py"]
    print(formatter.format_file_list(files))
    
    # Test progress
    print("\n=== Progress ===")
    print(formatter.format_progress(7, 10, "Running tests"))
    
    # Test JSON output
    print("\n=== JSON Output ===")
    data = {
        "status": "success",
        "files_created": ["file1.py", "file2.py", "file3.py", "file4.py"],
        "config": {
            "name": "test-project",
            "version": "1.0.0",
            "dependencies": ["dep1", "dep2", "dep3", "dep4", "dep5"]
        }
    }
    print(formatter.format_json_output(data))
    
    # Test output buffer
    print("\n=== Output Buffer ===")
    buffer = OutputBuffer(max_lines=10)
    buffer.add("Starting task execution", "task")
    buffer.add("Analyzing project structure", "think")
    buffer.add_section("Files found:", ["main.py", "utils.py", "config.py", "test.py", "setup.py"])
    buffer.add("Task complete", "success")
    print(buffer.render())