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



# import os
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
import re


def extract_text_from_pdf(pdf_path):
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

def extract_ruler_bill(pdf_path):
    text=extract_text_from_pdf(pdf_path)
    if not text:
        return None

    # Initialize details dictionary with all fields
    details = {
        'bill_date': None,
        'bill_number': None,
        'consumer_number': None,
        'consumer_name': None,
        'due_date': None,
        'consumption_kwh': None,
        'sanction_load': None,
        'amount': None,
        'power_factor': None,
        'penalty': None,
        'rebate_discount': None,
        'interest': None,
        'taxes': {},
        'fees': {},
        'unit_rate': None,
        'fc_charges': None,
        'ec_charges': None,
        'fac_charges': None,
        'meter_rent': None,
        'others': None
    }

    # Extract Bill Number
    bill_no_pattern = r'Bill No\s+(\d+)'
    bill_no_match = re.search(bill_no_pattern, text)
    if bill_no_match:
        details['bill_number'] = bill_no_match.group(1)

    # Extract Consumer Number (Connection ID)
    consumer_no_pattern = r'Connection ID\s+(\d+)'
    consumer_no_match = re.search(consumer_no_pattern, text)
    if consumer_no_match:
        details['consumer_number'] = consumer_no_match.group(1)

    # Fixed Bill Date extraction - correct pattern
    # Fixed Bill Date extraction - avoid matching PrevBillDate
    bill_date_pattern = r'(?<!Prev)BillDate\s+(\d{2}/\d{2}/\d{4})'
    bill_date_match = re.search(bill_date_pattern, text)
    if bill_date_match:
        details['bill_date'] = bill_date_match.group(1)

    # Extract Due Date
    due_date_pattern = r'Due Date\s+(\d{2}/\d{2}/\d{4})'
    due_date_match = re.search(due_date_pattern, text)
    if due_date_match:
        details['due_date'] = due_date_match.group(1)

    # Extract Consumer Name - improved pattern
    name_pattern = r'Customer Name\s+([A-Z\s]+?)(?:\s+Reason|\s+Father)'
    name_match = re.search(name_pattern, text)
    if name_match:
        details['consumer_name'] = name_match.group(1).strip()

    # Extract Consumption
    consumption_pattern = r'Consumption\s+(\d+)'
    consumption_match = re.search(consumption_pattern, text)
    if consumption_match:
        details['consumption_kwh'] = int(consumption_match.group(1))

    # Extract Sanction Load
    sload_pattern = r'SLoad\s+(\d+\.?\d*)'
    sload_match = re.search(sload_pattern, text)
    if sload_match:
        details['sanction_load'] = float(sload_match.group(1))

    # Extract Total Amount
    total_pattern = r'Total To Be Paid\s+(\d+\.?\d*)'
    total_match = re.search(total_pattern, text)
    if total_match:
        details['amount'] = float(total_match.group(1))

    # Extract Power Factor (if available)
    pf_pattern = r'Power Factor\s*:?\s*(\d+\.?\d*)'
    pf_match = re.search(pf_pattern, text, re.IGNORECASE)
    if pf_match:
        details['power_factor'] = float(pf_match.group(1))
    else:
        details['power_factor'] = "0"

    # Extract Penalty
    penalty_pattern = r'Penalty\s+(\d+\.?\d*)'
    penalty_match = re.search(penalty_pattern, text)
    if penalty_match:
        details['penalty'] = float(penalty_match.group(1))
    else:
        details['penalty'] = 0.0

    # Extract Rebate/Discount
    rebate_pattern = r'Rebate/Disc\s+(\d+\.?\d*)'
    rebate_match = re.search(rebate_pattern, text)
    if rebate_match:
        details['rebate_discount'] = float(rebate_match.group(1))
    else:
        details['rebate_discount'] = 0.0

    # Extract Interest
    interest_pattern = r'Interest\s+(\d+\.?\d*)'
    interest_match = re.search(interest_pattern, text)
    if interest_match:
        details['interest'] = float(interest_match.group(1))
    else:
        details['interest'] = 0.0

    # Extract FC (Fixed Charges)
    fc_pattern = r'FC\s+(\d+\.?\d*)'
    fc_match = re.search(fc_pattern, text)
    if fc_match:
        details['fc_charges'] = float(fc_match.group(1))

    # Extract EC (Energy Charges)
    ec_pattern = r'EC\s+(\d+\.?\d*)'
    ec_match = re.search(ec_pattern, text)
    if ec_match:
        details['ec_charges'] = float(ec_match.group(1))

    # Extract FAC (Fuel Adjustment Charges)
    fac_pattern = r'FAC\s+(\d+\.?\d*)'
    fac_match = re.search(fac_pattern, text)
    if fac_match:
        details['fac_charges'] = float(fac_match.group(1))

    # Extract Tax
    tax_pattern = r'Tax\s+(\d+\.?\d*)'
    tax_match = re.search(tax_pattern, text)
    if tax_match:
        details['taxes']['total_tax'] = float(tax_match.group(1))

    # Extract CGST
    cgst_pattern = r'CGST\s+(\d+\.?\d*)'
    cgst_match = re.search(cgst_pattern, text)
    if cgst_match:
        details['taxes']['cgst'] = float(cgst_match.group(1))

    # Extract SGST
    sgst_pattern = r'SGST\s+(\d+\.?\d*)'
    sgst_match = re.search(sgst_pattern, text)
    if sgst_match:
        details['taxes']['sgst'] = float(sgst_match.group(1))

    # Extract Meter Rent
    meter_rent_pattern = r'Meter Rent\s+(\d+\.?\d*)'
    meter_rent_match = re.search(meter_rent_pattern, text)
    if meter_rent_match:
        details['meter_rent'] = float(meter_rent_match.group(1))

    # Extract D&R fee (Disconnection & Reconnection fee)
    dr_fee_pattern = r'D&R fee\s+(\d+\.?\d*)'
    dr_fee_match = re.search(dr_fee_pattern, text)
    if dr_fee_match:
        details['fees']['d_r_fee'] = float(dr_fee_match.group(1))

    # Extract Cheque Dishonor fee
    chq_fee_pattern = r'Chq\. Dis fee\s+(\d+\.?\d*)'
    chq_fee_match = re.search(chq_fee_pattern, text)
    if chq_fee_match:
        details['fees']['cheque_dishonor_fee'] = float(chq_fee_match.group(1))

    # Extract Others
    others_pattern = r'Others\s+(\d+\.?\d*)'
    others_match = re.search(others_pattern, text)
    if others_match:
        details['others'] = float(others_match.group(1))

    # Calculate Unit Rate (if consumption and EC charges are available)
    if details['consumption_kwh'] and details['ec_charges']:
        if details['consumption_kwh'] > 0:
            details['unit_rate'] = round(details['ec_charges'] / details['consumption_kwh'], 2)

    return details
    
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

def extract_simple_format(pdf_path):
    """
    Extract bill details from electricity bill PDF using regex patterns
    """
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"The file {pdf_path} does not exist.")

    try:
        doc = fitz.open(pdf_path)
    except Exception as e:
        print(f"Error opening PDF file: {e}")
        raise

    bill_details = {
        "Consumer Number": extract_consumer_number(pdf_path),  # <-- Add this line
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
        "Bill Date": r"(\d{2}-\d{2}-\d{4})",  # More flexible date pattern
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
            r"(\d{12})",  # 12-digit bill numbers like 909058316924
            r"Account ID\s*(\d+)"
        ],
        "Bill Date": [
            r"Bill Date\s*(\d{2}-\d{2}-\d{4})",
            r"(\d{2}-\d{2}-\d{4})\s+(\d{2}-\d{2}-\d{4})\s+(\d{2}-\d{2}-\d{4})",  # Extract 2nd date from sequence
            r"Billing Period.*?(\d{2}-\d{2}-\d{4})\s+(\d{2}-\d{2}-\d{4})"  # 2nd date in billing period line
        ],
        "Due Date": [
            r"Due Date\s*(\d{2}-\d{2}-\d{4})",
            r"(\d{2}-\d{2}-\d{4})\s+(\d{2}-\d{2}-\d{4})\s+(\d{2}-\d{2}-\d{4})"  # Extract 3rd date from sequence
        ]
    }

    # Alternative patterns for more flexibility
    alternative_patterns = {
        "Bill Date": r"(\d{2}-\d{2}-\d{4})",  # Any date format
        "Power Factor": r"Present Reading.?(\d+(?:\.\d+)?)\s$",  # Last number in Present Reading line
        "Amount": r"Rs\.?\s*([\d,]+\.?\d*)",  # Any amount with Rs
        "Consumption": r"Net Consumption\s+(\d+)\s+\d+"  # Alternative consumption pattern
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
                except:
                    bill_details["Amount"] = value
            elif key == "Net Payable Amount":
                try:
                    bill_details["Net Payable Amount"] = str(round(float(value)))
                except:
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
                        # Look for 12-digit numbers first (like 909058316924)
                        for match in matches:
                            if len(match) == 12:
                                bill_details[field] = match
                                break
                        if bill_details[field] == "Not Found" and matches:
                            bill_details[field] = matches[0]
                    elif field == "Bill Date":
                        # Bill Date is the 2nd date in the sequence (04-06-2025)
                        if len(matches[0]) == 3:  # If tuple with 3 dates
                            bill_details[field] = matches[0][1]  # 2nd date
                        elif len(matches) >= 2:
                            bill_details[field] = matches[1]  # 2nd match
                        elif matches:
                            bill_details[field] = matches[0]
                    elif field == "Due Date":
                        # Due Date is the 3rd date in the sequence (18-06-2025)
                        if len(matches[0]) == 3:  # If tuple with 3 dates
                            bill_details[field] = matches[0][2]  # 3rd date
                        elif len(matches) >= 3:
                            bill_details[field] = matches[2]  # 3rd match
                        elif matches:
                            bill_details[field] = matches[-1]  # Last match
                    else:
                        bill_details[field] = matches[0]
                    break
    
    # Specific extraction for the date sequence in your bill format
    # Pattern: "04-05-2025 - 04-06-2025 18-06-2025 03-07-2025"
    date_sequence_pattern = r"(\d{2}-\d{2}-\d{4})\s*-\s*(\d{2}-\d{2}-\d{4})\s+(\d{2}-\d{2}-\d{4})\s+(\d{2}-\d{2}-\d{4})"
    date_match = re.search(date_sequence_pattern, full_text)
    if date_match:
        bill_details["Bill Date"] = date_match.group(2)  # 04-06-2025 (2nd date)
        bill_details["Due Date"] = date_match.group(3)   # 18-06-2025 (3rd date)

    # Fallback extraction using position-based method (your original approach)
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

            # Original position-based extraction for Power Factor
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
    except:
        pass

    try:
        if "Tax" in bill_details and bill_details["Tax"] != "Not Found":
            bill_details["Taxes and Fees"] = float(bill_details["Tax"])
    except:
        pass

    doc.close()
    return bill_details



def extract(pdf_path):
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""

    if "BESCOM" in text or "Hubli Electricity Supply Company" in text:
        return extract_ruler_bill(pdf_path)
    elif "HESCOM" in text or "Office of the Asst. Executive Engineer" in text:
        return extract_simple_format(pdf_path)
    else:
        # Fallback to general extraction
        return extract_simple_format(pdf_path)














