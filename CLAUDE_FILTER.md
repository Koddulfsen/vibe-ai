# Claude Code Intelligent Task Routing Filter v2.0

## Advanced Sequential Analysis Framework

**Perform these enhanced analysis steps in order for each user request:**

### Pre-Analysis: Language & Technology Detection
**Detect programming language and technology stack first:**
- **Python**: `python`, `pip`, `django`, `flask`, `fastapi`, `pandas`, `numpy`
- **JavaScript/Node**: `javascript`, `node`, `npm`, `react`, `vue`, `angular`, `express`
- **Go**: `golang`, `go mod`, `goroutine`, `gin`, `echo`
- **Rust**: `cargo`, `rustc`, `tokio`, `serde`, `actix`
- **Java**: `java`, `maven`, `gradle`, `spring`, `hibernate`
- **Docker/K8s**: `docker`, `kubernetes`, `container`, `pod`, `helm`
- **Databases**: `postgres`, `mysql`, `mongodb`, `redis`, `elasticsearch`
- **Cloud/DevOps**: `aws`, `gcp`, `azure`, `terraform`, `ansible`

**Technology Impact on Routing:**
- Complex frameworks (Spring, Django) → **Agents** (need architectural understanding)
- Simple scripts (basic Python/JS) → **Direct** (straightforward implementation)
- Infrastructure (Docker, K8s) → **Agents** (multi-step setup required)
- Data processing (pandas, numpy) → **Hybrid** (analysis + execution)

## Step 1: Intent Categorization

### Implementation Intent
Keywords: `implement`, `create`, `build`, `develop`, `code`
- **Sequential Questions:**
  1. Is this asking to write new code?
  2. Does this require understanding existing code?
  3. Are there dependencies or integrations needed?

### Analysis Intent  
Keywords: `analyze`, `review`, `check`, `examine`
- **Sequential Questions:**
  1. Does this require analyzing project structure?
  2. Are there quality or testing requirements?
  3. Is this a multi-step development workflow?

### File Operations Intent
Keywords: `file`, `directory`, `folder`, `read`, `write`
- **Sequential Questions:**
  1. Does this require reading or writing files?
  2. Are there multiple files involved?
  3. Does this need file structure analysis?

### Question Intent
Keywords: `what`, `how`, `why`, `explain`, `help`
- **Sequential Questions:**
  1. Is this a direct question with a clear answer?
  2. Can this be answered without external tools?
  3. Is this just requesting information or explanation?

### System Operations Intent
Keywords: `setup`, `configure`, `install`, `deploy`
- **Sequential Questions:**
  1. Does this require system-level changes?
  2. Are there external tools/dependencies needed?
  3. Is this a one-time setup or ongoing process?

## Step 2: Advanced Requirements Analysis

### File Operations Complexity Scoring
- **Single file read/write**: Score +1 (Direct handling likely)
- **Multiple files**: Score +2 (Agent consideration)
- **Directory restructuring**: Score +3 (Agents recommended)
- **File system architecture**: Score +4 (Agents required)

### External Dependencies Impact
- **Package management** (`npm install`, `pip install`): Score +2
- **Database operations** (schema, migrations): Score +3
- **API integrations** (REST, GraphQL): Score +2
- **Infrastructure** (Docker, K8s, cloud): Score +4
- **CI/CD pipelines**: Score +4

### Planning Complexity Matrix
- **Simple design** (single component): Score +1
- **System design** (multiple components): Score +3
- **Architecture planning** (full system): Score +4
- **Migration planning** (legacy systems): Score +5

### Testing Requirements Assessment
- **Unit tests only**: Score +1
- **Integration tests**: Score +2
- **E2E testing setup**: Score +3
- **Testing infrastructure**: Score +4
- **Performance/Load testing**: Score +4

### Performance & Scale Indicators
- **High-performance requirements**: Score +3
- **Scalability concerns**: Score +3
- **Real-time processing**: Score +4
- **Distributed systems**: Score +5

## Step 3: Enhanced Complexity Scoring Algorithm

### Simple (Score: 0-2)
- **Characteristics:**
  - Prompt under 50 words
  - Single clear intent
  - No external dependencies
  - Direct Q&A patterns
  - Single language/technology
- **Examples:** "What is async/await?", "Fix this typo", "Read config file"
- **Confidence Threshold:** 85%+

### Moderate (Score: 3-5)
- **Characteristics:**
  - Prompt 50-200 words
  - 1-2 requirement categories
  - Single technology stack
  - Limited file operations
  - Basic testing needs
- **Examples:** "Create REST API endpoint", "Add database migration"
- **Confidence Threshold:** 70%+

### Complex (Score: 6-9)
- **Characteristics:**
  - Prompt 200+ words OR multiple technologies
  - 3+ requirement categories
  - Multi-step workflows
  - System integration needs
  - Performance/scale considerations
- **Examples:** "Implement authentication system", "Setup CI/CD pipeline"
- **Confidence Threshold:** 60%+

### Multi-Agent (Score: 10+)
- **Characteristics:**
  - Enterprise-level complexity
  - Multiple technology stacks
  - Full system architecture
  - Cross-team coordination needs
  - Migration or transformation projects
- **Examples:** "Migrate monolith to microservices", "Implement multi-tenant SaaS"
- **Confidence Threshold:** 40%+ (high complexity, may need user input)

### Dynamic Scoring Modifiers
- **Urgency indicators** (`urgent`, `asap`, `quickly`): +1 score
- **Quality emphasis** (`production-ready`, `enterprise-grade`): +2 score
- **Learning context** (`tutorial`, `example`, `demo`): -1 score
- **Maintenance tasks** (`fix`, `update`, `patch`): -1 score

## Step 4: Advanced Routing Decision Engine

### Route DIRECT (Confidence 80%+)
**Primary Conditions:**
- Score ≤ 2 AND single technology
- Question intent with 85%+ confidence
- Single file operation without testing
- Maintenance/fix tasks
- Learning/tutorial requests

**Secondary Conditions (Score 3-4):**
- Well-known patterns (CRUD, basic API)
- Single requirement category
- No performance/scale concerns
- Standard development practices

### Route to AGENTS (Confidence 70%+)
**Primary Conditions:**
- Score ≥ 6 OR multiple technologies
- Implementation + Testing + Infrastructure
- Planning + Execution + Quality assurance
- System architecture or design patterns
- Performance/scale requirements

**Secondary Conditions:**
- New technology stack implementation
- Complex integrations (3+ services)
- Production deployment concerns
- Security-critical implementations

### Route HYBRID (Confidence 60%+)
**Analysis + Direct Execution:**
- Score 3-5 with planning keywords
- Design phase separate from implementation
- Architecture review + simple coding
- Research + prototype development

**Agent Planning + Direct Implementation:**
- Complex requirements but simple execution
- Need system design but straightforward coding
- Research-heavy but implementation-light tasks

### Dynamic Routing Adjustments
**Technology-Based Routing:**
- **Python/JavaScript simple**: Direct bias (-1 score)
- **Go/Rust complex**: Agent bias (+1 score)
- **Infrastructure tools**: Agent bias (+2 score)
- **Database design**: Agent bias (+1 score)

**Context-Based Routing:**
- **Existing codebase**: Agent bias (need analysis)
- **Greenfield project**: Direct bias (more freedom)
- **Legacy system**: Agent bias (careful planning)
- **Prototype/POC**: Direct bias (speed over perfection)

## Step 5: Intelligent Agent Command Selection

### Full Development Workflow
**Conditions:** Score ≥ 8 OR (Planning + Implementation + Testing + Quality)
**Best for:** Complete feature development, system implementation
```bash
./master-agent.py workflow --type full-dev --tag <project-tag>
```

### Planning-Heavy Workflow
**Conditions:** Architecture/design keywords + Score ≥ 6
**Best for:** System design, complex analysis, architectural decisions
```bash
./master-agent.py workflow --type planning --tag <analysis-tag>
```

### Execution-Focused Workflow
**Conditions:** Implementation keywords + Score 4-7 + minimal planning
**Best for:** Feature implementation, API development, database work
```bash
./master-agent.py workflow --type execute --tag <implementation-tag>
```

### Quality & Testing Workflow
**Conditions:** Testing/validation keywords OR maintenance tasks
**Best for:** Code review, testing setup, refactoring, bug fixes
```bash
./master-agent.py workflow --type quality --fix --tag <quality-tag>
```

### Quick Fix Workflow
**Conditions:** Maintenance + Score ≤ 5 + urgent indicators
**Best for:** Bug fixes, small updates, configuration changes
```bash
./master-agent.py workflow --type quick-fix --auto
```

### Research & Analysis Workflow
**Conditions:** Analysis intent + exploration keywords
**Best for:** Technology research, codebase analysis, feasibility studies
```bash
./master-agent.py analyze --deep --tag <research-tag>
```

### Agent Selection Matrix
**By Technology Stack:**
- **Python/Django**: Full-dev (complex MVC patterns)
- **Node.js/Express**: Execute (straightforward APIs)
- **React/Frontend**: Execute (component-based)
- **DevOps/Infrastructure**: Full-dev (multi-step setup)
- **Database/Schema**: Planning (careful design needed)
- **Testing/QA**: Quality (specialized focus)

**By Project Phase:**
- **Greenfield**: Planning → Full-dev
- **Feature Addition**: Execute
- **Refactoring**: Quality
- **Bug Fixing**: Quick-fix
- **Performance**: Planning → Quality
- **Security**: Full-dev (comprehensive approach)

## Decision Examples with Analysis

### DIRECT Examples
**"What is the difference between async and await?"**
- Intent: question
- Requirements: none
- Complexity: simple
- Confidence: 90%

**"Read config file and update connection string"**
- Intent: file_operations
- Requirements: file_ops + external_tools
- Complexity: moderate
- Reasoning: Single file operation, can handle directly

### AGENTS Examples  
**"Implement user authentication with database and testing"**
- Intent: implementation
- Requirements: external_tools + testing
- Complexity: complex
- Agent needs: execution + quality
- Command: `workflow --type execute`

**"Analyze project structure and create CI/CD pipeline"**
- Intent: implementation
- Requirements: planning + external_tools + testing
- Complexity: complex
- Agent needs: planning + execution + quality
- Command: `analyze` (planning heavy)

### HYBRID Examples
**"Design database schema then implement basic CRUD"**
- Intent: implementation
- Requirements: planning + file_ops
- Complexity: moderate
- Approach: Agent planning → Direct implementation

## Confidence Scoring

### High Confidence (80-90%)
- Clear single intent
- Obvious complexity level
- Well-defined requirements

### Medium Confidence (60-80%)
- Mixed signals
- Moderate complexity with edge cases
- Partial requirement matches

### Low Confidence (40-60%)
- Ambiguous intent
- Complex decision factors
- Escalate to user choice

## Advanced Patterns

### Multi-Step Indicators
- Count: `first`, `then`, `next`, `after`, `finally`
- 3+ steps = Multi-Agent complexity

### Complexity Keywords
- Architecture, system, integrate = +2 complexity
- Workflow, pipeline, automation = +2 complexity
- Framework, platform, infrastructure = +2 complexity

### Agent Requirement Mapping
- **Planning:** design, architecture, analyze, plan
- **Execution:** implement, create, build, develop
- **Quality:** test, validate, verify, lint
- **Repository:** structure, organize, manage files
- **Coordinator:** multi-step, workflow, pipeline