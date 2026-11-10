---
name: eco
description: >
  Usage-limit economy for Claude Code (5-hour window and weekly limit). Load at session start,
  before spawning a subagent or switching model, when the session gets long, before a large task,
  at session end, and on "usage", "limit", "quota", "save tokens", "audit", or /eco.
---

# eco — spend as little quota as possible without lowering quality

No setting removes the limits. This skill removes **waste**, which is most of the bill.
Answer in the user's language.

## Guardrail: quality is not negotiable

Nothing below is permission to do worse work. Same care, same tests, same verification at every
tier and at any session age. Never skip a necessary read, a test, or a step of the task to save
quota, and never ship a reduced version without saying so. If there is not enough quota to finish
well: stop cleanly with a handoff note. Quality versus economy: quality wins, and the user is told
in one line.

## How quota is actually spent

Every model call re-reads the **whole** context. So:

    session cost ≈ context size × number of calls × model weight

In a heavy-usage history, most of the weight is usually context re-reading inside a few very long
sessions, not the text Claude writes. Shortening answers saves little. Run `scripts/audit.py` to
see the real split on this machine.

## The 7 rules, by impact

1. **Short sessions.** One topic = one session. Offer a handoff (`references/session.md`) when a
   deliverable is done, after ~40 tool calls, or after a compaction. Never "just continue" a giant
   session: each call there costs 10 to 50 times more.
2. **Right model from the start.** Mid-tier model by default, the small model for search and
   summaries, the largest models only with the user's agreement, in a short dedicated session.
   Switching model mid-session rewrites the whole cache: start a new session instead.
3. **Do not lose the cache.** After a long pause the prompt cache expires and the whole context
   is rewritten at full price. If the user comes back to a heavy session after a break, offer to
   restart from a handoff note.
4. **Fewer calls.** Put independent tool calls in a single message. One script instead of five
   commands. No re-read after an edit, no repeated check, no polling loop.
5. **Small inputs.** Whatever enters the context is paid again on every later call. Search first,
   then read the part you need; bound command output; text instead of screenshots
   (`references/tools.md`).
6. **Small outputs.** Answer first, no recap of what is already visible, targeted edits instead
   of full rewrites, no unrequested documents.
7. **Right the first time.** Ask grouped questions before a large task and fix a yes/no check up
   front (`references/method.md`). A failed attempt costs double.

## Session start (one call)

Check current usage (desktop app: the usage tool; CLI: `/usage`), compare with the pacing targets
in `references/budget.md`, and report **one line**: used / target / tier.

| Tier | Trigger | Conduct |
|---|---|---|
| Green | on pace | the 7 rules |
| Orange | ahead of the weekly pace, or the 5-hour window is over 50 % before half the planned session | mid or small model, no subagents, screenshots only as final proof, earlier handoff |
| Red | 5-hour window over 85 %, or weekly over 90 % | finish the current step, write the handoff, stop and say when the window resets |

Tell the user in one line whenever the tier changes.

## Files — load only the one you need

| File | When |
|---|---|
| `references/budget.md` | pacing targets, tiers in detail |
| `references/models.md` | before a subagent, a multi-agent workflow, a model choice |
| `references/session.md` | handoff, compaction, pauses, a session getting long |
| `references/tools.md` | low-cost recipes for reading, searching, running |
| `references/method.md` | large task, "it's done", session end |
| `references/context.md` | trimming what loads in every session (MCP servers, skills) |
| `references/user-habits.md` | what the user can change; show it when they ask |
| `scripts/audit.py` | "audit", "where does my quota go": `python ~/.claude/skills/eco/scripts/audit.py --days 7` |
