"""
GitHub Agent
------------
Small wrapper around the GitHub REST API. Used only for opening issues
(the actual commit/push is done directly in the workflow YAML via git,
which is simpler and needs no extra permissions beyond `contents: write`).

Requires two environment variables, both provided automatically inside
GitHub Actions:
  GITHUB_TOKEN   - the workflow's automatic token (needs `issues: write`)
  GITHUB_REPOSITORY - "owner/repo", set automatically by Actions
"""
import json
import os
import urllib.request


def create_issue(title: str, body: str):
    token = os.environ.get("GITHUB_TOKEN")
    repo = os.environ.get("GITHUB_REPOSITORY")
    if not token or not repo:
        raise RuntimeError("GITHUB_TOKEN / GITHUB_REPOSITORY not set (not running in Actions?)")

    url = f"https://api.github.com/repos/{repo}/issues"
    payload = json.dumps({"title": title, "body": body}).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=payload,
        method="POST",
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "Content-Type": "application/json",
            "User-Agent": "codesprint-ai-agent",
        },
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())
