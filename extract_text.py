import pdfplumber
import os

pdf_dir = r"D:\Files\MUC-QMJH\References\Papers\English"
output_file = r"D:\Files\MUC-QMJH\References\Papers\extracted_abstracts.txt"

files = [f for f in os.listdir(pdf_dir) if f.lower().endswith(".pdf")]

with open(output_file, "w", encoding="utf-8") as out:
    for filename in files:
        filepath = os.path.join(pdf_dir, filename)
        print(f"Processing {filename}...")
        try:
            with pdfplumber.open(filepath) as pdf:
                out.write(f"=== {filename} ===\n")
                # Extract from first 4 pages (or fewer if the doc is shorter)
                limit = min(4, len(pdf.pages))
                for i in range(limit):
                    text = pdf.pages[i].extract_text()
                    if text:
                        out.write(text + "\n")
                out.write("\n\n")
            print(f"Success: {filename}")
        except Exception as e:
            print(f"Failure: {filename} - {e}")
