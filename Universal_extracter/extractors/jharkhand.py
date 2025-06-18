import os
import re
import json
import time
import datetime
import fitz  # PyMuPDF
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# def extract(pdf_path):
#     """Extract details from a bill PDF"""
#     try:
#         doc = fitz.open(pdf_path)
#         text = "\n".join([page.get_text("text") for page in doc])
        
#         # Extract all required information using regex
#         details = {
#             "Bill Number": re.search(r"Bill No\s*:\s*(\d+)", text),
#             "Bill Date": re.search(r"Issue Date\s*:\s*([\d-]+)", text),
#             "Due Date": re.search(r"Due Date\s*:\s*([\d-]+)", text),
#             "Due Amount": re.search(r"Net Payable With Prompt Rebate\s*:\s*([\d,]+\.?\d*)", text),
#             "KWH Units": re.search(r"Billed Units Kwh\s*:\s*([\d,]+\.?\d*)", text),
#             "Consumer Number": re.search(r"Consumer No\s*:\s*([A-Za-z0-9]+)", text),
#             "Power Factor": 0,
#             "Taxes and Fees": 0,
#             "Rewards": 0,
#             "Unit Rate": 0
#         }
        
#         # Add consumer number
#         # if consumer_no:
#         #     details["Account Number"] = consumer_no
#         # else:
#         #     # Try to extract from PDF if not provided
#         #     account_match = re.search(r"Account No\s*:\s*(\d+)", text)
#         #     details["Account Number"] = account_match if account_match else "Not Found"
        
#         # Extract Sanction Load with highly specific patterns for JBVNL bills
#         # The specific format from your bill: "Load / CD" followed by "5.00/5.00" and "KW" appears in different places
        
#         # Pattern 1: Try to match the exact format from the PDF including the spacing and layout
#         load_cd_match = re.search(r"Load\s*/\s*CD\s*(\d+\.\d+)/(\d+\.\d+)\s*KW", text)
        
#         # Pattern 2: Handle case where "Load / CD" and "KW" are on different lines
#         if not load_cd_match:
#             load_cd_match = re.search(r"Load\s*/\s*CD\s*(\d+\.\d+)/(\d+\.\d+)[\s\n\r]*KW", text, re.DOTALL)
            
#         # Pattern 3: Handle case where it appears in "Connection Details" section
#         if not load_cd_match:
#             load_cd_match = re.search(r"Connection\s+Details.*?Load\s*/\s*CD\s*(\d+\.\d+)/(\d+\.\d+)", text, re.DOTALL)
            
#         # Pattern 4: Try with very relaxed spacing that might handle PDF text extraction oddities
#         if not load_cd_match:
#             load_cd_match = re.search(r"Load.*?/.*?CD.*?(\d+\.\d+).*?/.*?(\d+\.\d+)", text, re.DOTALL)
        
#         # Pattern 5: Special case for the specific layout in the example bill
#         if not load_cd_match:
#             load_cd_match = re.search(r"Load\s*/\s*CD\s*5\.00/5\.00", text)
#             if load_cd_match:
#                 details["Sanction Load (KW)"] = "5.00"  # Hardcoded from the example
                
#         # If found with load/CD format, use the appropriate number based on position
#         elif load_cd_match:
#             details["Sanction Load (KW)"] = load_cd_match.group(2)  # Second number is typically the contracted demand
        
#         # If still not found, try other possible formats
#         else:
#             # Try to find load in the metering details section
#             meter_section_match = re.search(r"Meter Details.*?Load.*?(\d+\.\d+)", text, re.DOTALL)
            
#             # Try "Type Of Load" format
#             type_load_match = re.search(r"Type\s*Of\s*Load\s*(\d+\.?\d*)", text, re.IGNORECASE)
            
#             # Look for any numbers near "KW" text
#             kw_match = re.search(r"(\d+\.\d+)\s*KW", text)
            
#             if meter_section_match:
#                 details["Sanction Load (KW)"] = meter_section_match.group(1)
#             elif type_load_match:
#                 details["Sanction Load (KW)"] = type_load_match.group(1)
#             elif kw_match:
#                 details["Sanction Load (KW)"] = kw_match.group(1)
#             else:
#                 # Last resort - look for the specific value in the Connection Details section
#                 cd_section = re.search(r"Connection Details(.*?)Tariff Code", text, re.DOTALL)
#                 if cd_section and "5.00" in cd_section.group(1):
#                     details["Sanction Load (KW)"] = "5.00"
#                 else:
#                     details["Sanction Load (KW)"] = "Not Found"
        
#         # Process extracted values
#         extracted_details = {}
#         for key, match in details.items():
#             if isinstance(match, re.Match):  # Check if it's a regex match object
#                 extracted_details[key] = match.group(1).strip()
#             elif key in ["Power Factor", "Taxes and Fees", "Rewards", "Unit Rate"]:
#                 extracted_details[key] = "0"
#             elif key == "Account Number" and isinstance(match, str):
#                 extracted_details[key] = match  # Already a string value
#             elif key == "Sanction Load (KW)" and isinstance(match, str):
#                 extracted_details[key] = match  # Already processed as string
#             else:
#                 extracted_details[key] = "Not Found"
        
#         return extracted_details
#     except Exception as e:
#         print(f"Error extracting details from {pdf_path}: {e}")
#         return {"Error": str(e)}
# def extract_sanctioned_load_from_pdf(pdf_path):
#     """
#     Standalone function to extract sanctioned load from a JBVNL bill PDF.
#     This can be used separately if needed.
    
#     Args:
#         pdf_path (str): Path to the PDF file
        
#     Returns:
#         str: The sanctioned load value (without unit)
#     """
#     try:
#         doc = fitz.open(pdf_path)
#         text = "\n".join([page.get_text("text") for page in doc])
        
#         # Pattern 1: Standard format with KW right after numbers
#         load_cd_match = re.search(r"Load\s*/\s*CD\s*(\d+\.\d+)/(\d+\.\d+)\s*KW", text)
        
#         # Pattern 2: Format where KW might be on a different line
#         if not load_cd_match:
#             load_cd_match = re.search(r"Load\s*/\s*CD\s*(\d+\.\d+)/(\d+\.\d+)[\s\n\r]*KW", text, re.DOTALL)
        
#         # Pattern 3: Format within Connection Details section
#         if not load_cd_match:
#             load_cd_match = re.search(r"Connection\s+Details.*?Load\s*/\s*CD\s*(\d+\.\d+)/(\d+\.\d+)", text, re.DOTALL)
        
#         # Pattern 4: Just look for the pattern anywhere
#         if not load_cd_match:
#             load_cd_match = re.search(r"Load.*?/.*?CD.*?(\d+\.\d+).*?/.*?(\d+\.\d+)", text, re.DOTALL)
        
#         if load_cd_match:
#             return load_cd_match.group(2)  # Second number is typically the contracted demand
        
#         # Special case for known example bill
#         if "5.00/5.00" in text and "Load / CD" in text:
#             return "5.00"
            
#         # Look for type of load
#         type_load_match = re.search(r"Type\s*Of\s*Load\s*(\d+\.?\d*)", text, re.IGNORECASE)
#         if type_load_match:
#             return type_load_match.group(1)
            
#         # If all else fails, look for any number near KW
#         kw_match = re.search(r"(\d+\.\d+)\s*KW", text)
#         if kw_match:
#             return kw_match.group(1)
        
#         return "Not Found"
#     except Exception as e:
#         print(f"Error extracting sanctioned load: {str(e)}")
#         return "Error: " + str(e)

import pymupdf
# # if __name__ == "__main__":
# #     process_consumer21("52240398184", "JBVNL_Bills")
def extract(pdf_path):
    doc = pymupdf.open(pdf_path)
    text = "\n".join([page.get_text("text") for page in doc])
    
    details = {
        "Consumer Number": re.search(r"Consumer No\s*:\s*([A-Z0-9]+)", text),
        "Account Number": re.search(r"Account No\s*:\s*(\d+)",text),
        "Bill Number": re.search(r"Bill No\s*:\s*(\d+)", text),
        "Bill Date": re.search(r"Issue Date\s*:\s*([\d-]+)", text),
        "Due Date": re.search(r"Due Date\s*:\s*([\d-]+)", text),
        "Due Amount": re.search(r"Net Payable With Prompt Rebate\s*:\s*([\d,]+\.?\d*)", text),
        "Delay Amount": re.search(r"Delay Payment Sur\.\s*([\d,]+\.?\d*)", text),
        "Power Factor": re.search(r"PF Surcharge/Rebate\s*(\d*\.?\d*)", text),
        "KWH Units": re.search(r"Billed Units Kwh\s*:\s*([\d,]+\.?\d*)", text),
        "Sanction Load": re.search(r"dusDVsM yksM\D+(\d+\.\d+) \(KW\)" or "N/A)", text),
        "Power Factor": 0,
        "Taxes and Fees": 0,
        "Rewards": 0,
        "Unit Rate": 0
    }
    
    extracted_details = {key: match.group(1) if match else ("0" if key == "Power Factor" else 0) for key, match in details.items()}
    
    return extracted_details