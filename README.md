# 🚀 CodeSprint AI

> An automation pipeline that assigns me a daily coding problem, and once I solve it myself,
> reviews it, writes up the explanation, and updates this README. The agent plans and
> documents; I do the solving.

**How it works:** every day a GitHub Action opens an issue with a new problem and drops a
starter file in `solutions/pending/`. I solve it and push. A second workflow picks up my
solution, generates the write-up, moves it into `solutions/`, and updates the stats below.

---

### 🔥 Current Streak: 0 days

### ✅ Problems Solved: 0

### 📊 By Topic

_No problems completed yet._

### 🕒 Recent History

_No problems completed yet._


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
