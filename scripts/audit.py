#!/usr/bin/env python3
"""eco / audit.py - where does the Claude Code quota go?

Reads local transcripts (~/.claude/projects) and the local configuration.
It modifies nothing and sends nothing anywhere. Output is deliberately short.

Usage:
  python audit.py                 # last 7 days
  python audit.py --days 30
  python audit.py --project shop  # filter on the project folder name
  python audit.py --top 10        # number of sessions listed
  python audit.py --unused        # full list of skills never invoked in the period
"""
import argparse
import collections
import json
import os
import statistics
import sys
import time

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

HOME = os.path.expanduser("~")
CLAUDE = os.path.join(HOME, ".claude")

# INDICATIVE weights (not official prices): they are for comparing, not for billing.
# Per token type, relative to one regular input token.
W_OUT, W_WRITE_5M, W_WRITE_1H, W_READ, W_IN = 5.0, 1.25, 2.0, 0.1, 1.0
# Per model family. Adjust to current pricing.
MODEL_W = (("haiku", 1.0), ("sonnet", 3.0), ("opus", 5.0), ("fable", 5.0))


def model_weight(model):
    m = (model or "").lower()
    for key, w in MODEL_W:
        if key in m:
            return w
    return 3.0


def family(model):
    m = (model or "?").lower()
    for key, _ in MODEL_W:
        if key in m:
            return key
    return m[:18]


def fmt(n):
    n = float(n)
    if n >= 1e9:
        return "%.1f B" % (n / 1e9)
    if n >= 1e6:
        return "%.1f M" % (n / 1e6)
    if n >= 1e3:
        return "%.0f k" % (n / 1e3)
    return "%d" % n


def scan(days, project):
    root = os.path.join(CLAUDE, "projects")
    limit = time.time() - days * 86400
    limit_iso = time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(limit))
    sessions = {}
    tools = collections.Counter()
    skills = collections.Counter()
    seen = set()
    first_ctx, first_id = {}, {}
    for dirpath, _dirs, files in os.walk(root):
        for name in files:
            if not name.endswith(".jsonl"):
                continue
            path = os.path.join(dirpath, name)
            try:
                if os.path.getmtime(path) < limit:
                    continue
            except OSError:
                continue
            proj = os.path.relpath(path, root).split(os.sep)[0]
            if project and project.lower() not in proj.lower():
                continue
            try:
                handle = open(path, encoding="utf-8", errors="replace")
            except OSError:
                continue
            with handle:
                for line in handle:
                    if '"usage"' not in line or '"assistant"' not in line:
                        continue
                    try:
                        rec = json.loads(line)
                    except ValueError:
                        continue
                    msg = rec.get("message") or {}
                    usage = msg.get("usage")
                    if not usage or "synthetic" in (msg.get("model") or ""):
                        continue
                    sid = rec.get("sessionId") or name
                    if sid not in first_ctx and not rec.get("isSidechain"):
                        # True session start, even when older than the period.
                        first_ctx[sid] = ((usage.get("input_tokens") or 0)
                                          + (usage.get("cache_read_input_tokens") or 0)
                                          + (usage.get("cache_creation_input_tokens") or 0))
                        first_id[sid] = msg.get("id")
                    stamp = rec.get("timestamp") or ""
                    if stamp and stamp < limit_iso:
                        continue
                    # Tools: counted on every block (one line per content block).
                    for block in msg.get("content") or []:
                        if isinstance(block, dict) and block.get("type") == "tool_use":
                            tname = block.get("name") or ""
                            if tname == "Skill":
                                sk = (block.get("input") or {}).get("skill") or "?"
                                skills[sk.split(":")[-1]] += 1
                            elif tname.startswith("mcp__"):
                                tools[tname.split("__")[1]] += 1
                    # Tokens: once per response (the same usage is repeated on each block).
                    mid = msg.get("id") or rec.get("requestId") or rec.get("uuid")
                    if mid in seen:
                        continue
                    seen.add(mid)
                    s = sessions.get(sid)
                    if s is None:
                        s = sessions[sid] = {
                            "proj": proj, "turns": 0, "out": 0, "read": 0, "write": 0,
                            "inp": 0, "units": 0.0, "first_ctx": first_ctx.get(sid), "peak": 0,
                            "rewrites": 0, "rewrite_tok": 0, "sub_units": 0.0,
                            "models": collections.Counter(), "last": "",
                        }
                    out = usage.get("output_tokens") or 0
                    read = usage.get("cache_read_input_tokens") or 0
                    write = usage.get("cache_creation_input_tokens") or 0
                    inp = usage.get("input_tokens") or 0
                    cc = usage.get("cache_creation") or {}
                    w1h = cc.get("ephemeral_1h_input_tokens")
                    w5m = cc.get("ephemeral_5m_input_tokens")
                    if w1h is None and w5m is None:
                        w1h, w5m = 0, write
                    ctx = inp + read + write
                    mw = model_weight(msg.get("model"))
                    units = mw * (out * W_OUT + (w1h or 0) * W_WRITE_1H
                                  + (w5m or 0) * W_WRITE_5M + read * W_READ + inp * W_IN)
                    s["turns"] += 1
                    s["out"] += out
                    s["read"] += read
                    s["write"] += write
                    s["inp"] += inp
                    s["units"] += units
                    s["models"][family(msg.get("model"))] += units
                    s["last"] = max(s["last"], stamp)
                    if rec.get("isSidechain"):
                        s["sub_units"] += units
                    else:
                        if s["first_ctx"] is None:
                            s["first_ctx"] = first_ctx.setdefault(sid, ctx)
                        elif mid != first_id.get(sid) and ctx > 40000 and write > 0.6 * ctx:
                            # Whole context rewritten to cache: long pause, model switch
                            # or compaction.
                            s["rewrites"] += 1
                            s["rewrite_tok"] += write
                        s["peak"] = max(s["peak"], ctx)
    return sessions, tools, skills


def static_context():
    lines = []
    for label, path in (
        ("~/.claude/CLAUDE.md", os.path.join(CLAUDE, "CLAUDE.md")),
        ("~/CLAUDE.md", os.path.join(HOME, "CLAUDE.md")),
        ("./CLAUDE.md", os.path.join(os.getcwd(), "CLAUDE.md")),
    ):
        if os.path.exists(path):
            lines.append("%s %d chars" % (label, os.path.getsize(path)))
    sk_dir = os.path.join(CLAUDE, "skills")
    names, total = [], 0
    if os.path.isdir(sk_dir):
        for d in sorted(os.listdir(sk_dir)):
            f = os.path.join(sk_dir, d, "SKILL.md")
            if not os.path.exists(f):
                continue
            names.append(d)
            try:
                with open(f, encoding="utf-8", errors="replace") as h:
                    parts = h.read().split("---")
            except OSError:
                continue
            total += len(parts[1]) if len(parts) > 2 else 0
    return lines, names, total


def main():
    ap = argparse.ArgumentParser(description="Claude Code consumption audit")
    ap.add_argument("--days", type=int, default=7)
    ap.add_argument("--project", default="")
    ap.add_argument("--top", type=int, default=5)
    ap.add_argument("--unused", action="store_true")
    a = ap.parse_args()

    sessions, tools, skills = scan(a.days, a.project)
    print("ECO AUDIT - last %d days%s" % (a.days, (" - project " + a.project) if a.project else ""))
    if not sessions:
        print("No session found in the period.")
    else:
        tot = sum(s["units"] for s in sessions.values()) or 1.0
        out = sum(s["out"] for s in sessions.values())
        read = sum(s["read"] for s in sessions.values())
        write = sum(s["write"] for s in sessions.values())
        turns = sum(s["turns"] for s in sessions.values())
        print("%d sessions, %d model calls. Tokens: output %s | cache written %s | cache read %s"
              % (len(sessions), turns, fmt(out), fmt(write), fmt(read)))

        print("\n1. BY MODEL (share of estimated weight)")
        by_model = collections.Counter()
        for s in sessions.values():
            by_model.update(s["models"])
        for m, u in by_model.most_common():
            print("   %-8s %3.0f %%" % (m, 100 * u / tot))

        print("\n2. BY NATURE")
        def main_w(s):
            return model_weight(max(s["models"], key=s["models"].get))
        p_out = sum(main_w(s) * s["out"] * W_OUT for s in sessions.values())
        p_read = sum(main_w(s) * s["read"] * W_READ for s in sessions.values())
        p_other = max(tot - p_out - p_read, 0)
        print("   re-reading the context on each call : %3.0f %%" % (100 * p_read / tot))
        print("   writing to cache (new content)      : %3.0f %%" % (100 * p_other / tot))
        print("   text produced (answers + thinking)  : %3.0f %%" % (100 * p_out / tot))
        sub = sum(s["sub_units"] for s in sessions.values())
        if sub:
            print("   of which subagents                  : %3.0f %%" % (100 * sub / tot))

        firsts = [s["first_ctx"] for s in sessions.values() if s["first_ctx"]]
        if firsts:
            print("\n3. FIXED CONTEXT (paid before your first question, then on every call)")
            print("   median %s tokens | max %s" % (fmt(statistics.median(firsts)), fmt(max(firsts))))

        rw = sum(s["rewrites"] for s in sessions.values())
        rw_tok = sum(s["rewrite_tok"] for s in sessions.values())
        print("\n4. CACHE LOST (whole context rewritten: long pause, model switch, compaction)")
        print("   %d times, %s tokens rewritten" % (rw, fmt(rw_tok)))

        print("\n5. HEAVIEST SESSIONS")
        ranked = sorted(sessions.items(), key=lambda kv: -kv[1]["units"])
        n = max(1, len(ranked) // 10)
        print("   top %d = %.0f %% of the total" % (n, 100 * sum(s["units"] for _, s in ranked[:n]) / tot))
        for _sid, s in ranked[: a.top]:
            main_model = max(s["models"], key=s["models"].get)
            print("   %4.0f %%  %-6s %5d calls  peak %-6s  %s  %s"
                  % (100 * s["units"] / tot, main_model, s["turns"], fmt(s["peak"]),
                     s["last"][:10], s["proj"][-32:]))

    lines, names, total = static_context()
    print("\n6. LOADED IN EVERY SESSION")
    if lines:
        print("   " + " | ".join(lines))
    print("   %d personal skills, %s chars of descriptions" % (len(names), fmt(total)))
    if tools:
        print("   MCP servers actually used: " + ", ".join("%s (%d)" % kv for kv in tools.most_common(12)))
    else:
        print("   MCP servers actually used: none in the period")
    unused = [n for n in names if n not in skills]
    print("   personal skills used: %d / %d" % (len(names) - len(unused), len(names))
          + (" -> " + ", ".join("%s (%d)" % kv for kv in skills.most_common(8)) if skills else ""))
    if a.unused:
        print("   never invoked in the period: " + ", ".join(unused))
    else:
        print("   (%d never invoked in the period: --unused for the list)" % len(unused))
    print("\nWeight = relative estimate (model x token type), not an invoice.")


if __name__ == "__main__":
    main()
