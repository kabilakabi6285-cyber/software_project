import os
from github import Github
from dotenv import load_dotenv

load_dotenv()

class GitHubClient:
    def __init__(self):
        self.github = Github(os.getenv("GITHUB_TOKEN"))
        self.repo_name = os.getenv("GITHUB_REPO")
        self.repo = self.github.get_repo(self.repo_name)

    def get_pr_diff(self, pr_number: int) -> dict:
        """Fetches the diff and list of changed files for a given PR."""
        pr = self.repo.get_pull(pr_number)
        files = pr.get_files()
        
        # Combine patches into a single diff string
        diff_content = ""
        for file in files:
            if file.patch:
                diff_content += f"--- {file.filename}\n{file.patch}\n\n"
        
        return {"files": list(files), "diff": diff_content}

    def post_comments(self, pr_number: int, comments: list[dict]):
        """Posts a summary comment to the PR."""
        pr = self.repo.get_pull(pr_number)
        
        summary = "##  AI Code Review Summary\n\n"
        for comment in comments:
            emoji = "" if comment.get("severity") == "high" else "" if comment.get("severity") == "medium" else ""
            summary += f"- {emoji} **{comment['file']}:{comment['line']}** - {comment['comment']}\n"
        
        pr.create_issue_comment(summary)
        print(f" Posted summary comment to PR #{pr_number}")