import re
import json
import pdfplumber
from pathlib import Path
from typing import Dict, Optional

def extract_text_from_pdf(pdf_path: str) -> Optional[str]:
    """Extracts text from PDF file using pdfplumber"""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            text = ""
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
            return text
    except Exception as e:
        print(f"Error reading PDF: {e}")
        return None

def extract_with_patterns(text: str, patterns: list) -> str:
    """Helper method to extract data using multiple patterns"""
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        if match:
            return match.group(1).strip()
    return ""

def extract_numeric_value(text: str, patterns: list) -> str:
    """Helper function to safely extract and clean numeric values"""
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match and match.group(1):
            return match.group(1).replace(',', '')
    return ""

def extract_date_value(text: str, patterns: list) -> str:
    """Helper function to safely extract and standardize date values"""
    for pattern in patterns:
        match = re.search(pattern, text)
        if match and match.group(1):
            return match.group(1).replace('.', '-')
    return ""

def extract_due_dates_and_amounts(text: str, details: Dict):
    """Extract due dates with corresponding amounts for both formats"""
    # Format 1 patterns (First PDF format)
    due_date_patterns_format1 = [
        r'(\d{2}-\d{2}-\d{4})\s*rd ns; jkf\'k\s*(\d+\.?\d*)',
        r'(\d{2}-\d{2}-\d{4})\s*due amount[:\s](\d+\.?\d*)'
    ]
    
    # Format 2 patterns (Second PDF format)
    due_date_patterns_format2 = [
        r'(\d{2}\.\d{2}\.\d{4})\s*takx doya\s*kxula raiSa\s*(\d+\.?\d*)',
        r'(\d{2}-\d{2}-\d{4})\s*takx.?(\d+\.?\d*)'
    ]
    
    found_dates = []
    
    # Try Format 1 patterns first
    for pattern in due_date_patterns_format1:
        matches = re.findall(pattern, text)
        found_dates.extend(matches)
    
    # If no matches found, try Format 2 patterns
    if not found_dates:
        for pattern in due_date_patterns_format2:
            matches = re.findall(pattern, text)
            found_dates.extend(matches)
    
    # Sort by amount to identify early payment vs regular vs late payment
    if found_dates:
        found_dates.sort(key=lambda x: float(x[1]))
        
        if len(found_dates) >= 1:
            details["Early Payment Due Date"] = found_dates[0][0].replace('-', '/').replace('.', '/')
            details["Early Payment Amount"] = found_dates[0][1]
        
        if len(found_dates) >= 2:
            details["Due Date"] = found_dates[1][0].replace('-', '/').replace('.', '/')
            details["Total Amount Payable"] = found_dates[1][1]
        
        if len(found_dates) >= 3:
            details["Late Payment Amount"] = found_dates[2][1]
        elif len(found_dates) == 2:
            details["Total Amount Payable"] = found_dates[1][1]
        elif len(found_dates) == 1:
            details["Total Amount Payable"] = found_dates[0][1]

def extract_meter_details(text: str, details: Dict):
    """Extract meter number and readings for both formats"""
    # Format 1 meter patterns
    meter_patterns_format1 = [
        r'ehVj la\[;k\s*([A-Z0-9]+)',
        r'Meter Number[:\s]*([A-Z0-9]+)'
    ]
    
    # Format 2 meter patterns
    meter_patterns_format2 = [
        r'maITr saMKyaa\s*([A-Z0-9]+)',
        r'X(\d+)'
    ]
    
    # Try Format 1 first, then Format 2
    meter_number = extract_with_patterns(text, meter_patterns_format1)
    if not meter_number:
        meter_number = extract_with_patterns(text, meter_patterns_format2)
    details["Meter Number"] = meter_number
    
    # Extract meter readings - Format 1
    reading_patterns_format1 = [
        r'(\d{4,5})\s+(\d{2}-[A-Z]{3}-\d{2})\s+(\d{4,5})\s+(\d{1,3})\s+1\s+(\d{1,3})'
    ]
    
    # Extract meter readings - Format 2
    reading_patterns_format2 = [
        r'(\d{4,5})\s+(\d{2}\.\d{2}\.\d{2})\s+(\d{4,5})\s+(\d{1,4})\s+1\s+(\d{1,4})'
    ]
    
    # Try Format 1 first
    for pattern in reading_patterns_format1:
        match = re.search(pattern, text)
        if match:
            details["Current Reading"] = match.group(1)
            details["Previous Reading"] = match.group(3)
            return
    
    # Try Format 2 if Format 1 failed
    for pattern in reading_patterns_format2:
        match = re.search(pattern, text)
        if match:
            details["Current Reading"] = match.group(1)
            details["Previous Reading"] = match.group(3)
            return

def extract_address(text: str) -> str:
    """Extract consumer address from both formats"""
    lines = text.split('\n')
    address_parts = []
    
    found_pin = False
    for i, line in enumerate(lines):
        # Look for PIN code as address indicator
        if 'PIN' in line and not found_pin:
            found_pin = True
            # Take previous lines as potential address
            start_idx = max(0, i-3)
            for j in range(start_idx, i+1):
                line_clean = lines[j].strip()
                if (line_clean and 
                    not any(x in line_clean.upper() for x in ['BILL', 'DATE', 'NUMBER', 'COMPANY']) and
                    len(line_clean) > 5):
                    address_parts.append(line_clean)
            break
    
    return ', '.join(address_parts) if address_parts else ""

def extract(pdf_path: str) -> Dict:
    """
    Main extraction function that handles both PDF formats
    Returns extracted data as dictionary
    """
    text = extract_text_from_pdf(pdf_path)
    if not text:
        return {}
    
    # Initialize with the desired structure
    details = {
        "Consumer Number": "",
        "Consumer Name": "",
        "Bill Number": "",
        "Bill Date": "",
        "Bill Month": "",
        "Due Date": "",
        "Early Payment Due Date": "",
        "Total Amount Payable": "0",
        "Early Payment Amount": "0",
        "Late Payment Amount": "0",
        "Power Factor": "0",
        "KWH Consumption": "0",
        "Penalty": "0",
        "Sanction Load (KW)": "0",
        "Energy Charges": "0",
        "Fixed Charges": "0",
        "Electricity Duty": "0",
        "Subsidy": "0",
        "Meter Number": "",
        "Previous Reading": "0",
        "Current Reading": "0",
        "Address": "",
        "Account Number": "",
        "GSTIN": ""
    }
    
    # Extract Consumer Number - Format 1 first, then Format 2
    consumer_patterns_format1 = [
        r'miHkksäk la\[;k\s*(\d{12})',
        r'Consumer Number[:\s]*(\d{12})',
        r'miHkksäk la\[;k[:\s]*(\d+)'
    ]
    consumer_patterns_format2 = [
        r'Kaataa saMKyaa\s*(\d{9,12})',
        r'Account Number[:\s]*(\d{9,12})'
    ]
    
    consumer_number = extract_with_patterns(text, consumer_patterns_format1)
    if not consumer_number:
        consumer_number = extract_with_patterns(text, consumer_patterns_format2)
    details["Consumer Number"] = consumer_number
    
    # Extract Consumer Name - Both formats
    name_patterns = [
        r'([A-Z\s&]+(?:COMPANY|LIMITED|LTD|CORPORATION|CORP)[A-Z\s]*)',
        r'SMFG[A-Z\s]*',
        r'([A-Z]{2,}\s+[A-Z]{2,}(?:\s+[A-Z]{2,})*)',
        r'VIKAL KUMAR DUTTA',
        r'SRI\.([A-Z\s]+)'
    ]
    details["Consumer Name"] = extract_with_patterns(text, name_patterns)
    
    # Extract Bill Number - Format 1 first, then Format 2
    bill_num_patterns_format1 = [
        r'fcy la\[;k\s*(\d{17,20})',
        r'Bill Number[:\s]*(\d{17,20})',
        r'fcy la\[;k[:\s]*(\d+)'
    ]
    bill_num_patterns_format2 = [
        r'ibala saMKyaa\s*(\d{11,17})',
        r'(\d{17})',
        r'(\d{14,16})'
    ]
    
    bill_number = extract_with_patterns(text, bill_num_patterns_format1)
    if not bill_number:
        bill_number = extract_with_patterns(text, bill_num_patterns_format2)
    details["Bill Number"] = bill_number
    
    # Extract Bill Date - Format 1 first, then Format 2
    bill_date_patterns_format1 = [
        r'fcy frfFk\s*(\d{2}-\d{2}-\d{4})',
        r'Bill Date[:\s]*(\d{2}-\d{2}-\d{4})'
    ]
    bill_date_patterns_format2 = [
        r'ibala kxI idnaaMk\s*(\d{2}\.\d{2}\.\d{4})',
        r'idnaaMk\s*(\d{2}\.\d{2}\.\d{2,4})'
    ]
    
    bill_date = extract_date_value(text, bill_date_patterns_format1)
    if not bill_date:
        bill_date = extract_date_value(text, bill_date_patterns_format2)
    if bill_date:
        details["Bill Date"] = bill_date.replace('-', '/').replace('.', '/')
    
    # Extract Bill Month - Both formats
    month_patterns = [
        r'fcy ekg\s*([A-Z]+,?\s*\d{4})',
        r'Bill Month[:\s]*([A-Z]+,?\s*\d{4})',
        r'ibala maah\s*([A-Z]+-\d{4})'
    ]
    details["Bill Month"] = extract_with_patterns(text, month_patterns)
    
    # Extract Due Dates and Amounts
    extract_due_dates_and_amounts(text, details)
    
    # Extract Power Factor - Format 1 first, then Format 2
    pf_patterns_format1 = [
        r'ikoj QSDVj\s*(\d\.\d+)',
        r'Power Factor[:\s]*(\d\.\d+)'
    ]
    pf_patterns_format2 = [
        r'paavar fOxkTr\s*(\d+\.?\d*)',
        r'pf[:\s]*(\d+\.?\d*)'
    ]
    
    power_factor = extract_numeric_value(text, pf_patterns_format1)
    if not power_factor:
        power_factor = extract_numeric_value(text, pf_patterns_format2)
    details["Power Factor"] = power_factor
    
    # Extract KWH Consumption - Format 1 first, then Format 2
    kwh_patterns_format1 = [
        r'dqy \[kir\s*(\d+)',
        r'Total Consumption[:\s]*(\d+)'
    ]
    kwh_patterns_format2 = [
        r'GaaoiYata yaUinaT\\sa:\s*(\d+)',
        r'kuxla Kapata\s*(\d+)',
        r'Kapata\s*(\d+)'
    ]
    
    consumption = extract_numeric_value(text, kwh_patterns_format1)
    if not consumption:
        consumption = extract_numeric_value(text, kwh_patterns_format2)
    details["KWH Consumption"] = consumption or "0"
    
    # Extract Penalty - Format 1 first, then Format 2
    penalty_patterns_format1 = [
        r'foyEc vfèkHkkj.*?(\d+\.\d{2})',
        r'Late Payment Surcharge[:\s]*(\d+\.\d{2})',
        r'Penalty[:\s]*(\d+\.\d{2})'
    ]
    penalty_patterns_format2 = [
        r'ivalamba.?bakxayaa\s*(\d+\.?\d*)',
        r'Late Fee[:\s]*(\d+\.?\d*)',
        r'Surcharge[:\s]*(\d+\.?\d*)'
    ]
    
    penalty = extract_numeric_value(text, penalty_patterns_format1)
    if not penalty:
        penalty = extract_numeric_value(text, penalty_patterns_format2)
    details["Penalty"] = penalty
    
    # Extract Sanction Load - Format 1 first, then Format 2
    load_patterns_format1 = [
        r'Loh—r@lafonk Hkkj\s*([\d.]+)',
        r'Sanctioned Load[:\s]*([\d.]+)',
        r'Contract Demand[:\s]*([\d.]+)'
    ]
    load_patterns_format2 = [
        r'svaIkRta.?maaMga\s*([\d.]+)KW',
        r'Connected Load[:\s]*([\d.]+)'
    ]
    
    sanction_load = extract_numeric_value(text, load_patterns_format1)
    if not sanction_load:
        sanction_load = extract_numeric_value(text, load_patterns_format2)
    details["Sanction Load (KW)"] = sanction_load
    
    # Extract Energy Charges - Format 1 first, then Format 2
    energy_patterns_format1 = [
        r'ÅtkZ \'kqYd\s*(\d+\.\d{2})',
        r'Energy Charges[:\s]*(\d+\.\d{2})'
    ]
    energy_patterns_format2 = [
        r'{}jaa- Saulkx\s*([\d,]+\.?\d*)',
        r'Energy Charge[s]?[:\s]*([\d,]+\.?\d*)'
    ]
    
    energy_charges = extract_numeric_value(text, energy_patterns_format1)
    if not energy_charges:
        energy_charges = extract_numeric_value(text, energy_patterns_format2)
    details["Energy Charges"] = energy_charges
    
    # Extract Fixed Charges - Format 1 first, then Format 2
    fixed_patterns_format1 = [
        r'fQDLM@fMekaM pktZ\s*(\d+\.\d{2})',
        r'Fixed Charges[:\s]*(\d+\.\d{2})'
    ]
    fixed_patterns_format2 = [
        r'ifx@saD caaja-.?caaja-\s*([\d,]+\.?\d*)',
        r'Fixed Charge[s]?[:\s]*([\d,]+\.?\d*)',
        r'Demand Charge[s]?[:\s]*([\d,]+\.?\d*)'
    ]
    
    fixed_charges = extract_numeric_value(text, fixed_patterns_format1)
    if not fixed_charges:
        fixed_charges = extract_numeric_value(text, fixed_patterns_format2)
    details["Fixed Charges"] = fixed_charges
    
    # Extract Electricity Duty - Format 1 first, then Format 2
    duty_patterns_format1 = [
        r'fo\|qr dj\s*(\d+\.\d{2})',
        r'Electricity Duty[:\s]*(\d+\.\d{2})'
    ]
    duty_patterns_format2 = [
        r'ivaVuta Saulkx\s*([\d,]+\.?\d*)',
        r'Electricity Duty[:\s]*([\d,]+\.?\d*)'
    ]
    
    electricity_duty = extract_numeric_value(text, duty_patterns_format1)
    if not electricity_duty:
        electricity_duty = extract_numeric_value(text, duty_patterns_format2)
    details["Electricity Duty"] = electricity_duty
    
    # Extract Subsidy - Format 1 first, then Format 2
    subsidy_patterns_format1 = [
        r'jkT; ljdkj vuqnku\s*-(\d+\.\d{2})',
        r'Government Subsidy[:\s]*-?(\d+\.\d{2})'
    ]
    subsidy_patterns_format2 = [
        r'rajya sarkar.?-([\d,]+\.?\d*)',
        r'Government Subsidy[:\s]*-?([\d,]+\.?\d*)'
    ]
    
    subsidy = extract_numeric_value(text, subsidy_patterns_format1)
    if not subsidy:
        subsidy = extract_numeric_value(text, subsidy_patterns_format2)
    if subsidy:
        details["Subsidy"] = f"-{subsidy}" if not subsidy.startswith('-') else subsidy
    
    # Extract Meter Details
    extract_meter_details(text, details)
    
    # Extract Address
    details["Address"] = extract_address(text)
    
    # Extract Account Number - Format 1 first, then Format 2
    account_patterns_format1 = [
        r'\[kkrk la\[;k\s*(\d+)',
        r'Account Number[:\s]*(\d+)'
    ]
    account_patterns_format2 = [
        r'Kaataa saMKyaa\s*(\d+)'
    ]
    
    account_number = extract_with_patterns(text, account_patterns_format1)
    if not account_number:
        account_number = extract_with_patterns(text, account_patterns_format2)
    details["Account Number"] = account_number
    
    # Extract GSTIN - Both formats
    gstin_patterns = [
        r'th,lVhvkbZu\s*([A-Z0-9]+)',
        r'GSTIN[:\s]*([A-Z0-9]+)'
    ]
    details["GSTIN"] = extract_with_patterns(text, gstin_patterns)
    
    # Remove empty fields for cleaner output
    clean_details = {k: v for k, v in details.items() if v and v != "0"}
    
    # Save to JSON file
    output_filename = Path(pdf_path).stem + "_extracted_details.json"
    with open(output_filename, 'w', encoding='utf-8') as f:
        json.dump(clean_details, f, indent=4, ensure_ascii=False)
    
    print(f"Details extracted and saved to: {output_filename}")
    return clean_details

