#!/bin/bash
# record-commit.sh - PostToolUse hook: auto-record git commits to work journal
#
# Called by Claude Code PostToolUse hook when Bash tool is used.
# Input: JSON via stdin containing the tool call details.
#
# Behavior:
#   - If the command was "git commit" (not --amend), record it to today's journal
#   - Journal file: /d/work/工作内容-{YYYY-MM-DD}.md
#   - De-duplicates by checking if commit hash already exists in the file
#
# Exit codes: 0 (success or skip), non-zero only on unexpected errors.

set -euo pipefail

JOURNAL_DIR="/d/work"
TODAY=$(date +%Y-%m-%d)
JOURNAL_FILE="${JOURNAL_DIR}/工作内容-${TODAY}.md"

# Read all stdin into a variable
INPUT=$(cat || true)

# Quick check: is this a git commit command?
# The input JSON contains a "command" field with the bash command
if ! echo "$INPUT" | grep -qiE '"git\s+commit'; then
    exit 0
fi

# Skip amend commits
if echo "$INPUT" | grep -q 'git commit.*--amend'; then
    exit 0
fi

# Get commit info from the current git repo
COMMIT_HASH=$(git rev-parse --short HEAD 2>/dev/null) || exit 0
COMMIT_MSG=$(git log -1 --format="%s" 2>/dev/null) || exit 0

# Get module name from git root directory
GIT_ROOT=$(git rev-parse --show-toplevel 2>/dev/null) || exit 0
MODULE=$(basename "$GIT_ROOT")

# Get timestamp
TIMESTAMP=$(date +%H:%M)

# De-duplicate: skip if this commit hash is already recorded
if [ -f "$JOURNAL_FILE" ] && grep -qF "$COMMIT_HASH" "$JOURNAL_FILE"; then
    exit 0
fi

# Build the entry
ENTRY_LINE="- [${TIMESTAMP}] \`${COMMIT_HASH}\` ${COMMIT_MSG} (${MODULE})"

# Write to journal
if [ -f "$JOURNAL_FILE" ]; then
    # Append to the "## 备注" section, or at end of file
    if grep -q "^## 备注" "$JOURNAL_FILE"; then
        # Insert a line before ## 备注
        sed -i "/^## 备注/i \\\\n${ENTRY_LINE}\\n" "$JOURNAL_FILE"
    else
        echo "" >> "$JOURNAL_FILE"
        echo "$ENTRY_LINE" >> "$JOURNAL_FILE"
    fi
else
    # Create new journal with standard template
    cat > "$JOURNAL_FILE" << EOF
# ${TODAY} 工作纪要

## 完成任务

${ENTRY_LINE}

---

## 备注

- 自动记录
EOF
fi

exit 0
