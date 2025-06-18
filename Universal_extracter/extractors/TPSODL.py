import requests
import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
import re
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
    extracted_text = extract_text_from_pdf(pdf_path)

    if "No text found in PDF" in extracted_text or "Extraction error" in extracted_text:
        print(f"Skipping extraction for consumer_number, as PDF has no text.")
        return

    bill_details = {
        # "Consumer Number": consumer_number,
        "Consumer Number": re.search(r'Consumer\s+A/c\s+(No\.|Number)[:\s]([0-9]{12})', extracted_text).group(2) if re.search(r'Consumer\s+A/c\s+(No\.|Number)[:\s]([0-9]{12})', extracted_text, re.IGNORECASE) else "Not Found",
        "Bill Date": re.search(r"Bill Issue Date\s*:?\s*([\d/-]+)", extracted_text).group(1) if re.search(r"Bill Issue Date\s*:?\s*([\d/-]+)", extracted_text) else "Not Found",
        "Due Date": re.search(r"Due Date\s*:?\s*([\d/-]+)", extracted_text).group(1) if re.search(r"Due Date\s*:?\s*([\d/-]+)", extracted_text) else "Not Found",
        "Bill Number": re.search(r"Bill Number\s*:?\s*([\w\d/-]+)", extracted_text).group(1) if re.search(r"Bill Number\s*:?\s*([\w\d/-]+)", extracted_text) else "Not Found",
        "Power Factor": re.search(r"Power Factor\s*:?\s*([\d.]+)", extracted_text).group(1) if re.search(r"Power Factor\s*:?\s*([\d.]+)", extracted_text) else "Not Found",
        # "Total Amount Payable": re.search(r"Total Amount Payable.*?Rs\.\s*([\d,]+\.?\d*)", extracted_text, re.DOTALL).group(1) if re.search(r"Total Amount Payable.*?Rs\.\s*([\d,]+\.?\d*)", extracted_text, re.DOTALL) else "Not Found",
        "Total Amount Payable": (
            re.sub(r",", "", re.search(r"Total Amount Payable.*?Rs\.\s*([\d,]+\.?\d*)", extracted_text, re.DOTALL).group(1))
            if re.search(r"Total Amount Payable.*?Rs\.\s*([\d,]+\.?\d*)", extracted_text, re.DOTALL)
            else "Not Found"
        ),
        # "Consumer ID": re.search(r"Consumer ID\s*:?\s*([\w\d/-]+)", extracted_text).group(1) if re.search(r"Consumer ID\s*:?\s*([\w\d/-]+)", extracted_text) else "Not Found",
        "Sanction Load (KW)": re.search(r'Contract Demand\s*:\s*([\d.]+)\s*KW', extracted_text, re.IGNORECASE).group(1) if re.search(r'Contract Demand\s*:\s*([\d.]+)\s*KW', extracted_text, re.IGNORECASE) else "Not Found",
        "KWH Consumption": (
            re.search(r'KWH\s+[\d,.]+\s+[\d,.]+\s+([\d,.]+)', extracted_text).group(1)
            if re.search(r'KWH\s+[\d,.]+\s+[\d,.]+\s+([\d,.]+)', extracted_text)
            else (
                re.search(r'KWH\s+[\d,.]+\s+([\d,.]+)', extracted_text).group(1)
                if re.search(r'KWH\s+[\d,.]+\s+([\d,.]+)', extracted_text)
                else "Not Found"
            )
        ),
        "Rewards": 0,
        "Taxes and Fees": 0,
        "Penalty": 0,
        "Unit Rate": 0
        
    }
    return bill_details