import re
import PyPDF2

def debug_pdf_text(pdf_path, save_to_file=False):
    """Debug function to see extracted text from PDF"""
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()
        
        if save_to_file:
            debug_filename = f"debug_{pdf_path.replace('.pdf', '.txt')}"
            with open(debug_filename, 'w', encoding='utf-8') as f:
                f.write(text)
            print(f"Debug text saved to: {debug_filename}")
        else:
            print("="*60)
            print("EXTRACTED TEXT FROM PDF:")
            print("="*60)
            print(text[:1000] + "..." if len(text) > 1000 else text)
            print("="*60)
        
        return text
    except Exception as e:
        print(f"Error in debug: {e}")
        return None

def extract(pdf_path, debug=False):
    """Extract specific bill details from Adani electricity bill PDF"""
    
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()
        
        if debug:
            print(f"\nDEBUG - First 500 characters of extracted text:")
            print("-" * 50)
            print(text[:500])
            print("-" * 50)
            
    except Exception as e:
        print(f"Error reading PDF: {e}")
        return None
    
    bill_data = {}

    # Extract Consumer Number
    consumer_match = re.search(r'CA NO:(\d+)', text)
    bill_data['consumer_number'] = consumer_match.group(1) if consumer_match else "Not Found"

    # Extract Bill Date
    bill_date_patterns = [
        r'BILL DATE\s+(\d{2}-\d{2}-\d{4})',
        r'(\d{2}-\d{2}-\d{4})\s*Boriwali',
        r'(\d{2}-\d{2}-\d{4})\s*Powai',
        r'TYPE OF SUPPLY\s+(\d{2}-\d{2}-\d{4})',
        r'COMMERCIAL.*?(\d{2}-\d{2}-\d{4})'
    ]
    bill_data['bill_date'] = "Not Found"
    for pattern in bill_date_patterns:
        match = re.search(pattern, text)
        if match:
            bill_data['bill_date'] = match.group(1)
            break

    # Extract Due Date
    due_date_patterns = [
        r'Due Date:\s*(\d{2}-\d{2}-\d{4})',
        r'Due Date\s+(\d{2}-\d{2}-\d{4})',
        r'due date.*?(\d{2}-\d{2}-\d{4})'
    ]
    bill_data['due_date'] = "Not Found"
    for pattern in due_date_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            bill_data['due_date'] = match.group(1)
            break

    # Extract kWh (Units Consumed)
    kwh_patterns = [
        r'Units Consumed\s+(\d+)',
        r'Units Consumed.*?(\d+)',
        r'(\d+)\s*Previous Units'
    ]
    bill_data['kwh'] = "Not Found"
    for pattern in kwh_patterns:
        match = re.search(pattern, text)
        if match:
            bill_data['kwh'] = match.group(1)
            break

    # Extract Sanction Load
    load_patterns_kw = [
        r'CONNECTED LOAD\(kW\)\s+(\d+)',
        r'CONNECTED LOAD.*?(\d+)',
        r'Active\s+(\d+)'
    ]
    load_patterns_kva = [
        r'Contract Demand.?(\d+\.?\d)kVA',
        r'(\d+\.?\d+)kVA.*?Contract',
        r'Billing Demand.*?(\d+\.?\d+)kVA'
    ]
    bill_data['sanction_load'] = "Not Found"
    for pattern in load_patterns_kw:
        match = re.search(pattern, text)
        if match:
            bill_data['sanction_load'] = f"{match.group(1)} kW"
            break
    if bill_data['sanction_load'] == "Not Found":
        for pattern in load_patterns_kva:
            match = re.search(pattern, text)
            if match:
                bill_data['sanction_load'] = f"{match.group(1)} kVA"
                break

    # Extract Power Factor
    pf_patterns = [
        r'Average Power Factor\s+(\d+\.?\d*)%\s*(lag|lead)?',
        r'Power Factor.?(\d+\.?\d)%\s*(lag|lead)?',
        r'(\d+\.?\d*)%\s*(lag|lead)'
    ]
    bill_data['power_factor'] = "Not Found"
    power_factor_decimal = None

    for pattern in pf_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            pf_value = match.group(1)
            pf_type = f" {match.group(2)}" if len(match.groups()) > 1 and match.group(2) else ""
            bill_data['power_factor'] = f"{pf_value}%{pf_type}"
            
            try:
                pf_decimal = float(pf_value) / 100  # Convert percentage to decimal
                power_factor_decimal = round(pf_decimal, 3)  # rounded to 3 decimals
            except ValueError:
                power_factor_decimal = None
            break



    # Extract Bill Number
    bill_num_patterns = [
        r'\b(\d{11,14})\b',
        r'Bill Number.*?(\d{11,14})',
        r'Regular.*?(\d{11,14})'
    ]
    bill_data['bill_number'] = "Not Found"
    for pattern in bill_num_patterns:
        match = re.search(pattern, text)
        if match:
            bill_data['bill_number'] = match.group(1)
            break

    # Extract Amounts
    amounts = {}

    current_match = re.search(r'Current Month Bill\s+r(\d+\.\d+)', text)
    if current_match:
        amounts['current_month_bill'] = f"₹{current_match.group(1)}"

    rounded_match = re.search(r'\br\s?(\d{5,6}\.\d{2})\b', text)
    if rounded_match:
        amounts['rounded_payable'] = f"₹{rounded_match.group(1)}"

    prev_match = re.search(r'Previous Outstanding\s+r(\d+\.\d+)', text)
    if prev_match:
        amounts['previous_outstanding'] = f"₹{prev_match.group(1)}"

    discount_match = re.search(r'Round sum payable by discount date.*?Amt r(\d+\.\d+)', text)
    if discount_match:
        amounts['discount_amount'] = f"₹{discount_match.group(1)}"

    after_due_match = re.search(r'Round sum payable after due date.*?Amt r(\d+\.\d+)', text)
    if after_due_match:
        amounts['after_due_date_amount'] = f"₹{after_due_match.group(1)}"

    current_charges_match = re.search(r'Total current month charges.*?(\d+\.\d+)', text)
    if current_charges_match:
        amounts['current_month_charges'] = f"₹{current_charges_match.group(1)}"

    # ✅ Extract Total Bill Amount
    total_match = re.search(r'₹\s?(\d{1,3}(?:,\d{3})*|\d+)(\.\d{2})?', text)
    if total_match:
        amounts['total_bill_amount'] = f"₹{total_match.group(1)}{total_match.group(2) if total_match.group(2) else ''}"

    bill_data['amounts'] = amounts

    return bill_data



