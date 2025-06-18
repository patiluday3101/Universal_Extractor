import os
import re
import json
import time
import datetime
import requests
from pathlib import Path
import pdfplumber
import shutil
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager



def extract(pdf_path):
    """Extract relevant details from electricity bill PDF"""
    data = {
        "Consumer Number": "",
        "Bill Number": "",
        "Bill Date": "",
        "Due Date": "",
        "Total Amount Payable": "",
        "Power Factor": "",
        "KWH Consumption": "",
        "Rewards": "0",
        "panelty": "0",
        "Unit Rate": "",
        "Taxes and Fees": "",
        "Sanction Load (KW)": ""
    }
    
    try:
        with pdfplumber.open(pdf_path) as pdf:
            # Extract text from all pages and combine
            text = ""
            for page in pdf.pages:
                text += page.extract_text() + "\n"
            
            # Extract Consumer Number
            consumer_number_match = re.search(r'(\d{10})', text)
            if consumer_number_match:
                data["Consumer Number"] = consumer_number_match.group(1)
            
            # Extract Bill Number
            bill_number_match = re.search(r'(\d{5})', text)
            if bill_number_match:
                data["Bill Number"] = bill_number_match.group(1)
            
            # Extract Bill Date
            bill_date_match = re.search(r'(\d{2}\.\d{2}\.\d{4})', text)
            if bill_date_match:
                # Convert date format from DD.MM.YYYY to DD/MM/YYYY
                date_str = bill_date_match.group(1)
                date_parts = date_str.split('.')
                data["Bill Date"] = f"{date_parts[0]}/{date_parts[1]}/{date_parts[2]}"
            
            # Extract Due Date
            due_date_matches = re.findall(r'(\d{2}\.\d{2}\.\d{4})', text)
            if len(due_date_matches) > 1:
                # Use the second date as the due date
                date_parts = due_date_matches[1].split('.')
                data["Due Date"] = f"{date_parts[0]}/{date_parts[1]}/{date_parts[2]}"
            
            # Extract Total Amount Payable
            amount_match = re.search(r'Total Amount Rs\.\s*([\d,]+\.\d{2})', text)
            if amount_match:
                data["Total Amount Payable"] = amount_match.group(1).replace(',', '')
            
            # Extract Power Factor
            power_factors = re.findall(r'(\d+\.\d{2})', text)
            for pf in power_factors:
                if float(pf) < 2.0:  
                    data["Power Factor"] = pf
                    break
            
            # Extract KWH Consumption
            kwh_matches = re.findall(r'(\d+\.\d{2})\s*KWH', text, re.IGNORECASE)
            if kwh_matches:
                data["KWH Consumption"] = kwh_matches[0]
            else:
                # Try alternative approach
                kwh_matches = re.findall(r'(\d+\.\d{2})', text)
                for kwh in kwh_matches:
                    if float(kwh) > 1000:  
                        data["KWH Consumption"] = kwh
                        break
            
            # Extract Unit Rate
            unit_rate_match = re.search(r'(\d+\.\d{2})\s*250806\.40', text)
            if unit_rate_match:
                data["Unit Rate"] = unit_rate_match.group(1)
            else:
                # Alternative search for unit rate
                unit_rate_matches = re.findall(r'(\d+\.\d{2})', text)
                for rate in unit_rate_matches:
                    if float(rate) > 3 and float(rate) < 15:  # Typical unit rate range
                        data["Unit Rate"] = rate
                        break
            
            # Extract Taxes and Fees (Electricity Duty)
            taxes_match = re.search(r'Electricity Duty Rs\.\s*([\d,]+\.\d{2})', text)
            if taxes_match:
                data["Taxes and Fees"] = taxes_match.group(1).replace(',', '')
            
            # Extract Sanction Load
            load_match = re.search(r'(\d+)\s*KVA', text)
            if load_match:
                data["Sanction Load (KW)"] = load_match.group(1)
            
            # Check for penalties
            penalty_match = re.search(r'([\d,]+\.\d{2})\s*penalty', text, re.IGNORECASE)
            if penalty_match:
                data["panelty"] = penalty_match.group(1).replace(',', '')
            
    except Exception as e:
        print(f"Error extracting data from PDF: {e}")
    
    return data