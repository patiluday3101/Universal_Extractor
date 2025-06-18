import PyPDF2
import re
from datetime import datetime
import json


bill_data = {}
    
def extract_text_from_pdf(pdf_path):
    """Extract text content from PDF file"""
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()
            return text
    except Exception as e:
        print(f"Error reading PDF: {e}")
        return None

def extract(pdf_path):
    text=extract_text_from_pdf(pdf_path)
    bill_data = {
        'kwh_consumed': None,
        'sanctioned_load': None,
        'power_factor': 0,
        'bill_date': None,
        'due_date': None,
        'bill_number': None,
        'penalty': None,
        'payable_amount': None,
        'consumer_number': None,
        'consumer_name': None,
        'current_reading': None,
        'previous_reading': None,
        'current_bill': None,
        'previous_outstanding': None,
        'energy_charges': None,
        'fixed_charges': None,
        'taxes': None,
    }
    
    # Extract Units Consumed (kWh)
    kwh_patterns = [
        r'Units\s+Consumed\s+(\d+)',
        r'Units Consumed\s*:?\s*(\d+)',
        r'kWh Consumed\s*:?\s*(\d+)'
    ]
    for pattern in kwh_patterns:
        kwh_match = re.search(pattern, text, re.IGNORECASE)
        if kwh_match:
            bill_data['kwh_consumed'] = int(kwh_match.group(1))
            break
    
    # Extract Sanctioned Load
    load_patterns = [
        r'Sanctioned Load:\s*(\d+\.?\d*)\s*KW',
        r'Sanctioned Load\s*:\s*(\d+\.?\d*)',
        r'Load\s*:\s*(\d+\.?\d*)\s*KW'
    ]
    for pattern in load_patterns:
        load_match = re.search(pattern, text, re.IGNORECASE)
        if load_match:
            bill_data['sanctioned_load'] = float(load_match.group(1))
            break
    
    # Extract Bill Date
    bill_date_patterns = [
        r'Bill Date:\s*(\d{2}-[A-Za-z]{3}-\d{4})',
        r'Bill Date\s*:\s*(\d{2}-[A-Za-z]{3,4}-\d{4})',
        r'Bill Date\s*:\s*(\d{2}/\d{2}/\d{4})'
    ]
    for pattern in bill_date_patterns:
        bill_date_match = re.search(pattern, text, re.IGNORECASE)
        if bill_date_match:
            bill_data['bill_date'] = bill_date_match.group(1)
            break
    
    # Extract Due Date
    due_date_patterns = [
        r'Due Date:\s*(\d{2}-[A-Za-z]{3,4}-\d{4})',
        r'Due Date\s*:\s*(\d{2}/\d{2}/\d{4})',
        r'Payment Due Date\s*:\s*(\d{2}-[A-Za-z]{3,4}-\d{4})'
    ]
    for pattern in due_date_patterns:
        due_date_match = re.search(pattern, text, re.IGNORECASE)
        if due_date_match:
            bill_data['due_date'] = due_date_match.group(1)
            break
    
    # Extract Bill Number
    bill_no_patterns = [
        r'Bill No-(\d+)',
        r'Bill No\.\s*(\d+)',
        r'Bill Number\s*:\s*(\d+)',
        r'Bill No\s*:\s*(\d+)'
    ]
    for pattern in bill_no_patterns:
        bill_no_match = re.search(pattern, text, re.IGNORECASE)
        if bill_no_match:
            bill_data['bill_number'] = bill_no_match.group(1)
            break
    
    # Extract Payable Amount - Multiple comprehensive patterns
    payable_patterns = [
        r'Payable Amount\s*:?\s*(\d+(?:,\d+)*(?:\.\d+)?)',
        r'Amount Payable\s*:?\s*(?:₹|Rs\.?)?\s*(\d+(?:,\d+)*(?:\.\d+)?)',
        r'Total Amount\s*:?\s*(?:₹|Rs\.?)?\s*(\d+(?:,\d+)*(?:\.\d+)?)',
        r'Net Payable\s*:?\s*(?:₹|Rs\.?)?\s*(\d+(?:,\d+)*(?:\.\d+)?)',
        r'Amount Due\s*:?\s*(?:₹|Rs\.?)?\s*(\d+(?:,\d+)*(?:\.\d+)?)',
        # Pattern specifically for the format in your bill
        r'Payable Amount\s*:\s*(\d+)',
        # Pattern to catch amount after "Payable Amount" in next few lines
        r'Payable Amount\s*:?(?:\s*\n)?\s*(\d+)',
        # Look for standalone amount after payable amount text
        r'Payable Amount[:\s](?:\n|\r\n)?\s(\d+)'
    ]

    bill_data['payable_amount'] = None
    for pattern in payable_patterns:
        payable_match = re.search(pattern, text, re.IGNORECASE)
        if payable_match:
            amount_str = payable_match.group(1).replace(',', '')
            try:
                bill_data['payable_amount'] = float(amount_str)
                break
            except ValueError:
                continue

    # If still not found, try alternative approach using context
    if bill_data['payable_amount'] is None:
        payable_context = re.search(r'Payable Amount.*?(\d+)', text, re.IGNORECASE | re.DOTALL)
        if payable_context:
            try:
                bill_data['payable_amount'] = float(payable_context.group(1))
            except ValueError:
                pass

    # If payable amount not found, try to extract from current bill section
    if bill_data['payable_amount'] is None:
        current_bill_pattern = r'Current Bill\s*\([A-Z+\-]+\)\s*(\d+(?:\.\d+)?)'
        current_bill_match = re.search(current_bill_pattern, text)
        if current_bill_match:
            bill_data['current_bill'] = float(current_bill_match.group(1))
            
            # Look for previous outstanding
            outstanding_pattern = r'Previous Outstanding\s*\([A-Z]\)\s*(-?\d+(?:\.\d+)?)'
            outstanding_match = re.search(outstanding_pattern, text)
            if outstanding_match:
                bill_data['previous_outstanding'] = float(outstanding_match.group(1))
                # Calculate payable amount
                bill_data['payable_amount'] = bill_data['current_bill'] + bill_data['previous_outstanding']

    # Extract Consumer Number
    consumer_no_patterns = [
        r'Account-\s*(\d+)',
        r'Account\s*:\s*(\d+)',
        r'Consumer No\s*:\s*(\d+)',
        r'A/C No\s*:\s*(\d+)'
    ]
    for pattern in consumer_no_patterns:
        consumer_no_match = re.search(pattern, text, re.IGNORECASE)
        if consumer_no_match:
            bill_data['consumer_number'] = consumer_no_match.group(1)
            break
    
    # Extract Consumer Name
    consumer_name_patterns = [
        r'Consumer Name\s*:\s*([A-Za-z\s]+)',
        r'Name\s*:\s*([A-Za-z\s]+)',
        r'Consumer\s*:\s*([A-Za-z\s]+)'
    ]
    for pattern in consumer_name_patterns:
        consumer_name_match = re.search(pattern, text, re.IGNORECASE)
        if consumer_name_match:
            bill_data['consumer_name'] = consumer_name_match.group(1)
            break
    
    # Extract Current Reading
    current_reading_patterns = [
        r'Current Reading\s*:\s*(\d+)',
        r'Present Reading\s*:\s*(\d+)',
        r'Current Meter Reading\s*:\s*(\d+)'
    ]
    for pattern in current_reading_patterns:
        current_reading_match = re.search(pattern, text, re.IGNORECASE)
        if current_reading_match:
            bill_data['current_reading'] = int(current_reading_match.group(1))
            break
    
    # Extract Previous Reading
    previous_reading_patterns = [
        r'Previous Reading\s*:\s*(\d+)',
        r'Past Reading\s*:\s*(\d+)',
        r'Previous Meter Reading\s*:\s*(\d+)'
    ]
    for pattern in previous_reading_patterns:
        previous_reading_match = re.search(pattern, text, re.IGNORECASE)
        if previous_reading_match:
            bill_data['previous_reading'] = int(previous_reading_match.group(1))
            break
    
    # Extract Energy Charges
    energy_charges_patterns = [
        r'Energy Charges\s*:?\s*(\d+(?:,\d+)*(?:\.\d+)?)',
        r'Charge for Energy\s*:?\s*(\d+(?:,\d+)*(?:\.\d+)?)',
        r'Cost of Energy\s*:?\s*(\d+(?:,\d+)*(?:\.\d+)?)'
    ]
    for pattern in energy_charges_patterns:
        energy_charges_match = re.search(pattern, text, re.IGNORECASE)
        if energy_charges_match:
            bill_data['energy_charges'] = float(energy_charges_match.group(1).replace(',', ''))
            break
    
    # Extract Fixed Charges
    fixed_charges_patterns = [
        r'Fixed Charges\s*:?\s*(\d+(?:,\d+)*(?:\.\d+)?)',
        r'Charge for Fixed Cost\s*:?\s*(\d+(?:,\d+)*(?:\.\d+)?)',
        r'Fixed Cost\s*:?\s*(\d+(?:,\d+)*(?:\.\d+)?)'
    ]
    for pattern in fixed_charges_patterns:
        fixed_charges_match = re.search(pattern, text, re.IGNORECASE)
        if fixed_charges_match:
            bill_data['fixed_charges'] = float(fixed_charges_match.group(1).replace(',', ''))
            break
    
    # Extract Taxes
    taxes_patterns = [
        r'Taxes\s*:?\s*(\d+(?:,\d+)*(?:\.\d+)?)',
        r'GST\s*:?\s*(\d+(?:,\d+)*(?:\.\d+)?)',
        r'Government Taxes\s*:?\s*(\d+(?:,\d+)*(?:\.\d+)?)'
    ]
    for pattern in taxes_patterns:
        taxes_match = re.search(pattern, text, re.IGNORECASE)
        if taxes_match:
            bill_data['taxes'] = float(taxes_match.group(1).replace(',', ''))
            break
    
    # Extract Penalty
    penalty_patterns = [
        r'Penalty\s*:?\s*(\d+(?:,\d+)*(?:\.\d+)?)',
        r'Late Fee\s*:?\s*(\d+(?:,\d+)*(?:\.\d+)?)',
        r'Fine\s*:?\s*(\d+(?:,\d+)*(?:\.\d+)?)'
    ]
    for pattern in penalty_patterns:
        penalty_match = re.search(pattern, text, re.IGNORECASE)
        if penalty_match:
            bill_data['penalty'] = float(penalty_match.group(1).replace(',', ''))
            break

    # Calculate Power Factor if not directly available
    if bill_data['power_factor'] == 0 and bill_data['sanctioned_load'] is not None and bill_data['kwh_consumed'] is not None:
        try:
            # Assuming kWh Consumed is for the billing period in hours
            hours_in_billing_period = 30 * 24  # 30 days a month
            apparent_power = bill_data['kwh_consumed'] / hours_in_billing_period  # in kVA
            bill_data['power_factor'] = round(bill_data['sanctioned_load'] / apparent_power, 2)
        except ZeroDivisionError:
            bill_data['power_factor'] = 0

    return bill_data
