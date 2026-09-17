import os
import json
from google import genai
from google.genai import types
from pydantic import BaseModel
from typing import List, Optional
from dotenv import load_dotenv

load_dotenv()


class ReviewIssue(BaseModel):
    file: str
    line: int
    severity: str  # "high", "medium", or "low"
    category: str  # e.g., "bug", "style", "error-handling"
    comment: str
    suggestion: Optional[str] = None


class PRReviewAgent:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY is not set in .env file")
        
        self.client = genai.Client(api_key=api_key)
        self.model_name = os.getenv("GEMINI_MODEL", "gemini-3.1-flash-lite")
        print(f" Using Gemini model: {self.model_name}")

    def analyze_code(self, diff: str) -> List[ReviewIssue]:
        """Sends the PR diff to Gemini and gets structured review comments."""
        if not diff or not diff.strip():
            return []

        #  Properly closed multi-line f-string
        prompt = f"""You are a senior software engineer conducting a code review.
Analyze the following PR diff and identify issues.

Focus on:
1. Bugs and logic errors.
2. Missing error handling.
3. Security vulnerabilities.
4. Code style and best practices.

Here is the diff to review:

{diff}

Return a JSON array of issues.
"""

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_json_schema=ReviewIssue.model_json_schema(),
                    system_instruction="You are an expert code reviewer. Provide actionable feedback."
                )
            )
            
            # The response text is guaranteed to be valid JSON
            data = json.loads(response.text)
            
            # The response might be a single object or a list; handle both cases
            issues_data = data if isinstance(data, list) else [data]
            
            return [ReviewIssue(**item) for item in issues_data]
            
        except Exception as e:
            print(f" Error during Gemini analysis: {e}")
            return []