import os
import time
import json
import re
import pdfplumber
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

MONTHS_PATTERN = "Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec"
MONTH_MAP = {
    "Jan": "01", "Feb": "02", "Mar": "03", "Apr": "04",
    "May": "05", "Jun": "06", "Jul": "07", "Aug": "08",
    "Sep": "09", "Oct": "10", "Nov": "11", "Dec": "12"
}


def standardize_date(date_str):
    """Convert various date formats to DD/MM/YYYY format."""
    if not date_str or date_str == "Not Found":
        return date_str
    
    # Handle DD-MMM-YYYY format (e.g., "22-May-2025")
    pattern1 = re.compile(r"(\d{1,2})-(" + MONTHS_PATTERN + r")-(\d{4})")
    match = pattern1.match(date_str)
    if match:
        day, month, year = match.groups()
        return f"{day.zfill(2)}/{MONTH_MAP[month]}/{year}"
    
    # Handle DD/MMM/YYYY format (e.g., "07/May/2025")
    pattern2 = re.compile(r"(\d{1,2})/(" + MONTHS_PATTERN + r")/(\d{4})")
    match = pattern2.match(date_str)
    if match:
        day, month, year = match.groups()
        return f"{day.zfill(2)}/{MONTH_MAP[month]}/{year}"
    
    # Handle existing DD/MM/YYYY format
    if re.match(r"\d{1,2}/\d{1,2}/\d{4}", date_str):
        parts = date_str.split('/')
        if len(parts) == 3:
            day, month, year = parts
            return f"{day.zfill(2)}/{month.zfill(2)}/{year}"
    
    # Try to parse with datetime if all else fails
    try:
        for fmt in ["%d-%b-%Y", "%d/%b/%Y", "%d-%m-%Y", "%d/%m/%Y"]:
            try:
                dt = datetime.strptime(date_str, fmt)
                return dt.strftime("%d/%m/%Y")
            except ValueError:
                continue
    except Exception:
        pass
    
    return date_str



def extract(pdf_path):
    details = {
        "File Name": os.path.basename(pdf_path),
        "Consumer Number": "Not Found",
        "Bill Number": "Not Found",
        "Due Date": "Not Found",
        "Total Amount Payable": "Not Found",
        "Sanction Load (KW)": "Not Found",
        "KWH Consumption": "Not Found",
        "PF Surcharge": 0,
        "Penalty": 0,
        "Unit Rate": 0,
        "Taxes and Fees": 0,
        "Rewards": 0,
        "Bill Date": "Not Found",
        "Power Factor": 0,
        
    }

    try:
        with pdfplumber.open(pdf_path) as pdf:
            full_text = "\n".join([page.extract_text() or "" for page in pdf.pages])

            # Consumer Number (generally starts with an 'N' followed by 10 digits)
            match = re.search(r"\b([A-Z]\d{10})\b", full_text)
            if match:
                details["Consumer Number"] = match.group(1)

            # Bill Number (e.g. APR25N003402193)
            match = re.search(r"Bill Number\s*[:\-]?\s*([A-Z0-9]+)", full_text)
            if match:
                details["Bill Number"] = match.group(1)

            # Bill Date
            match = re.search(fr"(\d{{1,2}}-({MONTHS_PATTERN})-\d{{4}})", full_text)
            if match:
                bill_date = match.group(1).replace("-", "/")
                details["Bill Date"] = standardize_date(bill_date)

            # Total Amount Payable
            # match = re.search(r"Current\s*Payable\s*Amount.*?([\d,]+\.\d{2})", full_text, re.IGNORECASE)
            # if match:
            #     amount = match.group(1).replace(",", "").strip()
            #     details["Total Amount Payable"] = float(amount) if amount.replace(".", "").isdigit() else 0.0

            # Sanction Load
            match = re.search(r"Load Sanctioned\s*[:\-]?\s*([0-9.]+)\s*KW", full_text)
            if match:
                details["Sanction Load (KW)"] = match.group(1) 

            # KWH Consumption
            match = re.search(r"(?:Total Units|Units consumed).*?([0-9.]+)", full_text)
            if match:
                details["KWH Consumption"] = match.group(1)

            # PF Surcharge
            match = re.search(r"PF Surcharge\s*[:\-]?\s*₹?([0-9,.]+)", full_text, re.IGNORECASE)
            if match:
                details["PF Surcharge"] = "₹" + match.group(1).replace(",", "").strip()

    except Exception as e:
        print(f"Error processing {pdf_path}: {e}")

    return details


#     process_consumer12("2394007014", "madya")