# Budget and pacing

Adapt this file to your plan and your week. The defaults assume five working days and a weekly
limit that resets before the first one.

## Weekly pacing (expected usage by end of day)

| Day 1 | Day 2 | Day 3 | Day 4 | Day 5 |
|---|---|---|---|---|
| 20 % | 40 % | 60 % | 80 % | 100 % |

During the day, interpolate: midday on day 2 ≈ 30 %.

## Tiers

**Green** — on pace, 5-hour window under 50 %. The 7 rules are enough.

**Orange** — ahead of the weekly pace, or 5-hour window over 50 % before half the planned session.
- Mid-tier model, or the small model when the task allows. Never the largest models.
- No subagents, no multi-agent workflows.
- Screenshots only as final proof of visual work; everything else as text.
- Tests and verification stay complete: save on chatter, never on checking.
- Offer a handoff as soon as the first deliverable is done.
- Replies of at most 5 lines outside code.

**Red** — 5-hour window over 85 %, or weekly over 90 %.
- Finish only the current step; open no new one.
- Write the handoff note (`session.md`).
- Tell the user when the window resets and what is left.

## Session-start line

    Weekly 34 % (day-2 target 40 %) · 5-hour window 12 % · green

Nothing else. Mention usage again only when the tier changes.
