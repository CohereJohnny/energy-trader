# OpenSpec Workflow Guide

## What is OpenSpec?

OpenSpec is a **spec-driven development** framework that helps us:
1. **Plan changes** before implementing them (proposals)
2. **Document requirements** clearly (specs)
3. **Track implementation** step-by-step (tasks)
4. **Maintain truth** about what's built vs. what's proposed

## The Three Stages

### Stage 1: Creating Changes (Planning)
**When**: Before implementing new features, breaking changes, or architecture changes

**What happens**:
1. You request a new feature or change
2. I create a **change proposal** with:
   - `proposal.md` - Why we're doing this, what changes, and impact
   - `tasks.md` - Step-by-step implementation checklist
   - `specs/[capability]/spec.md` - Requirements and scenarios (what should be built)
   - `design.md` (optional) - Technical decisions if needed

**Example**: When you asked for the futures prices MCP server, I created `openspec/changes/add-futures-price-mcp-server/`

### Stage 2: Implementing Changes (Building)
**When**: After proposal is approved

**What happens**:
1. I read the proposal and tasks
2. I implement tasks sequentially
3. I update checkboxes in `tasks.md` as I complete them
4. I ensure everything matches the spec requirements

**Current status**: We're in Sprint 4, implementing the AI Agent integration

### Stage 3: Archiving Changes (Completing)
**When**: After feature is deployed and working

**What happens**:
1. Move the change from `changes/` to `changes/archive/`
2. Update `specs/` to reflect the new truth (what IS built)
3. Clean up completed work

## How We Work Together

### When You Want a New Feature

**You say**: "I want to add [feature]" or "Help me create a change proposal for [feature]"

**I do**:
1. Check existing specs and changes for conflicts
2. Create a change proposal with:
   - Unique change ID (e.g., `add-eia-data-mcp-server`)
   - Proposal explaining why/what/impact
   - Tasks checklist
   - Spec deltas (requirements)
3. **Wait for your approval** before implementing

**You review**: The proposal and approve or request changes

**Then**: I implement following the tasks checklist

### When You Want to Modify Existing Features

**You say**: "Update [feature] to do [something different]"

**I do**:
1. Check if it's a bug fix (fix directly) or a change (create proposal)
2. If change: Create proposal with MODIFIED requirements
3. Get approval, then implement

### When You Want Bug Fixes

**You say**: "Fix [bug]" or "This isn't working as expected"

**I do**:
- Fix directly (no proposal needed for bugs)
- Update code to match existing specs

### When You Want Quick Tasks

**You say**: "Add a test" or "Update documentation"

**I do**:
- Implement directly (no proposal needed for small tasks)

## Decision Tree: Do We Need a Proposal?

```
New request?
├─ Bug fix? → Fix directly ✅
├─ Typo/formatting? → Fix directly ✅
├─ New feature? → Create proposal 📋
├─ Breaking change? → Create proposal 📋
├─ Architecture change? → Create proposal 📋
└─ Unclear? → Create proposal 📋 (safer)
```

## Current Project Structure

```
openspec/
├── project.md              # Project conventions (tech stack, patterns)
├── specs/                  # What IS built (current truth)
│   └── futures-prices/     # Futures prices capability spec
├── changes/                # What SHOULD change (proposals)
│   ├── add-futures-price-mcp-server/  # Active change
│   └── archive/            # Completed changes
└── AGENTS.md               # Full OpenSpec instructions (for me)
```

## Example: How We Used OpenSpec for Futures Prices MCP Server

### Stage 1: Planning (You requested it)
**You**: "I want to add an MCP Server to lookup front month prices"

**I created**:
- `openspec/changes/add-futures-price-mcp-server/proposal.md`
- `openspec/changes/add-futures-price-mcp-server/tasks.md`
- `openspec/changes/add-futures-price-mcp-server/specs/futures-prices/spec.md`

**You reviewed**: Approved the proposal

### Stage 2: Implementation (Sprints 1-3)
**I implemented**:
- Sprint 1: Database setup and data loading
- Sprint 2: MCP server implementation
- Sprint 3: Testing and validation
- Sprint 4: AI Agent integration (in progress)

**I updated**: Tasks checklist as I completed each item

### Stage 3: Archiving (After Sprint 4)
**When complete**: I'll archive the change and update specs

## Best Practices for Working Together

### 1. Be Specific About Scope
**Good**: "I want to add EIA data access via MCP server"
**Less clear**: "Add more data sources"

### 2. Review Proposals Before Implementation
- I'll wait for your approval before starting implementation
- You can request changes or clarifications

### 3. Trust the Process
- Proposals help us think through changes before coding
- Specs document what should be built
- Tasks break down work into manageable steps

### 4. Ask Questions
- If something is unclear, ask me to clarify
- If you want to see what's planned, ask: "Show me the proposal for [change]"

## Common Commands (For You)

```bash
# See what changes are in progress
openspec list

# See what capabilities exist
openspec list --specs

# View a specific change proposal
openspec show add-futures-price-mcp-server

# Validate a change (check if it's well-formed)
openspec validate add-futures-price-mcp-server --strict
```

## What I Do Automatically

1. **Before any task**: I check existing specs and changes
2. **When you request features**: I create proposals (unless it's a bug fix)
3. **During implementation**: I update task checklists
4. **After completion**: I archive changes and update specs

## Current Status

**Active Change**: `add-futures-price-mcp-server`
- ✅ Proposal created and approved
- ✅ Sprints 1-3 completed
- 🔄 Sprint 4 in progress (AI Agent integration)

**Next Steps**:
- Complete Sprint 4 tasks
- Archive the change when complete
- Update specs to reflect deployed state

## Questions?

- **"What's the current status?"** → I'll check `openspec list` and task files
- **"What should I do next?"** → I'll check the current sprint tasks
- **"Can you create a proposal for [feature]?"** → I'll create a full proposal
- **"Show me what's planned"** → I'll show you the proposal and tasks

## Summary

**You focus on**: 
- Requesting features and changes
- Reviewing and approving proposals
- Testing and providing feedback

**I handle**:
- Creating proposals and specs
- Implementing according to tasks
- Updating documentation
- Following OpenSpec workflow

We work together to build features systematically, with clear documentation and step-by-step progress tracking.

