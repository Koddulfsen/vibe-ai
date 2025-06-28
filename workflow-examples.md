# Real-World Workflow Examples

## 🎯 Scenario 1: Working on a React Project

### Your Setup:
```
~/projects/my-react-app/
├── src/
├── package.json
└── README.md

~/dev-tools/
└── vibe.ai/  # Installed once, globally
```

### Your Workflow:
```bash
# 1. You're in your React project
cd ~/projects/my-react-app

# 2. You want to ask Claude Code: "Add authentication to my React app"
# 3. First, check with the filter:
python3 ~/dev-tools/vibe.ai/claude_code_filter.py "Add authentication to my React app"

# 4. Filter responds:
# 🤖 "Complex task - use agents first"
# Command: python3 ~/dev-tools/vibe.ai/master-agent.py analyze

# 5. Run the agents (they analyze YOUR current project):
cd ~/dev-tools/vibe.ai
python3 master-agent.py analyze

# 6. Agents scan ~/projects/my-react-app and create analysis
# 7. Now ask Claude Code with enhanced context
```

## 🎯 Scenario 2: Working on Multiple Projects

### Your Setup:
```
~/projects/
├── project-a/
├── project-b/
└── project-c/

~/dev-tools/vibe.ai/  # One installation for all projects
```

### Your Workflow:
```bash
# Working on project A
cd ~/projects/project-a
python3 ~/dev-tools/vibe.ai/claude_code_filter.py "implement CI/CD pipeline"

# Working on project B  
cd ~/projects/project-b
python3 ~/dev-tools/vibe.ai/claude_code_filter.py "optimize database queries"

# Same tool, different projects!
```

## 🎯 Scenario 3: Team Setup

### Team Setup:
```bash
# Each team member installs once:
git clone <vibe.ai-repo> ~/dev-tools/vibe.ai

# Or company-wide installation:
/opt/company-tools/vibe.ai/
```

### Team Workflow:
```bash
# Alice working on feature A:
cd ~/work/main-app
python3 ~/dev-tools/vibe.ai/claude_code_filter.py "add payment integration"

# Bob working on feature B:
cd ~/work/api-service  
python3 ~/dev-tools/vibe.ai/claude_code_filter.py "implement rate limiting"
```

## 🎯 Key Points

✅ **Install once, use everywhere** - You don't need to copy files to every project
✅ **Works from any directory** - The filter can analyze any project you're currently in
✅ **Agents understand context** - They automatically detect what kind of project you're working on
✅ **No project pollution** - Your actual projects stay clean