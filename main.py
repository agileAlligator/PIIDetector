import concurrent.futures
from input_handler import InputHandler  # Module 1
from filereader import FileReader      # Module 2
from pii_analyzer import PIIAnalyzer    # Module 3
from output_handler import OutputHandler  # Module 5


def process_file(file_path, mime_type, previous_hashes):
    """Process a single file - Extract text & Detect PII, skipping already scanned files."""
    file_hash = OutputHandler.compute_file_hash(file_path)

    if file_hash in previous_hashes:
        print(f"[SKIPPED] {file_path} (Already Scanned)")
        return None  # Skip this file

    reader = FileReader()
    extracted_text = reader.extract_text(file_path, mime_type)

    if not extracted_text.strip():
        return (file_path, {})

    pii_results = PIIAnalyzer.analyze(extracted_text)

    return (file_path, pii_results)


def main():
    # === Load Previously Scanned Files ===
    previous_results_file = input("Enter previous results file (CSV/JSON) or press Enter to skip: ").strip()
    previous_hashes = OutputHandler.load_previous_hashes(previous_results_file) if previous_results_file else {}

    # === Module 1: Collect Files ===
    base_path = input("Enter directory path to scan: ")
    max_depth = int(input("Enter max depth (0 for current dir only, -1 for unlimited): "))
    include_hidden = input("Include hidden files? (y/n): ").strip().lower() == 'y'

    max_depth = None if max_depth == -1 else max_depth

    input_handler = InputHandler(base_path, max_depth=max_depth, include_hidden=include_hidden)
    files_with_mime = input_handler.collect_files()

    if not files_with_mime:
        print("No valid files detected.")
        return

    print(f"Found {len(files_with_mime)} potential PII files. Processing in parallel...")

    # === Module 2 & 3: Parallel Processing with Hash Skipping ===
    results = []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        processed_files = list(executor.map(lambda f: process_file(*f, previous_hashes), files_with_mime))

    # Filter out skipped files (None results)
    results = [res for res in processed_files if res is not None]

    # === Module 5: Save & Display Results ===
    OutputHandler.display_summary(results)
    OutputHandler.save_to_csv(results)
    OutputHandler.save_to_json(results)


if __name__ == "__main__":
    main()
