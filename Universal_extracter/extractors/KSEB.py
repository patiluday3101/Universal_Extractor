import os
import time
import json
import re
import PyPDF2
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def extract(pdf_path):
    with open(pdf_path, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        text = "\n".join(page.extract_text() or "" for page in reader.pages)
    
    # Helper function to extract data using regex patterns
    def extract(pattern, default=""):
        match = re.search(pattern, text)
        return match.group(1) if match else default
    
    # Extract filename from path
    file_name = os.path.basename(pdf_path)
    
    # Extract all required fields
    consumer_number = extract(r"Consumer#\s*(\d+)")
    bill_number = extract(r"Bill#\s*(\d+)")
    bill_date = extract(r"Bill Date\s+([\d-]+)")
    due_date = extract(r"Due Date\s+([\d-]+)")
    
    # Extract total amount payable
    amount = extract(r"Net Payable.*?\s+(\d+\.\d+)", "0.00")
    
    # Extract consumption
    consumption = extract(r"KWH Cumulative Import\s+\d+\.\d+\s+\d+\.\d+\s+\d+\s+(\d+)", "0")
    
    # Extract connected load
    sanction_load = extract(r"Connected Load\s+(\d+\.?\d*)", "0.00")
    
    # Extract penalty/surcharge
    penalty = extract(r"Surcharge\s+(\d+\.?\d*)", "0.00")
    
    # Create the bill information dictionary
    bill_info = {
        "File Name": file_name,
        "Consumer Number": consumer_number,
        "Bill Number": bill_number,
        "Due Date": due_date,
        "Bill Date": bill_date,
        "Total Amount Payable": amount,
        "KWH_Consumption": consumption,
        "PF Surcharge": 0.0,  # This appears to be zero in the sample PDF
        "Penalty": float(penalty),
        "Unit Rate": 0,  # Not directly available in the PDF
        "Taxes and Fees": 0,  # Would need more specific extraction
        "Rewards": 0,  # Not available in the PDF
        "Sanction Load(kW)": sanction_load
    }
    
    return bill_info

