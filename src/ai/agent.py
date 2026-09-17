import os
import json
from google import genai
from google.genai import types
from pydantic import BaseModel
from typing import List, Optional
from dotenv import load_dotenv

from src.auth.permissions import PermissionManager
from src.auth.audit import AuditLogger
from src.learning.history import ReviewHistoryStore

load_dotenv()


class ReviewIssue(BaseModel):
    file: str
    line: int
    severity: str  # "high", "medium", or "low"
    category: str  # "bug", "style", "error-handling", "security"
    comment: str
    suggestion: Optional[str] = None


class PRReviewAgent:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY is not set in .env")

        self.client = genai.Client(api_key=api_key)
        self.model_name = os.getenv("GEMINI_MODEL", "gemini-3.1-flash-lite")

        # Part A: Permissions + Audit
        self.permissions = PermissionManager()
        self.audit = AuditLogger()

        # Part B: Team Learning
        self.history = ReviewHistoryStore()

        print(f"Using Gemini model: {self.model_name}", flush=True)

    def analyze_code(
        self,
        diff: str,
        files: list = None,
        pr_number: int = None,
    ) -> List[ReviewIssue]:
        """Analyze a PR diff with Gemini, applying permissions and learning."""
        if not diff or not diff.strip():
            return []

        # ---------- Part A: Permission filtering ----------
        if files:
            safe_files, blocked = self.permissions.filter_diff(files)
            if blocked:
                print(f"Blocked sensitive files: {blocked}", flush=True)
                # Rebuild diff using only safe files
                diff = ""
                for f in safe_files:
                    patch = getattr(f, "patch", None)
                    fname = getattr(f, "filename", str(f))
                    if patch:
                        diff += f"--- {fname}\n{patch}\n\n"

        if not diff.strip():
            print("No safe files to review after filtering.", flush=True)
            return []

        # ---------- Part B: Few-shot examples from history ----------
        examples = self.history.get_few_shot_examples(limit=3)
        examples_text = ""
        if examples:
            examples_text = (
                "\nHere are examples of reviews our team has accepted:\n"
            )
            for ex in examples:
                examples_text += f"- [{ex['severity']}] {ex['comment']}\n"
            examples_text += "\nMatch this style of feedback.\n"

        # ---------- Build prompt ----------
        prompt = f"""You are a senior software engineer conducting a code review.
Analyze the following PR diff and identify issues.

Focus on:
1. Bugs and logic errors.
2. Missing error handling.
3. Security vulnerabilities.
4. Code style and best practices.
{examples_text}
Here is the diff to review:

{diff}
"""

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_json_schema=ReviewIssue.model_json_schema(),
                    system_instruction=(
                        "You are an expert code reviewer. "
                        "Provide actionable feedback."
                    ),
                ),
            )

            data = json.loads(response.text)
            issues_data = data if isinstance(data, list) else [data]
            issues = [ReviewIssue(**item) for item in issues_data]

            # ---------- Part B: Store reviews in history ----------
            if pr_number:
                for issue in issues:
                    self.history.store(
                        pr_number=pr_number,
                        file=issue.file,
                        comment=issue.comment,
                        category=issue.category,
                        severity=issue.severity,
                        accepted=False,
                    )

            # ---------- Part A: Audit log ----------
            self.audit.log(
                action="analyze_code",
                user="github-actions",
                result="success",
                resource=f"PR#{pr_number}" if pr_number else "local",
                details={
                    "model": self.model_name,
                    "issues_found": len(issues),
                    "diff_length": len(diff),
                },
            )

            return issues

        except Exception as e:
            self.audit.log(
                action="analyze_code",
                user="github-actions",
                result="failure",
                resource=f"PR#{pr_number}" if pr_number else "local",
                details={"error": str(e)},
            )
            print(f"Error during Gemini analysis: {e}", flush=True)
            return []