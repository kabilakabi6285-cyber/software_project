"""PR Review Agent — Complete Demo"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.github.client import GitHubClient
from src.ai.agent import PRReviewAgent
from src.auth.permissions import PermissionManager
from src.auth.audit import AuditLogger
from src.learning.history import ReviewHistoryStore


def hr(title=""):
    print("=" * 60)
    if title:
        print(f"  {title}")
        print("=" * 60)


def main():
    hr("PR REVIEW AGENT — LIVE DEMO")
    print()

    # 1. GitHub
    print("[1] Connecting to GitHub...")
    client = GitHubClient()
    try:
        pr_num = int(input("Enter a PR number to review [default 1]: ") or "1")
    except ValueError:
        pr_num = 1
    data = client.get_pr_diff(pr_num)
    print(f"    [OK] Fetched PR #{pr_num}: {len(list(data['files']))} files")
    print()

    # 2. Permissions
    print("[2] Applying permission filters...")
    pm = PermissionManager()
    safe, blocked = pm.filter_diff(data["files"])
    print(f"    [OK] {len(safe)} safe files, {len(blocked)} blocked")
    if blocked:
        print(f"    [BLOCKED] {blocked}")
    print()

    # 3. AI Analysis
    print("[3] Analyzing with Gemini...")
    agent = PRReviewAgent()
    issues = agent.analyze_code(
        data["diff"],
        files=data["files"],
        pr_number=pr_num,
    )
    print(f"    [OK] Found {len(issues)} issues")
    print()

    # 4. Display issues
    if issues:
        print("[4] Issues found:")
        for i, issue in enumerate(issues, 1):
            print(f"    {i}. [{issue.severity.upper()}] {issue.file}:{issue.line}")
            print(f"       {issue.comment}")
            if issue.suggestion:
                print(f"       -> {issue.suggestion}")
        print()
    else:
        print("[4] No issues found — PR is clean!")
        print()

    # 5. Post to GitHub
    if issues:
        print("[5] Posting comments to GitHub...")
        comments = [i.model_dump() for i in issues]
        client.post_comments(pr_num, comments)
        print(f"    [OK] Posted {len(comments)} comments")
    else:
        print("[5] Skipping — no comments to post")
    print()

    # 6. Audit
    print("[6] Recent audit log:")
    audit = AuditLogger()
    for entry in audit.recent(3):
        ts = entry["timestamp"][:19]
        print(f"    [{ts}] {entry['action']} -> {entry['result']} ({entry['resource']})")
    print()

    # 7. History
    print("[7] Learning history:")
    history = ReviewHistoryStore()
    examples = history.get_few_shot_examples(5)
    print(f"    {len(examples)} accepted examples stored")
    print()

    hr("DEMO COMPLETE")
    print()
    print(f"Check your PR at:")
    print(f"https://github.com/{os.getenv('GITHUB_REPO')}/pull/{pr_num}")
    print()


if __name__ == "__main__":
    main()