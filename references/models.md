# Models and delegation

## Routing

| Model tier | When |
|---|---|
| mid (Sonnet) | default: everyday code, content, tests, commits |
| small (Haiku) | searches, inventories, summaries, file triage |
| large (Opus and above) | hard bug, multi-file redesign, architecture decision — with the user's agreement |

- Choose the model **at the start**. Switching mid-session rewrites the whole cache.
  Need the large model for one hard point? Write a handoff, then open a short dedicated session.
- If the task is beyond the current model, say so and propose the larger one instead of flailing.
  A cheap model that fails three times costs more than the right model once.
- Avoid extended-context (1M) variants for everyday work: they let a session grow until every
  call re-reads a million tokens.
- Avoid fast mode where it is billed at a premium: same work, higher price.
- Reasoning effort: medium is enough for routine work; high for a genuinely hard problem.

## Subagents

A subagent starts cold and pays the whole fixed context again. It only pays off when it keeps a
large volume of reading **out of the main session**.

- Default: work directly, no subagent.
- Worth it: a wide search where only the conclusion matters, on the small model, with the
  instruction "answer in at most 15 lines, with paths and line numbers".
- Worth it: a heavy, truly independent task, on the mid model.
- Never two agents on the same files. Never an agent for a task of fewer than ~10 calls.
- Always pass the model explicitly on each agent call.
- Plan before delegating; keep the plan, the final decisions and the integration.
- Read yourself the files and screenshots a decision depends on.
- Multi-agent workflows: only on the user's explicit request, and state the cost first.
