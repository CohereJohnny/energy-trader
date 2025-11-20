# Sprint Workflow

This directory contains sprint planning, tracking, and documentation.

## Directory Structure

```
sprints/
├── sprintplan.md          # High-level plan for all sprints
├── bug_swatting.md        # Critical bug fixes log
├── tech_debt.md          # Technical debt tracking
├── backlog.md            # Product backlog
├── sprint_1/             # Sprint 1 files
│   ├── sprint_1_tasks.md
│   ├── sprint_1_updates.md
│   └── sprint_1_testplan.md
└── archive/              # Completed sprints (created after sprint completion)
```

## Sprint Workflow

### Sprint Initialization
1. Create Git branch: `git checkout -b sprint-X`
2. Create sprint directory: `sprints/sprint_X/`
3. Create sprint files:
   - `sprint_X_tasks.md` - Task breakdown
   - `sprint_X_updates.md` - Progress notes
   - `sprint_X_testplan.md` - Test cases

### During Sprint
- Update `sprint_X_tasks.md` with progress notes
- Mark tasks as complete `[x]`
- Add notes to `sprint_X_updates.md` for context
- Log critical bugs in `bug_swatting.md`
- Add tech debt to `tech_debt.md`
- Add feature ideas to `backlog.md`

### Sprint Completion
1. Complete Sprint Review section in `sprint_X_tasks.md`
2. Create `sprint_X_report.md` with final summary
3. Commit all sprint documentation
4. Merge sprint branch to main
5. Tag release: `git tag sprint-X <commit-hash>`
6. Archive: `mv sprints/sprint_X sprints/archive/`
7. Delete branch: `git branch -d sprint-X`

## Sprint Files

### sprint_X_tasks.md
Primary file for tracking tasks, progress, and review notes. Contains:
- Sprint goals
- Task checklist with checkboxes
- Progress notes under each task section
- Sprint Review section (completed at end)

### sprint_X_updates.md
Ongoing notes, context, and progress updates during the sprint.

### sprint_X_testplan.md
Test cases and validation criteria for sprint deliverables.

### sprint_X_report.md
Final sprint summary (created at sprint completion).

## Central Logs

- **sprintplan.md**: High-level plan for all sprints
- **bug_swatting.md**: Log for critical bug fixes
- **tech_debt.md**: Log for non-critical issues/refactors
- **backlog.md**: Log for new feature ideas

