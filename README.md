# Vibe.AI Agent System

A comprehensive, standalone agent system for intelligent task management, execution, and quality control.

## 🚀 Super Quick Start (New!)

**One command does everything:**
```bash
./run
```

That's it! The system will:
- ✅ Check dependencies and auto-install what's needed
- 🎯 Launch an interactive menu interface
- 🤖 Guide you through everything step-by-step

## 🎛️ Interactive Interface

The new interactive launcher provides:
- 📋 **Smart Menu System** - Choose what you want to do
- 🔍 **Auto-Detection** - Automatically understands your project
- 🛠️ **Dependency Management** - Installs packages automatically
- 🎯 **Guided Workflows** - Step-by-step guidance
- ⚡ **One-Click Operations** - Complex tasks made simple

### Menu Options:
- **Analysis & Planning** - Understand your project
- **Quick Development** - Auto-detect and run optimal workflow
- **Full Workflow** - Complete automation pipeline
- **Quality Checks** - Comprehensive testing and validation
- **System Setup** - Automatic dependency installation

## 🖥️ Advanced CLI (For Power Users)

```bash
# Direct CLI commands (if you prefer command line)
./master-agent.py status
./master-agent.py analyze --tag your-tag
./master-agent.py workflow --type full-dev
```

## 📁 System Architecture

```
vibe.ai/
├── master-agent.py          # Main entry point - orchestrates all agents
├── agents/                  # Core agent implementations
│   ├── planning-analysis-agent.py    # Planning & complexity analysis
│   ├── universal-execution-agent.py  # Task execution
│   ├── quality-git-agent.py         # Quality control & git operations
│   ├── agent-coordinator.py         # Agent coordination & sync
│   └── repo-manager-agent.py        # Repository management
├── config/                  # Configuration files
├── docs/                   # Documentation & architecture
├── scripts/               # Helper scripts
└── tests/                # Test suites
```

## 🎯 Core Agents

### 1. Planning & Analysis Agent
- **Purpose**: Intelligent task analysis and complexity scoring
- **Features**: Sequential thinking, complexity analysis, subtask generation
- **Usage**: `./master-agent.py analyze --tag agents`

### 2. Universal Execution Agent  
- **Purpose**: Automated task execution and implementation
- **Features**: Multi-language support, dependency resolution, testing integration
- **Usage**: `./master-agent.py execute --task-id 1.2`

### 3. Quality & Git Agent
- **Purpose**: Code quality enforcement and git workflow management
- **Features**: Linting, testing, commit management, branch workflows
- **Usage**: `./master-agent.py quality --fix`

### 4. Agent Coordinator
- **Purpose**: Multi-agent synchronization and workflow orchestration
- **Features**: State management, conflict resolution, quality gates
- **Usage**: `./master-agent.py agent coordinator --workflow planning`

### 5. Repository Manager
- **Purpose**: Repository structure and file management
- **Features**: File organization, backup management, structure analysis
- **Usage**: `./master-agent.py agent repo --action sync`

## 🔧 Workflows

### Full Development Workflow
Complete end-to-end development process:
```bash
./master-agent.py workflow --type full-dev --tag your-project
```

**Phases:**
1. **Analysis & Planning** - Task complexity analysis and planning
2. **Repository Management** - Structure sync and organization  
3. **Task Execution** - Automated implementation
4. **Quality Control** - Testing, linting, and git operations

### Other Workflows

```bash
# Analysis-focused workflow
./master-agent.py workflow --type planning --tag research

# Quick fix workflow
./master-agent.py workflow --type quick-fix --task-id 2.3

# Quality-only workflow  
./master-agent.py workflow --type quality --fix
```

## 🛠️ Setup & Installation

### Prerequisites
- Python 3.8+
- Git
- Vibe Master CLI (for task data)

### Installation
1. Clone or download this agent system
2. Make master agent executable: `chmod +x master-agent.py`
3. Configure your project with Vibe Master tasks
4. Run: `./master-agent.py status` to verify setup

### Configuration
- **Config files**: Place in `config/` directory
- **Agent settings**: Modify individual agent files in `agents/`
- **Custom scripts**: Add to `scripts/` directory

## 📊 Features

### Intelligent Analysis
- **Complexity Scoring**: Automated task complexity assessment
- **Sequential Thinking**: Advanced problem-solving reasoning
- **Dependency Detection**: Automatic dependency mapping
- **Risk Assessment**: Project risk and challenge identification

### Automated Execution
- **Multi-Language Support**: Python, JavaScript, Bash, and more
- **Dependency Management**: Automatic package installation
- **Testing Integration**: Automated test execution
- **Error Recovery**: Intelligent error handling and retry logic

### Quality Assurance
- **Code Linting**: Multi-language code quality checks
- **Test Automation**: Unit, integration, and E2E testing
- **Git Workflows**: Branch management and commit automation
- **Documentation**: Automated documentation generation

### Orchestration
- **Multi-Agent Coordination**: Synchronized agent execution
- **Workflow Management**: Predefined and custom workflows
- **State Management**: Persistent state across agent runs
- **Conflict Resolution**: Automatic handling of agent conflicts

## 🎛️ Command Reference

### Main Commands
```bash
./master-agent.py status                    # System status
./master-agent.py analyze [options]         # Run analysis
./master-agent.py execute [options]         # Run execution  
./master-agent.py quality [options]         # Run quality checks
./master-agent.py workflow [options]        # Run workflow
./master-agent.py agent <name> [args]       # Run specific agent
```

### Analysis Options
```bash
--tag <tag>           # Analyze specific tag
--no-complexity       # Skip complexity analysis
```

### Execution Options
```bash
--task-id <id>        # Execute specific task
--auto                # Auto mode execution
```

### Quality Options
```bash
--fix                 # Auto-fix issues
```

### Workflow Options
```bash
--type <type>         # Workflow type: full-dev, planning, quick-fix, etc.
--tag <tag>           # Project tag
--task-id <id>        # Specific task
--auto                # Auto mode
--fix                 # Auto-fix issues
```

## 🔍 Monitoring & Debugging

### Status Monitoring
```bash
./master-agent.py status
```

### Individual Agent Testing
```bash
./master-agent.py agent planning --tag test --verbose
./master-agent.py agent execution --task-id 1.1 --verbose
./master-agent.py agent quality --verbose
```

### Log Files
- Agent coordination logs: Check individual agent output
- Error logs: Captured in agent results
- Workflow logs: Displayed in master agent output

## 🤝 Integration

### With Vibe Master CLI
This system works seamlessly with Vibe Master CLI:
```bash
# Generate tasks with Task Master
vibe-master parse-prd your-prd.txt

# Run agents on the tasks
./master-agent.py workflow --type full-dev
```

### With IDEs
- Use as external tools in your IDE
- Integrate with VS Code tasks
- Add as build/test commands

### With CI/CD
```bash
# In your CI pipeline
./master-agent.py workflow --type quality --fix
./master-agent.py analyze --tag ci-build
```

## 📈 Advanced Usage

### Custom Workflows
Modify `master-agent.py` to add custom workflow types for your specific needs.

### Agent Extension
Add new agents by:
1. Creating agent script in `agents/`
2. Adding to `self.agents` dict in `MasterAgent`
3. Implementing workflow integration

### Configuration Management
- Place project-specific configs in `config/`
- Use environment variables for sensitive data
- Customize agent behavior through config files

## 🚀 Performance Tips

1. **Use specific tags** for faster analysis
2. **Enable auto mode** for non-interactive execution
3. **Run quality checks incrementally** during development
4. **Use planning workflow** for complex projects before execution

## 📝 Contributing

This is a standalone, shareable system. To customize:
1. Fork or copy the entire `vibe.ai/` directory
2. Modify agents in `agents/` directory
3. Update `master-agent.py` for new workflows
4. Add tests in `tests/` directory

## 🎯 Roadmap

- [ ] Web interface for agent management
- [ ] Real-time agent monitoring dashboard  
- [ ] Plugin system for custom agents
- [ ] Integration with popular project management tools
- [ ] Advanced machine learning for task prediction

---

**Vibe.AI Agent System** - Intelligent automation for modern development workflows.