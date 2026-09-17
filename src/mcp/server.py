from fastmcp import FastMCP
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

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
        
        if not diff:
            return f"PR #{pr_number} has no changes to review."

        issues = agent.analyze_code(diff)
        
        if not issues:
            return f"Review complete for PR #{pr_number}. No issues found."

        comments = [issue.model_dump() for issue in issues]
        github_client.post_comments(pr_number, comments)
        
        return f" Review complete for PR #{pr_number}. Found and posted {len(issues)} issues."
    
    except Exception as e:
        return f" Error reviewing PR #{pr_number}: {str(e)}"


@mcp.tool()
def get_pr_diff(pr_number: int) -> str:
    """Get the diff of a pull request."""
    try:
        pr_data = github_client.get_pr_diff(pr_number)
        return pr_data["diff"][:2000] + "..."
    except Exception as e:
        return f"Error: {str(e)}"


if __name__ == "__main__":
    mcp.run(transport="stdio")