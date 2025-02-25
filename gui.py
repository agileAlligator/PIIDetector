import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import threading
import concurrent.futures

# Import your modules as in your original code
from input_handler import InputHandler    # Module 1
from filereader import FileReader          # Module 2
from pii_analyzer import PIIAnalyzer        # Module 3
from output_handler import OutputHandler    # Module 5


def process_file(file_path, mime_type):
    """Process a single file - Extract text & Detect PII."""
    reader = FileReader()
    extracted_text = reader.extract_text(file_path, mime_type)
    
    
    if not extracted_text.strip():
        return (file_path, {})

    # PII Detection
    pii_results = PIIAnalyzer.analyze(extracted_text)
    return (file_path, pii_results)


def run_processing(directory, max_depth, include_hidden, log_widget):
    """Main processing function to be run in a separate thread."""
    try:
        max_depth = int(max_depth)
        max_depth = None if max_depth == -1 else max_depth
    except ValueError:
        messagebox.showerror("Invalid Input", "Max depth must be an integer.")
        return

    # === Module 1: Collect Files ===
    input_handler = InputHandler(directory, max_depth=max_depth, include_hidden=include_hidden)
    files_with_mime = input_handler.collect_files()
    if not files_with_mime:
        log_widget.insert(tk.END, "No valid files detected.\n")
        return

    log_widget.insert(tk.END, f"Found {len(files_with_mime)} potential PII files. Processing in parallel...\n")
    log_widget.see(tk.END)

    # === Modules 2 & 3: Parallel Processing ===
    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = list(executor.map(lambda f: process_file(*f), files_with_mime))

    log_widget.insert(tk.END, "Processing complete.\n\n")
    log_widget.see(tk.END)

    # === Displaying Results ===
    log_widget.insert(tk.END, "Results:\n")
    for file_path, pii_results in results:
        if pii_results:
            log_widget.insert(tk.END, f"File: {file_path}\nPII: {pii_results}\n\n")
        else:
            log_widget.insert(tk.END, f"File: {file_path}\nNo PII detected.\n\n")
    log_widget.see(tk.END)

    # === Module 5: Save & Display Results (optional) ===
    OutputHandler.display_summary(results)
    OutputHandler.save_to_csv(results)
    OutputHandler.save_to_json(results)


def start_processing(log_widget, directory_entry, depth_entry, hidden_var):
    """Callback for the Start Processing button."""
    directory = directory_entry.get()
    if not directory:
        messagebox.showerror("Input Error", "Please select a directory.")
        return

    max_depth = depth_entry.get()
    include_hidden = bool(hidden_var.get())

    # Start processing in a separate thread to avoid blocking the GUI.
    threading.Thread(
        target=run_processing, 
        args=(directory, max_depth, include_hidden, log_widget),
        daemon=True
    ).start()


def browse_directory(directory_entry):
    """Opens a directory chooser dialog and updates the directory entry."""
    selected_dir = filedialog.askdirectory()
    if selected_dir:
        directory_entry.delete(0, tk.END)
        directory_entry.insert(0, selected_dir)


def create_gui():
    """Sets up the main GUI window."""
    root = tk.Tk()
    root.title("PII File Scanner")

    # Input frame for parameters.
    input_frame = tk.Frame(root)
    input_frame.pack(padx=10, pady=10)

    # Directory selection.
    tk.Label(input_frame, text="Directory:").grid(row=0, column=0, sticky="e")
    directory_entry = tk.Entry(input_frame, width=40)
    directory_entry.grid(row=0, column=1, padx=5)
    tk.Button(input_frame, text="Browse", command=lambda: browse_directory(directory_entry)).grid(row=0, column=2, padx=5)

    # Max depth input.
    tk.Label(input_frame, text="Max Depth (0 for current, -1 for unlimited):").grid(row=1, column=0, sticky="e")
    depth_entry = tk.Entry(input_frame, width=10)
    depth_entry.grid(row=1, column=1, sticky="w", padx=5)

    # Include hidden files.
    hidden_var = tk.IntVar()
    tk.Checkbutton(input_frame, text="Include hidden files", variable=hidden_var).grid(row=2, column=1, sticky="w")

    # Start button.
    tk.Button(root, text="Start Processing", 
              command=lambda: start_processing(log_widget, directory_entry, depth_entry, hidden_var)
             ).pack(pady=5)

    # Scrolled text area to display logs and results.
    log_widget = scrolledtext.ScrolledText(root, width=80, height=20)
    log_widget.pack(padx=10, pady=10)

    root.mainloop()


if __name__ == "__main__":
    create_gui()
