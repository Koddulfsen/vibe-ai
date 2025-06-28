# Vibe Master AI Agents

Collection of AI agents to automate and enhance Vibe Master workflows.

## 🤖 Intelligent Task Analysis Agents

Two complementary agents that analyze Vibe Master tasks and intelligently suggest optimal task breakdowns:

### 🔍 Task Complexity Analyzer Agent
- **Smart Complexity Scoring**: Uses 40+ indicators to analyze task complexity
- **Task Type Detection**: Recognizes different types of tasks (API, UI, testing, etc.)
- **Configurable Thresholds**: Customize when tasks should be expanded
- **Safe Analysis Mode**: Analyze complexity without making changes

### 🧠 Intelligent Task Discovery Agent
- **Codebase Analysis**: Scans actual project files to identify missing components
- **Dependency Detection**: Checks package.json for missing dependencies
- **TODO Discovery**: Finds and incorporates TODO comments from code
- **Smart Subtask Generation**: Creates relevant subtasks based on real project needs
- **No Hardcoded Templates**: Uses intelligent analysis instead of predefined patterns

### Quick Start

```bash
# Step 1: Analyze task complexity (safe)
./agents/run-complexity-analysis.sh

# Step 2: Run intelligent analysis and preview subtasks (safe)
./agents/run-intelligent-analysis.sh

# Step 3: Create subtasks based on intelligent analysis (requires careful review)
./agents/run-intelligent-analysis.sh expand-all
```

### Usage Examples

#### Complexity Analysis Only
```bash
python3 agents/task-complexity-agent.py --verbose
```

#### Intelligent Codebase Analysis
```bash
python3 agents/intelligent-task-agent.py --project /path/to/project
```

#### Analyze Specific Tasks
```bash
python3 agents/intelligent-task-agent.py --tasks=1,2,3
```

#### Execute Intelligent Subtask Creation
```bash
python3 agents/intelligent-task-agent.py --execute --tasks=1
```

### Configuration

Edit `agents/complexity-agent-config.json`:

```json
{
  "expansion_threshold": 6,      // Score needed to trigger expansion
  "max_subtasks": 8,            // Maximum subtasks to create
  "min_subtasks": 3,            // Minimum subtasks for complex tasks
  "auto_expand": false,         // Auto-expand by default
  "dry_run": false,            // Safe mode by default
  "verbose": true              // Detailed output
}
```

### How Complexity Scoring Works

The agent analyzes task titles, descriptions, and details for complexity indicators:

#### High Complexity Indicators (Score 4-5)
- `algorithm`, `security`, `deployment`, `integration`, `offline`, `business rules`

#### Medium Complexity Indicators (Score 2-3)
- `api`, `database`, `performance`, `error handling`, `component`, `testing`

#### Low Complexity Indicators (Score 1)
- `implement`, `create`, `setup`, `configure`

#### Task Type Bonuses
- **API Integration**: +4 complexity
- **Data Pipeline**: +5 complexity  
- **Deployment**: +5 complexity
- **UI Component**: +3 complexity

### Example Analysis Results

```
🔴 Task 2: Integrate Open Food Facts API...
   Complexity Score: 36
   Recommendation: High complexity task (score: 36). Recommend 7 subtasks.
   Complexity Indicators: api, integration, service, endpoint, error handling, caching
   🎯 Suggested Action: vibe-master expand --id=2 --num=7
```

### Command Line Options

```bash
--config <file>        # Custom configuration file
--auto-expand          # Automatically expand complex tasks
--dry-run             # Show what would be done (safe)
--verbose, -v         # Detailed output
--threshold <number>   # Custom complexity threshold (default: 6)
--max-subtasks <number> # Maximum subtasks to create (default: 8)
```

## 🛠️ Agent Development

### Creating New Agents

1. **Copy the base structure** from `task-complexity-agent.py`
2. **Extend the base class** with your specific functionality
3. **Add configuration options** in JSON format
4. **Create a convenience script** for easy usage
5. **Update this README** with documentation

### Base Agent Template

```python
class TaskMasterAgent:
    def __init__(self, config_path: Optional[str] = None):
        self.config = self._load_config(config_path)
    
    def get_taskmaster_tasks(self) -> List[Dict]:
        # Read from .taskmaster/tasks/tasks.json
        pass
    
    def analyze_tasks(self) -> List[Result]:
        # Your analysis logic
        pass
    
    def execute_actions(self, results: List[Result]) -> None:
        # Execute actions based on analysis
        pass
```

## 📋 Planned Agents

### Git Progress Monitor Agent
- Monitors git commits and maps to Vibe Master tasks
- Auto-updates task status based on code changes
- Detects when tasks are likely complete

### Smart Task Discovery Agent
- Scans codebase for TODOs, FIXMEs, and missing implementations
- Creates tasks for discovered work
- Suggests missing setup/testing tasks

### Quality Gate Agent
- Enforces completion criteria before marking tasks done
- Runs tests, linting, and quality checks
- Blocks task completion until criteria met

### Dependency Inference Agent
- Analyzes code relationships to suggest task dependencies
- Auto-updates dependencies when code structure changes
- Validates dependency logic

## 🔧 Requirements

- **Python 3.7+**
- **Vibe Master AI** installed and configured
- **Valid Vibe Master project** (`.taskmaster/` directory)
- **API credits** for auto-expansion features

## 📊 Integration with Vibe Master

The agents seamlessly integrate with Vibe Master:

1. **Read tasks** from `.taskmaster/tasks/tasks.json`
2. **Use Vibe Master CLI** commands for modifications
3. **Respect Vibe Master** configuration and structure
4. **Work with existing** Vibe Master workflows

## 🤝 Contributing

1. Fork the repository
2. Create your agent in the `agents/` directory
3. Add tests and documentation
4. Submit a pull request

## 📝 License

Same license as the main project.

---

**Made with ❤️ to automate your Vibe Master workflows!**