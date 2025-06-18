import os
import time
import json
import re
from datetime import datetime
from httpcore import TimeoutException
import pdfplumber
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options


def convert_date_format(date_str):
    """Convert date strings to DD/MM/YYYY format"""
    if not date_str or date_str == "Not Found" or date_str == "N/A":
        return date_str
        
    try:
        if re.match(r'^\d{4}-\d{2}-\d{2}$', date_str):
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            return date_obj.strftime('%d/%m/%Y')
            
        elif re.match(r'^\d{2}-[A-Za-z]{3}-\d{4}$', date_str):
            date_obj = datetime.strptime(date_str, '%d-%b-%Y')
            return date_obj.strftime('%d/%m/%Y')
            
        elif re.match(r'^\d{1,2} [A-Za-z]{3} \d{4}$', date_str):
            date_obj = datetime.strptime(date_str, '%d %b %Y')
            return date_obj.strftime('%d/%m/%Y')
        
    except ValueError:
        pass
        
    return date_str  



def extract(pdf_path):
    details = {
        "File Name": os.path.basename(pdf_path),
        "Consumer Number": "Not Found",
        "Bill Number": "Not Found",
        "Due Date": "Not Found",
        "Bill Date": "Not Found",
        "Total Amount Payable": "Not Found",
        "Sanction Load": "Not Found",
        "Total Units": "Not Found",
        "PF Surcharge": 0,
        "Penalty": 0,
        "Unit Rate": 0,
        "Taxes and Fees": 0,
        "Rewards": 0
    }

    try:
        with pdfplumber.open(pdf_path) as pdf:
            full_text = "\n".join([page.extract_text() or "" for page in pdf.pages])

            match = re.search(r"\b([A-Z]\d{10})\b", full_text)
            if match:
                details["Consumer Number"] = match.group(1)

            match = re.search(r"Bill Number\s*[:\-]?\s*([A-Z0-9]+)", full_text)
            if match:
                details["Bill Number"] = match.group(1)

            match = re.search(r"Bill\s*Date\s*[:]?\s*(\d{2})-([A-Za-z]{3})-(\d{4})", full_text, re.IGNORECASE)
            if match:
                day = match.group(1)
                month_name = match.group(2)
                year = match.group(3)
                
                month_map = {
                    "Jan": "01", "Feb": "02", "Mar": "03", "Apr": "04", "May": "05", "Jun": "06",
                    "Jul": "07", "Aug": "08", "Sep": "09", "Oct": "10", "Nov": "11", "Dec": "12"
                }
                month = month_map.get(month_name[:3], "01")  
                
                details["Bill Date"] = f"{day}/{month}/{year}"
            else:
                alt_match = re.search(r"Bill\s*Date\s*[:]?\s*(\d{2}-[A-Za-z]{3}-\d{4})", full_text, re.IGNORECASE)
                if alt_match:
                    bill_date = alt_match.group(1).strip()
                    details["Bill Date"] = convert_date_format(bill_date)

            # match = re.search(r"Current\s*Month\s*Bill.*?([\d,]+\.\d{2})", full_text, re.IGNORECASE | re.DOTALL)
            # if match:
            #     details["Total Amount Payable"] = float(match.group(1).replace(",", ""))

            match = re.search(r"Load Sanctioned\s*[:\-]?\s*([0-9.]+)\s*KW", full_text)
            if match:
                details["Sanction Load"] = match.group(1) 

            match = re.search(r"(?:Total Units|Units consumed).*?([0-9.]+)", full_text)
            if match:
                details["Total Units"] = match.group(1)

            match = re.search(r"(?:PF Surcharge|Power Factor Surcharge).*?₹?([0-9,.]+)", full_text, re.IGNORECASE)
            if match:
                pf_value = match.group(1).replace(",", "").strip()
                details["PF Surcharge"] = float(pf_value) if pf_value else 0
                
            penalty_match = re.search(r"(?:Penalty|Late Payment).*?₹?([0-9,.]+)", full_text, re.IGNORECASE)
            if penalty_match:
                penalty_value = penalty_match.group(1).replace(",", "").strip()
                details["Penalty"] = float(penalty_value) if penalty_value else 0

    except Exception as e:
        print(f"Error processing {pdf_path}: {e}")

    return details

