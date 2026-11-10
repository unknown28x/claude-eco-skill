# Sessions: length, cache, handoff

## Why this is rule 1

A call in a 50k-token session re-reads 50k. The same call in an 800k-token session re-reads 800k.
The work is identical; the cost is 16 times higher. A handful of giant sessions typically accounts
for most of a heavy user's consumption.

## When to offer a new session

- a deliverable is finished and verified;
- the topic changes;
- ~40 tool calls since the start, or a compaction just happened;
- the user returns after a long break to an already heavy session (the cache is gone: everything
  will be rewritten at full price, so restart light).

Offer it in one line, with the handoff already written. If the user prefers to stay, stay.

## The handoff note

Write it to `.claude/handoff.md` in the project (overwrite the previous one). 30 lines at most:

    # Handoff — <topic> — <date>
    ## Goal
    <one sentence>
    ## Done and verified
    - <fact> (proof: <command or screenshot>)
    ## Decisions made (do not reopen)
    - <decision> — <reason>
    ## Key files
    - path/file.ext:line — <role>
    ## Next step
    <precise action, first command to run>
    ## Pitfalls
    - <what failed and why>

Rules: paths and line numbers, not prose. Nothing the code already says.
The new session starts with: "read `.claude/handoff.md` and continue".

## Compaction

- A chosen handoff beats an endured compaction: compaction re-reads everything one last time,
  then rewrites the cache.
- If the session must continue, compact at a clean boundary (a finished step), not in the middle
  of debugging.
- After a compaction: re-read the handoff note if there is one, reload this skill, and do not
  reopen decisions already made.

## Pauses

- The prompt cache expires after a period of inactivity. The first message after that rewrites
  the whole context.
- Before a planned break on a heavy session: write the handoff.
- Do not start waits or polling that wake the session for nothing.
