"""
Memory Agent
------------
Keeps track of what's already been done so the Planner never repeats a
problem, and keeps streak/stat data that the Doc Agent renders into the README.

State lives in progress.json at the repo root. This file is read + written
by both the daily (planner) workflow and the on-push (reviewer) workflow,
so keep it as the single source of truth.
"""
import json
import os
from datetime import date, timedelta

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROGRESS_PATH = os.path.join(ROOT, "progress.json")

DEFAULT_STATE = {
    "completed_ids": [],       # problem ids the user has actually solved
    "pending_id": None,        # problem assigned today, not yet solved
    "pending_date": None,
    "streak": 0,
    "last_completed_date": None,
    "by_tag": {},              # tag -> count, for the README stats table
    "history": []              # [{id, title, date, difficulty}]
}


def load_state():
    if not os.path.exists(PROGRESS_PATH):
        return dict(DEFAULT_STATE)
    with open(PROGRESS_PATH, "r") as f:
        data = json.load(f)
    # backfill any keys added in later versions of the schema
    for k, v in DEFAULT_STATE.items():
        data.setdefault(k, v)
    return data


def save_state(state):
    with open(PROGRESS_PATH, "w") as f:
        json.dump(state, f, indent=2)


def set_pending(state, problem, today_str):
    state["pending_id"] = problem["id"]
    state["pending_date"] = today_str
    save_state(state)


def mark_completed(state, problem, today_str):
    """Called by the reviewer once the user's own solution has been reviewed."""
    if problem["id"] not in state["completed_ids"]:
        state["completed_ids"].append(problem["id"])

    # streak: only continue if the last completion was yesterday or today
    last = state.get("last_completed_date")
    if last:
        last_date = date.fromisoformat(last)
        today = date.fromisoformat(today_str)
        if today - last_date == timedelta(days=1):
            state["streak"] += 1
        elif today == last_date:
            pass  # same day, don't double count
        else:
            state["streak"] = 1
    else:
        state["streak"] = 1

    state["last_completed_date"] = today_str
    state["pending_id"] = None
    state["pending_date"] = None

    for tag in problem.get("tags", []):
        state["by_tag"][tag] = state["by_tag"].get(tag, 0) + 1

    state["history"].append({
        "id": problem["id"],
        "title": problem["title"],
        "difficulty": problem.get("difficulty", "Unknown"),
        "date": today_str,
    })

    save_state(state)
    return state
