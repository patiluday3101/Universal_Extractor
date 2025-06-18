import datetime
import os
import json
import re
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pdf2image import convert_from_path
import pytesseract
from PIL import Image, ImageEnhance, ImageFilter
from paddleocr import PaddleOCR
import logging


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
# Update ChromeDriver path if necessary
chromedriver_path = "C:\\Windows\\chromedriver.exe"  # Note the escaped backslashes
RETRY_LIMIT = 3

logging.basicConfig(filename="apepdcl_bill_log.log", level=logging.INFO,
                    format="%(asctime)s - %(levelname)s - %(message)s")

# Initialize PaddleOCR globally
ocr = PaddleOCR(use_angle_cls=True, lang='en')

# Preprocess image for better OCR
def preprocess_image(image):
    image = image.convert('L')
    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(2.5)
    image = image.filter(ImageFilter.SHARPEN)
    return image

# Extract text using Tesseract OCR
def extract_text(image):
    image = preprocess_image(image)
    custom_config = r'--oem 3 --psm 6'
    text = pytesseract.image_to_string(image, lang='eng', config=custom_config)
    return text

# Extract required fields from PDF
def extract(pdf_path):
    fields = {
        "Consumer Number": None,
        "Bill Date": None,
        "Due Date": None,
        "Sanction Load (KW)": None,
        "KWH Consumption": None,
        "Penalty": None,
        "Bill Number": None,
        "Total Amount Payable": None,
        "Power Factor": 0,
        "Unit Rate": 0,
        "Taxes and Fees": 0,
        "Rewards": 0,
    }

    images = convert_from_path(pdf_path)
    text = "".join([extract_text(img) for img in images])

    patterns = {
        "Consumer Number": r"Unique\s*Service\s*Number\s*[:\-]?\s*(\d+)",
        "Bill Date": r"(\d{2}-[A-Za-z]{3}-\d{4})",
        "Due Date": r"\d{2}-[A-Za-z]{3}-\d{4}\s+(\d{2}-[A-Za-z]{3}-\d{4})",
        "Sanction Load (KW)": r"Contracted\s*Load\s*\(KW\)\s*[:\-]?\s*([\d.]+)",
        "KWH Consumption": r"Billed\s*Units\s*[:\-]?\s*(\d+)",
        "Penalty": r"Penal\s*Energy\s*Charges\s*[:\-]?\s*([\d.]+)",
        "Bill Number": r"Bill\s*Number\s*[:\-]?\s*(\d+)",
        "Total Amount Payable": r"Net\s*Bill\s*Amount\s*[,:]?\s*([₹\d.,]+)"
    }
    
    for key, pattern in patterns.items():
        match = re.search(pattern, text)
        if match:
            fields[key] = match.group(1)

    if fields["Bill Date"]:
        fields["Bill Date"] = standardize_date(fields["Bill Date"])
    if fields["Due Date"]:
        fields["Due Date"] = standardize_date(fields["Due Date"])

    return fields

