import os
import time
import json
import re
import fitz  
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import cv2
import pytesseract


# def extract(pdf_path):
#     doc = fitz.open(pdf_path)

#     bill_details = {
#         # "consumer number": consumer_no,
#         "Bill Number": "Not Found",
#         "Bill Date": "Not Found",
#         "Due Date": "Not Found",
#         "Total Amount Payable": "Not Found",
#         "Power Factor": "0",
#         "Unit Rate": "0",
#         "KWH Consumption": "Not Found",  # Added field
#         "Energy Charges": "Not Found",
#         "Sanctioned Load (KW)": "Not Found",  # Added sanctioned load in KW
#         "penalty": "0",
#         "Rewards": "0",
#         "Taxes and Fees": "0"
#     }

#     for page in doc:
#         text_instances = []
#         for block in page.get_text("dict")["blocks"]:
#             if "lines" in block:
#                 for line in block["lines"]:
#                     for span in line["spans"]:
#                         text_instances.append({
#                             "text": span["text"].strip(),
#                             "x": span["bbox"][0],
#                             "y": span["bbox"][1]
#                         })

#         # Extract text content from the PDF
#         bill_text = " ".join([item["text"] for item in text_instances])

#         # Patterns for Net Consumption and Energy Charges
#         net_consumption_pattern = r"Net Consumption\s+(\d+)"
#         energy_charges_pattern = r"Energy Charges\s*:\s*(\d+(?:\.\d+)?)\s*kWh"
#         sanctioned_load_kw_pattern = r"Sanctioned load \(KW\)\s+(\d+(?:\.\d+)?)"

#         # Extract Net Consumption
#         match = re.search(net_consumption_pattern, bill_text)
#         if match:
#             bill_details["KWH Consumption"] = match.group(1)

#         # Extract Energy Charges
#         match = re.search(energy_charges_pattern, bill_text)
#         if match:
#             bill_details["Energy Charges"] = match.group(1)

#         # Extract Sanctioned Load in KW
#         match = re.search(sanctioned_load_kw_pattern, bill_text)
#         if match:
#             bill_details["Sanctioned Load (KW)"] = match.group(1)

#         # Identify header positions
#         header_positions = {}
#         for item in text_instances:
#             if "Bill No" in item["text"]:
#                 header_positions["Bill Number"] = item
#             elif "Billing Period" in item["text"]:
#                 header_positions["Billing Period"] = item
#             elif "Due Date" in item["text"]:
#                 header_positions["Due Date"] = item
#             elif "Power Factor" in item["text"] or "PF" in item["text"]:
#                 header_positions["Power Factor"] = item
#             elif "Sanctioned load (KW)" in item["text"]:
#                 header_positions["Sanctioned Load KW"] = item

#         # Extract values below headers
#         for key, header in header_positions.items():
#             for item in text_instances:
#                 if item["y"] > header["y"] and abs(item["x"] - header["x"]) < 50:
#                     if key in ["Sanctioned Load KW"]:
#                         # For sanctioned load, look for numeric values
#                         numeric_match = re.search(r'(\d+(?:\.\d+)?)', item["text"])
#                         if numeric_match:
#                             bill_details[key] = numeric_match.group(1)
#                     else:
#                         bill_details[key] = item["text"]
#                     break

#         # Alternative method to extract sanctioned load - look for specific patterns in the bill
#         # This handles cases where the regex might not catch the exact format
#         for item in text_instances:
#             # Look for KW value near "Sanctioned load (KW)"
#             if "Sanctioned load (KW)" in bill_text and bill_details["Sanctioned Load KW"] == "Not Found":
#                 # Find the position of sanctioned load KW text
#                 for text_item in text_instances:
#                     if "Sanctioned load (KW)" in text_item["text"]:
#                         # Look for numeric values in nearby text items
#                         for nearby_item in text_instances:
#                             if (abs(nearby_item["y"] - text_item["y"]) < 20 and 
#                                 nearby_item["x"] > text_item["x"]):
#                                 kw_match = re.search(r'(\d+(?:\.\d+)?)', nearby_item["text"])
#                                 if kw_match:
#                                     bill_details["Sanctioned Load KW"] = kw_match.group(1)
#                                     break
#                         break

#             # Look for HP value near "Sanctioned load (HP)"
#             # if "Sanctioned load (HP)" in bill_text and bill_details["Sanctioned Load HP"] == "Not Found":
#             #     for text_item in text_instances:
#             #         if "Sanctioned load (HP)" in text_item["text"]:
#             #             # Look for numeric values in nearby text items
#             #             for nearby_item in text_instances:
#             #                 if (abs(nearby_item["y"] - text_item["y"]) < 20 and 
#             #                     nearby_item["x"] > text_item["x"]):
#             #                     hp_match = re.search(r'(\d+(?:\.\d+)?)', nearby_item["text"])
#             #                     if hp_match:
#             #                         bill_details["Sanctioned Load HP"] = hp_match.group(1)
#             #                         break
#             #             break

#         # Extract Bill Date (First date from Billing Period)
#         if "Billing Period" in bill_details and bill_details["Billing Period"] != "Not Found":
#             date_match = re.findall(r'\d{2}-\d{2}-\d{4}', bill_details["Billing Period"])
#             if len(date_match) > 1:
#                 # Convert Bill Date format from DD-MM-YYYY to DD/MM/YYYY
#                 bill_details["Bill Date"] = date_match[1].replace("-", "/")

#         # Format Due Date if found
#         if "Due Date" in bill_details and bill_details["Due Date"] != "Not Found":
#             due_date_match = re.search(r'\d{2}-\d{2}-\d{4}', bill_details["Due Date"])
#             if due_date_match:
#                 # Convert Due Date format from DD-MM-YYYY to DD/MM/YYYY
#                 bill_details["Due Date"] = due_date_match.group(0).replace("-", "/")

#         # Extract Net Payable Amount (if found)
#         for item in text_instances:
#             if "Net Payable Amount" in item["text"]:
#                 amount_index = text_instances.index(item) + 1  # Get next item
#                 if amount_index < len(text_instances):
#                     bill_details["Total Amount Payable"] = text_instances[amount_index]["text"].replace(",", "").strip()
#                     break

#         # Extract Power Factor (correctly)
#         if "Power Factor" in header_positions:
#             pf_y = header_positions["Power Factor"]["y"]  # Y-coordinate of Power Factor label
#             pf_candidates = []
            
#             for item in text_instances:
#                 if item["y"] >= pf_y and abs(item["x"] - header_positions["Power Factor"]["x"]) < 80:
#                     pf_match = re.findall(r'\b\d+\.\d+\b', item["text"])  # Find decimal values
#                     if pf_match:
#                         pf_candidates.extend(pf_match)

#             if pf_candidates:
#                 bill_details["Power Factor"] = pf_candidates[0]  # Pick first valid PF value
#             else:
#                 bill_details["Power Factor"] = "0"  # Default to 0 if not found

#         # Ensure Power Factor is a valid numeric value (avoid text like "Disconnection")
#         if not re.match(r'^\d+\.\d+$', bill_details["Power Factor"]):
#             bill_details["Power Factor"] = "0"

#     # Remove "Billing Period" from the output since it's not needed
#     bill_details.pop("Billing Period", None)

#     return bill_details


import os
import re
import fitz
import PyPDF2
import json
def extract_text_from_pdf( pdf_path):
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            for page in pdf_reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text
            return text
    except Exception as e:
        print(f"Error reading PDF {pdf_path}: {str(e)}")
        return ""


def extract_invoice_format(pdf_path):
    text=extract_text_from_pdf( pdf_path)
    bill_details = {
        'bill_date': '',
        'bill_number': '',
        'due_date': '',
        'consumer_number': '',
        'consumer_name': '',
        'amount': 0.0,
        'kwh_consumption': 0,
        'sanctioned_load': '',
        'taxes_and_fees': 0.0,
        'rewards': 0.0,
        'penalty': 0.0,
        'power_factor': 0.0
    }
    
    # Clean up text for better parsing
    clean_text = re.sub(r'\s+', ' ', text.strip())
    
    # REFINED Consumer Number (Account ID) extraction for BESCOM format
    account_patterns = [
        # Pattern for BESCOM: "Account ID RR Number Name [number] [code] [name]"
        r'Account ID\s+RR Number\s+Name\s+(\d+)',
        # Alternative patterns
        r'Account ID\s+(\d+)\s+\w+',
        r'Account\s+ID\s+(\d+)',
        r'(\d{10,})'  # Long number as fallback
    ]
    
    for pattern in account_patterns:
        match = re.search(pattern, clean_text)
        if match:
            bill_details['consumer_number'] = match.group(1)
            break
    
    # REFINED Consumer Name extraction for BESCOM format
    # The format is: "Account ID RR Number Name [number] [code] [actual_name]"
    name_patterns = [
        # For BESCOM format: After "Account ID [number] [code]" comes the name
        r'Account ID\s+RR Number\s+Name\s+\d+\s+\w+\s+([A-Z][A-Z\s]+)',
        # Alternative: Look for name after account number and code
        r'Account ID\s+\d+\s+\w+\s+([A-Z][A-Z\s]+?)(?:\s+Sanctioned|\s+\d|\s+Bill)',
        # Direct name pattern after "Name"
        r'Name\s+\d+\s+\w+\s+([A-Z][A-Z\s]+?)(?:\s+Sanctioned|\s+\d)',
        # More generic pattern
        r'Name\s+([A-Z][A-Z\s]{3,})(?:\s+Sanctioned|\s+Load|\s+Tariff)'
    ]
    
    for pattern in name_patterns:
        match = re.search(pattern, clean_text)
        if match:
            name = match.group(1).strip()
            # Clean up the name
            name = re.sub(r'\s+', ' ', name)
            # Ensure it's a reasonable name (not too short, contains letters)
            if len(name) >= 3 and re.match(r'^[A-Z\s]+$', name):
                bill_details['consumer_name'] = name
                break
    
    # REFINED Bill Number extraction
    bill_num_patterns = [
        r'Bill No\s+(\d+)',
        r'Bill No\s+Billing period\s+Bill Date\s+Due Date\s+(\d+)',
        r'(\d{12,})'  # Long number format
    ]
    
    for pattern in bill_num_patterns:
        match = re.search(pattern, clean_text)
        if match:
            bill_details['bill_number'] = match.group(1)
            break
    
    # REFINED Bill Date extraction
    # Look for the billing period line: "217774982833 13-Mar-2025 TO 13-Apr-2025 13th day of the month 27-Apr-2025"
    billing_period_match = re.search(r'(\d{12})\s+(\d{1,2}-\w{3}-\d{4})\s+TO\s+(\d{1,2}-\w{3}-\d{4})\s+.*?(\d{1,2}-\w{3}-\d{4})', clean_text)
    
    if billing_period_match:
        bill_details['bill_number'] = billing_period_match.group(1)
        bill_details['bill_date'] = billing_period_match.group(2)  # Start date of billing period
        bill_details['due_date'] = billing_period_match.group(4)   # Due date
    else:
        # Fallback patterns for bill date
        bill_date_patterns = [
            r'Bill Date\s+(\d{1,2}-\w{3}-\d{4})',
            r'(\d{1,2}-\w{3}-\d{4})\s+TO',
            r'Date:\s*(\d{1,2}-\w{3}-\d{4})'
        ]
        
        for pattern in bill_date_patterns:
            match = re.search(pattern, clean_text)
            if match:
                bill_details['bill_date'] = match.group(1)
                break
        
        # Fallback patterns for due date
        due_date_patterns = [
            r'Due Date\s+(\d{1,2}-\w{3}-\d{4})',
            r'(\d{1,2}-\w{3}-\d{4})(?:\s*$|\s+[A-Z])',  # Date at end of line or before text
        ]
        
        for pattern in due_date_patterns:
            match = re.search(pattern, clean_text)
            if match:
                due_date_candidate = match.group(1)
                # Make sure it's not the same as bill date
                if due_date_candidate != bill_details['bill_date']:
                    bill_details['due_date'] = due_date_candidate
                    break
    
    # Sanctioned Load extraction
    load_patterns = [
        r'(\d+(?:\.\d+)?)\s*kW',
        r'Sanctioned Load.*?(\d+(?:\.\d+)?)\s*kW'
    ]
    for pattern in load_patterns:
        match = re.search(pattern, clean_text)
        if match:
            bill_details['sanctioned_load'] = match.group(1) + ' kW'
            break
    
    # Electricity Consumption
    consumption_patterns = [
        r'Electricity Consumption \(in Units\)\s+(\d+)',
        r'Consumption.*?(\d+)',
        r'Present Reading\s+\d+\s+Electricity Consumption \(in Units\)\s+(\d+)'
    ]
    for pattern in consumption_patterns:
        match = re.search(pattern, clean_text)
        if match:
            bill_details['kwh_consumption'] = int(match.group(1))
            break
    
    # Current Bill Amount
    amount_patterns = [
        r'Current Bill amount \(INR\)\s+(\d+(?:\.\d+)?)',
        r'Current Bill amount.*?(\d+(?:\.\d+)?)'
    ]
    for pattern in amount_patterns:
        match = re.search(pattern, clean_text)
        if match:
            bill_details['amount'] = float(match.group(1))
            break
    
    # Power Factor extraction
    power_factor_patterns = [
        r'PF Recorded\s+(\d+(?:\.\d+)?)',
        r'Power Factor.*?(\d+(?:\.\d+)?)'
    ]
    for pattern in power_factor_patterns:
        match = re.search(pattern, clean_text)
        if match:
            bill_details['power_factor'] = float(match.group(1))
            break
    
    # Tax and Fuel Adjustment Charges
    taxes_fees = 0.0
    
    # Extract individual tax components
    tax_match = re.search(r'Tax \(INR\)\s+(\d+(?:\.\d+)?)', clean_text)
    fuel_adj_match = re.search(r'Fuel Adjustment Charges \(INR\)\s+(\d+(?:\.\d+)?)', clean_text)
    
    if tax_match:
        taxes_fees += float(tax_match.group(1))
    if fuel_adj_match:
        taxes_fees += float(fuel_adj_match.group(1))
        
    bill_details['taxes_and_fees'] = taxes_fees
    
    # Rebates/Rewards
    rebates_match = re.search(r'Rebates \(INR\)\s+(\d+(?:\.\d+)?)', clean_text)
    if rebates_match:
        bill_details['rewards'] = float(rebates_match.group(1))
    
    # Penalties (Power Factor penalty, MD penalty, Interest)
    total_penalty = 0.0
    penalty_patterns = [
        r'Power Factor penalty \(INR\)\s+(\d+(?:\.\d+)?)',
        r'Excess MD penalty \(INR\)\s+(\d+(?:\.\d+)?)',
        r'Interest \(INR\)\s+(\d+(?:\.\d+)?)'
    ]
    
    for pattern in penalty_patterns:
        match = re.search(pattern, clean_text)
        if match:
            total_penalty += float(match.group(1))
            
    bill_details['penalty'] = total_penalty
    return bill_details

    


def extract_simple_format(pdf_path):
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"The file {pdf_path} does not exist.")

    try:
        doc = fitz.open(pdf_path)
    except Exception as e:
        print(f"Error opening PDF file: {e}")
        raise

    bill_details = {
        "consumer number": extract_consumer_number(pdf_path),
        "Bill Number": "Not Found",
        "Bill Date": "Not Found",
        "Due Date": "Not Found",
        # "Total Amount Payable": "Not Found",
        "Power Factor": "0",
        "Unit Rate": "0",
        "KWH Consumption": "Not Found",  # Added field
        "Energy Charges": "Not Found",
        # "Sanctioned Load ": "Not Found",  # Added sanctioned load in KW
        "penalty": "0",
        "Rewards": "0",
        "Taxes and Fees": "0"
    }

    for page in doc:
        text_instances = []
        for block in page.get_text("dict")["blocks"]:
            if "lines" in block:
                for line in block["lines"]:
                    for span in line["spans"]:
                        text_instances.append({
                            "text": span["text"].strip(),
                            "x": span["bbox"][0],
                            "y": span["bbox"][1]
                        })

        header_positions = {}
        for item in text_instances:
            if "Bill No" in item["text"]:
                header_positions["Bill Number"] = item
            elif "Bill Date" in item["text"]:
                header_positions["Bill Date"] = item
            elif "Due Date" in item["text"]:
                header_positions["Due Date"] = item
            elif "Current Bill Amount" in item["text"]:
                header_positions["Amount"] = item
            elif "Power Factor" in item["text"] or "PF" in item["text"]:
                header_positions["Power Factor"] = item
            elif "Sanction Load" in item["text"]:
                header_positions["Sanction Load"] = item

        # Extract based on x/y position proximity
        for key, header in header_positions.items():
            for item in text_instances:
                if item["y"] > header["y"] and abs(item["x"] - header["x"]) < 50:
                    bill_details[key] = item["text"]
                    break

        for idx, item in enumerate(text_instances):
            text = item["text"]

            if "Sanctioned load (KW)" in text:
                if idx + 1 < len(text_instances):
                    bill_details["Sanction Load"] = text_instances[idx + 1]["text"]

            if "Current Bill Amount" in text:
                if idx + 1 < len(text_instances):
                    amount_text = text_instances[idx + 1]["text"]
                    try:
                        bill_details["Amount"] = str(round(float(amount_text.replace(',', ''))))
                    except:
                        bill_details["Amount"] = amount_text

            if "Present Reading" in text:
                # Look ahead for the next 5 items on the same line and grab the last numeric value as PF
                values_collected = []
                for offset in range(1, 6):
                    if idx + offset < len(text_instances):
                        next_text = text_instances[idx + offset]["text"]
                        if next_text.replace('.', '', 1).isdigit():
                            values_collected.append(next_text)
                if len(values_collected) >= 4:
                    bill_details["Power Factor"] = values_collected[-1]

            # Extract KWH consumption (line like "Consumption 319 0 0.14")
            if "Difference" in text:
                # Line: Difference 319 0 0.14
                if idx + 1 < len(text_instances):
                    kwh_candidate = text_instances[idx + 1]["text"]
                    if kwh_candidate.replace('.', '', 1).isdigit():
                        bill_details["KWH Consumption"] = kwh_candidate

            if "Net Payable Amount" in text:
                for offset in range(1, 3):
                    if idx + offset < len(text_instances):
                        amount = text_instances[idx + offset]["text"]
                        amount_cleaned = amount.replace(',', '').strip()
                        if amount_cleaned.replace('.', '', 1).isdigit():
                            bill_details["Net Payable Amount"] = str(round(float(amount_cleaned)))
                            break


    return bill_details

def extract_consumer_number(pdf_path):
    import fitz
    import re
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"The file {pdf_path} does not exist.")

    try:
        doc = fitz.open(pdf_path)
    except Exception as e:
        print(f"Error opening PDF file: {e}")
        raise

    consumer_number = "Not Found"

    for page in doc:
        text_instances = []
        for block in page.get_text("dict")["blocks"]:
            if "lines" in block:
                for line in block["lines"]:
                    for span in line["spans"]:
                        text_instances.append({
                            "text": span["text"].strip(),
                            "x": span["bbox"][0],
                            "y": span["bbox"][1]
                        })

        for idx, item in enumerate(text_instances):
            text = item["text"]

            # Extract Consumer Number from Account ID line
            if "Account ID" in text:
                if idx + 1 < len(text_instances):
                    candidate = text_instances[idx + 1]["text"]
                    if candidate.isdigit() and len(candidate) == 10:
                        consumer_number = candidate

            # Alternative: Extract from the *9093050000* pattern
            if text.startswith("*") and text.endswith("*") and len(text) == 12:
                candidate = text[1:-1]
                if candidate.isdigit() and len(candidate) == 10:
                    consumer_number = candidate

    # Additional regex-based extraction for Consumer Number if not found
    if consumer_number == "Not Found":
        full_text = ""
        for page in doc:
            full_text += page.get_text()
        consumer_patterns = [
            r"Account ID\s*(\d{10})",
            r"\*(\d{10})\*",
            r"(\d{10})",
        ]
        for pattern in consumer_patterns:
            match = re.search(pattern, full_text)
            if match:
                consumer_number = match.group(1)
                break

    return consumer_number
def extract(pdf_path):
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""

    if "BESCOM Mithra" in text or "BILL / INVOICE" in text:
        return extract_invoice_format(pdf_path)
    else:
        return extract_simple_format(pdf_path)




