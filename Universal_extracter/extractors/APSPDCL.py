import json
import re
from typing import Dict, Any
import PyPDF2
import pdfplumber
from datetime import datetime

def read_pdf_with_pypdf2(file_path: str) -> str:
    """Extract text from PDF using PyPDF2"""
    try:
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
        return text
    except Exception as e:
        print(f"Error reading PDF with PyPDF2: {e}")
        return ""

def read_pdf_with_pdfplumber(file_path: str) -> str:
    """Extract text from PDF using pdfplumber (more accurate)"""
    try:
        with pdfplumber.open(file_path) as pdf:
            text = ""
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        return text
    except Exception as e:
        print(f"Error reading PDF with pdfplumber: {e}")
        return ""

def extract_bill_data(bill_text: str) -> Dict[str, Any]:
    """
    Extract electricity bill data and format it into the required JSON structure.
    """
    
    # Debug: Print the bill text to see what we're working with
    print("DEBUG: Bill text content:")
    print("-" * 50)
    print(bill_text)
    print("-" * 50)
    
    # Initialize the output structure with default values
    extracted_data = {
        "Bill Number": "",
        "Bill_date": "",
        "Due_date": "",
        "Total Amount Payable": "",
        "Consumer Number": "",
        "Sanction Load (KW)": "",
        "KWH Consumption": "",
        "Penalty": ".00",
        "Charges": "",
        "Rewards": 0,
        "Taxes and Fees": 0,
        "Unit Rate": 0,
        "Power Factor": ""
    }
    
    # Extract Bill Number - prioritize DTR Code
    bill_number_patterns = [
        r'DTR Code\s*:?\s*(\d+)',  # DTR Code pattern (primary)
        r'Bill\s*(?:No|Number)\s*:?\s*([A-Z0-9\/\-]+)',
        r'BILL\s*NO\s*:?\s*([A-Z0-9\/\-]+)',
        r'Bill\s*#\s*([A-Z0-9\/\-]+)',
    ]
    
    for pattern in bill_number_patterns:
        bill_match = re.search(pattern, bill_text, re.IGNORECASE)
        if bill_match:
            extracted_data["Bill Number"] = bill_match.group(1)
            break
    
    # Extract Consumer Number - the long number in the bill
    consumer_patterns = [
        r'(\d{13,15})',  # Long number pattern (13-15 digits)
        r'Consumer\s*(?:No|Number)\s*:?\s*(\d{10,15})',
        r'Account\s*(?:No|Number)\s*:?\s*(\d{10,15})',
    ]
    
    # Find all potential consumer numbers and pick the longest one
    potential_consumer_numbers = []
    for pattern in consumer_patterns:
        matches = re.findall(pattern, bill_text, re.IGNORECASE)
        potential_consumer_numbers.extend(matches)
    
    # Filter and pick the longest number (likely the consumer number)
    if potential_consumer_numbers:
        longest_number = max(potential_consumer_numbers, key=len)
        if len(longest_number) >= 10:  
            extracted_data["Consumer Number"] = longest_number
    
    date_patterns = [
        r'Bill Date\s*:?\s*([A-Za-z]+ \d+,? \d+)',
        r'Bill Date\s*:?\s*(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{4})',
        r'Date\s*:?\s*(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{4})',
    ]
    
    for pattern in date_patterns:
        bill_date_match = re.search(pattern, bill_text, re.IGNORECASE)
        if bill_date_match:
            date_str = bill_date_match.group(1)
            extracted_data["Bill_date"] = format_date(date_str)
            break
    
    due_patterns = [
        r'Due Date\s*:?\s*([A-Za-z]+ \d+,? \d+)',
        r'Due Date\s*:?\s*(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{4})',
        r'Pay.*by\s*:?\s*(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{4})',
    ]
    
    for pattern in due_patterns:
        due_date_match = re.search(pattern, bill_text, re.IGNORECASE)
        if due_date_match:
            date_str = due_date_match.group(1)
            extracted_data["Due_date"] = format_date(date_str)
            break
    
    amount_patterns = [
        r'TOTAL AMOUNT\s*:?\s*(\d+)',  
        r'Total.*Payable\s*:?\s*(?:Rs\.?\s*)?(\d+(?:\.\d+)?)',
        r'Amount.*Due\s*:?\s*(?:Rs\.?\s*)?(\d+(?:\.\d+)?)',
        r'Net Amount\s*:?\s*(?:Rs\.?\s*)?(\d+(?:\.\d+)?)',
        r'BILL AMOUNT\s*:?\s*(\d+)',  
    ]
    
    for pattern in amount_patterns:
        total_match = re.search(pattern, bill_text, re.IGNORECASE)
        if total_match:
            extracted_data["Total Amount Payable"] = total_match.group(1)
            break
    
    load_patterns = [
        r'Load\s*:?\s*(\d+(?:\.\d+)?)',  
        r'(?:Sanction|Contract).*Load\s*:?\s*(\d+(?:\.\d+)?)',
        r'Connected Load\s*:?\s*(\d+(?:\.\d+)?)',
    ]
    
    for pattern in load_patterns:
        load_match = re.search(pattern, bill_text, re.IGNORECASE)
        if load_match:
            load_value = load_match.group(1)
            extracted_data["Sanction Load (KW)"] = f"{load_value}.00" if '.' not in load_value else load_value
            break
    
    units_patterns = [
        r'Units\s*:?\s*(\d+)',
        r'(?:KWH|kWh)\s*Consumed\s*:?\s*(\d+)',
        r'Consumption\s*:?\s*(\d+)',
        r'Energy Consumed\s*:?\s*(\d+)',
    ]
    
    for pattern in units_patterns:
        units_match = re.search(pattern, bill_text, re.IGNORECASE)
        if units_match:
            extracted_data["KWH Consumption"] = units_match.group(1)
            break
    
    pf_patterns = [
        r'Power Factor\s*:?\s*(\d+\.\d+)',
        r'PF\s*:?\s*(\d+\.\d+)',
    ]
    
    for pattern in pf_patterns:
        pf_match = re.search(pattern, bill_text, re.IGNORECASE)
        if pf_match:
            extracted_data["Power Factor"] = pf_match.group(1)
            break
    
    charges_patterns = [
        r'Energy charges\s+(\d+\.?\d*)',  
        r'Electricity charges\s*:?\s*(\d+(?:\.\d+)?)',
        r'Current charges\s*:?\s*(\d+(?:\.\d+)?)',
    ]
    
    for pattern in charges_patterns:
        charges_match = re.search(pattern, bill_text, re.IGNORECASE)
        if charges_match:
            extracted_data["Charges"] = charges_match.group(1)
            break
    
    tax_patterns = [
        r'Electric duty\s+(\d+)',  
        r'Tax\s*:?\s*(\d+(?:\.\d+)?)',
        r'Duty\s*:?\s*(\d+(?:\.\d+)?)',
    ]
    
    total_taxes = 0
    for pattern in tax_patterns:
        tax_matches = re.findall(pattern, bill_text, re.IGNORECASE)
        for match in tax_matches:
            try:
                total_taxes += float(match)
            except ValueError:
                continue
    
    if total_taxes > 0:
        extracted_data["Taxes and Fees"] = total_taxes
    
    penalty_patterns = [
        r'Penalty\s*:?\s*(\d+(?:\.\d+)?)',
        r'Late.*charge\s*:?\s*(\d+(?:\.\d+)?)',
        r'Surcharge\s*:?\s*(\d+(?:\.\d+)?)',
        r'Interest on ED\s+(\d+\.?\d*)', 
    ]
    
    total_penalty = 0
    for pattern in penalty_patterns:
        penalty_matches = re.findall(pattern, bill_text, re.IGNORECASE)
        for match in penalty_matches:
            try:
                total_penalty += float(match)
            except ValueError:
                continue
    
    if total_penalty > 0:
        extracted_data["Penalty"] = str(total_penalty)
    
    # Calculate Unit Rate if possible
    if extracted_data["Charges"] and extracted_data["KWH Consumption"]:
        try:
            charges = float(extracted_data["Charges"])
            units = float(extracted_data["KWH Consumption"])
            if units > 0:
                extracted_data["Unit Rate"] = round(charges / units, 2)
        except ValueError:
            pass
    
    return extracted_data

def format_date(date_str: str) -> str:
    """Convert various date formats to DD/MM/YYYY"""
    try:
        # Try different date formats
        formats = [
            "%B %d, %Y",    # June 1, 2025
            "%B %d %Y",     # June 1 2025
            "%d/%m/%Y",     # 01/06/2025
            "%d-%m-%Y",     # 01-06-2025
            "%m/%d/%Y",     # 06/01/2025
            "%Y-%m-%d",     # 2025-06-01
        ]
        
        for fmt in formats:
            try:
                date_obj = datetime.strptime(date_str, fmt)
                return date_obj.strftime("%d/%m/%Y")
            except ValueError:
                continue
        
        return date_str
    except:
        return date_str

def extract(file_path):
    """Main function to process PDF and extract bill data"""
    print(f"Processing PDF: {file_path}")
    
    bill_text = read_pdf_with_pdfplumber(file_path)
    
    if not bill_text.strip():
        print("Trying PyPDF2...")
        bill_text = read_pdf_with_pypdf2(file_path)
    
    if not bill_text.strip():
        raise Exception("Could not extract text from PDF")
    
    print("PDF text extracted successfully!")
    print("First 500 characters of extracted text:")
    print(bill_text[:500])
    print("\n" + "="*50 + "\n")
    
    extracted_data = extract_bill_data(bill_text)
    
    return extracted_data

