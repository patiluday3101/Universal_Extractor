
import os
import time
import json
import re
import fitz  # PyMuPDF
import pytesseract
import cv2
import numpy as np
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def format_date(date_str):
    try:
        date_parts = re.split('[/-]', date_str)
        if len(date_parts) == 3:
            day, month, year = date_parts
            return f"{day}/{month}/{year}"
        return date_str 
    except Exception as e:
        print(f"Error formatting date: {e}")
        return date_str 




def extract(pdf_path):
    text = extract_text_from_pdf(pdf_path)

    bill_details = {
        "Consumer Number": "N/A",
        "Bill Number": "N/A",
        "Bill Date": "N/A",
        "Due Date": "N/A",
        "Total Amount Payable": "N/A",
        "Power Factor": "0",
        "KWH Consumption": "Not Found",
        "Rewards": "0",
        "panelty": "0",
        "Unit Rate": "0",
        "Taxes and Fees": "0",
        "Sanction Load (KW)": "0",
         
        
    }

    patterns = {
        "Consumer Number": r"(?:USC\s*No\.?|Consumer\s*No\.?)[:\-]?\s*(\d+)",
        "Bill Number": r"Bill\s*No[:\-]?\s*(\d+)",
        "Bill Date": r"(?:Bill\s*Date|Dt)[:\-]?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{8})",
        "Due Date": r"Due\s*Date[:\-]?\s*(\d{2}[-/]\d{2}[-/]\d{4})",
        "Total Amount Payable": r"Bill\s*Amount[:\-]?\s*([\d,.]+)",
        "Power Factor": r"Power\s*Factor[:\-]?\s*([\d.]+)",
        "KWH Consumption": r"UNITS[:\-]?\s*(\d+)",
        "Sanction Load (KW)":r"Contracted Load:\s*(\d)"
    }

    for key, pattern in patterns.items():
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            bill_details[key] = match.group(1).strip()
    if bill_details["Bill Date"] != "N/A":
        bill_details["Bill Date"] = format_date(bill_details["Bill Date"])

    if bill_details["Due Date"] != "N/A":
        bill_details["Due Date"] = format_date(bill_details["Due Date"])

    return bill_details
def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    full_text = ""

    for page in doc:
        text = page.get_text("text")
        if text.strip():
            full_text += text + "\n"

    if not full_text.strip():
        full_text = extract_text_with_ocr(pdf_path)

    return full_text.strip()


def extract_text_with_ocr(pdf_path):
    doc = fitz.open(pdf_path)
    ocr_text = ""

    for page in doc:
        pix = page.get_pixmap()
        img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.h, pix.w, pix.n)
        img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        text = pytesseract.image_to_string(img_gray)
        ocr_text += text + "\n"

    return ocr_text.strip()