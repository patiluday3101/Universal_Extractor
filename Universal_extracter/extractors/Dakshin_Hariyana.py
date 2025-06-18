import pdfplumber
import os
import re
import traceback
import logging
import json  # <-- Add this import

def extract(pdf_path):
    """Extract specific data from DHBVN bill PDF in the requested format"""
    bill_details = {
        "File Name": os.path.basename(pdf_path),
        "Consumer Number": "Not Found",
        "Bill Number": "Not Found",
        "Due Date": "Not Found",
        "Bill Date": "Not Found",
        "Total Amount Payable": "Not Found",
        "KWH_Consumtion": "Not Found",
        "PF Surcharge": 0,
        "Penalty": 0,
        "Unit Rate": 0,
        "Taxes and Fees": 0,
        "Rewards": 0
    }
    

    with pdfplumber.open(pdf_path) as pdf:
        text = "\n".join([page.extract_text() for page in pdf.pages if page.extract_text()])
    
    # Extract account/consumer number
    account_match = re.search(r"Account No:\s*(\d+)", text)
    if account_match:
        bill_details["Consumer Number"] = account_match.group(1).strip()
    
    # Extract bill number
    bill_no_match = re.search(r"Bill No:\s*([A-Za-z0-9\/\-]+)", text)
    if bill_no_match:
        bill_details["Bill Number"] = bill_no_match.group(1).strip()
    
    # Extract due date
    due_date_match = re.search(r"Due Date:\s*(\d{2}\/\d{2}\/\d{4})", text)
    if due_date_match:
        bill_details["Due Date"] = due_date_match.group(1).strip()
    
    # Extract bill date (issue date)
    bill_date_match = re.search(r"Issue Date:\s*(\d{2}\/\d{2}\/\d{4})", text)
    if bill_date_match:
        bill_details["Bill Date"] = bill_date_match.group(1).strip()
    
    # Extract total amount payable - Fixed regex pattern
    if "Net Payable Amount on or before Due Date (`):" in text:
        bill_details["Total Amount Payable"] = text.split("Net Payable Amount on or before Due Date (`):")[1].split("\n")[0].strip()

    
    # Extract sanctioned load
    load_match = re.search(r"Sanctioned Load\s*\(Kw\/CD\)\s*([\d\.]+)", text)
    if not load_match:  # Try alternative pattern
        load_match = re.search(r"Sanctioned Load\s*([\d\.]+)", text)
    if load_match:
        bill_details["Sanction Load(kW)"] = load_match.group(1).strip()
    
    # Extract total units consumed - New improved regex
    units_match = re.search(r"Billed\s*Units\s*([\d\.]+)", text)
    if units_match:
        bill_details["KWH_Consumtion"] = units_match.group(1).strip()
    else:
        # Try to extract from meter reading section
        meter_section = re.search(r"Consumed\s*Units\s*([\d\.]+)", text)
        if meter_section:
            bill_details["KWH_Consumtion"] = meter_section.group(1).strip()
        else:
            # Try one more pattern specific to this bill format
            meter_section = re.search(r"kWh\s+[\d\.]+\s+[\d\.]+\s+\d+\s+([\d\.]+)", text)
            if meter_section:
                bill_details["KWH_Consumtion"] = meter_section.group(1).strip()
    
    # Extract unit rate - Improved pattern
    # First look in the Slab Calculation section
    unit_rate_match = re.search(r"Unit Rate\s*([\d\.]+)", text)
    if not unit_rate_match:
        # Try to find it near the total units
        slab_section = re.search(r"(\d+\.\d+)\s+([\d\.]+)\s+[\d\.]+", text)
        if slab_section:
            bill_details["Unit Rate"] = 0
    else:
        bill_details["Unit Rate"] = 0
    # Extract PF Surcharge - could be capacitor surcharge or power factor surcharge
    pf_match = re.search(r"Capacitor Surcharge\s*([\d\.]+)", text)
    if pf_match:
        try:
            bill_details["PF Surcharge"] = float(pf_match.group(1).strip())
        except ValueError:
            bill_details["PF Surcharge"] = 0
    
    # Extract penalty (surcharge)
    penalty_match = re.search(r"Surcharge\(`\):\s*([\d\.]+)", text)
    if penalty_match:
        try:
            bill_details["Penalty"] = float(penalty_match.group(1).strip())
        except ValueError:
            bill_details["Penalty"] = 0
    
    # Calculate taxes and fees (ED + Municipal Tax)
    taxes = 0
    
    bill_details["Taxes and Fees"] = taxes
    
    # Extract rewards or rebates
    rewards = 0
    bill_details["Rewards"] = rewards
    
    return bill_details
        

