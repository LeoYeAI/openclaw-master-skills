import os
import sys
import shutil
import zipfile
import pdfplumber
from datetime import datetime

def extract_text_from_pdf(pdf_path):
    """Extract text from PDF file using pdfplumber"""
    text = ""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except Exception as e:
        print(f"Error extracting text from {pdf_path}: {e}")
    return text

def extract_zip_if_needed(zip_path, extract_dir):
    """Extract ZIP file if needed"""
    if zipfile.is_zipfile(zip_path):
        print(f"Extracting ZIP file: {zip_path}")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)
        return extract_dir
    return os.path.dirname(zip_path)

def main():
    if len(sys.argv) < 2:
        print("Usage: python step1_extract_resumes.py <zip_or_resume_path> [output_dir]")
        print("Example: python step1_extract_resumes.py resumes.zip resumes_output")
        sys.exit(1)

    input_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "resumes_text"

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = f"{output_dir}_{timestamp}"

    os.makedirs(output_dir, exist_ok=True)

    temp_dir = os.path.join(output_dir, "temp")
    os.makedirs(temp_dir, exist_ok=True)

    resume_dir = extract_zip_if_needed(input_path, temp_dir)

    pdf_files = []
    for root, dirs, files in os.walk(resume_dir):
        for file in files:
            if file.lower().endswith('.pdf'):
                pdf_files.append(os.path.join(root, file))

    print(f"Found {len(pdf_files)} PDF files to process")

    success_count = 0
    for pdf_file in pdf_files:
        print(f"Processing: {os.path.basename(pdf_file)}")

        text = extract_text_from_pdf(pdf_file)

        base_name = os.path.splitext(os.path.basename(pdf_file))[0]
        output_file = os.path.join(output_dir, f"{base_name}.txt")

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(text)

        print(f"  -> Saved to {output_file}")
        success_count += 1

    shutil.rmtree(temp_dir)

    print(f"\nDone! Successfully extracted {success_count} resumes to {output_dir}")
    print(f"Output directory: {os.path.abspath(output_dir)}")

if __name__ == "__main__":
    main()
