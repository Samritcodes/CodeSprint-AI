"""
Planner Agent
-------------
Runs once a day (via .github/workflows/daily.yml).

Responsibility: pick the next problem you haven't done yet, and hand it to
YOU to solve. It does NOT write the solution. It writes:
  - solutions/pending/<date>-<slug>.js   (a stub with the problem + starter code)
  - a GitHub issue titled "Day N: <Problem Title>" so it shows up in your inbox

If there's already a pending problem you haven't solved yet, it does nothing
(it will not pile up new problems on top of unsolved ones) unless
ALLOW_SKIP=1 is set, in which case it marks the old one skipped and moves on.
"""
import json
import os
import random
import sys
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from memory import load_state, save_state, set_pending
import github

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOPICS_PATH = os.path.join(ROOT, "topics", "dsa.json")
PENDING_DIR = os.path.join(ROOT, "solutions", "pending")

STARTER_TEMPLATES = {
    "js": """// {title} ({difficulty})
// Tags: {tags}
// LeetCode: {url}
//
// {prompt}
//
// Write your solution below. When you push this file (filled in),
// the Reviewer Agent will pick it up, generate the explanation +
// complexity write-up, and update the README automatically.

/**
 * @param {{*}} input
 * @return {{*}}
 */
function solve(input) {{
  // TODO: your solution here
}}

module.exports = solve;
""",
}


def load_topics():
    with open(TOPICS_PATH, "r") as f:
        return json.load(f)


def pick_next_problem(topics, state):
    done = set(state["completed_ids"])
    candidates = [t for t in topics if t["id"] not in done]
    if not candidates:
        return None  # you've cleared the whole bank!
    # Bias towards easier problems early, harder ones as you build a streak
    random.shuffle(candidates)
    if state["streak"] >= 10:
        candidates.sort(key=lambda t: {"Easy": 0, "Medium": 1, "Hard": 2}.get(t["difficulty"], 1), reverse=True)
    return candidates[0]


def write_stub(problem, today_str):
    os.makedirs(PENDING_DIR, exist_ok=True)
    filename = f"{today_str}-{problem['id']}.js"
    path = os.path.join(PENDING_DIR, filename)
    content = STARTER_TEMPLATES["js"].format(
        title=problem["title"],
        difficulty=problem.get("difficulty", "Unknown"),
        tags=", ".join(problem.get("tags", [])),
        url=problem.get("leetcode_url", ""),
        prompt=problem["prompt"],
    )
    with open(path, "w") as f:
        f.write(content)
    return path


def main():
    today_str = date.today().isoformat()
    state = load_state()

    if state.get("pending_id"):
        allow_skip = os.environ.get("ALLOW_SKIP") == "1"
        if not allow_skip:
            print(f"Problem '{state['pending_id']}' from {state['pending_date']} is still pending. "
                  f"Solve it and push to solutions/ before the next one is assigned. "
                  f"(Set ALLOW_SKIP=1 to override.)")
            return
        else:
            print(f"Skipping unsolved pending problem '{state['pending_id']}'.")

    topics = load_topics()
    problem = pick_next_problem(topics, state)
    if problem is None:
        print("No unsolved problems left in the topic bank. Add more to topics/dsa.json!")
        return

    stub_path = write_stub(problem, today_str)
    set_pending(state, problem, today_str)

    print(f"Assigned: {problem['title']} ({problem['difficulty']}) -> {stub_path}")

    # Open a GitHub issue so it shows up as a notification, if credentials exist
    day_number = len(state["completed_ids"]) + 1
    issue_title = f"Day {day_number}: {problem['title']} ({problem['difficulty']})"
    issue_body = (
        f"**Tags:** {', '.join(problem.get('tags', []))}\n\n"
        f"{problem['prompt']}\n\n"
        f"LeetCode: {problem.get('leetcode_url', 'N/A')}\n\n"
        f"Starter file: `solutions/pending/{today_str}-{problem['id']}.js`\n\n"
        f"Solve it, then push to `solutions/pending/`. The Reviewer Agent will "
        f"generate the explanation, move it into `solutions/`, and update the README."
    )
    try:
        github.create_issue(issue_title, issue_body)
    except Exception as e:
        print(f"(Skipping issue creation: {e})")


if __name__ == "__main__":
    main()
