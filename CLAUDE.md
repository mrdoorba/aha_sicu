# Project Rules for Claude

## Git Branching Strategy

**ENFORCE THESE RULES ON EVERY COMMIT:**

| Branch    | Purpose                          | Commit Policy                                      |
|-----------|----------------------------------|----------------------------------------------------|
| `main`    | Production                       | **NO commits** unless user explicitly requests it  |
| `develop` | Development integration          | **Merge from feature only** at milestones          |
| `feature` | Active work & experimentation    | **ALL commits go here first**                      |

## Commit Standards

- **Atomic commits required** - Each commit should represent ONE logical change
- Keep commits small, focused, and self-contained
- Each commit should be able to stand on its own
- Don't bundle unrelated changes together
- **Never include Co-Authored-By lines** in commit messages
- **Always commit when work is complete** - Don't wait to be asked
- **Always end commit messages with:** `Author: Mr. Door`

## PR Standards

- **Always end PR descriptions with:** `Author: Mr. Door`

## Before Any Commit

1. Confirm which branch you're on
2. If on `main` - STOP and ask user for explicit permission
3. If on `develop` - STOP, switch to feature branch first
4. If on `feature` - Proceed with atomic commits

## Workflow

**ALWAYS follow this flow:**

1. Create/switch to `feature` branch before any work
2. Commit frequently with atomic commits on `feature`
3. When milestone reached, merge `feature` → `develop`
4. **Delete the feature branch** immediately after successful merge
5. Only touch `main` when user explicitly requests production deployment

**Proactive Commits:** After completing any logical unit of work (file created, feature done, bug fixed), commit immediately. Don't wait for user to ask.

**Branch Cleanup:** Always delete `feature/*` branches after merging. Keep the repository clean - no stale branches.

## Protected Directories

**NEVER delete these directories:**

- `_bmad/` - BMAD framework configuration and workflows
- `_bmad-output/` - BMAD workflow outputs and artifacts
- `.agent/` - Agent configuration
- `.claude/` - Claude configuration
- `.cursor/` - Cursor configuration
- `.gemini/` - Gemini configuration

These directories contain critical project configuration.

## Lessons Learned

Read `_bmad-output/lessons-learned.md` for accumulated knowledge from code reviews, retrospectives, and implementation patterns. Consult it before writing new code.

## Command Autonomy

**Proceed without asking** for all commands EXCEPT the following, which require explicit user approval:

- `git push` - Always ask before pushing to any remote
- `git merge` - Always ask before merging branches
- `gh pr create` / any PR creation - Always ask before opening pull requests

Everything else (file edits, git add, git commit, running tests, installing dependencies, builds, etc.) can be executed freely.
