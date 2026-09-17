import sys
import os

sys.path.insert(
    0,
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
)

from fastmcp import FastMCP
from src.github.client import GitHubClient
from src.ai.agent import PRReviewAgent

mcp = FastMCP("PR Review Agent")

github_client = GitHubClient()
agent = PRReviewAgent()


@mcp.tool()
def review_pr(pr_number: int) -> str:
    """Review a GitHub pull request and post AI-generated comments."""
    try:
        pr_data = github_client.get_pr_diff(pr_number)
        diff = pr_data["diff"]
        files = pr_data["files"]

        if not diff:
            return f"PR #{pr_number} has no changes to review."

        issues = agent.analyze_code(diff, files=files, pr_number=pr_number)

        if not issues:
            return f"Review complete for PR #{pr_number}. No issues found."

        comments = [issue.model_dump() for issue in issues]
        github_client.post_comments(pr_number, comments)

        return (
            f"Review complete for PR #{pr_number}. "
            f"Found and posted {len(issues)} issues."
        )

    except Exception as e:
        return f"Error reviewing PR #{pr_number}: {str(e)}"


@mcp.tool()
def get_pr_diff(pr_number: int) -> str:
    """Get the diff of a pull request."""
    try:
        pr_data = github_client.get_pr_diff(pr_number)
        diff = pr_data["diff"]
        return diff[:2000] + "..." if len(diff) > 2000 else diff
    except Exception as e:
        return f"Error: {str(e)}"


if __name__ == "__main__":
    mcp.run(transport="stdio")