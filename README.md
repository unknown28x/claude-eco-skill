# eco — a Claude Code skill that makes your usage limits last

`eco` is a skill for [Claude Code](https://claude.com/claude-code). It does not bypass or remove
any limit. It removes waste: the habits that burn most of a 5-hour window or a weekly limit
without producing anything.

It comes with a local audit script that shows where your quota actually went.

*Version française plus bas.*

## The idea

Every model call re-reads the whole conversation. So:

    session cost ≈ context size × number of calls × model weight

Most people try to save quota by asking for shorter answers. That is usually the smallest part of
the bill. The large parts are very long sessions, the largest model used for everything, a cache
lost after a break, and a fixed context bloated by tools and skills nobody uses.

## What you get

- **7 rules ranked by impact**, with a hard guardrail: economy never lowers the quality of the work.
- **Three tiers** (green, orange, red) driven by your current usage.
- **Handoff notes**, so a long session can be replaced by a fresh one without losing the thread.
- **Reference files** loaded only when needed: budget, models, sessions, tools, method, context.
- **`scripts/audit.py`**: reads your local transcripts and prints a one-screen report.

## Install

macOS, Linux, Git Bash:

```bash
git clone https://github.com/unknown28x/claude-eco-skill ~/.claude/skills/eco
```

Windows PowerShell:

```powershell
git clone https://github.com/unknown28x/claude-eco-skill "$HOME\.claude\skills\eco"
```

Start a new session. The skill is listed as `eco` and can be called with `/eco`.

To make Claude load it without being asked, add this to your `CLAUDE.md`:

```markdown
Quota economy applies to waste, never to the quality of the work.
Detailed rules are in the `eco` skill. Load it unprompted at session start, before a subagent
or a model switch, when the session gets long, before a large task, and at session end.
```

## The audit

```bash
python ~/.claude/skills/eco/scripts/audit.py --days 7
```

Python 3.8+, standard library only. It reads `~/.claude/projects` on your machine, changes
nothing and sends nothing anywhere.

Illustrative output (made-up figures):

```text
ECO AUDIT - last 7 days
12 sessions, 2140 model calls. Tokens: output 1.9 M | cache written 24.0 M | cache read 610.0 M

1. BY MODEL (share of estimated weight)
   opus      71 %
   sonnet    27 %
   haiku      2 %

2. BY NATURE
   re-reading the context on each call :  63 %
   writing to cache (new content)      :  29 %
   text produced (answers + thinking)  :   8 %

3. FIXED CONTEXT (paid before your first question, then on every call)
   median 62 k tokens | max 71 k

4. CACHE LOST (whole context rewritten: long pause, model switch, compaction)
   14 times, 6.3 M tokens rewritten

5. HEAVIEST SESSIONS
   top 1 = 48 % of the total
     48 %  opus     905 calls  peak 610 k   2026-01-14  my-shop
```

Options: `--days N`, `--project NAME`, `--top N`, `--unused` (skills never invoked in the period).

The weights are relative estimates (model × token type) meant for comparison. They are not
official prices and the report is not an invoice. Edit the constants at the top of the script
to match current pricing.

## Customize

- `references/budget.md`: your pacing targets and tier thresholds.
- `references/models.md`: your model routing.
- Everything is plain Markdown. Change what does not fit how you work.

## Uninstall

Delete the `~/.claude/skills/eco` folder.

## Limits

- It cannot raise your limits and cannot promise a given percentage.
- It only works when Claude loads it, hence the `CLAUDE.md` snippet above.
- Transcript formats may change between Claude Code versions; the audit skips what it cannot read.

## En français

`eco` est un skill pour Claude Code. Il ne contourne aucune limite : il supprime le gaspillage,
c'est-à-dire les habitudes qui vident une fenêtre de 5 heures ou une limite hebdomadaire sans
rien produire.

Chaque appel au modèle relit toute la conversation. Le coût d'une session dépend donc de la taille
du contexte, du nombre d'appels et du modèle. Raccourcir les réponses rapporte peu ; ce qui
rapporte, ce sont des sessions courtes, le bon modèle dès le départ, un cache qu'on ne perd pas et
un contexte de départ allégé.

Installation : la commande `git clone` ci-dessus, puis une nouvelle session.
Audit : `python ~/.claude/skills/eco/scripts/audit.py --days 7`. Le script lit vos sessions en
local, ne modifie rien et n'envoie rien.

Le skill est rédigé en anglais, mais Claude répond dans votre langue.

## License

MIT
