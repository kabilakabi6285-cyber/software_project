import re
import yaml
import os
import fnmatch


class PermissionManager:
    """Filters out sensitive files before sending code to the LLM.

    Supports both glob patterns (*.env) and regex patterns (.*\\.env$).
    """

    def __init__(self, config_path: str = ".pr-review.yml"):
        # Built-in defaults — these are glob patterns
        self.blocked_globs = [
            "*.env",
            "*.env.*",
            "secrets/*",
            "credentials/*",
            "*.pem",
            "*.key",
            "id_rsa",
            ".aws/*",
            ".ssh/*",
            "*.token",
        ]

        # Convert globs to regex once (compiled for speed)
        self.blocked_regexes = [
            self._glob_to_regex(g) for g in self.blocked_globs
        ]

        # Load extra patterns from .pr-review.yml
        if os.path.exists(config_path):
            try:
                with open(config_path) as f:
                    config = yaml.safe_load(f) or {}
                for pat in config.get("exclude_patterns", []):
                    if not pat:
                        continue
                    # If it looks like a glob (contains * or ?), convert it.
                    # Otherwise treat as regex.
                    if "*" in pat or "?" in pat:
                        self.blocked_regexes.append(self._glob_to_regex(pat))
                    else:
                        try:
                            self.blocked_regexes.append(re.compile(pat, re.IGNORECASE))
                        except re.error:
                            # Bad regex — fall back to glob handling
                            self.blocked_regexes.append(self._glob_to_regex(pat))
            except Exception as e:
                print(f"Warning: could not load {config_path}: {e}", flush=True)

    @staticmethod
    def _glob_to_regex(pattern: str) -> re.Pattern:
        """Convert a glob pattern like *.env into a compiled regex."""
        # Escape special regex chars, then turn glob wildcards into regex ones.
        escaped = re.escape(pattern)
        escaped = escaped.replace(r"\*", ".*").replace(r"\?", ".")
        return re.compile(f"^{escaped}$|/{escaped}$|.*/{escaped}$", re.IGNORECASE)

    def is_safe(self, filename: str) -> bool:
        """Return True if this file is safe to send to the LLM."""
        filename = filename.replace("\\", "/")

        for rx in self.blocked_regexes:
            if rx.search(filename) or rx.match(filename):
                return False

        return True

    def filter_diff(self, files: list) -> tuple:
        """Split files into (safe, blocked)."""
        safe, blocked = [], []
        for f in files:
            fname = getattr(f, "filename", str(f))
            if self.is_safe(fname):
                safe.append(f)
            else:
                blocked.append(fname)
        return safe, blocked