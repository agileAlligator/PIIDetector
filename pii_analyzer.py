from regex_detector import RegexDetector
from ner_detector import NERDetector


class PIIAnalyzer:
    @staticmethod
    def analyze(text: str) -> dict:
        pii_matches = RegexDetector.detect(text)
        ner_matches = NERDetector.detect(text)

        # Merge regex and NER results
        pii_matches.update(ner_matches)
        return pii_matches
