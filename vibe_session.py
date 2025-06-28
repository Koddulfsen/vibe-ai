#!/usr/bin/env python3
"""
vibe Session Command Line Tool
Access and manage vibe.ai sessions
"""

import sys
import json
import argparse
from pathlib import Path
from datetime import datetime, timedelta

# Import session components
from session_manager import get_session_manager
from session_store import SessionStore, SessionQuery
from session_analyzer import SessionAnalyzer
from session_ui import SessionUI


def cmd_current(args):
    """Show current session information"""
    manager = get_session_manager()
    summary = manager.get_session_summary()
    
    if not summary:
        print("No active session")
        return
    
    print(f"Current Session: {summary['title']}")
    print(f"ID: {summary['session_id']}")
    print(f"Duration: {summary['duration_seconds']:.0f} seconds")
    print(f"Events: {summary['total_events']}")
    print(f"Files Modified: {summary['files_modified']}")
    print(f"Commands: {summary['commands_executed']}")
    
    if args.verbose:
        print("\nEvent Breakdown:")
        for event_type, count in summary['event_counts'].items():
            print(f"  {event_type}: {count}")


def cmd_list(args):
    """List recent sessions"""
    store = SessionStore()
    
    query = SessionQuery(
        start_date=datetime.now() - timedelta(days=args.days),
        limit=args.limit
    )
    
    sessions = store.search_sessions(query)
    
    if not sessions:
        print("No sessions found")
        return
    
    print(f"Recent Sessions (last {args.days} days):")
    print("-" * 80)
    
    for session in sessions:
        start_time = datetime.fromisoformat(session['start_time'])
        duration = session.get('duration_seconds', 0)
        
        print(f"{session['id'][:8]} | {session.get('title', 'Untitled'):40} | "
              f"{start_time.strftime('%Y-%m-%d %H:%M')} | "
              f"{duration/60:.0f}m | "
              f"{'✅' if session.get('end_time') else '🔴'}")


def cmd_view(args):
    """View session details"""
    if args.session_id == "current":
        manager = get_session_manager()
        if not manager.current_session:
            print("No active session")
            return
        session_data = manager._session_to_dict()
    else:
        store = SessionStore()
        session_data = store.get_session_by_id(args.session_id)
        
        if not session_data:
            print(f"Session {args.session_id} not found")
            return
    
    if args.json:
        print(json.dumps(session_data, indent=2))
    else:
        # Pretty print
        print(f"Session: {session_data.get('title', 'Untitled')}")
        print(f"ID: {session_data['id']}")
        print(f"Start: {session_data['start_time']}")
        if session_data.get('end_time'):
            print(f"End: {session_data['end_time']}")
        
        print(f"\nEvents: {len(session_data.get('events', []))}")
        print(f"Files Modified: {len(session_data.get('files_modified', {}))}")
        print(f"Commands: {len(session_data.get('commands_executed', []))}")
        
        if args.events:
            print("\nRecent Events:")
            for event in session_data.get('events', [])[-20:]:
                print(f"  [{event['timestamp']}] {event['description']}")


def cmd_analyze(args):
    """Analyze a session"""
    analyzer = SessionAnalyzer()
    
    if args.session_id == "current":
        manager = get_session_manager()
        if not manager.current_session:
            print("No active session")
            return
        session_data = manager._session_to_dict()
    else:
        store = SessionStore()
        session_data = store.get_session_by_id(args.session_id)
        
        if not session_data:
            print(f"Session {args.session_id} not found")
            return
    
    print("Analyzing session...")
    analysis = analyzer.analyze_session(session_data)
    
    if args.json:
        print(json.dumps(analysis, indent=2))
    else:
        # Print summary
        print(analysis['summary'])
        
        # Print key insights
        if analysis['insights']:
            print("\nKey Insights:")
            for insight in analysis['insights'][:5]:
                print(f"\n• {insight['title']}")
                print(f"  {insight['description']}")
                if insight['recommendations']:
                    print("  Recommendations:")
                    for rec in insight['recommendations']:
                        print(f"    - {rec}")


def cmd_export(args):
    """Export a session"""
    manager = get_session_manager()
    
    if args.session_id == "current":
        if not manager.current_session:
            print("No active session")
            return
        content = manager.export_session(args.format)
        session_id = manager.current_session.id
    else:
        store = SessionStore()
        session_data = store.get_session_by_id(args.session_id)
        
        if not session_data:
            print(f"Session {args.session_id} not found")
            return
        
        if args.format == "json":
            content = json.dumps(session_data, indent=2)
        else:
            # Use analyzer to generate markdown
            analyzer = SessionAnalyzer()
            analysis = analyzer.analyze_session(session_data)
            content = analysis['summary']
        
        session_id = args.session_id
    
    # Save to file
    if args.output:
        output_path = Path(args.output)
    else:
        output_path = Path(f"session_{session_id[:8]}.{args.format}")
    
    with open(output_path, 'w') as f:
        f.write(content)
    
    print(f"Session exported to {output_path}")


def cmd_stats(args):
    """Show session statistics"""
    store = SessionStore()
    stats = store.get_statistics(days=args.days)
    
    print(f"Session Statistics (last {args.days} days)")
    print("=" * 50)
    print(f"Total Sessions: {stats['total_sessions']}")
    print(f"Total Time: {stats.get('total_duration', 0)/3600:.1f} hours")
    print(f"Average Session: {stats.get('avg_duration', 0)/60:.1f} minutes")
    print(f"Files Modified: {stats.get('total_files', 0)}")
    print(f"Commands Run: {stats.get('total_commands', 0)}")
    print(f"Sessions with Errors: {stats.get('sessions_with_errors', 0)}")
    
    if stats.get('most_active_days'):
        print("\nMost Active Days:")
        for day in stats['most_active_days'][:5]:
            print(f"  {day['day']}: {day['session_count']} sessions")
    
    if stats.get('most_used_commands'):
        print("\nTop Commands:")
        for cmd in stats['most_used_commands'][:10]:
            print(f"  {cmd['command_name']}: {cmd['usage_count']}")


def cmd_ui(args):
    """Launch interactive UI"""
    ui = SessionUI()
    ui.run()


def cmd_search(args):
    """Search sessions"""
    store = SessionStore()
    
    query = SessionQuery()
    
    if args.days:
        query.start_date = datetime.now() - timedelta(days=args.days)
    
    if args.title:
        query.title_contains = args.title
    
    if args.file:
        query.file_path_contains = args.file
    
    if args.command:
        query.command_contains = args.command
    
    if args.errors:
        query.has_errors = True
    
    sessions = store.search_sessions(query)
    
    print(f"Found {len(sessions)} sessions")
    
    for session in sessions[:20]:
        start_time = datetime.fromisoformat(session['start_time'])
        print(f"{session['id'][:8]} | {session.get('title', 'Untitled'):40} | "
              f"{start_time.strftime('%Y-%m-%d %H:%M')}")
    
    if len(sessions) > 20:
        print(f"\n... and {len(sessions) - 20} more")


def cmd_summary(args):
    """Generate session summary for context switching"""
    manager = get_session_manager()
    
    if not manager.current_session:
        print("No active session")
        return
    
    # Generate comprehensive summary
    summary = manager.get_session_summary()
    session_data = manager._session_to_dict()
    
    print("=== SESSION CONTEXT SUMMARY ===")
    print(f"\nSession: {summary['title']}")
    print(f"Duration: {summary['duration_seconds']/60:.0f} minutes")
    print(f"Started: {manager.current_session.start_time}")
    
    # Files modified
    if manager.current_session.files_modified:
        print("\n📁 Files Modified:")
        for file_path, mods in list(manager.current_session.files_modified.items())[:10]:
            file_name = Path(file_path).name
            actions = set(m["action"] for m in mods)
            print(f"  - {file_name} ({', '.join(actions)})")
    
    # Recent commands
    if manager.current_session.commands_executed:
        print("\n💻 Recent Commands:")
        for cmd in manager.current_session.commands_executed[-5:]:
            print(f"  - {cmd['command']}")
    
    # Key decisions
    if manager.current_session.decisions:
        print("\n🎯 Key Decisions:")
        for decision in manager.current_session.decisions[-3:]:
            print(f"  - {decision['type']}: {decision['description']}")
    
    # Current context
    if manager.current_session.context:
        print("\n📌 Context:")
        for key, value in manager.current_session.context.items():
            print(f"  - {key}: {str(value)[:100]}")
    
    # Export path
    export_path = Path(f"session_context_{manager.current_session.id[:8]}.json")
    with open(export_path, 'w') as f:
        json.dump(session_data, f, indent=2)
    
    print(f"\n✅ Full session data exported to: {export_path}")
    print("\nUse this file to restore context in a new chat session.")


def main():
    parser = argparse.ArgumentParser(
        description="vibe.ai Session Manager - Track and analyze your development sessions"
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Current session
    current_parser = subparsers.add_parser('current', help='Show current session')
    current_parser.add_argument('-v', '--verbose', action='store_true', help='Show detailed info')
    current_parser.set_defaults(func=cmd_current)
    
    # List sessions
    list_parser = subparsers.add_parser('list', help='List recent sessions')
    list_parser.add_argument('-d', '--days', type=int, default=7, help='Days to look back')
    list_parser.add_argument('-l', '--limit', type=int, default=20, help='Maximum sessions to show')
    list_parser.set_defaults(func=cmd_list)
    
    # View session
    view_parser = subparsers.add_parser('view', help='View session details')
    view_parser.add_argument('session_id', help='Session ID or "current"')
    view_parser.add_argument('-j', '--json', action='store_true', help='Output as JSON')
    view_parser.add_argument('-e', '--events', action='store_true', help='Show events')
    view_parser.set_defaults(func=cmd_view)
    
    # Analyze session
    analyze_parser = subparsers.add_parser('analyze', help='Analyze a session')
    analyze_parser.add_argument('session_id', help='Session ID or "current"')
    analyze_parser.add_argument('-j', '--json', action='store_true', help='Output as JSON')
    analyze_parser.set_defaults(func=cmd_analyze)
    
    # Export session
    export_parser = subparsers.add_parser('export', help='Export a session')
    export_parser.add_argument('session_id', help='Session ID or "current"')
    export_parser.add_argument('-f', '--format', choices=['json', 'markdown'], default='markdown')
    export_parser.add_argument('-o', '--output', help='Output file path')
    export_parser.set_defaults(func=cmd_export)
    
    # Statistics
    stats_parser = subparsers.add_parser('stats', help='Show session statistics')
    stats_parser.add_argument('-d', '--days', type=int, default=30, help='Days to analyze')
    stats_parser.set_defaults(func=cmd_stats)
    
    # Search
    search_parser = subparsers.add_parser('search', help='Search sessions')
    search_parser.add_argument('-d', '--days', type=int, help='Days to search back')
    search_parser.add_argument('-t', '--title', help='Title contains')
    search_parser.add_argument('-f', '--file', help='File path contains')
    search_parser.add_argument('-c', '--command', help='Command contains')
    search_parser.add_argument('-e', '--errors', action='store_true', help='Only sessions with errors')
    search_parser.set_defaults(func=cmd_search)
    
    # Summary for context switching
    summary_parser = subparsers.add_parser('summary', help='Generate context summary for switching chats')
    summary_parser.set_defaults(func=cmd_summary)
    
    # Interactive UI
    ui_parser = subparsers.add_parser('ui', help='Launch interactive UI')
    ui_parser.set_defaults(func=cmd_ui)
    
    args = parser.parse_args()
    
    if args.command:
        args.func(args)
    else:
        # Default to showing current session
        cmd_current(argparse.Namespace(verbose=False))


if __name__ == "__main__":
    main()