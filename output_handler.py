import csv
import json
import hashlib
from typing import List, Dict, Tuple


class OutputHandler:
    @staticmethod
    def compute_file_hash(file_path: str) -> str:
        """Compute SHA-256 hash of a file."""
        hasher = hashlib.sha256()
        try:
            with open(file_path, "rb") as f:
                while chunk := f.read(8192):
                    hasher.update(chunk)
            return hasher.hexdigest()
        except Exception as e:
            print(f"[ERROR] Could not hash file {file_path}: {e}")
            return None

    @staticmethod
    def save_to_csv(results: List[Tuple[str, Dict[str, List[str]]]], output_file: str = "output/pii_results.csv"):
        """Save PII detection results to a CSV file including file hashes for all scanned files."""
        with open(output_file, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["File Path", "SHA256 Hash", "PII Type", "Detected Values"])

            for file_path, pii_data in results:
                file_hash = OutputHandler.compute_file_hash(file_path)
                if not file_hash:
                    continue  # Skip files that couldn't be hashed

                if pii_data:
                    for pii_type, values in pii_data.items():
                        writer.writerow([file_path, file_hash, pii_type, ", ".join(values)])
                else:
                    writer.writerow([file_path, file_hash, "NONE", "No PII Detected"])

        print(f"[INFO] Results saved to CSV: {output_file}")

    @staticmethod
    def save_to_json(results: List[Tuple[str, Dict[str, List[str]]]], output_file: str = "output/pii_results.json"):
        """Save PII detection results to a JSON file including file hashes for all scanned files."""
        formatted_results = []
        for file_path, pii_data in results:
            file_hash = OutputHandler.compute_file_hash(file_path)
            if not file_hash:
                continue  # Skip files that couldn't be hashed

            formatted_results.append({"file_path": file_path, "file_hash": file_hash, "pii_data": pii_data or {"NONE": ["No PII Detected"]}})

        with open(output_file, mode="w", encoding="utf-8") as file:
            json.dump(formatted_results, file, indent=4, ensure_ascii=False)

        print(f"[INFO] Results saved to JSON: {output_file}")

    @staticmethod
    def load_previous_hashes(input_file: str) -> Dict[str, str]:
        """Load hashes from an existing CSV/JSON file to skip already scanned files."""
        previous_hashes = {}

        try:
            if input_file.endswith(".json"):
                with open(input_file, "r", encoding="utf-8") as file:
                    data = json.load(file)
                    for entry in data:
                        previous_hashes[entry["file_hash"]] = entry["file_path"]

            elif input_file.endswith(".csv"):
                with open(input_file, "r", encoding="utf-8") as file:
                    reader = csv.DictReader(file)
                    for row in reader:
                        previous_hashes[row["SHA256 Hash"]] = row["File Path"]

            print(f"[INFO] Loaded {len(previous_hashes)} previously scanned files from {input_file}")
        except Exception as e:
            print(f"[WARNING] Could not load previous hashes from {input_file}: {e}")

        return previous_hashes

    @staticmethod
    def display_summary(results: List[Tuple[str, Dict[str, List[str]]]]):
        """Display a summary of detected PII."""
        print("\n=== PII Detection Summary ===")
        for file_path, pii_data in results:
            if pii_data and pii_data.get("NONE") is None:  # If PII was found
                print(f"[PII DETECTED] {file_path}:")
                for pii_type, values in pii_data.items():
                    print(f"  - {pii_type.upper()}: {', '.join(values)}")
            else:
                print(f"[NO PII FOUND] {file_path}")

        print("\n[INFO] Scan complete. Check CSV/JSON reports for details.")
