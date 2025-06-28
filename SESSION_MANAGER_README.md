# vibe.ai Session Manager

A comprehensive session tracking system for vibe.ai that maintains context across chat sessions and tracks all development activities.

## 🚀 Features

### Core Components

1. **session_manager.py** - Main session tracking system
   - Tracks files created/modified/deleted
   - Records all commands executed
   - Monitors API calls
   - Captures decisions made
   - Maintains session context
   - Auto-saves every 30 seconds
   - Thread-safe operations

2. **session_store.py** - Persistent storage backend
   - SQLite database for metadata
   - JSON file storage for full sessions
   - Advanced search capabilities
   - Session archiving
   - Statistics generation
   - Cleanup utilities

3. **session_analyzer.py** - Intelligent analysis
   - Identifies patterns and insights
   - Detects error patterns
   - Analyzes productivity
   - Tracks workflow patterns
   - Generates recommendations
   - Creates summaries

4. **session_ui.py** - Visual browser
   - Rich terminal interface
   - Browse and search sessions
   - View detailed analytics
   - Compare sessions
   - Export capabilities
   - Live activity monitoring

5. **session_integration.py** - Tool integration
   - Decorators for tracking
   - Automatic integration with vibe.ai tools
   - Subprocess patching
   - API call tracking

## 📋 Usage

### Command Line Tool

```bash
# View current session
python3 vibe_session.py current

# Generate context summary for switching chats
python3 vibe_session.py summary

# List recent sessions
python3 vibe_session.py list -d 7

# Analyze a session
python3 vibe_session.py analyze current

# Export session
python3 vibe_session.py export current -f markdown

# Search sessions
python3 vibe_session.py search --title "project" --file "*.py"

# View statistics
python3 vibe_session.py stats -d 30

# Launch interactive UI
python3 vibe_session.py ui
```

### In Code

```python
from session_manager import get_session_manager, track_file, track_command

# Get session manager
session = get_session_manager()

# Track activities
track_file("myfile.py", "created", content)
track_command("python test.py", output="Success")
session.track_api_call("openai", "/completions", params={})
session.track_decision("architecture", "Choose framework", chosen="FastAPI")

# Add context
session.add_context("project_type", "web_api")

# Get summary
summary = session.get_session_summary()
```

### Integration with Existing Tools

The session manager automatically integrates with:
- `vibe.py` - Tracks all task executions
- `idea_to_solution_engine.py` - Tracks PRD generation
- `vibe_perfect.py` - Tracks workflow execution
- `enhanced_taskmaster_bridge.py` - Tracks task processing

## 🔄 Context Switching

When switching Claude sessions:

1. Run summary command:
   ```bash
   python3 vibe_session.py summary
   ```

2. This creates `session_context_[id].json` with:
   - All files modified
   - Commands executed
   - Decisions made
   - Current context
   - Session timeline

3. In new chat, reference this file to restore context

## 📊 Session Structure

Sessions track:
- **Events**: All activities with timestamps
- **Files**: Create/modify/delete operations
- **Commands**: Shell commands with output
- **API Calls**: External service interactions
- **Decisions**: Choices made during development
- **Context**: Key-value pairs for session state
- **Tags**: Categorization for searching

## 🗄️ Storage

- Sessions stored in `~/.vibe/sessions/`
- SQLite database: `~/.vibe/sessions/sessions.db`
- Active session: `~/.vibe/sessions/active_session.json`
- Archives: `~/.vibe/sessions/archive/`

## 🔍 Search Capabilities

Search by:
- Date range
- Title/description
- File paths
- Commands
- Error presence
- Tags
- Duration

## 📈 Analytics

The analyzer provides:
- Error pattern detection
- Productivity metrics
- File change patterns
- Workflow analysis
- Decision patterns
- Key moments identification
- Actionable recommendations

## 🎯 Best Practices

1. **Regular Summaries**: Generate summaries before long breaks
2. **Tag Important Sessions**: Use meaningful titles and tags
3. **Review Analytics**: Check insights to improve workflow
4. **Archive Old Sessions**: Keep storage clean
5. **Export Important Sessions**: Backup critical work

## 🛠️ Advanced Features

### Custom Decorators

```python
from session_integration import SessionIntegration

@SessionIntegration.track_tool_execution("my_tool")
@SessionIntegration.track_file_operation("modified")
def my_function(file_path):
    # Your code here
    pass
```

### Session Comparison

```python
analyzer = SessionAnalyzer()
comparison = analyzer.compare_sessions(session1, session2)
```

### Live Monitoring

The UI supports real-time session monitoring to watch activities as they happen.

## 🚀 Benefits

1. **Never Lose Context**: Complete history of all activities
2. **Better Collaboration**: Share session summaries with team
3. **Learning Tool**: Analyze patterns to improve
4. **Debugging Aid**: Trace back through session history
5. **Productivity Insights**: Understand work patterns

The session manager ensures you never lose track of what you've done in vibe.ai, making it easy to resume work, share progress, and maintain context across different chat sessions.