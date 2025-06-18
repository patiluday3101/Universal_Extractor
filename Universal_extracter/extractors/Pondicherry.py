import json
import re
import os
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
    Handles both Tamil/English bills and regular English bills.
    """
    
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
    
    # Extract Bill Number
    bill_number_patterns = [
        r'Bill\s*(?:No|Number)\s*:?\s*([A-Z0-9\/\-]+)',
        r'Bill\s*No\s*[:\-]?\s*([A-Z0-9\/\-]+)',
        r'Reference\s*(?:No|Number)\s*:?\s*([A-Z0-9\/\-]+)',
        r'Invoice\s*(?:No|Number)\s*:?\s*([A-Z0-9\/\-]+)',
        r'(\d+\/\d+)',  # Pattern like 1/17511
        r'Bill\s*ID\s*:?\s*([A-Z0-9\/\-]+)',
        r'Document\s*(?:No|Number)\s*:?\s*([A-Z0-9\/\-]+)',
        r'ல்\s*எண்\s*([A-Z0-9\/\-]+)',  # Tamil pattern
    ]
    
    for pattern in bill_number_patterns:
        bill_match = re.search(pattern, bill_text, re.IGNORECASE)
        if bill_match and bill_match.group(1) not in ['-', '']:
            extracted_data["Bill Number"] = bill_match.group(1)
            break
    
    # Extract Consumer Number - IMPROVED PATTERNS
    consumer_patterns = [
        r'Consumer\s*(?:No|Number|code)\s*:?\s*([A-Z0-9\-]+)',
        r'Account\s*(?:No|Number)\s*:?\s*([A-Z0-9\-]+)',
        r'கர்ேவார்\s*எண்\s*(\d{2}-\d{2}-\d{2}-\d{4}[A-Z]{2})',  # Fixed Tamil pattern
        r'Consumer\s*code\s*(\d{2}-\d{2}-\d{2}-\d{4}[A-Z]{2})',  # Direct pattern
        r'(\d{2}-\d{2}-\d{2}-\d{4}[A-Z]{2})',  # Pattern matching your format: 07-40-05-0454LG
        r'(\d{11,15})',  # Long number pattern
    ]
    
    for pattern in consumer_patterns:
        consumer_match = re.search(pattern, bill_text, re.IGNORECASE)
        if consumer_match and consumer_match.group(1) not in ['-', '']:
            extracted_data["Consumer Number"] = consumer_match.group(1)
            break
    
    # Extract Bill Date - IMPROVED PATTERNS
    bill_date_patterns = [
        r'Bill date\s*:?\s*(\d{1,2}[-/]\d{1,2}[-/]\d{4})',
        r'Bill Date\s*:?\s*([A-Za-z]+ \d+,? \d+)',
        r'பட்யல்\s*ேத\s*(\d{2}-\d{2}-\d{4})',  # Fixed Tamil pattern
        r'Bill\s*date\s*(\d{2}-\d{2}-\d{4})',  # Direct pattern
        r'Date\s*:?\s*(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{4})',
        r'(\d{2}-\d{2}-\d{4})',  # General DD-MM-YYYY pattern
    ]
    
    for pattern in bill_date_patterns:
        bill_date_match = re.search(pattern, bill_text, re.IGNORECASE)
        if bill_date_match:
            date_str = bill_date_match.group(1)
            extracted_data["Bill_date"] = format_date(date_str)
            break
    
    # Extract Due Date - IMPROVED PATTERNS FOR YOUR BILL
    due_date_patterns = [
        r'Due date:\s*(\d{2}-\d{2}-\d{4})',  # Exact pattern from your bill
        r'Due date\s*:?\s*(\d{1,2}[-/]\d{1,2}[-/]\d{4})',
        r'Due Date\s*:?\s*([A-Za-z]+ \d+,? \d+)',
        r'இ\s*ேத\s*(\d{2}-\d{2}-\d{4})',  # Fixed Tamil pattern
        r'Pay.*by\s*:?\s*(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{4})',
        r'due\s*date.*?(\d{2}-\d{2}-\d{4})',  # More flexible pattern
    ]
    
    for pattern in due_date_patterns:
        due_date_match = re.search(pattern, bill_text, re.IGNORECASE)
        if due_date_match:
            date_str = due_date_match.group(1)
            extracted_data["Due_date"] = format_date(date_str)
            break
    
    # Extract Total Amount Payable - IMPROVED PATTERNS
    amount_patterns = [
        r'Net payable.*?₹\)\s*(\d+\.?\d*)',
        r'Net payable.*?due date.*?₹.*?(\d+\.00)',  # Specific pattern for your bill
        r'TOTAL AMOUNT\s*:?\s*(\d+(?:\.\d+)?)',
        r'Total.*Payable\s*:?\s*(?:Rs\.?\s*)?(\d+(?:\.\d+)?)',
        r'Net Bill Amount\s*(\d+\.?\d*)',
        r'நிকর.*?ெதাைக.*?(\d+\.?\d*)',
        r'(\d{4,5}\.00)',  # Pattern for amounts like 9625.00
    ]
    
    for pattern in amount_patterns:
        total_match = re.search(pattern, bill_text, re.IGNORECASE | re.DOTALL)
        if total_match:
            extracted_data["Total Amount Payable"] = total_match.group(1)
            break
    
    # Extract Sanctioned Load - COMPLETELY REVISED FOR YOUR BILL
    load_patterns = [
        r'Sanctioned load\s*(\d+)',  # Direct pattern from your bill: 12480
        r'ஒப்পందிক்கப்பட்ட\s*भार\s*(\d+)',  # Tamil pattern
        r'(?:Sanction|Contract).*Load\s*:?\s*(\d+(?:\.\d+)?)',
        r'Load\s*:?\s*(\d+(?:\.\d+)?)\s*(?:KW|kW)',
        r'Connected Load\s*:?\s*(\d+(?:\.\d+)?)',
        r'Sanctioned.*?(\d{4,5})',  # Pattern for large numbers like 12480
    ]
    
    for pattern in load_patterns:
        load_match = re.search(pattern, bill_text, re.IGNORECASE)
        if load_match:
            load_value = float(load_match.group(1))
            # If value is large (like 12480), it's in watts, convert to KW
            if load_value > 100:
                load_value = load_value / 1000
            extracted_data["Sanction Load (KW)"] = f"{load_value:.2f}"
            break
    
    # Extract KWH Consumption - IMPROVED PATTERNS
    units_patterns = [
        r'Total Units Consumed\s*(\d+)',  # Direct pattern from your bill
        r'Units\s*:?\s*(\d+)',
        r'(?:KWH|kWh)\s*Consumed\s*:?\s*(\d+)',
        r'Consumption\s*:?\s*(\d+)',
        r'ெமாத্ত.*?উপেযাগিত্ত.*?அল.*?(\d+)',
        r'Units.*?(\d{3})',  # Pattern for 3-digit consumption
    ]
    
    for pattern in units_patterns:
        units_match = re.search(pattern, bill_text, re.IGNORECASE)
        if units_match:
            extracted_data["KWH Consumption"] = units_match.group(1)
            break
    
    # Extract Power Factor
    pf_patterns = [
        r'Power Factor\s*:?\s*(\d+\.\d+)',
        r'PF\s*:?\s*(\d+\.\d+)',
    ]
    
    for pattern in pf_patterns:
        pf_match = re.search(pattern, bill_text, re.IGNORECASE)
        if pf_match:
            extracted_data["Power Factor"] = pf_match.group(1)
            break
    
    # Extract Energy/Electricity Charges - IMPROVED FOR YOUR BILL
    charges_patterns = [
        r'Energy Charges\s*(\d+\.00)',  # Direct pattern: Energy Charges 6275.00
        r'Energy charges\s*:?\s*₹?\s*(\d+(?:\.\d+)?)',
        r'Electricity charges\s*:?\s*₹?\s*(\d+(?:\.\d+)?)',
        r'Current charges\s*:?\s*₹?\s*(\d+(?:\.\d+)?)',
        r'Fixed.*Charge\s*:?\s*₹?\s*(\d+(?:\.\d+)?)',
        r'Variable.*Charge\s*:?\s*₹?\s*(\d+(?:\.\d+)?)',
        r'Consumption.*Charge\s*:?\s*₹?\s*(\d+(?:\.\d+)?)',
        r'Unit.*Charge\s*:?\s*₹?\s*(\d+(?:\.\d+)?)',
        r'ন্\s*কট্টাণम্.*?(\d+\.?\d*)',
    ]
    
    for pattern in charges_patterns:
        charges_match = re.search(pattern, bill_text, re.IGNORECASE)
        if charges_match:
            extracted_data["Charges"] = charges_match.group(1)
            break
    
    # Extract Taxes and Fees - IMPROVED FOR YOUR BILL
    tax_patterns = [
        r'Regulatory Surcharge\s*(\d+\.00)',  # Pattern: Regulatory Surcharge 877.00
        r'Electric duty\s+(\d+(?:\.\d+)?)',
        r'Tax\s*:?\s*(\d+(?:\.\d+)?)',
        r'Duty\s*:?\s*(\d+(?:\.\d+)?)',
        r'তল্.*?வரি.*?(\d+\.?\d*)',
    ]
    
    for pattern in tax_patterns:
        tax_match = re.search(pattern, bill_text, re.IGNORECASE)
        if tax_match:
            extracted_data["Taxes and Fees"] = float(tax_match.group(1))
            break
    
    # Extract Penalty - IMPROVED
    penalty_patterns = [
        r'BPSC\s*(\d+\.00)',  # Pattern: BPSC 0.00
        r'Penalty\s*:?\s*(\d+(?:\.\d+)?)',
        r'Late.*charge\s*:?\s*(\d+(?:\.\d+)?)',
        r'Surcharge\s*:?\s*(\d+(?:\.\d+)?)',
        r'কালতামত.*?কট্টাণম্.*?(\d+\.?\d*)',
    ]
    
    for pattern in penalty_patterns:
        penalty_match = re.search(pattern, bill_text, re.IGNORECASE)
        if penalty_match and float(penalty_match.group(1)) > 0:
            extracted_data["Penalty"] = penalty_match.group(1)
            break
    
    # Extract Rewards (Rebate) - IMPROVED
    rebate_patterns = [
        r'Rebate \(-\)\s*(\d+\.00)',  # Pattern: Rebate (-) 23.00
        r'Discount\s*(\d+\.?\d*)',
        r'তল্ল্প.*?(\d+\.?\d*)',
    ]
    
    for pattern in rebate_patterns:
        rebate_match = re.search(pattern, bill_text, re.IGNORECASE)
        if rebate_match and float(rebate_match.group(1)) > 0:
            extracted_data["Rewards"] = float(rebate_match.group(1))
            break
    
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
        # Handle DD-MM-YYYY or DD/MM/YYYY formats
        if re.match(r'\d{1,2}[-/]\d{1,2}[-/]\d{4}', date_str):
            return date_str.replace('-', '/')
        
        # Handle month name formats like "June 1, 2025"
        formats = [
            "%B %d, %Y",    # June 1, 2025
            "%B %d %Y",     # June 1 2025
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

def debug_pdf_extraction(pdf_path: str) -> None:
    """
    Debug function to see the raw text extracted from PDF.
    Useful for understanding why certain patterns might not match.
    """
    try:
        print(f"=== DEBUG: Extracting text from {pdf_path} ===")
        
        # Try pdfplumber first
        text_plumber = read_pdf_with_pdfplumber(pdf_path)
        print(f"\n--- PDFPLUMBER OUTPUT ({len(text_plumber)} chars) ---")
        print(text_plumber[:2000] + ("..." if len(text_plumber) > 2000 else ""))
        
        # Try PyPDF2
        text_pypdf2 = read_pdf_with_pypdf2(pdf_path)
        print(f"\n--- PYPDF2 OUTPUT ({len(text_pypdf2)} chars) ---")
        print(text_pypdf2[:2000] + ("..." if len(text_pypdf2) > 2000 else ""))
        
        # Use the better extraction
        final_text = text_plumber if text_plumber.strip() else text_pypdf2
        
        # Look for key patterns
        print(f"\n--- PATTERN ANALYSIS ---")
        
        # Look for sanctioned load specifically
        load_patterns = re.findall(r'Sanctioned load\s*(\d+)', final_text, re.IGNORECASE)
        print(f"Sanctioned Load Matches: {load_patterns}")
        
        # Look for potential due dates
        due_patterns = re.findall(r'Due date:\s*(\d{2}-\d{2}-\d{4})', final_text, re.IGNORECASE)
        print(f"Due Date Matches: {due_patterns}")
        
        # Look for consumer codes
        consumer_patterns = re.findall(r'(\d{2}-\d{2}-\d{2}-\d{4}[A-Z]{2})', final_text)
        print(f"Consumer Code Matches: {consumer_patterns}")
        
        # Look for dates
        date_patterns = re.findall(r'\d{1,2}[-/]\d{1,2}[-/]\d{4}', final_text)
        print(f"All Date Patterns: {date_patterns}")
        
        # Look for amounts
        amount_patterns = re.findall(r'₹\s*(\d+(?:\.\d+)?)|Rs\.?\s*(\d+(?:\.\d+)?)', final_text, re.IGNORECASE)
        print(f"Found Amounts: {amount_patterns}")
        
    except Exception as e:
        print(f"Debug error: {e}")

def process_bill_pdf(pdf_path: str, output_path: str = None, debug: bool = False) -> str:
    """
    Process electricity bill PDF and extract data to JSON.
    
    Args:
        pdf_path (str): Path to the input PDF file
        output_path (str, optional): Path for output JSON file. If None, uses PDF name with .json extension
        debug (bool): If True, shows debug information about text extraction
    
    Returns:
        str: Path to the generated JSON file
    """
    try:
        # Validate input file
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file '{pdf_path}' not found")
        
        if not pdf_path.lower().endswith('.pdf'):
            raise ValueError("Input file must be a PDF")
        
        # Set output path if not provided
        if output_path is None:
            output_path = pdf_path.rsplit('.', 1)[0] + '.json'
        
        print(f"Processing: {pdf_path}")
        
        # Debug mode
        if debug:
            debug_pdf_extraction(pdf_path)
            print("\n" + "="*50)
        
        print("Extracting text from PDF...")
        
        # Try pdfplumber first (usually more accurate)
        bill_text = read_pdf_with_pdfplumber(pdf_path)
        
        # If pdfplumber fails, try PyPDF2
        if not bill_text.strip():
            print("Pdfplumber failed, trying PyPDF2...")
            bill_text = read_pdf_with_pypdf2(pdf_path)
        
        if not bill_text.strip():
            raise Exception("Could not extract text from PDF")
        
        print("Extracting bill data...")
        # Extract structured data
        extracted_data = extract_bill_data(bill_text)
        
        # Write JSON output to file
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(extracted_data, f, indent=2, ensure_ascii=False)
        
        print(f"✓ Success! Data extracted to: {output_path}")
        
        # Print summary
        print("\n--- Extraction Summary ---")
        for key, value in extracted_data.items():
            if value and value != "" and value != 0 and value != ".00":
                print(f"{key}: {value}")
        
        return output_path
        
    except FileNotFoundError as e:
        error_msg = {"error": str(e)}
        print(f"Error: {e}")
        return None
    except Exception as e:
        error_msg = {"error": f"Error processing PDF: {str(e)}"}
        print(f"Error: {e}")
        return None

# Example usage functions
def extract(pdf_path) -> str:
    """
    Simple function to extract bill data from PDF and return as JSON string.
    This maintains compatibility with the original function signature.
    """
    
    # Try pdfplumber first (usually more accurate)
    bill_text = read_pdf_with_pdfplumber(pdf_path)
    
    # If pdfplumber fails, try PyPDF2
    if not bill_text.strip():
        bill_text = read_pdf_with_pypdf2()
    
    if not bill_text.strip():
        raise Exception("Could not extract text from PDF")
    
    # Extract structured data
    extracted_data = extract_bill_data(bill_text)
    
    # Convert to JSON string
    return json.dumps(extracted_data, indent=2, ensure_ascii=False)
    

