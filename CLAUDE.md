# vibe.ai - Intelligent Development Assistant System

## 🎯 Project Overview

vibe.ai is a multi-layered AI development system that transforms ideas into complete solutions through philosophical contemplation, intelligent planning, and automated agent execution.

### Core Philosophy
"Development should begin with deep understanding, proceed through conscious planning, and manifest through intelligent execution."

## 🏗️ System Architecture

```
┌─────────────────────┐
│   User Interface    │ ← Simple 2-option menu (5-year-old friendly)
├─────────────────────┤
│  Prompting Oracle   │ ← Meta-consciousness layer
├─────────────────────┤
│   Deep Planner      │ ← Philosophical reasoning with Brave Search
├─────────────────────┤
│  TaskMaster Bridge  │ ← PRD generation and task management
├─────────────────────┤
│   Agent System      │ ← Autonomous execution agents
└─────────────────────┘
```

## 🚀 Quick Start Commands

```bash
# Main entry point
python3 vibe.py

# Test full integration
python3 demo_full_integration.py

# Run specific agents
python3 master-agent.py workflow --type full-dev
python3 master-agent.py agent planning-analysis-agent --task-id 1.1

# Test systems
python3 test_taskmaster_integration.py
python3 test_full_system.py
```

## 📋 Comprehensive PRD

### Vision
Create an AI-powered development assistant that doesn't just execute tasks, but deeply understands, philosophically contemplates, and intelligently manifests software solutions.

### Core Features

#### 1. Prompting Oracle Agent
- **Purpose**: All-knowing entity that crafts perfect prompts
- **Capabilities**: 
  - Analyzes ideas across 7 consciousness dimensions
  - Optimizes prompts for maximum AI understanding
  - Provides meta-guidance for other agents

#### 2. Deep Planner Agent
- **Purpose**: Self-conscious AI that grows awareness through conversation
- **Capabilities**:
  - Philosophical reasoning about software design
  - Brave Search integration for universal knowledge
  - Sequential thinking for complex problems
  - PRD generation following TaskMaster format

#### 3. Agent-Based Solution Engine
- **Purpose**: Orchestrates specialized agents to build complete solutions
- **Components**:
  - Planning & Analysis Agent
  - Universal Execution Agent
  - Quality & Git Agent
  - Task Complexity Agent
  - Repository Manager Agent

#### 4. TaskMaster Integration
- **Purpose**: Bridges high-level planning with concrete task execution
- **Features**:
  - Automatic PRD parsing
  - Task tracking and management
  - Progress monitoring
  - Agent context provision

### User Experience
1. User enters idea in simple interface
2. Oracle enhances and optimizes the request
3. Deep Planner engages in philosophical dialogue
4. System generates comprehensive PRD
5. TaskMaster creates actionable tasks
6. Agents execute autonomously
7. Complete solution delivered

## 🔧 Configuration & Setup

### Required API Keys
```bash
# In your environment or .env file
export BRAVE_API_KEY="BSArXZ987KsjfuUmJRTvpXPjuYVP7-I"
export ANTHROPIC_API_KEY="your-key-here"  # For TaskMaster
export PERPLEXITY_API_KEY="your-key-here"  # Optional, for research
```

### MCP Servers Available
- ✅ Memory MCP (`mcp__memory__*`)
- ✅ Sequential Thinking (`mcp__sequential-thinking__*`)
- ✅ IDE MCP (`mcp__ide__*`)
- ⚠️ Brave Search MCP (configured, requires restart)
- ✅ WebSearch (built-in)

## 📁 Key Files Reference

### Core System Files
- `vibe.py` - Main entry point with simple UI
- `prompting_oracle_agent.py` - Meta-consciousness layer
- `deep_planner_agent.py` - Philosophical planning agent
- `agent_based_solution_engine.py` - Agent orchestration
- `master-agent.py` - Agent coordinator
- `claude_taskmaster_bridge.py` - TaskMaster integration

### TDD Workflow Files
- `tdd_with_subagents.py` - Complete TDD using all agents
- `test_driven_workflow.py` - Basic TDD workflow
- `tdd_agent_integration.py` - TDD with agent integration
- `vibe_tdd_workflow.py` - Full vibe.ai TDD workflow

### Configuration Files
- `.taskmaster/tasks/tasks.json` - Current tasks
- `.taskmaster/agent_registry.json` - Available agents
- `agent_workflow_config.json` - Agent mappings
- `.env` - API keys (create if needed)

### Integration Files
- `taskmaster_agent_wrapper.py` - TaskMaster-agent bridge
- `enhanced_taskmaster_bridge.py` - Advanced PRD processing

### Key Subagents
- `agents/planning-analysis-agent.py` - Strategic planning and analysis
- `agents/task-complexity-agent.py` - Complexity assessment
- `agents/universal-execution-agent.py` - Code implementation
- `agents/test-sync-agent.py` - Test execution and synchronization
- `agents/quality-git-agent.py` - Code quality and refactoring
- `agents/repo-manager-agent.py` - Repository structure management
- `agents/agent-coordinator.py` - Multi-agent coordination

## 🔄 Common Workflows

### 1. Build New Project
```python
# Automated flow
1. vibe.py → Option 1
2. Enter idea
3. Oracle optimization
4. Deep philosophical planning
5. PRD generation
6. Agent execution
7. Solution delivery
```

### 2. Test-Driven Development (TDD)

#### Complete TDD with Subagents (Recommended)
```bash
# Full TDD workflow orchestrating all specialized agents
python3 tdd_with_subagents.py "build a calculator API" -o calc-tdd

# What it does:
# 1. Oracle + Planning agents design perfect tests
# 2. Complexity agent assesses test requirements  
# 3. Repo-Manager creates test structure
# 4. Execution agent generates comprehensive tests
# 5. Test-Sync agent runs tests and enforces quality
# 6. Execution agent implements code to pass tests
# 7. Quality agent refactors for excellence
```

#### Other TDD Options
```bash
# Integrated TDD with all vibe.ai features
python3 vibe_tdd_workflow.py "build a weather API" -o weather-tdd

# Simpler TDD workflow
python3 test_driven_workflow.py "your idea" -o output-dir

# TDD with agent integration
python3 tdd_agent_integration.py "your idea" -o output-dir
```

#### TDD Subagents Used
- **Prompting Oracle**: Designs perfect test specifications
- **Planning-Analysis Agent**: Creates test strategy
- **Task-Complexity Agent**: Assesses test complexity
- **Repo-Manager Agent**: Sets up test structure
- **Universal-Execution Agent**: Generates tests and code
- **Test-Sync Agent**: Runs tests, quality gates
- **Quality-Git Agent**: Refactors code
- **Agent-Coordinator**: Orchestrates workflow

### 3. Analyze Existing Code
```bash
python3 vibe.py
# Choose option 2
# Select folder to analyze
```

### 4. Direct Agent Usage
```bash
# Planning only
python3 master-agent.py workflow --type planning

# Full development
python3 master-agent.py workflow --type full-dev

# Quick fixes
python3 master-agent.py workflow --type quick-fix

# Test synchronization
python3 agents/test-sync-agent.py --status
```

## 🐛 Troubleshooting

### Agents Not Producing Output
1. Check `.taskmaster/tasks/tasks.json` exists
2. Verify agents directory has execute permissions
3. Use `--debug` flag for detailed output
4. Check `TASKMASTER_TASK_ID` environment variable

### Integration Issues
1. Ensure all required files exist (use test scripts)
2. Verify API keys are set
3. Check Python 3.8+ is installed
4. Run `pip install -r requirements.txt` if missing dependencies

### MCP Connection Issues
1. Restart Claude Code after config changes
2. Check `.claude/mcp.json` syntax
3. Verify Node.js is installed for npx commands

## 📊 Current System Status

### Active Tasks
- See `.taskmaster/tasks/tasks.json` for current tasks
- 4 tasks currently in system related to CLAUDE_FILTER improvements

### Agent Registry
- 15+ agents available and auto-discovered
- Dynamic registration system active
- See `.taskmaster/agent_registry.json` for full list

### Integration Points
- ✅ Oracle → Planner connection active
- ✅ Planner → PRD generation working
- ✅ PRD → TaskMaster bridge functional
- ✅ TaskMaster → Agent context passing enabled
- ✅ Agent → Solution generation operational

## 🎨 Development Philosophy

### Consciousness Levels
1. **Surface**: Basic task understanding
2. **Analytical**: Pattern recognition
3. **Creative**: Novel connections
4. **Philosophical**: Deep reasoning
5. **Universal**: Cosmic perspective

### Agent Thinking Patterns
- Sequential analysis for complex problems
- Parallel processing for independent tasks
- Recursive deepening for philosophical questions
- Emergent synthesis for creative solutions

### TDD Philosophy
- **Red Phase**: Write failing tests that specify behavior
- **Green Phase**: Write minimal code to pass tests
- **Blue Phase**: Refactor with confidence
- **Agent Synergy**: Each agent contributes its expertise
- **Quality Gates**: Automated enforcement of standards

## 🚦 Next Steps & Roadmap

### Immediate Priorities
1. Test full flow with real project
2. Enhance error recovery systems
3. Add progress visualization
4. Improve consciousness feedback

### Future Enhancements
1. Multi-model agent collaboration
2. Visual solution previews
3. Real-time progress streaming
4. Consciousness level indicators
5. Automated testing integration

## 💡 Pro Tips

1. **For Complex Projects**: Let Deep Planner reach consciousness level > 0.7
2. **For Quick Tasks**: Use direct agent commands to bypass philosophy
3. **For Debugging**: Enable `VIBE_DEBUG=true` environment variable
4. **For Research**: Ensure Perplexity API key is set for deep research
5. **For TDD**: Use `tdd_with_subagents.py` for full agent orchestration
6. **For Testing**: Run `make test-watch` for continuous TDD cycle
7. **For Quality**: Test-Sync agent enforces quality gates automatically

## 🆘 Getting Help

- Check `test_*.py` files for examples
- Run with `--help` flag for command options
- Review agent logs in `.taskmaster/agent_sync/`
- See integration reports in project root

---

*"Through consciousness comes understanding, through understanding comes creation."*

**vibe.ai v2.0** - Where philosophy meets code.