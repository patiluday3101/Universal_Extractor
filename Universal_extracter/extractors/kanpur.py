import fitz  # PyMuPDF
import re
import json

def extract_text_from_pdf(pdf_path):
    text = ""
    doc = fitz.open(pdf_path)
    for page in doc:
        text += page.get_text()
    return text

def extract(pdf_path):
    text = extract_text_from_pdf(pdf_path)
    details = {
        "Bill Number": re.search(r"िबल संखया/ Bill Number\s*:\s*(\d+)", text),
        "Bill_date": re.search(r"िबल ितिथ / Bill Date\s*(\d{2}-[A-Z]{3}-\d{4})", text),
        "Due_date": re.search(r"देय ितिथ / Due Date\s*(\d{2}-[A-Z]{3}-\d{4})", text),
        "Total Amount Payable": re.search(r"देय धनरािश ?/ ?Payable Amount\s+(\d+)", text),
        "Consumer Number": re.search(r"Account No.\s*:\s*(\d+)", text),
        "Sanction Load (KW)": re.search(r"सवीकृत भार / Sanction Load\s*:\s*(\d+)", text),
        "KWH Consumption": re.search(r"Net Billed Unit\s*\n\s*(\d+\.\d+)", text),
        "Penalty": re.search(r"अितिरक मांग पभार.*?(\d+\.\d+)", text),
        "Charges": 0,  # Not directly extractable
        "Rewards": 0,
        "Taxes and Fees": re.search(r"िवदुत कर / Electricity Duty\s+(\d+\.\d+)", text),
        "Unit Rate": 0,  
        "Power Factor": re.search(r"Power Factor.*?(\d+\.\d+)", text)
    }

    for key, match in details.items():
        if isinstance(match, re.Match):
            details[key] = match.group(1)
        elif details[key] is None:
            if key == "Power Factor":
                details[key] = 0  
            else:
                details[key] = ""

    return details