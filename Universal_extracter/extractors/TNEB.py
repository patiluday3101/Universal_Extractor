import re
from typing import Optional, Dict, Any
from datetime import datetime
import PyPDF2
import pdf2image
import pytesseract

PATTERNS = {
    'consumer_name': [
        r'Name[:/\s]*([A-Z\s\.]+)(?=\n|Address|SF)',
        r'Consumer[:\s]*([A-Z\s\.]+)',
        r'Name/Address[^:]:\s([A-Z\s\.]+)'
    ],
    'service_connection': [
        r'Service Connection Number[:\s]*(\d{2}-\d{3}-\d{3}-\d{4})',
        r'Servie Connection Number[:\s]*(\d{2}-\d{3}-\d{3}-\d{4})',
        r'Connection Number[:\s]*(\d{2}-\d{3}-\d{3}-\d{4})',
        r'Service.?Connection.?Number[:\s]*(\d{10,15})',
        r'Connection.?No[:\s](\d{10,15})'
    ],
    'invoice_number': [
        r'Invoice No[:\s]*(L\d+)',
        r'Bill No[:\s]*([A-Z0-9]+)'
    ],
    'invoice_date': [
        r'Invoice No[^/]/\s*Date[:\s](\d{2}/\d{2}/\d{4})',
        r'Bill Date[:\s]*(\d{2}/\d{2}/\d{4})',
        r'Date[:\s]*(\d{2}/\d{2}/\d{4})'
    ],
    'due_date': [
        r'Due Date[:\s]*(\d{2}/\d{2}/\d{4})',
        r'Last Date[:\s]*(\d{2}/\d{2}/\d{4})'
    ],
    'meter_number': [
        r'Meter No[:\s]*([A-Z0-9]+)',
        r'Meter Number[:\s]*([A-Z0-9]+)'
    ],
    'sanctioned_load': [
        r'Sanctioned Load[:\s](\d+\.?\d)\s*KW',
        r'Connected Load[:\s](\d+\.?\d)\s*KW'
    ],
    'total_amount': [
        r'Bill Amount[:\s]*Rs\.?([\d,]+)[/-]',
        r'Total Amount[:\s]*Rs\.?([\d,]+)[/-]',
        r'Net Payable Amt[^:]Rs\.?\s([\d,]+)'
    ],
    'energy_charges': [
        r'Energy Charges[:\s](\d+\.?\d)',
        r'Power Charges[:\s](\d+\.?\d)'
    ],
    'fixed_charges': [
        r'Fixed Charges[:\s](\d+\.?\d)',
        r'Minimum Charges[:\s](\d+\.?\d)'
    ],
    'kwh_consumption': [
        r'Consumption\s*[:\s]([0-9]+\.?[0-9])',
        r'READING\s+\d+\.\d+\s+\d+\.\d+\s+\d+\s+([0-9]+\.?[0-9]*)'
    ],
    'power_factor': [
        r'Power Factor\s*Recorded\s*:?\s*(\d+(?:\.\d+)?)',
        r'(?i)power\s+factor\s+recorded\s*:?\s*(\d+(?:\.\d+)?)',
        r'Power Factor\s*Recorded\s*(\d+(?:\.\d+)?)',
        r'Power\s+Factor[:\s]*(\d+(?:\.\d+)?)',
        r'READING\s+(\d+\.\d+)\s+(\d+\.\d+)\s+(\d+)\s+(\d+\.\d+)\s+(\d+\.\d+)\s+(\d+\.\d+)\s+(\d+\.\d+)'
    ],
    'max_demand': [
        r'Max Dmd\s*Recorded\s*(\d+(?:\.\d+)?)',
        r'Maximum Demand[:\s]*(\d+(?:\.\d+)?)',
        r'Max\s*Demand[:\s]*(\d+(?:\.\d+)?)',
        r'READING\s+(\d+\.\d+)\s+(\d+\.\d+)\s+(\d+)\s+(\d+\.\d+)\s+(\d+\.\d+)\s+(\d+\.\d+)'
    ],
}

def extract_text_from_pdf(pdf_path: str) -> str:
    text = ""
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        if len(text.strip()) < 100:
            print("PDF text extraction insufficient, using OCR...")
            text = extract_text_with_ocr(pdf_path)
    except Exception as e:
        print(f"PyPDF2 extraction failed: {e}")
        text = extract_text_with_ocr(pdf_path)
    return text

def extract_text_with_ocr(pdf_path: str) -> str:
    try:
        images = pdf2image.convert_from_path(pdf_path)
        text = ""
        for image in images:
            page_text = pytesseract.image_to_string(image)
            text += page_text + "\n"
        return text
    except Exception as e:
        print(f"OCR extraction failed: {e}")
        return ""

def extract_field(text: str, field_name: str) -> Optional[str]:
    for pattern in PATTERNS.get(field_name, []):
        match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
        if match:
            return match.group(1).strip()
    return None

def extract_power_factor(text: str) -> Optional[str]:
    for pattern in PATTERNS.get('power_factor', [])[:-1]:
        match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
        if match:
            return match.group(1).strip()
    reading_pattern = PATTERNS['power_factor'][-1]
    match = re.search(reading_pattern, text, re.IGNORECASE | re.MULTILINE)
    if match:
        return match.group(7).strip()
    return None

def extract_max_demand(text: str) -> Optional[str]:
    for pattern in PATTERNS.get('max_demand', [])[:-1]:
        match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
        if match:
            return match.group(1).strip()
    reading_pattern = PATTERNS['max_demand'][-1]
    match = re.search(reading_pattern, text, re.IGNORECASE | re.MULTILINE)
    if match:
        return match.group(5).strip()
    return None

def extract_service_connection_number(text: str) -> Optional[str]:
    for pattern in PATTERNS.get('service_connection', []):
        matches = re.findall(pattern, text, re.IGNORECASE | re.DOTALL)
        if matches:
            number = re.sub(r'[\s-]+', '', matches[0])
            if re.match(r'^\d{10,15}$', number):
                return number
    return None

def clean_amount(amount_str: str) -> Optional[float]:
    if not amount_str:
        return None
    cleaned = re.sub(r'[₹Rs,/-]', '', amount_str).strip()
    try:
        return float(cleaned)
    except ValueError:
        return None

def extract(pdf_path: str) -> Dict[str, Any]:
    print(f"Processing: {pdf_path}")
    text = extract_text_from_pdf(pdf_path)
    if not text.strip():
        return {"error": "Could not extract text from PDF"}

    bill_details = {
        'consumer_name': extract_field(text, 'consumer_name'),
        'service_connection_number': extract_service_connection_number(text),
        'invoice_number': extract_field(text, 'invoice_number'),
        'invoice_date': extract_field(text, 'invoice_date'),
        'due_date': extract_field(text, 'due_date'),
        'meter_number': extract_field(text, 'meter_number'),
        'sanctioned_load_kw': extract_field(text, 'sanctioned_load'),
        'power_factor': clean_amount(extract_power_factor(text)),
        'max_demand': clean_amount(extract_max_demand(text)),
    }

    kwh_str = extract_field(text, 'kwh_consumption')
    bill_details['consumption_units'] = float(kwh_str) if kwh_str else None

    bill_details['total_amount'] = clean_amount(extract_field(text, 'total_amount'))
    bill_details['energy_charges'] = clean_amount(extract_field(text, 'energy_charges'))
    bill_details['fixed_charges'] = clean_amount(extract_field(text, 'fixed_charges'))
    bill_details['extracted_at'] = datetime.now().isoformat()

    return bill_details