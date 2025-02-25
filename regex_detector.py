import re
import json


class RegexDetector:
    PATTERNS = {}

    @staticmethod
    def load_patterns(pattern_file="data/regex_patterns.json"):
        """Load regex patterns from an external JSON file."""
        try:
            with open(pattern_file, "r", encoding="utf-8-sig") as file:
                file.seek(0)
                patterns = json.load(file)
                # Convert regex strings to compiled patterns
                RegexDetector.PATTERNS = {key: re.compile(value) for key, value in patterns.items()}
        except Exception as e:
            print(f"[ERROR] Failed to load regex patterns: {e}")
            RegexDetector.PATTERNS = {}  # Fail-safe

    @staticmethod
    def detect(text: str) -> dict:
        """Detect PII using regex patterns."""
        if not RegexDetector.PATTERNS:
            RegexDetector.load_patterns()  # Ensure patterns are loaded

        matches = {}
        for pii_type, pattern in RegexDetector.PATTERNS.items():
            found = pattern.findall(text)
            if found:
                matches[pii_type] = found
        return matches


# Load patterns when the module is imported
RegexDetector.load_patterns()
