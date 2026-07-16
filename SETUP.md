# Setup

## 1. Create the repo
Push this folder as a new GitHub repo (public, so it shows on your profile contribution graph).

```bash
cd CodeSprint-AI
git init
git add .
git commit -m "init: CodeSprint AI"
git branch -M main
git remote add origin https://github.com/<you>/CodeSprint-AI.git
git push -u origin main
```

## 2. Add one secret
Only one secret is needed: an Anthropic API key, used by the Reviewer Agent to write the
explanation for a solution you've already submitted (it never uses this key to solve anything).

Repo → Settings → Secrets and variables → Actions → New repository secret:
- Name: `ANTHROPIC_API_KEY`
- Value: your key from console.anthropic.com

`GITHUB_TOKEN` is provided automatically by Actions -- nothing to add there.

## 3. Enable Actions
Repo → Actions tab → enable workflows if prompted. Two workflows exist:
- `daily.yml` — runs every day at 06:00 UTC, assigns a new problem (only if you don't
  already have one pending), opens a GitHub issue, and commits the stub file.
- `review.yml` — runs whenever you push a change under `solutions/pending/`, generates
  the explanation for *your* code, moves it into `solutions/`, and updates the README.

You can also trigger either manually from the Actions tab (`workflow_dispatch`) to test them
without waiting for the cron.

## 4. Daily routine
1. Check the day's GitHub issue (or `solutions/pending/`) for today's problem.
2. Solve it yourself in the stub file. Don't touch the comment header.
3. `git add solutions/pending && git commit -m "solve: <problem>" && git push`
4. The review workflow picks it up within a minute or two, and the README updates itself.

## 5. Growing the problem bank
`topics/dsa.json` currently has 12 problems. Add more objects in the same shape
(`id`, `title`, `difficulty`, `tags`, `prompt`, `leetcode_url`) whenever you're running low --
the planner will refuse to hand out duplicates and will tell you when the bank is empty.

You can also add `topics/web.json`, `topics/system_design.json`, etc. and extend
`agent/planner.py`'s `load_topics()` to pull from all of them if you want to branch out
beyond DSA later (this is exactly how the original CodeSprint AI concept scales up to
multiple tracks).
