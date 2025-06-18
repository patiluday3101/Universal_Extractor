import sys
import os
import fitz
import pytesseract
from pdf2image import convert_from_path
import re
import json

def extract_text_from_pdf(pdf_path):
    text = ""
    try:
        doc = fitz.open(pdf_path)
        for page in doc:
            text += page.get_text("text") + "\n"
        if not text.strip():
            images = convert_from_path(pdf_path)
            text = " ".join([pytesseract.image_to_string(img) for img in images])
    except Exception as e:
        print(f"Error extracting text from {pdf_path}: {e}")
    return text

def clean_data(raw_data):
    if raw_data is None:
        return None
    return re.sub(r"\s*-\s*", "/", raw_data.strip())

def extract(pdf_path):
    text = extract_text_from_pdf(pdf_path)
    
    if not text:
        return None
    
    # Initialize result with default structure
    bill_details = {
        "Consumer Number": None,
        "Bill Date": None,
        "Due Date": None,
        "Bill Number": None,
        "Power Factor": "0.0000",
        "Total Amount Payable": None,
        "Sanction Load (KW)": None,
        "KWH Consumption": None,
        "Rewards": 0,
        "Taxes and Fees": 0,
        "Penalty": 0,
        "Unit Rate": 0
    }
    
    try:
        # Extract Consumer Number
        consumer_no = re.search(r"Contract Account Number.*?(\d{11})", text)
        if consumer_no:
            bill_details["Consumer Number"] = consumer_no.group(1)
        
        # Extract Bill Date
        bill_date = re.search(r"Bill Date\s*:\s*(\d{2}/\d{2}/\d{4})", text)
        if bill_date:
            bill_details["Bill Date"] = bill_date.group(1)
        
        # Extract Due Date
        due_date = re.search(r"Due Date\s*:\s*(\d{2}/\d{2}/\d{4})", text)
        if due_date:
            bill_details["Due Date"] = due_date.group(1)
        
        # Extract Bill Number
        bill_number = re.search(r"Bill Number\s*:\s*(\d+)", text)
        if bill_number:
            bill_details["Bill Number"] = bill_number.group(1)
        
        # Extract Total Amount Payable
        amount_payable = re.search(r"Bill Amount Payable Rs\.(\d+\.?\d*)", text)
        if amount_payable:
            bill_details["Total Amount Payable"] = amount_payable.group(1)
        
        # Extract Sanctioned Load
        sanction_load = re.search(r"Sanctioned Load\s*:\s*(\d+\.?\d*)KW", text)
        if sanction_load:
            bill_details["Sanction Load (KW)"] = sanction_load.group(1)
        
        # Extract KWH Consumption (Reading Difference from meter reading section)
        consumption_patterns = [
            r"Reading\s*Difference\s*.*?(\d+)",
            r"(\d+)\s+1\.00\s+(\d+)\s+OK",  # Pattern: difference, factor, consumption, status
            r"Consumption\s+Reading\s*Remark.*?(\d+)\s+OK"
        ]
        
        for pattern in consumption_patterns:
            consumption = re.search(pattern, text)
            if consumption:
                # Get the last group which should be the consumption value
                consumption_value = consumption.group(consumption.lastindex)
                bill_details["KWH Consumption"] = consumption_value + ".0000"
                break
        
        # If still not found, try to extract from the detailed consumption table
        if not bill_details["KWH Consumption"]:
            # Look for the consumption value in the meter reading table
            consumption_match = re.search(r"(\d{4})\s+(\d{2}\.\d{2}\.\d{4})\s+(\d+)\s+(\d{2}\.\d{2}\.\d{4})\s+(\d+)\s+(\d+)\s+1\.00\s+(\d+)", text)
            if consumption_match:
                bill_details["KWH Consumption"] = consumption_match.group(7) + ".0000"
        
        # Extract Taxes and Fees (Electricity Duty + Public Lighting Duty)
        taxes_fees = 0
        
        # Electricity Duty
        electricity_duty = re.search(r"Electricity Duty @ Rs 0\.70/KWh\s+(\d+\.?\d*)", text)
        if electricity_duty:
            taxes_fees += float(electricity_duty.group(1))
        
        # Public Lighting Duty
        public_lighting_duty = re.search(r"Public Lighting Duty@ Rs\.0\.08/KWH\s+(\d+\.?\d*)", text)
        if public_lighting_duty:
            taxes_fees += float(public_lighting_duty.group(1))
        
        bill_details["Taxes and Fees"] = round(taxes_fees, 2) if taxes_fees > 0 else 0
        
        # Extract Penalty (Delay Payment Charges)
        delay_charges = re.search(r"Delay Payment Charges\s*Till Bill Date\s*\(C\)\s+(\d+\.?\d*)", text)
        if delay_charges:
            bill_details["Penalty"] = float(delay_charges.group(1))
        
        # Calculate Unit Rate
        energy_charges = re.search(r"Energy charges\s*(\d+\.?\d*)", text)
        if energy_charges and bill_details["KWH Consumption"]:
            consumption_val = float(bill_details["KWH Consumption"].replace(".0000", ""))
            if consumption_val > 0:
                unit_rate = float(energy_charges.group(1)) / consumption_val
                bill_details["Unit Rate"] = round(unit_rate, 4)
        
        # Clean data
        for key, value in bill_details.items():
            if isinstance(value, str):
                bill_details[key] = clean_data(value)
        
        return bill_details
        
    except Exception as e:
        print(f"Error extracting bill details: {e}")
        return None

