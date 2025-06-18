import fitz  # PyMuPDF
import re
import json

def extract_text_from_pdf(pdf_path):
    text = ""
    with fitz.open(pdf_path) as doc:
        for page in doc:
            text += page.get_text()
    return text
def extract_kwh_consumption(text):
        # Pattern 1: Look for the meter reading table format
        # JA07101850 31-12-2024 31-01-2025 31 22.222 KVAH 10340.96 11140.53 1 799.57 799.57 OK OK A
        meter_pattern = r"[A-Z0-9]+\s+\d{2}-\d{2}-\d{4}\s+\d{2}-\d{2}-\d{4}\s+\d+\s+[\d.]+\s+KVAH\s+[\d.]+\s+[\d.]+\s+\d+\s+([\d.]+)\s+([\d.]+)"
        match = re.search(meter_pattern, text)
        if match:
            return float(match.group(1))  # Return consumed units
        
        # Pattern 2: Look for Billed Units in the table
        billed_pattern = r"Billed\s+Units\s+खपत\s+([\d.]+)"
        match = re.search(billed_pattern, text)
        if match:
            return float(match.group(1))
        
        # Pattern 3: Look in previous consumption pattern
        prev_pattern = r"JAN-2025\s+([\d.]+)\s+[\d.]+\s+OK"
        match = re.search(prev_pattern, text)
        if match:
            return float(match.group(1))
        
        # Pattern 4: Look for any number followed by "799.57 799.57 OK OK"
        specific_pattern = r"(\d+\.?\d*)\s+\d+\.?\d*\s+OK\s+OK"
        match = re.search(specific_pattern, text)
        if match:
            return float(match.group(1))
        
        return 0

def extract(pdf_path):
    text = extract_text_from_pdf(pdf_path)
    text = re.sub(r'\s+', ' ', text)  # Normalize whitespace

    details = {
        "Bill Number": re.search(r"Bill No[:\s]+(\d{9,})", text),
        "Bill_date": (re.search(r"Issue Date[:\s]*जारी करने दी तरीक[:\s]*(\d{2}-\d{2}-\d{4})", text)) or (re.search(r"Issue Date[:\s]*(\d{2}-\d{2}-\d{4})", text)),
        "Due_date": re.search(r"Due Date[:\s]+(\d{2}-\d{2}-\d{4})", text),
        "Total Amount Payable": re.search(r"Amount on or before due date[:\s]+(\d+)", text),
        "Consumer Number": re.search(r"Account No[:\s]+(\d+)", text),
        "Sanction Load (KW)": re.search(r"Sanctioned Load \(kW\)[^\d]*(\d+\.\d+|\d+)", text),
        "KWH Consumption": extract_kwh_consumption(text),
                          
        "Penalty": re.search(r"Penalty\s+(\d+\.\d+|\d+)", text),
        "Charges": "",  
        "Rewards": 0,
        "Taxes and Fees": re.search(r"Electricity Duty\s+(\d+\.\d+|\d+)", text),
        "Unit Rate": 0,
        "Power Factor": 0
    }

    for key, match in details.items():
        if isinstance(match, re.Match):
            details[key] = match.group(1)
        elif match is None:
            details[key] = 0 if key in ["Rewards", "Unit Rate", "Power Factor"] else ""

    return details
