"""
Reviewer + Documentation Agent
-------------------------------
Triggered on push, when a file changes under solutions/pending/.

IMPORTANT BOUNDARY: this agent never writes or rewrites your solution logic.
It only reads the solution YOU already wrote, and:
  1. Generates a Markdown explanation (approach, complexity, edge cases).
  2. Generates a short code review (things to double check / alternatives),
     appended as comments, not a rewrite.
  3. Moves the file from solutions/pending/ -> solutions/
  4. Marks the problem completed in progress.json (streak, tags, history).
  5. Calls the Doc Agent to regenerate README.md.

If the pending file still has the TODO / empty stub body, it refuses to mark
the problem complete -- that's the guardrail that keeps this from turning
into an auto-solver.
"""
import json
import os
import sys
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from memory import load_state, mark_completed
import readme as doc_agent

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOPICS_PATH = os.path.join(ROOT, "topics", "dsa.json")
PENDING_DIR = os.path.join(ROOT, "solutions", "pending")
SOLUTIONS_DIR = os.path.join(ROOT, "solutions")

ANTHROPIC_MODEL = os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-5")


def load_topics():
    with open(TOPICS_PATH, "r") as f:
        return {t["id"]: t for t in json.load(f)}


def looks_unsolved(code: str) -> bool:
    """Guardrail: refuse to 'complete' a problem whose stub is still empty."""
    stripped = code.strip()
    if "// TODO: your solution here" in stripped and len(stripped.splitlines()) < 20:
        return True
    return False


def call_claude(prompt: str) -> str:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError("ANTHROPIC_API_KEY not set")
    payload = json.dumps({
        "model": ANTHROPIC_MODEL,
        "max_tokens": 1000,
        "messages": [{"role": "user", "content": prompt}],
    }).encode("utf-8")
    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=payload,
        method="POST",
        headers={
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
    )
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read())
    return "".join(block.get("text", "") for block in data.get("content", []))


def build_review_prompt(problem, user_code):
    return f"""You are reviewing a HUMAN'S OWN solution to a coding problem. Do not
rewrite or replace their code. Your job is only to:

1. Write a short Markdown explanation of the approach *that this code actually uses*
   (don't invent a different approach).
2. State the time and space complexity of THIS implementation.
3. Point out (briefly) any edge cases it might miss, or a possible follow-up
   optimization -- as suggestions, not corrections.

Problem: {problem['title']} ({problem['difficulty']})
Tags: {', '.join(problem.get('tags', []))}
Prompt: {problem['prompt']}

User's solution:
```javascript
{user_code}
```

Respond in Markdown with sections: ## Approach, ## Complexity, ## Notes.
Keep it concise -- this is going into a daily learning log, not a textbook.
"""


def find_pending_files():
    if not os.path.isdir(PENDING_DIR):
        return []
    return [f for f in os.listdir(PENDING_DIR) if f.endswith(".js")]


def main():
    topics = load_topics()
    state = load_state()
    pending_files = find_pending_files()

    if not pending_files:
        print("No pending solutions found. Nothing to review.")
        return

    for filename in pending_files:
        # filename format: YYYY-MM-DD-<slug>.js
        date_str = filename[:10]
        slug = filename[11:-3]
        problem = topics.get(slug)
        if problem is None:
            print(f"Skipping {filename}: no matching problem in topics/dsa.json")
            continue

        path = os.path.join(PENDING_DIR, filename)
        with open(path, "r") as f:
            user_code = f.read()

        if looks_unsolved(user_code):
            print(f"Skipping {filename}: looks like the stub hasn't been solved yet.")
            continue

        try:
            explanation = call_claude(build_review_prompt(problem, user_code))
        except Exception as e:
            print(f"Could not generate explanation for {filename}: {e}")
            explanation = "_(explanation generation unavailable this run)_"

        # Move solution + write explanation into solutions/
        os.makedirs(SOLUTIONS_DIR, exist_ok=True)
        final_code_path = os.path.join(SOLUTIONS_DIR, filename)
        with open(final_code_path, "w") as f:
            f.write(user_code)
        os.remove(path)

        explanation_path = os.path.join(SOLUTIONS_DIR, f"{date_str}-{slug}.md")
        with open(explanation_path, "w") as f:
            f.write(f"# {problem['title']} ({problem['difficulty']})\n\n{explanation}\n")

        state = mark_completed(state, problem, date_str)
        print(f"Reviewed and completed: {problem['title']} -> {final_code_path}, {explanation_path}")

    doc_agent.regenerate(state)
    print("README.md updated.")


if __name__ == "__main__":
    main()
