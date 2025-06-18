import os
import cv2
import time
import json
import logging
import pymupdf
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from paddleocr import PaddleOCR
import pdfplumber




def extract_text_from_pdf(pdf_path):
    """Extracts text from the given PDF file."""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            text = "\n".join(page.extract_text() for page in pdf.pages if page.extract_text())
        return text if text.strip() else "No text found in PDF"
    except Exception as e:
        return f"Extraction error: {str(e)}"

def extract(pdf_path):
    """Extracts bill details, saves JSON, text, and renames the PDF."""
    bill_text = extract_text_from_pdf(pdf_path)

    if "No text found in PDF" in bill_text or "Extraction error" in bill_text:
        print(f"Skipping extraction for consumer_number, as PDF has no text.")
        return
    
    details = {}

    # Bill Date (convert . to /)
    issue_date = re.search(r"Billing Date\s*:\s*(\d{2}\.\d{2}\.\d{4})", bill_text)
    details["Bill Date"] = issue_date.group(1).replace('.', '/') if issue_date else "Not Found"

    # Total Amount Payable (within due date)
    total_amount = re.search(r"Amount due within due dates\(Rs\.\)\s*(\d+\.\d+)", bill_text)
    details["Total Amount Payable"] = total_amount.group(1) if total_amount else "Not Found"

    # Due Date (convert . to /)
    due_date = re.search(r"Due dates to avail Monthly Rebates\s*(\d{2}\.\d{2}\.\d{4})", bill_text)
    details["Due Date"] = due_date.group(1).replace('.', '/') if due_date else "Not Found"

    details["Power Factor"] = "0.0000"
    # TE KWH extraction (Unit Consumed)
    te_kwh_match = re.search(r'\b\d+\.\d+\s+\d+\.\d+\s+\d+\.\d+\s+(\d+\.\d+)', bill_text)
    details["KWH Consumption"] = te_kwh_match.group(1) if te_kwh_match else "Not Found"

    

    # Penalty (difference between amounts before/after due date)
    amt_before = re.search(r"Amt Due within Due Dt\(Rs\.\)\s*(\d+\.\d{2})", bill_text)
    amt_after = re.search(r"Amt Due After Due Dt\(Rs\.\)\s*(\d+\.\d{2})", bill_text)
    if amt_before and amt_after:
        penalty = float(amt_after.group(1)) - float(amt_before.group(1))
        details["Penalty"] = f"{penalty:.2f}"
    else:
        details["Penalty"] = "0"

    # Consumer Number
    consumer_id = re.search(r"Consumer Id\s*:\s*(\d+)", bill_text)
    details["Consumer Number"] = consumer_id.group(1) if consumer_id else "Not Found"

    # Bill Number
    bill_no = re.search(r"Invoice No\.\s*:\s*(\d+)", bill_text)
    details["Bill Number"] = bill_no.group(1) if bill_no else "Not Found"
    
    details["Rewards"] = 0
    details["Taxes and Fees"] = 0
    details["Unit Rate"] = 0
    sanction_load = re.search(r"Connected Load\s*:\s*(\d+\.\d+)\s*KVA", bill_text)
    details["Sanction Load (KW)"] = sanction_load.group(1) if sanction_load else "Not Found"

    return details


# process_consumer15("402209888", "21761523", "west_bengal_bills")