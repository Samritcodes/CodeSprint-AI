"""
Documentation Agent
--------------------
Regenerates README.md from progress.json. Pure templating, no LLM call --
this data is already structured, so there's nothing to "generate," just
render.
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
README_PATH = os.path.join(ROOT, "README.md")

HEADER = """# 🚀 CodeSprint AI

> An automation pipeline that assigns me a daily coding problem, and once I solve it myself,
> reviews it, writes up the explanation, and updates this README. The agent plans and
> documents; I do the solving.

**How it works:** every day a GitHub Action opens an issue with a new problem and drops a
starter file in `solutions/pending/`. I solve it and push. A second workflow picks up my
solution, generates the write-up, moves it into `solutions/`, and updates the stats below.

---

"""

FOOTER = """

---

### Repo structure
```
CodeSprint-AI/
├── agent/            # planner, reviewer, memory, readme, github agents
├── topics/            # problem bank the planner picks from
├── solutions/
│   ├── pending/        # today's unsolved stub -- lives here until I push a solution
│   └── *.js / *.md     # my solved code + generated explanation, once reviewed
├── progress.json       # streak / history / tag stats (source of truth for this README)
└── .github/workflows/  # daily.yml (assign) + review.yml (on push to pending/)
```
"""


def render_stats_table(by_tag):
    if not by_tag:
        return "_No problems completed yet._"
    rows = sorted(by_tag.items(), key=lambda kv: -kv[1])
    lines = ["| Tag | Count |", "|---|---|"]
    for tag, count in rows:
        lines.append(f"| {tag} | {count} |")
    return "\n".join(lines)


def render_history_table(history):
    if not history:
        return "_No problems completed yet._"
    lines = ["| Date | Problem | Difficulty |", "|---|---|---|"]
    for entry in reversed(history[-15:]):  # most recent 15
        lines.append(f"| {entry['date']} | {entry['title']} | {entry['difficulty']} |")
    return "\n".join(lines)


def regenerate(state):
    total = len(state["completed_ids"])
    streak = state.get("streak", 0)
    pending = state.get("pending_id")

    body = HEADER
    body += f"### 🔥 Current Streak: {streak} day{'s' if streak != 1 else ''}\n\n"
    body += f"### ✅ Problems Solved: {total}\n\n"
    if pending:
        body += f"### ⏳ Currently Assigned: `{pending}` (in `solutions/pending/`)\n\n"

    body += "### 📊 By Topic\n\n"
    body += render_stats_table(state.get("by_tag", {})) + "\n\n"

    body += "### 🕒 Recent History\n\n"
    body += render_history_table(state.get("history", [])) + "\n"

    body += FOOTER

    with open(README_PATH, "w") as f:
        f.write(body)


if __name__ == "__main__":
    import sys
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from memory import load_state
    regenerate(load_state())
