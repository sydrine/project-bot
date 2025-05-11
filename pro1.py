
import os
import json
import pdfplumber
from pdf2image import convert_from_path
import pytesseract
import tempfile
import re
import tkinter as tk
from tkinter import filedialog

def clean_text(text):
    """Remove excessive newlines and strip leading/trailing spaces."""
    text = re.sub(r'\n+', '\n', text)
    return text.strip()

def extract_text_from_pdf(file_path, min_text_length=100):
    """Extract text from PDF using pdfplumber, fallback to OCR if too short."""
    text = ""
    try:
        with pdfplumber.open(file_path) as pdf:
            text = "\n".join(page.extract_text() or "" for page in pdf.pages)
    except Exception as e:
        print(f"[pdfplumber error] {e}")

    if len(text.strip()) < min_text_length:
        print("⚠️ Text too short. Falling back to OCR...")
        text = ""
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                images = convert_from_path(file_path, output_folder=temp_dir)
                for img in images:
                    text += pytesseract.image_to_string(img)
        except Exception as e:
            print(f"[OCR error] {e}")
            text = ""
    return clean_text(text)

def extract_sections(text):
    """Extract only Skills, Projects, and Experience sections from resume text."""
    section_patterns = {
        'Skills': r'(Skills|Technical Skills|Core Competencies)[\s:\-]*\n(.*?)(?=\n[A-Z][a-z]|$)',
        'Projects': r'(Projects|Project Experience|Academic Projects)[\s:\-]*\n(.*?)(?=\n[A-Z][a-z]|$)',
        'Experience': r'(Experience|Work Experience|Professional Experience)[\s:\-]*\n(.*?)(?=\n[A-Z][a-z]|$)',
    }

    extracted = {}
    for section, pattern in section_patterns.items():
        match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
        if match:
            extracted[section] = match.group(2).strip()
        else:
            extracted[section] = "Not found"

    return extracted

# ✅ Properly initialize tkinter
root = tk.Tk()
root.withdraw()  # Hide the root window

print("📁 Please select a PDF or JSON file...")
file_path = filedialog.askopenfilename(
    title="Select a resume file",
    filetypes=[("PDF and JSON files", "*.pdf *.json")]
)

if not file_path:
    print("❌ No file selected. Exiting.")
    exit()

filename = os.path.basename(file_path)
print("✅ Selected file:", filename)

# Handle file based on its extension
if filename.lower().endswith(".pdf"):
    print("\n📄 Detected PDF file. Extracting text...\n")
    full_text = extract_text_from_pdf(file_path)
    sections = extract_sections(full_text)

    print("\n=== Extracted Resume Sections ===")
    for section, content in sections.items():
        print(f"\n--- {section} ---\n{content[:2000]}")  # Limit long sections

elif filename.lower().endswith(".json"):
    print("\n📦 Detected JSON file. Reading contents...\n")
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print("=== JSON Content ===")
        print(json.dumps(data, indent=2))
    except Exception as e:
        print(f"❌ Error reading JSON: {e}")

else:
    print("❌ Unsupported file type. Please select a .pdf or .json file.")
