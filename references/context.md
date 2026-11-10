# Trimming what loads in every session

The fixed context (tools, MCP servers, skills, instruction files) is paid before the first
question and re-read on every call. At 80k tokens over a 100-call session, that is 8M tokens
re-read for nothing. The audit prints the real figure under "FIXED CONTEXT".

Change **nothing** here without the user's agreement: propose, they decide.

## What weighs, heaviest first
1. **MCP servers and connectors**: every tool adds its name, every server its instructions.
   Hundreds of tools are often declared when a session uses one or two servers.
2. **Skills**: every installed skill adds its description to every session.
3. **CLAUDE.md and memory index**: usually a few hundred tokens. Rarely the problem.

## Levers
- **Connectors per session**: keep only those the day's topic needs.
- **Global MCP servers** (`~/.claude.json`, key `mcpServers`): move the ones used by a single
  project to that project's configuration.
- **Unused skills**: move them to `~/.claude/skills-archive/` (outside the scanned folder).
  Nothing is deleted; restore by moving the folder back.
  List them: `python ~/.claude/skills/eco/scripts/audit.py --days 60 --unused`.
- **Skill descriptions**: a 1,000-character description is paid in every session; 150 to 300
  characters are enough to trigger.
- **CLAUDE.md**: only what must apply to every message, plus what must survive compaction.
  Details go in a skill.

## Checking the effect
Before and after a change, open a fresh session and run the audit: the "FIXED CONTEXT" line
should drop.
