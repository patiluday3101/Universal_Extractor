# import os
# import time
# import re
# import cv2
# import pdfplumber
# import pytesseract
# import glob
# import shutil
# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# import json
# month_map = {
#     'JAN': '01', 'FEB': '02', 'MAR': '03', 'APR': '04',
#     'MAY': '05', 'JUN': '06', 'JUL': '07', 'AUG': '08',
#     'SEP': '09', 'OCT': '10', 'NOV': '11', 'DEC': '12'
# }


# def extract(pdf_path):
#     with pdfplumber.open(pdf_path) as pdf:
#         text = "\n".join(page.extract_text() for page in pdf.pages if page.extract_text())
#     details = {}
    
#     # Debug: Print first 500 characters to verify text extraction
#     print(text[:10000])
#     print("==================================")
    
#     # Improved patterns with optional whitespace and variations
#     patterns = {
#         'Bill Date': r'(?:िबल ितिथ|Bill Date)\s*[:]?\s*(\d{2}-[A-Z]{3}-\d{4})',
#         'Total Amount Payable': r'(?:देय धनरािश|Payable Amount)\s*[:]?\s*(\d[\d,]*)',
#         'Due Date': r'(?:देय ितिथ|Due Date)\s*[:]?\s*(\d{2}-[A-Z]{3}-\d{4})',
#         'Consumer Number': r'(?:अकाउंट सं\.|Account No\.)\s*[:]?\s*(\d{10})',
#         'Bill Number': r'(?:िबल संखया|Bill Number)\s*[:]?\s*(\d{12})',
#         'Sanction Load': r'(?:सवीक\s*ृत भार|Sanction Load)\s*[:]?\s*(\d+\.?\d*\s)',
#         'Penalty': r'(?:वतरमान िवलमब भुगतान अिधभार|Current LPSC)\s*[:]?\s*(\d+\.?\d*)',
#         'Power Factor': r'(?:शक्ती गुणांक|Power Factor)\s*[:]?\s*([\d.]+)',
#         'Taxes and Fees': r'(?:कर|Taxes)\s*[:]?\s*(\d+\.?\d*)',
#         'Unit Rate': r'(?:यूनिट दर|Unit Rate)\s*[:]?\s*(\d+\.?\d*)',
#         'KWH Consumption': r"Charges\s*Slab\s*1\s*([\d,.]+)",
#     }
    
#     for field, pattern in patterns.items():
#         match = re.search(pattern, text, re.IGNORECASE)
#         if match:
#             value = match.group(1).replace(',', '') if field == 'Total Amount Payable' else match.group(1)
            
#             # Convert date format if the field is a date
#             if field in ['Bill Date', 'Due Date']:
#                 day, month_abbr, year = value.split('-')
#                 month = month_map.get(month_abbr.upper(), '00')  # Default to '00' if month not found
#                 value = f"{day}/{month}/{year}"
            
#             details[field] = value
#         else:
#             if field in ["Power Factor", "Taxes and Fees", "Unit Rate"]:
#                 details[field] = 0
#             else:
#                 details[field] = "Not Found"
    
#     match = re.search(r"Charges\s*Slab\s*1\s*([\d,.]+)", text)
#     if match:
#         kwh_value = match.group(1)
#         print("KWH Consumption:", kwh_value)
    
#     return details

import re
import PyPDF2
from pdf2image import convert_from_path
import pytesseract

def extract_text_from_pdf(pdf_path):
    text = ""
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text
        
        if len(text.strip()) < 100:  # Arbitrary threshold
            images = convert_from_path(pdf_path)
            if images:
                text = pytesseract.image_to_string(images[0], lang='hin+eng')
    except Exception as e:
        print(f"Error reading PDF: {e}")
    return text

def extract(pdf_path):
    text = extract_text_from_pdf(pdf_path)
    details = {}
    
    # Debug: Print first 500 characters to verify text extraction
    print("=== DEBUG: First 500 characters ===")
    print(text[:500])
    print("==================================")
    
    # Improved patterns with optional whitespace and variations
    patterns = {
        'Bill Issue Date': r'(?:िबल ितिथ|Bill Date)\s*[:]?\s*(\d{2}-[A-Z]{3}-\d{4})',
        'Total Amount Payable': r'(?:देय धनरािश|Payable Amount)\s*[:]?\s*(\d[\d,]*)',
        'Due Date': r'(?:देय ितिथ|Due Date)\s*[:]?\s*(\d{2}-[A-Z]{3}-\d{4})',
        'Consumer Number': r'(?:अकाउंट सं\.|Account No\.)\s*[:]?\s*(\d{10})',
        'Bill Number': r'(?:िबल संखया|Bill Number)\s*[:]?\s*(\d{12})',
        'Current Billed Units': r'(?:नेट िबलड यूिनट|Net Billed Unit)\s*[:]?\s*(\d+\.?\d*)',
        'Sanction Load': r'(?:सवीक\s*ृत भार|Sanction Load)\s*[:]?\s*(\d+\.?\d*\s*[kK][wW])',
        'Penalty': r'(?:वतरमान िवलमब भुगतान अिधभार|Current LPSC)\s*[:]?\s*(\d+\.?\d*)',
        'Power Factor': r'(?:शक्ती गुणांक|Power Factor)\s*[:]?\s*([\d.]+)',
        'Taxes and Fees': r'(?:कर|Taxes)\s*[:]?\s*(\d+\.?\d*)',
        'Unit Rate': r'(?:यूनिट दर|Unit Rate)\s*[:]?\s*(\d+\.?\d*)',
    }
    
    for field, pattern in patterns.items():
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            value = match.group(1).replace(',', '') if field == 'Total Amount Payable' else match.group(1)
            details[field] = value
        else:
            if field in ["Power Factor", "Taxes and Fees", "Unit Rate"]:
                details[field] = 0
            else:
                details[field] = "Not Found"
    
    return details

