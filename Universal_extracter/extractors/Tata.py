import re
import pdfplumber
import time
from typing import Dict, Any
import PyPDF2
def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract text from PDF using PyPDF2"""
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            for page in pdf_reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text
            return text
    except Exception as e:
        print(f"Error reading PDF {pdf_path}: {str(e)}")
        return ""

def extract(pdf_path):
    text= extract_text_from_pdf(pdf_path)
    details = {
        "Bill Number": None, "Bill Date": None, "Due Date": None, "Due Amount": None,
        "Delay Amount": None, "Power Factor": None, "Sanction Load": None, "KWh Units": None
    }


    patterns = {
        "Bill Number": r"Bill No\.\s*:?\s*(\d+)",
        "Bill Date": r"Bill Date\s*:?\s*(\d{2}\.\d{2}\.\d{4})",
        "Due Date": r"Due Date\s*:?\s*(\d{2}\.\d{2}\.\d{4})",
        "Due Amount": r"Bill Amount\s*:?\s*Rs\.\s*([\d,]+\.\d{2})",
        "Delay Amount": r"Amt After Due Dt\.\s*:\s*Rs\.\s*([\d,]+\.\d{2})",
        "Power Factor": r"Power Factor:\s*([0-9\.]+)\s*\((Lead|Lag)\)",
        "Sanction Load": r"Sanctioned load \(kW\):\s*(\d+\.\d+)",
        "KWh Units": r"Total UNITS \(kWh\)\s*:?\s*([\d,]+)"
    }

    for key, pattern in patterns.items():
        match = re.search(pattern, text)
        if match:
            if key == "Power Factor":
                details[key] = f"{match.group(1)} ({match.group(2)})"
            else:
                details[key] = match.group(1).replace(",", "") if "Amount" in key else match.group(1)

    return details
# def open_pdf_safely(pdf_path):
#     for _ in range(5):  
#         try:
#             with pdfplumber.open(pdf_path) as pdf:
#                 return "\n".join(page.extract_text() for page in pdf.pages if page.extract_text())
#         except Exception as e:
#             print(f"Retrying PDF read due to: {e}")
#             time.sleep(1)  
#     return ""