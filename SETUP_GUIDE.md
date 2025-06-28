# Claude Code Intelligent Filter - Setup Guide

## 🎯 What This System Does

Imagine you're working in Claude Code and you type:
- "what is 2+2?" → System says: "Handle this directly, it's simple"
- "implement a complete authentication system" → System says: "Use specialized agents for this complex task"

## 📁 Current File Structure

```
your-project/
├── tools/
│   └── vibe.ai/
│       ├── claude_code_filter.py      # The brain (sequential thinking)
│       ├── claude-code-wrapper.py     # The interface
│       ├── master-agent.py           # Agent coordinator
│       ├── agents/                   # Specialized agents
│       │   ├── planning-analysis-agent.py
│       │   ├── universal-execution-agent.py
│       │   ├── quality-git-agent.py
│       │   └── ...
│       └── start.py                  # Interactive launcher
```

## 🚀 How to Use It RIGHT NOW

### Method 1: Manual Pre-Filter (Current Setup)
```bash
# Before asking Claude Code anything complex, run:
python3 tools/vibe.ai/claude-code-wrapper.py --filter "implement user authentication"

# It will tell you:
# ✅ "Handle directly" OR 🤖 "Use agents first"
```

### Method 2: Interactive Mode
```bash
# Run the intelligent interface:
python3 tools/vibe.ai/claude-code-integration.py --interactive

# Then type your requests and it guides you
```

### Method 3: Test Your Prompts
```bash
# Test different prompts to see how it routes them:
python3 tools/vibe.ai/claude_code_filter.py "your prompt here" --verbose
```

## 🎯 Ideal Future Integration

What we WANT is for this to be automatic:

```
You type in Claude Code: "implement authentication"
    ↓
Filter automatically analyzes it
    ↓
"This is complex, let me run agents first..."
    ↓
Agents do the heavy lifting
    ↓
Claude Code gets enhanced context and results
```

## 🔧 Current Workflow (Manual)

1. **You have a task** (e.g., "build a login system")

2. **Check with the filter first:**
   ```bash
   python3 tools/vibe.ai/claude-code-wrapper.py --filter "build a login system"
   ```

3. **Filter tells you:**
   - ✅ "Simple - just ask Claude Code directly"
   - 🤖 "Complex - run agents first: `python3 master-agent.py workflow --type full-dev`"

4. **If agents recommended, run them:**
   ```bash
   python3 tools/vibe.ai/master-agent.py analyze
   # Agents analyze your codebase, plan the work, etc.
   ```

5. **Then ask Claude Code** with the enhanced context

## 🎮 Try It Out - Examples

### Simple Query (Direct to Claude Code):
```bash
python3 claude-code-wrapper.py --filter "what is the difference between var and let in JavaScript?"
# → ✅ Handle directly in Claude Code
```

### Complex Implementation (Use Agents First):
```bash
python3 claude-code-wrapper.py --filter "implement OAuth authentication with Google, Facebook, and email signup"
# → 🤖 Route to agents first
# → Run: python3 master-agent.py workflow --type full-dev
```

### File Operations (Maybe Agents):
```bash
python3 claude-code-wrapper.py --filter "read all Python files and create a dependency graph"
# → 🔄 Hybrid approach - agents for analysis, Claude Code for presentation
```

## 🏢 Workspace Setup

### Minimal Setup (Works Now):
```
your-project/
├── (your code files)
└── tools/
    └── vibe.ai/
        └── (all the agent files we created)
```

### Required Files:
- `claude_code_filter.py` - The brain
- `claude-code-wrapper.py` - The interface  
- `master-agent.py` - Agent coordinator
- `agents/` folder with agent scripts

### Dependencies:
```bash
pip install requests  # For GitHub integration (optional)
```

## 🔮 Future Vision: Automatic Integration

**What we're building toward:**

1. **Seamless Integration**: Filter runs automatically before every Claude Code interaction

2. **Background Processing**: Agents run in background when beneficial

3. **Enhanced Context**: Claude Code always has the best possible context

4. **Smart Caching**: Results cached so agents don't re-run unnecessarily

## 🎯 Quick Start Command

```bash
# Clone or download the vibe.ai folder to your project
# Then test it:
cd tools/vibe.ai
python3 claude-code-wrapper.py --demo
```

This shows you exactly how it routes different types of requests!

## 🤔 When to Use What

| Your Request | Recommended Flow |
|-------------|------------------|
| "What is X?" | Direct to Claude Code |
| "How does Y work?" | Direct to Claude Code |
| "Fix this small bug" | Direct to Claude Code |
| "Implement feature X" | Check filter first |
| "Analyze entire codebase" | Definitely use agents |
| "Set up CI/CD pipeline" | Definitely use agents |
| "Multi-step complex task" | Definitely use agents |

## 🚧 Current Limitations

- Manual process (you have to remember to run the filter)
- Requires command line usage
- Not yet integrated directly into Claude Code interface
- Agent execution can take time

## 🎯 Next Steps

1. **Try the demo** to see how it works
2. **Test with your real prompts** to see the routing decisions
3. **Use it manually** for complex tasks to see the benefits
4. **Provide feedback** on accuracy of routing decisions