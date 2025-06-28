# 🧪 TDD Quick Reference - vibe.ai

## 🚀 Quick Start Commands

### Full TDD with All Subagents (Best Option)
```bash
python3 tdd_with_subagents.py "your project idea" -o output-dir
```

### What Each Subagent Does in TDD

| Phase | Agent | Role | Output |
|-------|-------|------|--------|
| 1️⃣ | **Prompting Oracle** | Designs perfect test specs | Enhanced test requirements |
| 2️⃣ | **Planning-Analysis** | Creates test strategy | Test categories & approach |
| 3️⃣ | **Task-Complexity** | Assesses complexity | Effort estimates & recommendations |
| 4️⃣ | **Repo-Manager** | Sets up structure | Test directories & config files |
| 5️⃣ | **Universal-Execution** | Generates tests | Complete test suites |
| 6️⃣ | **Test-Sync** | Runs tests | Test results & quality gates |
| 7️⃣ | **Universal-Execution** | Implements code | Working implementation |
| 8️⃣ | **Quality-Git** | Refactors | Improved code quality |
| 9️⃣ | **Agent-Coordinator** | Orchestrates | Seamless workflow |

## 📊 TDD Workflow Phases

### 🔴 Red Phase - Write Failing Tests
```bash
# What happens:
- Oracle designs test specifications
- Planning agent creates strategy  
- Execution agent generates test files
- Test-Sync runs tests (all fail)
```

### 🟢 Green Phase - Make Tests Pass
```bash
# What happens:
- Execution agent implements code
- Only enough code to pass tests
- Test-Sync validates implementation
- Quality gates enforced
```

### 🔵 Blue Phase - Refactor
```bash
# What happens:
- Quality agent improves code
- Tests ensure nothing breaks
- Code quality metrics improve
- Final validation by all agents
```

## 📁 Generated Structure

```
output-dir/
├── tests/
│   ├── unit/          # Unit tests (70%)
│   ├── integration/   # Integration tests (20%)
│   ├── e2e/          # End-to-end tests (10%)
│   ├── fixtures/     # Test data
│   └── mocks/        # Mock objects
├── src/              # Implementation
├── .taskmaster/      # Agent coordination
├── pytest.ini        # Test configuration
├── conftest.py       # Test fixtures
├── .coveragerc       # Coverage config
├── Makefile          # Convenience commands
├── requirements.txt  # App dependencies
└── test-requirements.txt  # Test dependencies
```

## 🎯 Make Commands

```bash
make test           # Run all tests
make test-unit      # Run unit tests only
make test-integration  # Run integration tests
make test-e2e       # Run end-to-end tests
make coverage       # Generate coverage report
make test-watch     # Watch mode for TDD
make clean          # Clean test artifacts
```

## 💡 TDD Best Practices with vibe.ai

### 1. Let Agents Drive the Process
```bash
# Don't write tests manually - let Oracle design them
# Don't guess implementation - let tests guide you
# Don't skip refactoring - Quality agent knows best
```

### 2. Trust the Quality Gates
```bash
# Test-Sync agent enforces:
- All tests must pass
- Coverage requirements met
- No linting issues
- Performance acceptable
```

### 3. Use Agent Specialization
```bash
# Each agent excels at:
- Oracle: Perfect specifications
- Planning: Strategic thinking
- Complexity: Realistic estimates
- Execution: Clean implementation
- Quality: Professional polish
```

## 🔍 Debugging TDD Issues

### Tests Not Generating?
```bash
# Check agent availability
python3 master-agent.py list-agents

# Verify test-sync agent
python3 agents/test-sync-agent.py --status
```

### Implementation Not Working?
```bash
# Check TaskMaster tasks
cat output-dir/.taskmaster/tasks/tasks.json

# Review agent sync state
ls output-dir/.taskmaster/agent_sync/
```

### Quality Gates Failing?
```bash
# Run specific test category
make test-unit

# Check coverage
make coverage

# Review quality report
cat output-dir/TDD_SUBAGENTS_REPORT.md
```

## 📈 TDD Metrics

### What You Get
- **Test Coverage**: 90%+ automatically
- **Test Categories**: Unit, Integration, E2E
- **Quality Score**: 9.0+ after refactoring
- **Documentation**: Tests serve as living docs
- **Confidence**: Refactor without fear

### Time Saved
- **Manual TDD**: 10-15 hours
- **With Subagents**: 10-15 minutes
- **Quality Gain**: Professional-grade tests

## 🎉 Example Success Story

```bash
$ python3 tdd_with_subagents.py "build a calculator API" -o calc-api

# Results:
✅ 25 comprehensive tests generated
✅ Full implementation created
✅ 95% test coverage achieved
✅ Quality score: 9.2/10
✅ Production-ready in 15 minutes
```

## 🚦 Next Steps After TDD

1. **Deploy with Confidence**
   - All tests passing
   - Quality gates met
   - Documentation complete

2. **Maintain with Ease**
   - Tests catch regressions
   - Refactor safely
   - Add features confidently

3. **Scale with Agents**
   - Add more test cases
   - Enhance implementation
   - Maintain quality standards

---

*Remember: With vibe.ai TDD, you're not just writing tests - you're orchestrating a symphony of specialized agents working in perfect harmony!* 🎭