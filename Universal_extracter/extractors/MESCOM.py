# import os
# import time
# import json
# import re
# import fitz  
# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC

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

#         # Extract Net Consumption
#         match = re.search(net_consumption_pattern, bill_text)
#         if match:
#             bill_details["KWH Consumption"] = match.group(1)

#         # Extract Energy Charges
#         match = re.search(energy_charges_pattern, bill_text)
#         if match:
#             bill_details["Energy Charges"] = match.group(1)

#         # Identify header positions
#         header_positions = {}
#         for item in text_instances:
#             if "Bill No" in item["text"]:
#                 header_positions["Bill Number"] = item
#             elif "Billing Period" in item["text"]:
#                 header_positions["Billing Period"] = item
#             elif "Due Date" in item["text"]:
#                 header_positions["Due Date"] = item
#             # elif "Current Bill Amount" in item["text"]:  
#             #     header_positions["Amount"] = item
#             elif "Power Factor" in item["text"] or "PF" in item["text"]:
#                 header_positions["Power Factor"] = item

#         # Extract values below headers
#         for key, header in header_positions.items():
#             for item in text_instances:
#                 if item["y"] > header["y"] and abs(item["x"] - header["x"]) < 50:
#                     bill_details[key] = item["text"]
#                     break

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
#                 bill_details["Power Factor"] = pf_candidates[0]  
                
#                 bill_details["Power Factor"] = "0" 

#         if not re.match(r'^\d+\.\d+$', bill_details["Power Factor"]):
#             bill_details["Power Factor"] = "0"

#         for idx, item in enumerate(text_instances):
#             text = item["text"]

#             if "Sanctioned load (KW)" in text:
#                 if idx + 1 < len(text_instances):
#                     bill_details["Sanction Load"] = text_instances[idx + 1]["text"]

#             if "Present Reading" in text:
#                 # Look ahead for the next 5 items on the same line and grab the last numeric value as PF
#                 values_collected = []
#                 for offset in range(1, 6):
#                     if idx + offset < len(text_instances):
#                         next_text = text_instances[idx + offset]["text"]
#                         if next_text.replace('.', '', 1).isdigit():
#                             values_collected.append(next_text)
#                 if len(values_collected) >= 4:
#                     bill_details["Power Factor"] = values_collected[-1]

#     bill_details.pop("Billing Period", None)

#     return bill_details


# import os  # this is working code for extracting bill details from MESCOM electricity bills in PDF format.
# import fitz
# import re
# import json

# def extract_consumer_number(pdf_path):
#     import fitz
#     import re
#     if not os.path.exists(pdf_path):
#         raise FileNotFoundError(f"The file {pdf_path} does not exist.")

#     try:
#         doc = fitz.open(pdf_path)
#     except Exception as e:
#         print(f"Error opening PDF file: {e}")
#         raise

#     consumer_number = "Not Found"

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

#         for idx, item in enumerate(text_instances):
#             text = item["text"]

#             # Extract Consumer Number from Account ID line
#             if "Account ID" in text:
#                 if idx + 1 < len(text_instances):
#                     candidate = text_instances[idx + 1]["text"]
#                     if candidate.isdigit() and len(candidate) == 10:
#                         consumer_number = candidate

#             # Alternative: Extract from the *9093050000* pattern
#             if text.startswith("*") and text.endswith("*") and len(text) == 12:
#                 candidate = text[1:-1]
#                 if candidate.isdigit() and len(candidate) == 10:
#                     consumer_number = candidate

#     # Additional regex-based extraction for Consumer Number if not found
#     if consumer_number == "Not Found":
#         full_text = ""
#         for page in doc:
#             full_text += page.get_text()
#         consumer_patterns = [
#             r"Account ID\s*(\d{10})",
#             r"\*(\d{10})\*",
#             r"(\d{10})",
#         ]
#         for pattern in consumer_patterns:
#             match = re.search(pattern, full_text)
#             if match:
#                 consumer_number = match.group(1)
#                 break

#     return consumer_number

# def extract(pdf_path):
#     """
#     Extract bill details from electricity bill PDF using regex patterns
#     """
#     if not os.path.exists(pdf_path):
#         raise FileNotFoundError(f"The file {pdf_path} does not exist.")

#     try:
#         doc = fitz.open(pdf_path)
#     except Exception as e:
#         print(f"Error opening PDF file: {e}")
#         raise

#     bill_details = {
#         "Consumer Number": extract_consumer_number(pdf_path),  # <-- Add this line
#         "Bill Number": "Not Found",
#         "Bill Date": "Not Found",
#         "Due Date": "Not Found",
#         "Amount": "Not Found",
#         "Power Factor": "0",
#         "Sanction Load": "Not Found",
#         "KWH Consumption": "Not Found",
#         "Net Payable Amount": "Not Found",
#         "Rewards": 0,
#         "Taxes and Fees": 0,
#     }

#     # Extract all text from PDF
#     full_text = ""
#     for page in doc:
#         full_text += page.get_text()

#     # Define regex patterns for extraction
#     patterns = {
#         "Bill Number": r"Bill No\.?\s*(\d+)",
#         "Bill Date": r"(\d{2}-\d{2}-\d{4})",  # More flexible date pattern
#         "Due Date": r"Due Date\s*(\d{2}-\d{2}-\d{4})",
#         "Current Bill Amount": r"Current Bill Amount\s*([\d,]+\.?\d*)",
#         "Net Payable Amount": r"Net Payable Amount\s*([\d,]+\.?\d*)",
#         "Sanctioned Load": r"Sanctioned load \(KW\)\s*([\d.]+)",
#         "KWH Consumption": r"Consumption\s+(\d+)\s+\d+\s+[-\d.]+",
#         "Power Factor": r"Present Reading\s+\d{2}-[A-Z]{3}-\d{4}\s+\d+\s+\d+\s+[\d.]+\s+(\d+(?:\.\d+)?)"
#     }

#     # Additional specific patterns for missing fields
#     specific_patterns = {
#         "Bill Number": [
#             r"Bill No\.?\s*(\d+)",
#             r"(\d{12})",  # 12-digit bill numbers like 909058316924
#             r"Account ID\s*(\d+)"
#         ],
#         "Bill Date": [
#             r"Bill Date\s*(\d{2}-\d{2}-\d{4})",
#             r"(\d{2}-\d{2}-\d{4})\s+(\d{2}-\d{2}-\d{4})\s+(\d{2}-\d{2}-\d{4})",  # Extract 2nd date from sequence
#             r"Billing Period.*?(\d{2}-\d{2}-\d{4})\s+(\d{2}-\d{2}-\d{4})"  # 2nd date in billing period line
#         ],
#         "Due Date": [
#             r"Due Date\s*(\d{2}-\d{2}-\d{4})",
#             r"(\d{2}-\d{2}-\d{4})\s+(\d{2}-\d{2}-\d{4})\s+(\d{2}-\d{2}-\d{4})"  # Extract 3rd date from sequence
#         ]
#     }

#     # Alternative patterns for more flexibility
#     alternative_patterns = {
#         "Bill Date": r"(\d{2}-\d{2}-\d{4})",  # Any date format
#         "Power Factor": r"Present Reading.?(\d+(?:\.\d+)?)\s$",  # Last number in Present Reading line
#         "Amount": r"Rs\.?\s*([\d,]+\.?\d*)",  # Any amount with Rs
#         "Consumption": r"Net Consumption\s+(\d+)\s+\d+"  # Alternative consumption pattern
#     }

#     # Extract using regex patterns
#     for key, pattern in patterns.items():
#         match = re.search(pattern, full_text, re.IGNORECASE | re.MULTILINE)
#         if match:
#             value = match.group(1).replace(',', '').strip()
            
#             # Map to bill_details keys
#             if key == "Current Bill Amount":
#                 try:
#                     bill_details["Amount"] = str(round(float(value)))
#                 except:
#                     bill_details["Amount"] = value
#             elif key == "Net Payable Amount":
#                 try:
#                     bill_details["Net Payable Amount"] = str(round(float(value)))
#                 except:
#                     bill_details["Net Payable Amount"] = value
#             elif key == "Sanctioned Load":
#                 bill_details["Sanction Load"] = value
#             elif key == "KWH Consumption":
#                 bill_details["KWH Consumption"] = value
#             elif key == "Power Factor":
#                 bill_details["Power Factor"] = value
#             else:
#                 bill_details[key] = value

#     # Try specific patterns for missing fields
#     for field, pattern_list in specific_patterns.items():
#         if bill_details[field] == "Not Found":
#             for pattern in pattern_list:
#                 matches = re.findall(pattern, full_text, re.IGNORECASE | re.MULTILINE)
#                 if matches:
#                     if field == "Bill Number":
#                         # Look for 12-digit numbers first (like 909058316924)
#                         for match in matches:
#                             if len(match) == 12:
#                                 bill_details[field] = match
#                                 break
#                         if bill_details[field] == "Not Found" and matches:
#                             bill_details[field] = matches[0]
#                     elif field == "Bill Date":
#                         # Bill Date is the 2nd date in the sequence (04-06-2025)
#                         if len(matches[0]) == 3:  # If tuple with 3 dates
#                             bill_details[field] = matches[0][1]  # 2nd date
#                         elif len(matches) >= 2:
#                             bill_details[field] = matches[1]  # 2nd match
#                         elif matches:
#                             bill_details[field] = matches[0]
#                     elif field == "Due Date":
#                         # Due Date is the 3rd date in the sequence (18-06-2025)
#                         if len(matches[0]) == 3:  # If tuple with 3 dates
#                             bill_details[field] = matches[0][2]  # 3rd date
#                         elif len(matches) >= 3:
#                             bill_details[field] = matches[2]  # 3rd match
#                         elif matches:
#                             bill_details[field] = matches[-1]  # Last match
#                     else:
#                         bill_details[field] = matches[0]
#                     break
    
#     # Specific extraction for the date sequence in your bill format
#     # Pattern: "04-05-2025 - 04-06-2025 18-06-2025 03-07-2025"
#     date_sequence_pattern = r"(\d{2}-\d{2}-\d{4})\s*-\s*(\d{2}-\d{2}-\d{4})\s+(\d{2}-\d{2}-\d{4})\s+(\d{2}-\d{2}-\d{4})"
#     date_match = re.search(date_sequence_pattern, full_text)
#     if date_match:
#         bill_details["Bill Date"] = date_match.group(2)  # 04-06-2025 (2nd date)
#         bill_details["Due Date"] = date_match.group(3)   # 18-06-2025 (3rd date)

#     # Fallback extraction using position-based method (your original approach)
#     if bill_details["Power Factor"] == "0":
#         for page in doc:
#             text_instances = []
#             for block in page.get_text("dict")["blocks"]:
#                 if "lines" in block:
#                     for line in block["lines"]:
#                         for span in line["spans"]:
#                             text_instances.append({
#                                 "text": span["text"].strip(),
#                                 "x": span["bbox"][0],
#                                 "y": span["bbox"][1]
#                             })

#             # Original position-based extraction for Power Factor
#             for idx, item in enumerate(text_instances):
#                 text = item["text"]
                
#                 if "Present Reading" in text:
#                     # Look ahead for the next 5 items and grab the last numeric value as PF
#                     values_collected = []
#                     for offset in range(1, 6):
#                         if idx + offset < len(text_instances):
#                             next_text = text_instances[idx + offset]["text"]
#                             if next_text.replace('.', '', 1).replace('-', '', 1).isdigit():
#                                 values_collected.append(next_text)
#                     if len(values_collected) >= 4:
#                         bill_details["Power Factor"] = values_collected[-1]

#     # Extract additional fields using regex
#     additional_extractions = {
#         "Interest on ISD/ASD": r"Interest on ISD/ASD.?([-\d,]+\.?\d)",
#         "Tax": r"Tax\s*([\d,]+\.?\d*)",
#         "Fixed Charges": r"Fixed charges.?([\d,]+\.?\d)",
#         "Energy Charges": r"Energy Charges.?([\d,]+\.?\d)"
#     }

#     for field, pattern in additional_extractions.items():
#         match = re.search(pattern, full_text, re.IGNORECASE)
#         if match:
#             value = match.group(1).replace(',', '').strip()
#             bill_details[field] = value

#     # Calculate rewards and taxes
#     try:
#         if "Interest on ISD/ASD" in bill_details and bill_details["Interest on ISD/ASD"] != "Not Found":
#             isd_value = float(bill_details["Interest on ISD/ASD"].replace('-', ''))
#             if isd_value > 0:
#                 bill_details["Rewards"] = isd_value
#     except:
#         pass

#     try:
#         if "Tax" in bill_details and bill_details["Tax"] != "Not Found":
#             bill_details["Taxes and Fees"] = float(bill_details["Tax"])
#     except:
#         pass

#     doc.close()
#     return bill_details


import os
import re
import fitz
import PyPDF2
import json


def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract text from PDF using PyPDF2"""
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


def extract_ruler_bill(pdf_path):
    """Extract details from ruler bill format"""
    text = extract_text_from_pdf(pdf_path)
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

    # Account/Consumer Number patterns
    account_patterns = [
        r'Account ID\s+(\d+)', 
        r'Account\s+ID\s+RR\s+Number\s+RR\s+Number\s+(\d+)', 
        r'(\d+)\s+SR\d+'
    ]
    for pattern in account_patterns:
        match = re.search(pattern, text)
        if match:
            bill_details['consumer_number'] = match.group(1)
            break

    # Bill Number patterns
    bill_num_patterns = [
        r'Bill No\s+(\d+)', 
        r'BILL/INVOICE\s+No:\s*(\d+)', 
        r'Bill/Invoice\s+No:\s*(\d+)', 
        r'(\d{12,})'
    ]
    for pattern in bill_num_patterns:
        match = re.search(pattern, text)
        if match:
            bill_details['bill_number'] = match.group(1)
            break

    # Consumer Name patterns
    name_patterns = [
        r'Account ID\s+\d+\s+\w+\s+([A-Z]{2,}(?:\s+[A-Z]{1,2})*\s+[A-Z]{2,})', 
        r'Name\s+([A-Z]{2,}(?:\s+[A-Z]{1,2})*\s+[A-Z]{2,})', 
        r'SR\d+\s+([A-Z]{2,}(?:\s+[A-Z]{1,2})*\s+[A-Z]{2,})'
    ]
    for pattern in name_patterns:
        match = re.search(pattern, text)
        if match:
            name = match.group(1).strip()
            name = re.sub(r'\s+', ' ', name)
            if len(name) > 5:
                bill_details['consumer_name'] = name
                break

    # Bill Date patterns
    bill_date_patterns = [
        r'Date:\s*(\d{2}-\d{2}-\d{4})', 
        r'Bill Date\s+(\d{2}-\d{2}-\d{4})', 
        r'Date:\s*(.+?)(?:\n)', 
        r'(\d{2}-\d{2}-\d{4})', 
        r'(\d{2}-\w{3}-\d{4})'
    ]
    for pattern in bill_date_patterns:
        match = re.search(pattern, text)
        if match:
            bill_details['bill_date'] = match.group(1).strip()
            break

    # Due Date patterns
    due_date_patterns = [
        r'Due Date\s+(\d{1,2}-\w{3}-\d{4})', 
        r'Due Date\s+(\d{1,2}\s+\w{3}\s+\d{4})', 
        r'Due Date\s+(\d{1,2}-\d{1,2}-\d{4})', 
        r'(?:Due Date|due date).*?(\d{1,2}-\w{3}-\d{4})'
    ]
    
    # Special billing line pattern
    billing_line_match = re.search(
        r'(\d+)\s+(\d{2}-\d{2}-\d{4})\s+to\s+(\d{2}-\d{2}-\d{4})\s+(\d{2}-\d{2}-\d{4})\s+(\d{1,2}-\w{3}-\d{4})', 
        text
    )
    if billing_line_match:
        bill_details['due_date'] = billing_line_match.group(5)
    else:
        for pattern in due_date_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                due_date = match.group(1).strip()
                if due_date != bill_details['bill_number'] and len(due_date) > 8:
                    bill_details['due_date'] = due_date
                    break

    # Sanctioned Load patterns
    load_patterns = [
        r'(\d+(?:\.\d+)?)\s*kW\d+(?:\.\d+)?\s*HP', 
        r'Sanctioned Load.*?(\d+(?:\.\d+)?)\s*kW', 
        r'(\d+(?:\.\d+)?)\s*kW'
    ]
    for pattern in load_patterns:
        match = re.search(pattern, text)
        if match:
            bill_details['sanctioned_load'] = match.group(1) + ' kW'
            break

    # Consumption patterns
    consumption_patterns = [
        r'Electricity Consumption \(in Units\)\s+(\d+)', 
        r'Electricity Consumption.*?(\d+)', 
        r'Consumption.*?(\d+)'
    ]
    for pattern in consumption_patterns:
        match = re.search(pattern, text)
        if match:
            bill_details['kwh_consumption'] = int(match.group(1))
            break

    # Amount patterns
    amount_patterns = [
        r'Current Bill amount \(INR\)\s+(\d+(?:\.\d+)?)', 
        r'Current Bill amount.*?(\d+(?:\.\d+)?)', 
        r'Bill amount.*?(\d+(?:\.\d+)?)'
    ]
    for pattern in amount_patterns:
        match = re.search(pattern, text)
        if match:
            bill_details['amount'] = float(match.group(1))
            break

    # Power Factor patterns
    power_factor_patterns = [
        r'PF Recorded\s+(\d+(?:\.\d+)?)', 
        r'Power Factor Recorded\s+(\d+(?:\.\d+)?)', 
        r'PF\s+(\d+(?:\.\d+)?)', 
        r'Power Factor\s+(\d+(?:\.\d+)?)'
    ]
    for pattern in power_factor_patterns:
        match = re.search(pattern, text)
        if match:
            bill_details['power_factor'] = float(match.group(1))
            break

    # Taxes and fees calculation
    taxes_fees = 0.0
    tax_match = re.search(r'Tax \(INR\)\s+(\d+(?:\.\d+)?)', text)
    fuel_adj_match = re.search(r'Fuel Adjustment Charges \(INR\)\s+(\d+(?:\.\d+)?)', text)
    if tax_match:
        taxes_fees += float(tax_match.group(1))
    if fuel_adj_match:
        taxes_fees += float(fuel_adj_match.group(1))
    bill_details['taxes_and_fees'] = taxes_fees

    # Rewards/Rebates
    rebates_match = re.search(r'Rebates \(INR\)\s+(\d+(?:\.\d+)?)', text)
    if rebates_match:
        bill_details['rewards'] = float(rebates_match.group(1))

    # Penalty calculation
    pf_penalty_match = re.search(r'Power Factor penalty \(INR\)\s+(\d+(?:\.\d+)?)', text)
    md_penalty_match = re.search(r'Excess MD penalty \(INR\)\s+(\d+(?:\.\d+)?)', text)
    interest_match = re.search(r'Interest \(INR\)\s+(\d+(?:\.\d+)?)', text)
    total_penalty = 0.0
    if pf_penalty_match:
        total_penalty += float(pf_penalty_match.group(1))
    if md_penalty_match:
        total_penalty += float(md_penalty_match.group(1))
    if interest_match:
        total_penalty += float(interest_match.group(1))
    bill_details['penalty'] = total_penalty

    return bill_details


def extract_consumer_number(pdf_path):
    """Extract consumer number using PyMuPDF (fitz)"""
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

    doc.close()
    return consumer_number


def extract_simple_format(pdf_path):
    """Extract bill details from electricity bill PDF using regex patterns"""
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"The file {pdf_path} does not exist.")

    try:
        doc = fitz.open(pdf_path)
    except Exception as e:
        print(f"Error opening PDF file: {e}")
        raise

    bill_details = {
        "Consumer Number": extract_consumer_number(pdf_path),
        "Bill Number": "Not Found",
        "Bill Date": "Not Found",
        "Due Date": "Not Found",
        "Amount": "Not Found",
        "Power Factor": "0",
        "Sanction Load": "Not Found",
        "KWH Consumption": "Not Found",
        "Net Payable Amount": "Not Found",
        "Rewards": 0,
        "Taxes and Fees": 0,
    }

    # Extract all text from PDF
    full_text = ""
    for page in doc:
        full_text += page.get_text()

    # Define regex patterns for extraction
    patterns = {
        "Bill Number": r"Bill No\.?\s*(\d+)",
        "Bill Date": r"(\d{2}-\d{2}-\d{4})",
        "Due Date": r"Due Date\s*(\d{2}-\d{2}-\d{4})",
        "Current Bill Amount": r"Current Bill Amount\s*([\d,]+\.?\d*)",
        "Net Payable Amount": r"Net Payable Amount\s*([\d,]+\.?\d*)",
        "Sanctioned Load": r"Sanctioned load \(KW\)\s*([\d.]+)",
        "KWH Consumption": r"Consumption\s+(\d+)\s+\d+\s+[-\d.]+",
        "Power Factor": r"Present Reading\s+\d{2}-[A-Z]{3}-\d{4}\s+\d+\s+\d+\s+[\d.]+\s+(\d+(?:\.\d+)?)"
    }

    # Additional specific patterns for missing fields
    specific_patterns = {
        "Bill Number": [
            r"Bill No\.?\s*(\d+)",
            r"(\d{12})",  # 12-digit bill numbers
            r"Account ID\s*(\d+)"
        ],
        "Bill Date": [
            r"Bill Date\s*(\d{2}-\d{2}-\d{4})",
            r"(\d{2}-\d{2}-\d{4})\s+(\d{2}-\d{2}-\d{4})\s+(\d{2}-\d{2}-\d{4})",
            r"Billing Period.*?(\d{2}-\d{2}-\d{4})\s+(\d{2}-\d{2}-\d{4})"
        ],
        "Due Date": [
            r"Due Date\s*(\d{2}-\d{2}-\d{4})",
            r"(\d{2}-\d{2}-\d{4})\s+(\d{2}-\d{2}-\d{4})\s+(\d{2}-\d{2}-\d{4})"
        ]
    }

    # Extract using regex patterns
    for key, pattern in patterns.items():
        match = re.search(pattern, full_text, re.IGNORECASE | re.MULTILINE)
        if match:
            value = match.group(1).replace(',', '').strip()
            
            # Map to bill_details keys
            if key == "Current Bill Amount":
                try:
                    bill_details["Amount"] = str(round(float(value)))
                except ValueError:
                    bill_details["Amount"] = value
            elif key == "Net Payable Amount":
                try:
                    bill_details["Net Payable Amount"] = str(round(float(value)))
                except ValueError:
                    bill_details["Net Payable Amount"] = value
            elif key == "Sanctioned Load":
                bill_details["Sanction Load"] = value
            elif key == "KWH Consumption":
                bill_details["KWH Consumption"] = value
            elif key == "Power Factor":
                bill_details["Power Factor"] = value
            else:
                bill_details[key] = value

    # Try specific patterns for missing fields
    for field, pattern_list in specific_patterns.items():
        if bill_details[field] == "Not Found":
            for pattern in pattern_list:
                matches = re.findall(pattern, full_text, re.IGNORECASE | re.MULTILINE)
                if matches:
                    if field == "Bill Number":
                        # Look for 12-digit numbers first
                        for match in matches:
                            if isinstance(match, tuple):
                                match = match[0] if match[0] else match[1]
                            if len(str(match)) == 12:
                                bill_details[field] = str(match)
                                break
                        if bill_details[field] == "Not Found" and matches:
                            first_match = matches[0]
                            if isinstance(first_match, tuple):
                                first_match = first_match[0] if first_match[0] else first_match[1]
                            bill_details[field] = str(first_match)
                    elif field == "Bill Date":
                        # Bill Date is the 2nd date in the sequence
                        first_match = matches[0]
                        if isinstance(first_match, tuple) and len(first_match) == 3:
                            bill_details[field] = first_match[1]  # 2nd date
                        elif len(matches) >= 2:
                            bill_details[field] = matches[1]  # 2nd match
                        elif matches:
                            bill_details[field] = str(matches[0])
                    elif field == "Due Date":
                        # Due Date is the 3rd date in the sequence
                        first_match = matches[0]
                        if isinstance(first_match, tuple) and len(first_match) == 3:
                            bill_details[field] = first_match[2]  # 3rd date
                        elif len(matches) >= 3:
                            bill_details[field] = matches[2]  # 3rd match
                        elif matches:
                            bill_details[field] = str(matches[-1])  # Last match
                    else:
                        first_match = matches[0]
                        if isinstance(first_match, tuple):
                            first_match = first_match[0] if first_match[0] else first_match[1]
                        bill_details[field] = str(first_match)
                    break
    
    # Specific extraction for the date sequence
    date_sequence_pattern = r"(\d{2}-\d{2}-\d{4})\s*-\s*(\d{2}-\d{2}-\d{4})\s+(\d{2}-\d{2}-\d{4})\s+(\d{2}-\d{2}-\d{4})"
    date_match = re.search(date_sequence_pattern, full_text)
    if date_match:
        bill_details["Bill Date"] = date_match.group(2)  # 2nd date
        bill_details["Due Date"] = date_match.group(3)   # 3rd date

    # Fallback extraction using position-based method for Power Factor
    if bill_details["Power Factor"] == "0":
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

            # Position-based extraction for Power Factor
            for idx, item in enumerate(text_instances):
                text = item["text"]
                
                if "Present Reading" in text:
                    # Look ahead for the next 5 items and grab the last numeric value as PF
                    values_collected = []
                    for offset in range(1, 6):
                        if idx + offset < len(text_instances):
                            next_text = text_instances[idx + offset]["text"]
                            if next_text.replace('.', '', 1).replace('-', '', 1).isdigit():
                                values_collected.append(next_text)
                    if len(values_collected) >= 4:
                        bill_details["Power Factor"] = values_collected[-1]

    # Extract additional fields using regex
    additional_extractions = {
        "Interest on ISD/ASD": r"Interest on ISD/ASD.?([-\d,]+\.?\d)",
        "Tax": r"Tax\s*([\d,]+\.?\d*)",
        "Fixed Charges": r"Fixed charges.?([\d,]+\.?\d)",
        "Energy Charges": r"Energy Charges.?([\d,]+\.?\d)"
    }

    for field, pattern in additional_extractions.items():
        match = re.search(pattern, full_text, re.IGNORECASE)
        if match:
            value = match.group(1).replace(',', '').strip()
            bill_details[field] = value

    # Calculate rewards and taxes
    try:
        if "Interest on ISD/ASD" in bill_details and bill_details["Interest on ISD/ASD"] != "Not Found":
            isd_value = float(bill_details["Interest on ISD/ASD"].replace('-', ''))
            if isd_value > 0:
                bill_details["Rewards"] = isd_value
    except (ValueError, KeyError):
        pass

    try:
        if "Tax" in bill_details and bill_details["Tax"] != "Not Found":
            bill_details["Taxes and Fees"] = float(bill_details["Tax"])
    except (ValueError, KeyError):
        pass

    doc.close()
    return bill_details


def extract(pdf_path):
    """Main extraction function that determines the format and extracts accordingly"""
    # First, check if file exists
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"The file {pdf_path} does not exist.")
    
    # Extract text to determine format
    text = extract_text_from_pdf(pdf_path)
    if "Nanna MESCOM" in text or "BILL/INVOICE" in text:
        print("Using extract_ruler_bill for extraction.")
        return extract_ruler_bill(pdf_path)
    elif "Your Detailed Bill" in text or "P&G Surcharge" in text:
        print("Using extract_simple_format for extraction.")
        return extract_simple_format(pdf_path)
    else:
        print("Unknown format. Defaulting to extract_simple_format.")
        return extract_simple_format(pdf_path)
