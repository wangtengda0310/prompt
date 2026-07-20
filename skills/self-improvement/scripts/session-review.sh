#!/bin/bash
# Self-Improvement Session Review Hook
# Triggers on Stop to remind Claude to review session for learnings
# Keep output minimal (~60 tokens)

cat << 'EOF'
<session-review-reminder>
Before ending this session, evaluate:
- Did the user correct you on something non-obvious?
- Did you discover a better approach than your initial one?
- Did you encounter project-specific knowledge not in docs?

If yes: Log to .learnings/ using self-improvement skill format.
</session-review-reminder>
EOF
