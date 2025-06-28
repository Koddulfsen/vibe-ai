#!/usr/bin/env python3
"""
Session Manager for vibe.ai
Tracks all activities, file modifications, and context for seamless chat switching
"""

import os
import sys
import json
import hashlib
import threading
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, asdict, field
from collections import defaultdict
import time
import atexit

# Event types
class EventType:
    FILE_CREATED = "file_created"
    FILE_MODIFIED = "file_modified"
    FILE_DELETED = "file_deleted"
    FILE_READ = "file_read"
    COMMAND_EXECUTED = "command_executed"
    API_CALLED = "api_called"
    AGENT_EXECUTED = "agent_executed"
    DECISION_MADE = "decision_made"
    ERROR_OCCURRED = "error_occurred"
    CONTEXT_ADDED = "context_added"
    PRD_GENERATED = "prd_generated"
    TASK_CREATED = "task_created"
    MCP_ACTIVATED = "mcp_activated"


@dataclass
class SessionEvent:
    """Represents a single event in the session"""
    timestamp: str
    event_type: str
    description: str
    details: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class FileModification:
    """Track file modifications"""
    path: str
    action: str  # created, modified, deleted, read
    timestamp: str
    size_before: Optional[int] = None
    size_after: Optional[int] = None
    diff_summary: Optional[str] = None
    content_hash: Optional[str] = None


@dataclass
class Session:
    """Represents a complete session"""
    id: str
    start_time: str
    end_time: Optional[str] = None
    title: str = "vibe.ai Session"
    description: str = ""
    events: List[SessionEvent] = field(default_factory=list)
    files_modified: Dict[str, List[FileModification]] = field(default_factory=dict)
    commands_executed: List[Dict[str, Any]] = field(default_factory=list)
    api_calls: List[Dict[str, Any]] = field(default_factory=list)
    decisions: List[Dict[str, Any]] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict)
    tags: Set[str] = field(default_factory=set)
    
    def add_event(self, event: SessionEvent):
        """Add an event to the session"""
        self.events.append(event)
        # Update tags
        self.tags.update(event.tags)


class SessionManager:
    """Main session manager class"""
    
    def __init__(self, session_dir: Optional[Path] = None):
        self.session_dir = session_dir or Path.home() / ".vibe" / "sessions"
        self.session_dir.mkdir(parents=True, exist_ok=True)
        
        self.current_session: Optional[Session] = None
        self.session_file: Optional[Path] = None
        self._lock = threading.Lock()
        self._auto_save_interval = 30  # seconds
        self._auto_save_thread = None
        self._file_watchers = {}
        
        # Initialize or resume session
        self._initialize_session()
        
        # Register cleanup
        atexit.register(self.close_session)
    
    def _initialize_session(self):
        """Initialize a new session or resume existing one"""
        # Check for active session
        active_session_file = self.session_dir / "active_session.json"
        
        if active_session_file.exists():
            # Resume existing session
            with open(active_session_file) as f:
                session_info = json.load(f)
                self.session_file = Path(session_info["file"])
                self.load_session(self.session_file)
        else:
            # Create new session
            self.create_new_session()
    
    def create_new_session(self, title: Optional[str] = None) -> Session:
        """Create a new session"""
        session_id = datetime.now().strftime("%Y%m%d_%H%M%S") + "_" + \
                    hashlib.md5(os.urandom(16)).hexdigest()[:8]
        
        self.current_session = Session(
            id=session_id,
            start_time=datetime.now().isoformat(),
            title=title or f"vibe.ai Session {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        )
        
        # Create session file
        self.session_file = self.session_dir / f"session_{session_id}.json"
        self._save_session()
        
        # Mark as active
        self._mark_active_session()
        
        # Start auto-save
        self._start_auto_save()
        
        # Log session start
        self.add_event(
            EventType.CONTEXT_ADDED,
            "Session started",
            {"session_id": session_id, "title": self.current_session.title}
        )
        
        return self.current_session
    
    def load_session(self, session_file: Path) -> Session:
        """Load an existing session"""
        with open(session_file) as f:
            data = json.load(f)
        
        # Convert back to Session object
        self.current_session = Session(
            id=data["id"],
            start_time=data["start_time"],
            end_time=data.get("end_time"),
            title=data["title"],
            description=data["description"],
            events=[SessionEvent(**e) for e in data["events"]],
            files_modified=data["files_modified"],
            commands_executed=data["commands_executed"],
            api_calls=data["api_calls"],
            decisions=data["decisions"],
            context=data["context"],
            tags=set(data["tags"])
        )
        
        self.session_file = session_file
        self._start_auto_save()
        
        return self.current_session
    
    def add_event(self, event_type: str, description: str, 
                  details: Optional[Dict[str, Any]] = None,
                  tags: Optional[List[str]] = None):
        """Add an event to the current session"""
        if not self.current_session:
            self.create_new_session()
        
        event = SessionEvent(
            timestamp=datetime.now().isoformat(),
            event_type=event_type,
            description=description,
            details=details or {},
            tags=tags or []
        )
        
        with self._lock:
            self.current_session.add_event(event)
    
    def track_file_modification(self, file_path: str, action: str,
                               content: Optional[str] = None):
        """Track a file modification"""
        if not self.current_session:
            self.create_new_session()
        
        file_path = str(Path(file_path).resolve())
        
        # Get file info
        size_before = None
        size_after = None
        content_hash = None
        
        if Path(file_path).exists():
            size_after = Path(file_path).stat().st_size
            if content:
                content_hash = hashlib.md5(content.encode()).hexdigest()
        
        modification = FileModification(
            path=file_path,
            action=action,
            timestamp=datetime.now().isoformat(),
            size_before=size_before,
            size_after=size_after,
            content_hash=content_hash
        )
        
        with self._lock:
            if file_path not in self.current_session.files_modified:
                self.current_session.files_modified[file_path] = []
            self.current_session.files_modified[file_path].append(asdict(modification))
        
        # Add event
        self.add_event(
            f"file_{action}",
            f"File {action}: {Path(file_path).name}",
            {"path": file_path, "size": size_after}
        )
    
    def track_command(self, command: str, output: Optional[str] = None,
                     error: Optional[str] = None, return_code: Optional[int] = None):
        """Track a command execution"""
        if not self.current_session:
            self.create_new_session()
        
        command_info = {
            "command": command,
            "timestamp": datetime.now().isoformat(),
            "output": output[:1000] if output else None,  # Limit output size
            "error": error,
            "return_code": return_code
        }
        
        with self._lock:
            self.current_session.commands_executed.append(command_info)
        
        # Add event
        self.add_event(
            EventType.COMMAND_EXECUTED,
            f"Command: {command.split()[0] if command else 'unknown'}",
            command_info
        )
    
    def track_api_call(self, api_name: str, endpoint: str,
                      params: Optional[Dict[str, Any]] = None,
                      result: Optional[Any] = None,
                      error: Optional[str] = None):
        """Track an API call"""
        if not self.current_session:
            self.create_new_session()
        
        api_info = {
            "api_name": api_name,
            "endpoint": endpoint,
            "params": params,
            "result": str(result)[:500] if result else None,  # Limit size
            "error": error,
            "timestamp": datetime.now().isoformat()
        }
        
        with self._lock:
            self.current_session.api_calls.append(api_info)
        
        # Add event
        self.add_event(
            EventType.API_CALLED,
            f"API Call: {api_name} - {endpoint}",
            api_info
        )
    
    def track_decision(self, decision_type: str, description: str,
                      options: Optional[List[str]] = None,
                      chosen: Optional[str] = None,
                      reasoning: Optional[str] = None):
        """Track a decision made during the session"""
        if not self.current_session:
            self.create_new_session()
        
        decision_info = {
            "type": decision_type,
            "description": description,
            "options": options,
            "chosen": chosen,
            "reasoning": reasoning,
            "timestamp": datetime.now().isoformat()
        }
        
        with self._lock:
            self.current_session.decisions.append(decision_info)
        
        # Add event
        self.add_event(
            EventType.DECISION_MADE,
            f"Decision: {decision_type}",
            decision_info
        )
    
    def add_context(self, key: str, value: Any):
        """Add context information to the session"""
        if not self.current_session:
            self.create_new_session()
        
        with self._lock:
            self.current_session.context[key] = value
        
        # Add event
        self.add_event(
            EventType.CONTEXT_ADDED,
            f"Context added: {key}",
            {"key": key, "value": str(value)[:200]}
        )
    
    def get_session_summary(self) -> Dict[str, Any]:
        """Get a summary of the current session"""
        if not self.current_session:
            return {}
        
        # Count events by type
        event_counts = defaultdict(int)
        for event in self.current_session.events:
            event_counts[event.event_type] += 1
        
        # Get unique files
        unique_files = set()
        for file_path, mods in self.current_session.files_modified.items():
            unique_files.add(file_path)
        
        # Calculate duration
        start_time = datetime.fromisoformat(self.current_session.start_time)
        end_time = datetime.now()
        if self.current_session.end_time:
            end_time = datetime.fromisoformat(self.current_session.end_time)
        duration = (end_time - start_time).total_seconds()
        
        return {
            "session_id": self.current_session.id,
            "title": self.current_session.title,
            "description": self.current_session.description,
            "start_time": self.current_session.start_time,
            "duration_seconds": duration,
            "total_events": len(self.current_session.events),
            "event_counts": dict(event_counts),
            "files_modified": len(unique_files),
            "commands_executed": len(self.current_session.commands_executed),
            "api_calls": len(self.current_session.api_calls),
            "decisions_made": len(self.current_session.decisions),
            "tags": list(self.current_session.tags)
        }
    
    def export_session(self, format: str = "json") -> str:
        """Export the current session"""
        if not self.current_session:
            return ""
        
        if format == "json":
            return json.dumps(self._session_to_dict(), indent=2)
        elif format == "markdown":
            return self._export_markdown()
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def _export_markdown(self) -> str:
        """Export session as markdown"""
        lines = []
        summary = self.get_session_summary()
        
        lines.append(f"# {self.current_session.title}")
        lines.append(f"\n**Session ID:** {self.current_session.id}")
        lines.append(f"**Duration:** {summary['duration_seconds']:.0f} seconds")
        lines.append(f"**Total Events:** {summary['total_events']}")
        
        # Files modified
        if self.current_session.files_modified:
            lines.append("\n## Files Modified")
            for file_path in sorted(self.current_session.files_modified.keys()):
                lines.append(f"- {file_path}")
        
        # Commands executed
        if self.current_session.commands_executed:
            lines.append("\n## Commands Executed")
            for cmd in self.current_session.commands_executed[-10:]:  # Last 10
                lines.append(f"- `{cmd['command']}`")
        
        # Key decisions
        if self.current_session.decisions:
            lines.append("\n## Key Decisions")
            for decision in self.current_session.decisions:
                lines.append(f"- **{decision['type']}**: {decision['description']}")
                if decision.get('chosen'):
                    lines.append(f"  - Chosen: {decision['chosen']}")
        
        # Recent events
        lines.append("\n## Recent Events")
        for event in self.current_session.events[-20:]:  # Last 20
            lines.append(f"- [{event.timestamp}] {event.description}")
        
        return "\n".join(lines)
    
    def close_session(self):
        """Close the current session"""
        if self.current_session:
            self.current_session.end_time = datetime.now().isoformat()
            self._save_session()
            
            # Remove active session marker
            active_file = self.session_dir / "active_session.json"
            if active_file.exists():
                active_file.unlink()
            
            # Stop auto-save
            if self._auto_save_thread:
                self._auto_save_thread = None
    
    def _save_session(self):
        """Save the current session to disk"""
        if not self.current_session or not self.session_file:
            return
        
        with self._lock:
            data = self._session_to_dict()
            
            # Write to temp file first
            temp_file = self.session_file.with_suffix('.tmp')
            with open(temp_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            # Atomic rename
            temp_file.rename(self.session_file)
    
    def _session_to_dict(self) -> Dict[str, Any]:
        """Convert session to dictionary"""
        return {
            "id": self.current_session.id,
            "start_time": self.current_session.start_time,
            "end_time": self.current_session.end_time,
            "title": self.current_session.title,
            "description": self.current_session.description,
            "events": [e.to_dict() for e in self.current_session.events],
            "files_modified": self.current_session.files_modified,
            "commands_executed": self.current_session.commands_executed,
            "api_calls": self.current_session.api_calls,
            "decisions": self.current_session.decisions,
            "context": self.current_session.context,
            "tags": list(self.current_session.tags)
        }
    
    def _mark_active_session(self):
        """Mark the current session as active"""
        active_file = self.session_dir / "active_session.json"
        with open(active_file, 'w') as f:
            json.dump({
                "file": str(self.session_file),
                "id": self.current_session.id,
                "title": self.current_session.title
            }, f)
    
    def _start_auto_save(self):
        """Start auto-save thread"""
        def auto_save():
            while self._auto_save_thread:
                time.sleep(self._auto_save_interval)
                if self._auto_save_thread:  # Check again after sleep
                    self._save_session()
        
        self._auto_save_thread = threading.Thread(target=auto_save, daemon=True)
        self._auto_save_thread.start()


# Global session manager instance
_session_manager: Optional[SessionManager] = None


def get_session_manager() -> SessionManager:
    """Get the global session manager instance"""
    global _session_manager
    if _session_manager is None:
        _session_manager = SessionManager()
    return _session_manager


# Convenience functions
def track_file(file_path: str, action: str, content: Optional[str] = None):
    """Track a file modification"""
    get_session_manager().track_file_modification(file_path, action, content)


def track_command(command: str, output: Optional[str] = None,
                 error: Optional[str] = None, return_code: Optional[int] = None):
    """Track a command execution"""
    get_session_manager().track_command(command, output, error, return_code)


def track_api_call(api_name: str, endpoint: str, **kwargs):
    """Track an API call"""
    get_session_manager().track_api_call(api_name, endpoint, **kwargs)


def track_decision(decision_type: str, description: str, **kwargs):
    """Track a decision"""
    get_session_manager().track_decision(decision_type, description, **kwargs)


def add_context(key: str, value: Any):
    """Add context to the session"""
    get_session_manager().add_context(key, value)


def get_summary() -> Dict[str, Any]:
    """Get session summary"""
    return get_session_manager().get_session_summary()


if __name__ == "__main__":
    # Test the session manager
    manager = SessionManager()
    
    # Track some activities
    track_file("test.py", "created", "print('hello')")
    track_command("python test.py", "hello", None, 0)
    track_api_call("openai", "/completions", params={"model": "gpt-4"})
    track_decision("architecture", "Choose framework", 
                   options=["django", "fastapi"], chosen="fastapi")
    
    # Get summary
    print(json.dumps(get_summary(), indent=2))
    
    # Export
    print("\n" + manager.export_session("markdown"))