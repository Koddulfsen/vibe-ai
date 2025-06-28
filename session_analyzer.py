#!/usr/bin/env python3
"""
Session Analyzer for vibe.ai
Analyzes sessions to provide insights and generate summaries
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from collections import defaultdict, Counter
import re
from dataclasses import dataclass
import statistics


@dataclass
class SessionInsight:
    """Represents an insight from session analysis"""
    category: str
    title: str
    description: str
    severity: str  # info, warning, suggestion
    data: Dict[str, Any]
    recommendations: List[str]


class SessionAnalyzer:
    """Analyzes sessions to extract insights and patterns"""
    
    def __init__(self):
        self.patterns = {
            "error_patterns": [
                (r"ModuleNotFoundError", "Missing module dependencies"),
                (r"ImportError", "Import issues"),
                (r"SyntaxError", "Syntax errors in code"),
                (r"TypeError", "Type-related errors"),
                (r"FileNotFoundError", "Missing files"),
                (r"PermissionError", "Permission issues"),
            ],
            "productivity_patterns": [
                (r"git commit", "Version control activity"),
                (r"npm install|pip install", "Dependency installation"),
                (r"test|pytest|jest", "Testing activity"),
                (r"docker", "Container operations"),
            ],
            "file_patterns": [
                (r"\.py$", "Python files"),
                (r"\.js$|\.ts$", "JavaScript/TypeScript files"),
                (r"\.md$", "Documentation files"),
                (r"\.json$|\.yaml$|\.yml$", "Configuration files"),
            ]
        }
    
    def analyze_session(self, session_data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform comprehensive analysis on a session"""
        insights = []
        
        # Basic metrics
        metrics = self._calculate_metrics(session_data)
        
        # Analyze patterns
        insights.extend(self._analyze_error_patterns(session_data))
        insights.extend(self._analyze_productivity(session_data))
        insights.extend(self._analyze_file_changes(session_data))
        insights.extend(self._analyze_workflow_patterns(session_data))
        insights.extend(self._analyze_decision_patterns(session_data))
        
        # Generate summary
        summary = self._generate_summary(session_data, metrics, insights)
        
        # Identify key moments
        key_moments = self._identify_key_moments(session_data)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(insights)
        
        return {
            "metrics": metrics,
            "insights": [insight.__dict__ for insight in insights],
            "summary": summary,
            "key_moments": key_moments,
            "recommendations": recommendations,
            "analysis_timestamp": datetime.now().isoformat()
        }
    
    def _calculate_metrics(self, session_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate basic session metrics"""
        events = session_data.get("events", [])
        
        # Time metrics
        start_time = datetime.fromisoformat(session_data["start_time"])
        end_time = datetime.now()
        if session_data.get("end_time"):
            end_time = datetime.fromisoformat(session_data["end_time"])
        
        duration = (end_time - start_time).total_seconds()
        
        # Event metrics
        event_types = Counter(e["event_type"] for e in events)
        
        # File metrics
        files_modified = session_data.get("files_modified", {})
        file_extensions = Counter()
        total_modifications = 0
        
        for file_path, mods in files_modified.items():
            ext = Path(file_path).suffix
            if ext:
                file_extensions[ext] += 1
            total_modifications += len(mods)
        
        # Command metrics
        commands = session_data.get("commands_executed", [])
        command_types = Counter()
        failed_commands = 0
        
        for cmd in commands:
            cmd_name = cmd["command"].split()[0] if cmd["command"] else "unknown"
            command_types[cmd_name] += 1
            if cmd.get("return_code") and cmd["return_code"] != 0:
                failed_commands += 1
        
        # Activity intensity (events per minute)
        activity_intensity = len(events) / (duration / 60) if duration > 0 else 0
        
        return {
            "duration_seconds": duration,
            "duration_formatted": self._format_duration(duration),
            "total_events": len(events),
            "event_types": dict(event_types),
            "files_modified_count": len(files_modified),
            "total_file_modifications": total_modifications,
            "file_extensions": dict(file_extensions),
            "commands_executed": len(commands),
            "command_types": dict(command_types.most_common(10)),
            "failed_commands": failed_commands,
            "api_calls": len(session_data.get("api_calls", [])),
            "decisions_made": len(session_data.get("decisions", [])),
            "activity_intensity": round(activity_intensity, 2),
            "error_rate": sum(1 for e in events if e["event_type"] == "error_occurred") / len(events) if events else 0
        }
    
    def _analyze_error_patterns(self, session_data: Dict[str, Any]) -> List[SessionInsight]:
        """Analyze error patterns in the session"""
        insights = []
        events = session_data.get("events", [])
        commands = session_data.get("commands_executed", [])
        
        # Collect all errors
        errors = []
        for event in events:
            if event["event_type"] == "error_occurred":
                errors.append(event)
        
        for cmd in commands:
            if cmd.get("error"):
                errors.append({
                    "timestamp": cmd["timestamp"],
                    "description": f"Command error: {cmd['command']}",
                    "details": {"error": cmd["error"]}
                })
        
        if not errors:
            return insights
        
        # Categorize errors
        error_categories = defaultdict(list)
        for error in errors:
            error_text = str(error.get("details", {}).get("error", ""))
            for pattern, category in self.patterns["error_patterns"]:
                if re.search(pattern, error_text, re.IGNORECASE):
                    error_categories[category].append(error)
                    break
            else:
                error_categories["Other errors"].append(error)
        
        # Create insights
        for category, category_errors in error_categories.items():
            if len(category_errors) >= 2:  # Pattern detected
                insights.append(SessionInsight(
                    category="errors",
                    title=f"Recurring {category}",
                    description=f"Found {len(category_errors)} instances of {category}",
                    severity="warning",
                    data={"count": len(category_errors), "errors": category_errors[:3]},
                    recommendations=[
                        f"Review and fix {category.lower()}",
                        "Consider adding error handling",
                        "Check dependencies and imports"
                    ]
                ))
        
        return insights
    
    def _analyze_productivity(self, session_data: Dict[str, Any]) -> List[SessionInsight]:
        """Analyze productivity patterns"""
        insights = []
        metrics = self._calculate_metrics(session_data)
        
        # Activity intensity
        if metrics["activity_intensity"] > 10:
            insights.append(SessionInsight(
                category="productivity",
                title="High Activity Session",
                description=f"Very active session with {metrics['activity_intensity']} events per minute",
                severity="info",
                data={"intensity": metrics["activity_intensity"]},
                recommendations=["Great productivity! Keep up the momentum"]
            ))
        elif metrics["activity_intensity"] < 1:
            insights.append(SessionInsight(
                category="productivity",
                title="Low Activity Detected",
                description="Session had low activity, possibly stuck or exploring",
                severity="suggestion",
                data={"intensity": metrics["activity_intensity"]},
                recommendations=[
                    "Consider breaking down complex tasks",
                    "Use planning tools to organize work"
                ]
            ))
        
        # Command patterns
        commands = session_data.get("commands_executed", [])
        productivity_commands = defaultdict(int)
        
        for cmd in commands:
            cmd_text = cmd["command"]
            for pattern, category in self.patterns["productivity_patterns"]:
                if re.search(pattern, cmd_text, re.IGNORECASE):
                    productivity_commands[category] += 1
        
        if productivity_commands:
            insights.append(SessionInsight(
                category="productivity",
                title="Development Activities",
                description="Productive development patterns detected",
                severity="info",
                data=dict(productivity_commands),
                recommendations=["Continue with current workflow"]
            ))
        
        return insights
    
    def _analyze_file_changes(self, session_data: Dict[str, Any]) -> List[SessionInsight]:
        """Analyze file change patterns"""
        insights = []
        files_modified = session_data.get("files_modified", {})
        
        if not files_modified:
            return insights
        
        # Analyze by file type
        file_categories = defaultdict(list)
        for file_path in files_modified.keys():
            for pattern, category in self.patterns["file_patterns"]:
                if re.search(pattern, file_path):
                    file_categories[category].append(file_path)
                    break
        
        # Most modified files
        modification_counts = {
            path: len(mods) for path, mods in files_modified.items()
        }
        hot_files = sorted(modification_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        if hot_files and hot_files[0][1] > 5:
            insights.append(SessionInsight(
                category="files",
                title="Frequently Modified Files",
                description="Some files were modified many times",
                severity="info",
                data={
                    "hot_files": [{"path": path, "count": count} for path, count in hot_files]
                },
                recommendations=[
                    "Consider refactoring frequently modified files",
                    "These might be core components needing attention"
                ]
            ))
        
        # File type distribution
        if len(file_categories) > 1:
            insights.append(SessionInsight(
                category="files",
                title="Multi-Language Development",
                description=f"Working with {len(file_categories)} different file types",
                severity="info",
                data={"categories": {cat: len(files) for cat, files in file_categories.items()}},
                recommendations=["Good cross-functional development"]
            ))
        
        return insights
    
    def _analyze_workflow_patterns(self, session_data: Dict[str, Any]) -> List[SessionInsight]:
        """Analyze workflow patterns"""
        insights = []
        events = session_data.get("events", [])
        
        # Detect common workflows
        workflow_sequences = []
        for i in range(len(events) - 2):
            sequence = [events[i]["event_type"], events[i+1]["event_type"], events[i+2]["event_type"]]
            workflow_sequences.append(tuple(sequence))
        
        # Count common sequences
        sequence_counts = Counter(workflow_sequences)
        common_sequences = sequence_counts.most_common(5)
        
        if common_sequences and common_sequences[0][1] > 3:
            insights.append(SessionInsight(
                category="workflow",
                title="Repetitive Workflow Detected",
                description="Found repeated action sequences",
                severity="suggestion",
                data={
                    "sequences": [
                        {"sequence": list(seq), "count": count}
                        for seq, count in common_sequences[:3]
                    ]
                },
                recommendations=[
                    "Consider automating repetitive workflows",
                    "Create scripts or aliases for common sequences"
                ]
            ))
        
        return insights
    
    def _analyze_decision_patterns(self, session_data: Dict[str, Any]) -> List[SessionInsight]:
        """Analyze decision-making patterns"""
        insights = []
        decisions = session_data.get("decisions", [])
        
        if not decisions:
            return insights
        
        # Analyze decision types
        decision_types = Counter(d["type"] for d in decisions)
        
        # Time between decisions
        if len(decisions) > 1:
            decision_times = []
            for i in range(1, len(decisions)):
                t1 = datetime.fromisoformat(decisions[i-1]["timestamp"])
                t2 = datetime.fromisoformat(decisions[i]["timestamp"])
                decision_times.append((t2 - t1).total_seconds())
            
            avg_time = statistics.mean(decision_times)
            
            if avg_time < 60:  # Less than 1 minute between decisions
                insights.append(SessionInsight(
                    category="decisions",
                    title="Rapid Decision Making",
                    description="Making decisions quickly, possibly rushed",
                    severity="warning",
                    data={
                        "avg_seconds_between": avg_time,
                        "total_decisions": len(decisions)
                    },
                    recommendations=[
                        "Consider taking more time for important decisions",
                        "Document reasoning for future reference"
                    ]
                ))
        
        return insights
    
    def _identify_key_moments(self, session_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify key moments in the session"""
        key_moments = []
        events = session_data.get("events", [])
        
        # Key event types
        key_event_types = {
            "prd_generated": "PRD Generated",
            "task_created": "Task Created",
            "decision_made": "Important Decision",
            "error_occurred": "Error Encountered",
            "file_created": "New File Created"
        }
        
        for event in events:
            if event["event_type"] in key_event_types:
                key_moments.append({
                    "timestamp": event["timestamp"],
                    "type": key_event_types[event["event_type"]],
                    "description": event["description"],
                    "details": event.get("details", {})
                })
        
        # Sort by timestamp
        key_moments.sort(key=lambda x: x["timestamp"])
        
        return key_moments[:10]  # Top 10 moments
    
    def _generate_summary(self, session_data: Dict[str, Any], 
                         metrics: Dict[str, Any], 
                         insights: List[SessionInsight]) -> str:
        """Generate a human-readable summary"""
        lines = []
        
        # Session overview
        lines.append(f"## Session Summary: {session_data.get('title', 'Untitled Session')}")
        lines.append(f"\n**Duration:** {metrics['duration_formatted']}")
        lines.append(f"**Total Events:** {metrics['total_events']}")
        lines.append(f"**Files Modified:** {metrics['files_modified_count']}")
        lines.append(f"**Commands Executed:** {metrics['commands_executed']}")
        
        # Key activities
        if metrics["event_types"]:
            lines.append("\n### Main Activities")
            top_activities = sorted(metrics["event_types"].items(), 
                                  key=lambda x: x[1], reverse=True)[:5]
            for activity, count in top_activities:
                lines.append(f"- {activity.replace('_', ' ').title()}: {count}")
        
        # Insights summary
        if insights:
            lines.append("\n### Key Insights")
            for insight in insights[:5]:
                lines.append(f"- **{insight.title}**: {insight.description}")
        
        # Productivity metrics
        lines.append(f"\n### Productivity Metrics")
        lines.append(f"- Activity Intensity: {metrics['activity_intensity']} events/minute")
        lines.append(f"- Error Rate: {metrics['error_rate']:.1%}")
        if metrics["failed_commands"] > 0:
            lines.append(f"- Failed Commands: {metrics['failed_commands']}")
        
        return "\n".join(lines)
    
    def _generate_recommendations(self, insights: List[SessionInsight]) -> List[str]:
        """Generate actionable recommendations"""
        all_recommendations = []
        
        # Collect unique recommendations
        seen = set()
        for insight in insights:
            for rec in insight.recommendations:
                if rec not in seen:
                    seen.add(rec)
                    all_recommendations.append(rec)
        
        # Prioritize by severity
        priority_insights = sorted(insights, 
                                 key=lambda x: {"warning": 0, "suggestion": 1, "info": 2}[x.severity])
        
        # Add general recommendations based on patterns
        if any(i.category == "errors" for i in insights):
            all_recommendations.insert(0, "Focus on resolving errors before adding new features")
        
        if any(i.category == "workflow" for i in insights):
            all_recommendations.append("Consider creating workflow automation tools")
        
        return all_recommendations[:10]  # Top 10 recommendations
    
    def _format_duration(self, seconds: float) -> str:
        """Format duration in human-readable form"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        
        parts = []
        if hours > 0:
            parts.append(f"{hours}h")
        if minutes > 0:
            parts.append(f"{minutes}m")
        if secs > 0 or not parts:
            parts.append(f"{secs}s")
        
        return " ".join(parts)
    
    def compare_sessions(self, session1: Dict[str, Any], 
                        session2: Dict[str, Any]) -> Dict[str, Any]:
        """Compare two sessions"""
        metrics1 = self._calculate_metrics(session1)
        metrics2 = self._calculate_metrics(session2)
        
        comparison = {
            "duration_change": metrics2["duration_seconds"] - metrics1["duration_seconds"],
            "events_change": metrics2["total_events"] - metrics1["total_events"],
            "files_change": metrics2["files_modified_count"] - metrics1["files_modified_count"],
            "error_rate_change": metrics2["error_rate"] - metrics1["error_rate"],
            "productivity_change": metrics2["activity_intensity"] - metrics1["activity_intensity"]
        }
        
        # Identify improvements
        improvements = []
        if comparison["error_rate_change"] < -0.1:
            improvements.append("Significant reduction in errors")
        if comparison["productivity_change"] > 2:
            improvements.append("Increased productivity")
        
        return {
            "comparison": comparison,
            "improvements": improvements,
            "metrics1": metrics1,
            "metrics2": metrics2
        }


if __name__ == "__main__":
    # Test the analyzer
    analyzer = SessionAnalyzer()
    
    # Create a sample session for testing
    sample_session = {
        "id": "test123",
        "title": "Test Session",
        "start_time": (datetime.now() - timedelta(hours=2)).isoformat(),
        "end_time": datetime.now().isoformat(),
        "events": [
            {
                "timestamp": datetime.now().isoformat(),
                "event_type": "file_created",
                "description": "Created test.py",
                "details": {"path": "test.py"}
            },
            {
                "timestamp": datetime.now().isoformat(),
                "event_type": "error_occurred",
                "description": "Import error",
                "details": {"error": "ModuleNotFoundError: No module named 'foo'"}
            }
        ],
        "files_modified": {
            "test.py": [{"action": "created", "timestamp": datetime.now().isoformat()}]
        },
        "commands_executed": [
            {
                "command": "python test.py",
                "timestamp": datetime.now().isoformat(),
                "return_code": 1,
                "error": "ModuleNotFoundError"
            }
        ],
        "decisions": [],
        "api_calls": []
    }
    
    # Analyze
    analysis = analyzer.analyze_session(sample_session)
    print(json.dumps(analysis, indent=2))