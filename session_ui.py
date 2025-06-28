#!/usr/bin/env python3
"""
Session UI for vibe.ai
Visual interface for browsing and managing sessions
"""

import os
import sys
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any

# Rich terminal UI
try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.layout import Layout
    from rich.tree import Tree
    from rich.prompt import Prompt, Confirm, IntPrompt
    from rich.markdown import Markdown
    from rich.syntax import Syntax
    from rich.progress import track
    from rich import box
    from rich.columns import Columns
    from rich.text import Text
    RICH_AVAILABLE = True
except ImportError:
    print("Rich library not available. Install with: pip install rich")
    RICH_AVAILABLE = False
    sys.exit(1)

from session_manager import SessionManager, get_session_manager
from session_store import SessionStore, SessionQuery
from session_analyzer import SessionAnalyzer


class SessionUI:
    """Interactive UI for session management"""
    
    def __init__(self):
        self.console = Console()
        self.session_manager = get_session_manager()
        self.session_store = SessionStore()
        self.session_analyzer = SessionAnalyzer()
        self.current_page = 0
        self.page_size = 10
    
    def run(self):
        """Main UI loop"""
        self.console.clear()
        
        while True:
            try:
                self._show_main_menu()
                choice = Prompt.ask(
                    "\n[cyan]Choose an option[/cyan]",
                    choices=["1", "2", "3", "4", "5", "6", "7", "8", "9", "q"],
                    default="1"
                )
                
                if choice == "q":
                    break
                elif choice == "1":
                    self._browse_sessions()
                elif choice == "2":
                    self._view_current_session()
                elif choice == "3":
                    self._search_sessions()
                elif choice == "4":
                    self._view_statistics()
                elif choice == "5":
                    self._analyze_session()
                elif choice == "6":
                    self._compare_sessions()
                elif choice == "7":
                    self._export_session()
                elif choice == "8":
                    self._manage_sessions()
                elif choice == "9":
                    self._view_live_activity()
                    
            except KeyboardInterrupt:
                if Confirm.ask("\n[yellow]Exit session browser?[/yellow]"):
                    break
            except Exception as e:
                self.console.print(f"\n[red]Error: {e}[/red]")
                self.console.print("[dim]Press Enter to continue...[/dim]")
                input()
    
    def _show_main_menu(self):
        """Display main menu"""
        self.console.clear()
        
        # Header
        self.console.print(Panel.fit(
            "[bold cyan]vibe.ai Session Browser[/bold cyan]\n" +
            "[dim]Manage and analyze your development sessions[/dim]",
            border_style="cyan"
        ))
        
        # Get current session info
        current_summary = self.session_manager.get_session_summary()
        
        # Menu options
        menu = Table(show_header=False, box=None, padding=(0, 2))
        menu.add_column(style="cyan", width=3)
        menu.add_column()
        
        menu.add_row("1", "Browse Recent Sessions")
        menu.add_row("2", f"View Current Session [green]({current_summary.get('total_events', 0)} events)[/green]")
        menu.add_row("3", "Search Sessions")
        menu.add_row("4", "View Statistics")
        menu.add_row("5", "Analyze Session")
        menu.add_row("6", "Compare Sessions")
        menu.add_row("7", "Export Session")
        menu.add_row("8", "Manage Sessions (Archive/Cleanup)")
        menu.add_row("9", "View Live Activity")
        menu.add_row("q", "Quit")
        
        self.console.print(menu)
    
    def _browse_sessions(self):
        """Browse recent sessions"""
        self.console.clear()
        self.console.print(Panel("Recent Sessions", style="cyan"))
        
        # Get recent sessions
        query = SessionQuery(
            start_date=datetime.now() - timedelta(days=30),
            limit=100
        )
        sessions = self.session_store.search_sessions(query)
        
        if not sessions:
            self.console.print("[yellow]No sessions found[/yellow]")
            input("\nPress Enter to continue...")
            return
        
        # Paginate
        total_pages = (len(sessions) + self.page_size - 1) // self.page_size
        
        while True:
            self.console.clear()
            self.console.print(Panel(f"Recent Sessions (Page {self.current_page + 1}/{total_pages})", style="cyan"))
            
            # Create table
            table = Table(box=box.ROUNDED)
            table.add_column("ID", style="dim", width=12)
            table.add_column("Title", width=40)
            table.add_column("Start Time", style="cyan")
            table.add_column("Duration", style="green")
            table.add_column("Events", justify="right")
            table.add_column("Files", justify="right")
            table.add_column("Status", justify="center")
            
            # Add sessions for current page
            start_idx = self.current_page * self.page_size
            end_idx = min(start_idx + self.page_size, len(sessions))
            
            for i, session in enumerate(sessions[start_idx:end_idx], start_idx + 1):
                # Format duration
                duration = "N/A"
                if session.get("duration_seconds"):
                    duration = self._format_duration(session["duration_seconds"])
                
                # Status
                status = "✅" if session.get("end_time") else "🔴"
                if session.get("has_errors"):
                    status = "⚠️"
                
                table.add_row(
                    f"{i}. {session['id'][:8]}",
                    session.get("title", "Untitled"),
                    datetime.fromisoformat(session["start_time"]).strftime("%Y-%m-%d %H:%M"),
                    duration,
                    str(session.get("total_events", 0)),
                    str(session.get("files_modified", 0)),
                    status
                )
            
            self.console.print(table)
            
            # Navigation
            nav_text = "\n[cyan]Navigation:[/cyan] "
            if self.current_page > 0:
                nav_text += "[p]revious "
            if self.current_page < total_pages - 1:
                nav_text += "[n]ext "
            nav_text += "[number] to view session, [q]uit"
            
            self.console.print(nav_text)
            choice = Prompt.ask("Choice")
            
            if choice == "q":
                break
            elif choice == "p" and self.current_page > 0:
                self.current_page -= 1
            elif choice == "n" and self.current_page < total_pages - 1:
                self.current_page += 1
            elif choice.isdigit():
                idx = int(choice) - 1
                if 0 <= idx < len(sessions):
                    self._view_session_details(sessions[idx]["id"])
    
    def _view_current_session(self):
        """View current active session"""
        self.console.clear()
        
        summary = self.session_manager.get_session_summary()
        if not summary:
            self.console.print("[yellow]No active session[/yellow]")
            input("\nPress Enter to continue...")
            return
        
        self._display_session_summary(summary)
        
        # Show recent events
        if self.session_manager.current_session:
            self.console.print("\n[cyan]Recent Events:[/cyan]")
            events = self.session_manager.current_session.events[-20:]
            
            for event in events:
                timestamp = datetime.fromisoformat(event.timestamp).strftime("%H:%M:%S")
                self.console.print(f"[dim]{timestamp}[/dim] {event.description}")
        
        # Options
        self.console.print("\n[cyan]Options:[/cyan] [a]nalyze, [e]xport, [r]efresh, [q]uit")
        choice = Prompt.ask("Choice", choices=["a", "e", "r", "q"], default="q")
        
        if choice == "a":
            self._analyze_current_session()
        elif choice == "e":
            self._export_current_session()
        elif choice == "r":
            self._view_current_session()
    
    def _view_session_details(self, session_id: str):
        """View detailed session information"""
        self.console.clear()
        
        # Load full session
        session_data = self.session_store.get_session_by_id(session_id)
        if not session_data:
            self.console.print(f"[red]Session {session_id} not found[/red]")
            input("\nPress Enter to continue...")
            return
        
        # Create layout
        layout = Layout()
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="main"),
            Layout(name="footer", size=3)
        )
        
        # Header
        layout["header"].update(Panel(
            f"[bold]{session_data.get('title', 'Untitled Session')}[/bold]\n" +
            f"[dim]ID: {session_id}[/dim]",
            style="cyan"
        ))
        
        # Main content with tabs
        tab_choice = "1"
        while tab_choice != "q":
            self.console.clear()
            
            tabs = ["1. Overview", "2. Files", "3. Commands", "4. Events", "5. Analysis", "q. Back"]
            self.console.print(Panel(" | ".join(tabs), style="dim"))
            
            if tab_choice == "1":
                self._show_session_overview(session_data)
            elif tab_choice == "2":
                self._show_session_files(session_data)
            elif tab_choice == "3":
                self._show_session_commands(session_data)
            elif tab_choice == "4":
                self._show_session_events(session_data)
            elif tab_choice == "5":
                self._show_session_analysis(session_data)
            
            tab_choice = Prompt.ask("\nTab", choices=["1", "2", "3", "4", "5", "q"], default="1")
    
    def _show_session_overview(self, session_data: Dict[str, Any]):
        """Show session overview"""
        # Basic info
        info_table = Table(show_header=False, box=None)
        info_table.add_column(style="cyan", width=20)
        info_table.add_column()
        
        start_time = datetime.fromisoformat(session_data["start_time"])
        info_table.add_row("Start Time:", start_time.strftime("%Y-%m-%d %H:%M:%S"))
        
        if session_data.get("end_time"):
            end_time = datetime.fromisoformat(session_data["end_time"])
            duration = (end_time - start_time).total_seconds()
            info_table.add_row("End Time:", end_time.strftime("%Y-%m-%d %H:%M:%S"))
            info_table.add_row("Duration:", self._format_duration(duration))
        
        info_table.add_row("Total Events:", str(len(session_data.get("events", []))))
        info_table.add_row("Files Modified:", str(len(session_data.get("files_modified", {}))))
        info_table.add_row("Commands Run:", str(len(session_data.get("commands_executed", []))))
        info_table.add_row("API Calls:", str(len(session_data.get("api_calls", []))))
        info_table.add_row("Decisions Made:", str(len(session_data.get("decisions", []))))
        
        self.console.print(Panel(info_table, title="Session Information"))
        
        # Tags
        if session_data.get("tags"):
            tags_text = " ".join(f"[cyan]#{tag}[/cyan]" for tag in session_data["tags"])
            self.console.print(Panel(tags_text, title="Tags"))
        
        # Context
        if session_data.get("context"):
            context_tree = Tree("Context")
            for key, value in session_data["context"].items():
                context_tree.add(f"{key}: {str(value)[:50]}...")
            self.console.print(Panel(context_tree))
    
    def _show_session_files(self, session_data: Dict[str, Any]):
        """Show files modified in session"""
        files = session_data.get("files_modified", {})
        
        if not files:
            self.console.print("[yellow]No files modified in this session[/yellow]")
            return
        
        # Create tree view
        tree = Tree("📁 Modified Files")
        
        # Group by directory
        dir_files = {}
        for file_path in sorted(files.keys()):
            dir_path = str(Path(file_path).parent)
            if dir_path not in dir_files:
                dir_files[dir_path] = []
            dir_files[dir_path].append(file_path)
        
        for dir_path, file_list in sorted(dir_files.items()):
            dir_branch = tree.add(f"📂 {dir_path}")
            for file_path in file_list:
                mods = files[file_path]
                file_name = Path(file_path).name
                mod_count = len(mods)
                actions = set(m["action"] for m in mods)
                
                # Icon based on action
                icon = "📄"
                if "created" in actions:
                    icon = "✨"
                elif "deleted" in actions:
                    icon = "🗑️"
                elif mod_count > 3:
                    icon = "🔥"
                
                dir_branch.add(f"{icon} {file_name} ({mod_count} changes)")
        
        self.console.print(tree)
    
    def _show_session_commands(self, session_data: Dict[str, Any]):
        """Show commands executed in session"""
        commands = session_data.get("commands_executed", [])
        
        if not commands:
            self.console.print("[yellow]No commands executed in this session[/yellow]")
            return
        
        table = Table(title="Commands Executed")
        table.add_column("Time", style="dim", width=10)
        table.add_column("Command", style="cyan")
        table.add_column("Status", justify="center", width=10)
        
        for cmd in commands[-50:]:  # Last 50 commands
            timestamp = datetime.fromisoformat(cmd["timestamp"]).strftime("%H:%M:%S")
            
            # Status icon
            status = "✅"
            if cmd.get("return_code") and cmd["return_code"] != 0:
                status = "❌"
            elif cmd.get("error"):
                status = "⚠️"
            
            # Truncate long commands
            command = cmd["command"]
            if len(command) > 80:
                command = command[:77] + "..."
            
            table.add_row(timestamp, command, status)
        
        self.console.print(table)
    
    def _show_session_events(self, session_data: Dict[str, Any]):
        """Show session events timeline"""
        events = session_data.get("events", [])
        
        if not events:
            self.console.print("[yellow]No events in this session[/yellow]")
            return
        
        # Group events by type
        event_groups = {}
        for event in events:
            event_type = event["event_type"]
            if event_type not in event_groups:
                event_groups[event_type] = []
            event_groups[event_type].append(event)
        
        # Show summary
        summary_table = Table(title="Event Summary")
        summary_table.add_column("Event Type", style="cyan")
        summary_table.add_column("Count", justify="right")
        summary_table.add_column("Percentage", justify="right")
        
        total = len(events)
        for event_type, event_list in sorted(event_groups.items(), key=lambda x: len(x[1]), reverse=True):
            count = len(event_list)
            percentage = count / total * 100
            summary_table.add_row(
                event_type.replace("_", " ").title(),
                str(count),
                f"{percentage:.1f}%"
            )
        
        self.console.print(summary_table)
        
        # Show recent events
        self.console.print("\n[cyan]Recent Events:[/cyan]")
        for event in events[-30:]:
            timestamp = datetime.fromisoformat(event["timestamp"]).strftime("%H:%M:%S")
            self.console.print(f"[dim]{timestamp}[/dim] {event['description']}")
    
    def _show_session_analysis(self, session_data: Dict[str, Any]):
        """Show session analysis"""
        self.console.print("[cyan]Analyzing session...[/cyan]")
        
        analysis = self.session_analyzer.analyze_session(session_data)
        
        # Summary
        self.console.print(Panel(Markdown(analysis["summary"]), title="Summary", border_style="green"))
        
        # Insights
        if analysis["insights"]:
            self.console.print("\n[cyan]Key Insights:[/cyan]")
            for insight in analysis["insights"]:
                severity_color = {
                    "info": "blue",
                    "warning": "yellow",
                    "suggestion": "magenta"
                }.get(insight["severity"], "white")
                
                self.console.print(f"\n[{severity_color}]• {insight['title']}[/{severity_color}]")
                self.console.print(f"  {insight['description']}")
                if insight["recommendations"]:
                    self.console.print("  [dim]Recommendations:[/dim]")
                    for rec in insight["recommendations"]:
                        self.console.print(f"    - {rec}")
        
        # Key moments
        if analysis["key_moments"]:
            self.console.print("\n[cyan]Key Moments:[/cyan]")
            for moment in analysis["key_moments"][:5]:
                timestamp = datetime.fromisoformat(moment["timestamp"]).strftime("%H:%M:%S")
                self.console.print(f"[dim]{timestamp}[/dim] {moment['type']}: {moment['description']}")
    
    def _search_sessions(self):
        """Search sessions with filters"""
        self.console.clear()
        self.console.print(Panel("Search Sessions", style="cyan"))
        
        # Build query
        query = SessionQuery()
        
        # Date range
        if Confirm.ask("Filter by date range?", default=False):
            days_back = IntPrompt.ask("Days back", default=30)
            query.start_date = datetime.now() - timedelta(days=days_back)
        
        # Title search
        title_search = Prompt.ask("Title contains (leave empty to skip)", default="")
        if title_search:
            query.title_contains = title_search
        
        # File search
        file_search = Prompt.ask("File path contains (leave empty to skip)", default="")
        if file_search:
            query.file_path_contains = file_search
        
        # Command search
        cmd_search = Prompt.ask("Command contains (leave empty to skip)", default="")
        if cmd_search:
            query.command_contains = cmd_search
        
        # Error filter
        if Confirm.ask("Only show sessions with errors?", default=False):
            query.has_errors = True
        
        # Execute search
        self.console.print("\n[cyan]Searching...[/cyan]")
        results = self.session_store.search_sessions(query)
        
        if not results:
            self.console.print("[yellow]No sessions found matching criteria[/yellow]")
            input("\nPress Enter to continue...")
            return
        
        # Display results
        self.console.print(f"\n[green]Found {len(results)} sessions[/green]")
        
        table = Table()
        table.add_column("ID", style="dim")
        table.add_column("Title")
        table.add_column("Date", style="cyan")
        table.add_column("Duration")
        
        for session in results[:20]:  # Show first 20
            duration = "N/A"
            if session.get("duration_seconds"):
                duration = self._format_duration(session["duration_seconds"])
            
            table.add_row(
                session["id"][:8],
                session.get("title", "Untitled"),
                datetime.fromisoformat(session["start_time"]).strftime("%Y-%m-%d"),
                duration
            )
        
        self.console.print(table)
        
        if len(results) > 20:
            self.console.print(f"\n[dim]... and {len(results) - 20} more[/dim]")
        
        input("\nPress Enter to continue...")
    
    def _view_statistics(self):
        """View session statistics"""
        self.console.clear()
        self.console.print(Panel("Session Statistics", style="cyan"))
        
        days = IntPrompt.ask("Statistics for last N days", default=30)
        stats = self.session_store.get_statistics(days=days)
        
        # Overall stats
        overall = Table(title=f"Overall Statistics (Last {days} days)")
        overall.add_column("Metric", style="cyan")
        overall.add_column("Value", justify="right")
        
        overall.add_row("Total Sessions", str(stats["total_sessions"]))
        overall.add_row("Total Time", self._format_duration(stats.get("total_duration", 0)))
        overall.add_row("Average Session", self._format_duration(stats.get("avg_duration", 0)))
        overall.add_row("Total Files Modified", str(stats.get("total_files", 0)))
        overall.add_row("Total Commands", str(stats.get("total_commands", 0)))
        overall.add_row("Total API Calls", str(stats.get("total_api_calls", 0)))
        overall.add_row("Sessions with Errors", str(stats.get("sessions_with_errors", 0)))
        
        self.console.print(overall)
        
        # Most active days
        if stats.get("most_active_days"):
            self.console.print("\n[cyan]Most Active Days:[/cyan]")
            for day_stat in stats["most_active_days"][:5]:
                self.console.print(
                    f"  {day_stat['day']}: {day_stat['session_count']} sessions, "
                    f"{self._format_duration(day_stat['total_duration'])}"
                )
        
        # Most modified files
        if stats.get("most_modified_files"):
            self.console.print("\n[cyan]Most Modified Files:[/cyan]")
            for file_stat in stats["most_modified_files"][:10]:
                file_name = Path(file_stat["file_path"]).name
                self.console.print(
                    f"  {file_name}: {file_stat['total_modifications']} changes "
                    f"in {file_stat['session_count']} sessions"
                )
        
        # Most used commands
        if stats.get("most_used_commands"):
            cmd_table = Table(title="Most Used Commands")
            cmd_table.add_column("Command", style="cyan")
            cmd_table.add_column("Count", justify="right")
            
            for cmd_stat in stats["most_used_commands"][:10]:
                cmd_table.add_row(cmd_stat["command_name"], str(cmd_stat["usage_count"]))
            
            self.console.print(cmd_table)
        
        input("\nPress Enter to continue...")
    
    def _analyze_session(self):
        """Choose and analyze a session"""
        self.console.clear()
        
        # Get session ID
        session_id = Prompt.ask("Enter session ID (or 'current' for active session)")
        
        if session_id == "current":
            if not self.session_manager.current_session:
                self.console.print("[yellow]No active session[/yellow]")
                input("\nPress Enter to continue...")
                return
            session_data = self.session_manager._session_to_dict()
        else:
            session_data = self.session_store.get_session_by_id(session_id)
            if not session_data:
                self.console.print(f"[red]Session {session_id} not found[/red]")
                input("\nPress Enter to continue...")
                return
        
        self._show_session_analysis(session_data)
        input("\nPress Enter to continue...")
    
    def _compare_sessions(self):
        """Compare two sessions"""
        self.console.clear()
        self.console.print(Panel("Compare Sessions", style="cyan"))
        
        # Get session IDs
        id1 = Prompt.ask("First session ID")
        id2 = Prompt.ask("Second session ID")
        
        # Load sessions
        session1 = self.session_store.get_session_by_id(id1)
        session2 = self.session_store.get_session_by_id(id2)
        
        if not session1 or not session2:
            self.console.print("[red]One or both sessions not found[/red]")
            input("\nPress Enter to continue...")
            return
        
        # Compare
        comparison = self.session_analyzer.compare_sessions(session1, session2)
        
        # Display comparison
        table = Table(title="Session Comparison")
        table.add_column("Metric", style="cyan")
        table.add_column(f"Session 1\n{id1[:8]}", justify="right")
        table.add_column(f"Session 2\n{id2[:8]}", justify="right")
        table.add_column("Change", justify="right")
        
        # Duration
        dur1 = comparison["metrics1"]["duration_seconds"]
        dur2 = comparison["metrics2"]["duration_seconds"]
        dur_change = comparison["comparison"]["duration_change"]
        table.add_row(
            "Duration",
            self._format_duration(dur1),
            self._format_duration(dur2),
            f"{'+' if dur_change > 0 else ''}{self._format_duration(abs(dur_change))}"
        )
        
        # Events
        table.add_row(
            "Total Events",
            str(comparison["metrics1"]["total_events"]),
            str(comparison["metrics2"]["total_events"]),
            f"{comparison['comparison']['events_change']:+d}"
        )
        
        # Files
        table.add_row(
            "Files Modified",
            str(comparison["metrics1"]["files_modified_count"]),
            str(comparison["metrics2"]["files_modified_count"]),
            f"{comparison['comparison']['files_change']:+d}"
        )
        
        # Error rate
        err1 = comparison["metrics1"]["error_rate"] * 100
        err2 = comparison["metrics2"]["error_rate"] * 100
        err_change = comparison["comparison"]["error_rate_change"] * 100
        table.add_row(
            "Error Rate",
            f"{err1:.1f}%",
            f"{err2:.1f}%",
            f"{err_change:+.1f}%"
        )
        
        self.console.print(table)
        
        # Improvements
        if comparison["improvements"]:
            self.console.print("\n[green]Improvements:[/green]")
            for improvement in comparison["improvements"]:
                self.console.print(f"  ✅ {improvement}")
        
        input("\nPress Enter to continue...")
    
    def _export_session(self):
        """Export a session"""
        self.console.clear()
        
        session_id = Prompt.ask("Enter session ID (or 'current' for active session)")
        
        if session_id == "current":
            if not self.session_manager.current_session:
                self.console.print("[yellow]No active session[/yellow]")
                input("\nPress Enter to continue...")
                return
        
        format_choice = Prompt.ask(
            "Export format",
            choices=["json", "markdown"],
            default="markdown"
        )
        
        # Export
        if session_id == "current":
            content = self.session_manager.export_session(format_choice)
            filename = f"session_{self.session_manager.current_session.id}.{format_choice}"
        else:
            session_data = self.session_store.get_session_by_id(session_id)
            if not session_data:
                self.console.print(f"[red]Session {session_id} not found[/red]")
                input("\nPress Enter to continue...")
                return
            
            if format_choice == "json":
                content = json.dumps(session_data, indent=2)
            else:
                # Convert to markdown using session manager
                temp_session = self.session_manager.current_session
                self.session_manager.current_session = session_data
                content = self.session_manager._export_markdown()
                self.session_manager.current_session = temp_session
            
            filename = f"session_{session_id}.{format_choice}"
        
        # Save
        output_path = Path(filename)
        with open(output_path, 'w') as f:
            f.write(content)
        
        self.console.print(f"[green]Session exported to {output_path}[/green]")
        input("\nPress Enter to continue...")
    
    def _export_current_session(self):
        """Export current session"""
        format_choice = Prompt.ask(
            "Export format",
            choices=["json", "markdown"],
            default="markdown"
        )
        
        content = self.session_manager.export_session(format_choice)
        filename = f"session_{self.session_manager.current_session.id}.{format_choice}"
        
        with open(filename, 'w') as f:
            f.write(content)
        
        self.console.print(f"[green]Session exported to {filename}[/green]")
        input("\nPress Enter to continue...")
    
    def _analyze_current_session(self):
        """Analyze current session"""
        session_data = self.session_manager._session_to_dict()
        self._show_session_analysis(session_data)
        input("\nPress Enter to continue...")
    
    def _manage_sessions(self):
        """Session management options"""
        self.console.clear()
        self.console.print(Panel("Session Management", style="cyan"))
        
        options = Table(show_header=False, box=None)
        options.add_column(style="cyan", width=3)
        options.add_column()
        
        options.add_row("1", "Archive old sessions")
        options.add_row("2", "Clean up incomplete sessions")
        options.add_row("3", "Delete specific session")
        options.add_row("q", "Back")
        
        self.console.print(options)
        
        choice = Prompt.ask("Choice", choices=["1", "2", "3", "q"])
        
        if choice == "1":
            days = IntPrompt.ask("Archive sessions older than N days", default=30)
            count = self.session_store.archive_old_sessions(days)
            self.console.print(f"[green]Archived {count} sessions[/green]")
            input("\nPress Enter to continue...")
        
        elif choice == "2":
            count = self.session_store.cleanup_incomplete_sessions()
            self.console.print(f"[green]Cleaned up {count} incomplete sessions[/green]")
            input("\nPress Enter to continue...")
        
        elif choice == "3":
            session_id = Prompt.ask("Session ID to delete")
            if Confirm.ask(f"[red]Delete session {session_id}?[/red]", default=False):
                # Implementation would go here
                self.console.print("[yellow]Delete functionality not implemented yet[/yellow]")
                input("\nPress Enter to continue...")
    
    def _view_live_activity(self):
        """View live session activity"""
        self.console.clear()
        
        if not self.session_manager.current_session:
            self.console.print("[yellow]No active session[/yellow]")
            input("\nPress Enter to continue...")
            return
        
        self.console.print(Panel("Live Session Activity", style="cyan"))
        self.console.print("[dim]Press Ctrl+C to stop[/dim]\n")
        
        last_event_count = 0
        
        try:
            while True:
                # Get current events
                events = self.session_manager.current_session.events
                
                # Show new events
                if len(events) > last_event_count:
                    for event in events[last_event_count:]:
                        timestamp = datetime.fromisoformat(event.timestamp).strftime("%H:%M:%S")
                        
                        # Color based on event type
                        color = "white"
                        if "error" in event.event_type:
                            color = "red"
                        elif "file" in event.event_type:
                            color = "green"
                        elif "command" in event.event_type:
                            color = "cyan"
                        elif "api" in event.event_type:
                            color = "yellow"
                        
                        self.console.print(
                            f"[dim]{timestamp}[/dim] [{color}]{event.event_type}[/{color}] "
                            f"{event.description}"
                        )
                    
                    last_event_count = len(events)
                
                # Sleep briefly
                import time
                time.sleep(1)
                
        except KeyboardInterrupt:
            pass
    
    def _display_session_summary(self, summary: Dict[str, Any]):
        """Display session summary"""
        # Create info table
        info = Table(show_header=False, box=None)
        info.add_column(style="cyan", width=20)
        info.add_column()
        
        info.add_row("Session ID:", summary["session_id"][:8])
        info.add_row("Title:", summary["title"])
        info.add_row("Duration:", self._format_duration(summary["duration_seconds"]))
        info.add_row("Total Events:", str(summary["total_events"]))
        info.add_row("Files Modified:", str(summary["files_modified"]))
        info.add_row("Commands Run:", str(summary["commands_executed"]))
        info.add_row("API Calls:", str(summary["api_calls"]))
        info.add_row("Decisions Made:", str(summary["decisions_made"]))
        
        self.console.print(Panel(info, title="Current Session"))
        
        # Event breakdown
        if summary["event_counts"]:
            event_table = Table(title="Event Breakdown")
            event_table.add_column("Event Type", style="cyan")
            event_table.add_column("Count", justify="right")
            
            for event_type, count in sorted(summary["event_counts"].items(), 
                                          key=lambda x: x[1], reverse=True):
                event_table.add_row(
                    event_type.replace("_", " ").title(),
                    str(count)
                )
            
            self.console.print(event_table)
    
    def _format_duration(self, seconds: float) -> str:
        """Format duration nicely"""
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


def main():
    """Main entry point"""
    ui = SessionUI()
    ui.run()


if __name__ == "__main__":
    main()