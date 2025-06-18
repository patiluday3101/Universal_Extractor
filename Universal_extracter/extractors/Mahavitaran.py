# import os
# import time
# import base64
# import json
# import logging
# import shutil
# from datetime import datetime
# import pandas as pd
# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.support.ui import Select
# from webdriver_manager.chrome import ChromeDriverManager
# from paddleocr import PaddleOCR
# import pdfplumber
# import re
# import cv2

# # Setup Logging
# logging.basicConfig(filename="maha_bill_log.log", level=logging.INFO,
#                     format="%(asctime)s - %(levelname)s - %(message)s")

# # Initialize PaddleOCR globally
# ocr = PaddleOCR(use_angle_cls=True, lang='en')
# def ocr_with_paddle(img_path):
#     result = ocr.ocr(img_path, cls=True)
#     captcha_text = " ".join(line[1][0] for res in result for line in res).strip()
#     return captcha_text if captcha_text else "N/A"
# month_map = {
#     'JAN': '01', 'FEB': '02', 'MAR': '03', 'APR': '04',
#     'MAY': '05', 'JUN': '06', 'JUL': '07', 'AUG': '08',
#     'SEP': '09', 'OCT': '10', 'NOV': '11', 'DEC': '12'
# }

# def extract_total_consumption(text):
    
#     patterns = [
 
#         r'\d{4,5}\s+\d{4,5}\s+\d{2}\s+(\d+)\s+\d+\s+\1',


#         r'Not Available\s+\d+\s+\d+\s+(\d+)\s+\d+\s+\1'
        
        
#     ]
    
#     for pattern in patterns:
#         match = re.search(pattern, text)
#         if match:
#             return f"{match.group(1)}"  
    
#     return "Not Found"  

# def extract(pdf_path):
#     details = {}
    
#     with pdfplumber.open(pdf_path) as pdf:
#         text = "\n".join(page.extract_text() for page in pdf.pages if page.extract_text())
#     print("DEBUG PDF TEXT:\n", text[:1000])  # Print first 1000 chars for debugging

#     match = re.search(r'Consumer No:\s*(\d+)', text)
#     details['Consumer Number'] = match.group(1) if match else None
#     details['KWH Consumption'] = extract_total_consumption(text)

#     match = re.search(r'Due Date:\s*(\d{2})-([A-Z]{3})-(\d{2})', text)
#     if match:
#         day, mon, yr = match.groups()
#         details['Due Date'] = f"{day}/{month_map.get(mon.upper(), '00')}/20{yr}"
#     else:
#         details['Due Date'] = None

#     match = re.search(r'Bill Date:\s*(\d{2})-([A-Z]{3})-(\d{2})', text)
#     if match:
#         day, mon, yr = match.groups()
#         details['Bill Date'] = f"{day}/{month_map.get(mon.upper(), '00')}/20{yr}"
#     else:
#         details['Bill Date'] = None

#     match = re.search(r'Bill Amount Rs:\s*([\d,]+\.\d+)', text)
#     details['Total Amount Payable'] = match.group(1) if match else None

#     match = re.search(r'If Paid After Due Date:\s*([\d,]+\.\d+)', text)
#     details['Delay Amount'] = match.group(1) if match else None

#     match = re.search(r'BILL NO.\(GGN\):\s*(\d+)', text)
#     details['Bill Number'] = match.group(1) if match else None

#     match = re.search(r'Fixed Charges\s*([\d,]+\.\d+)', text)
#     details['Fixed Charges'] = match.group(1) if match else None

#     match = re.search(r'Energy Charges\s*([\d,]+\.\d+)', text)
#     details['Energy Charges'] = match.group(1) if match else None

#     match = re.search(r'Wheeling Charges\s*[\d.]+/ Unit\s*([\d,]+\.\d+)', text)
#     details['Wheeling Charges'] = match.group(1) if match else None

#     match = re.search(r'F\.A\.C\.\s*([\d,]+\.\d+)', text)
#     details['F.A.C.'] = match.group(1) if match else None

#     match = re.search(r'Tax on Sale\s*[\d.]+/ Unit\s*([\d,]+\.\d+)', text)
#     details['Taxes and Fees'] = match.group(1) if match else None

#     match = re.search(r'Sanct\. Load:\s*([\d.]+)\s?', text)
#     details['Sanction Load (KW)'] = match.group(1) if match else None

#     details['Rewards'] = "0"
#     details['Power Factor'] = "0"
#     details['Unit Rate'] = "0"
#     details['penalty'] = "0"

#     return details

# # Make sure to update the rest of your code to use extract_bill_details instead of extract.
# pdf_path = r"C:\Users\Computer Point\OneDrive\Desktop\Universal_extracter\searchable_bill.pdf"  # Replace with your actual PDF path
# extract(pdf_path)  # Call the function to test extraction
# import os
# import re
# import io
# import pdfplumber
# from PyPDF2 import PdfMerger
# from pdf2image import convert_from_path
# import pytesseract
# from datetime import datetime

# month_map = {
#     'JAN': '01', 'FEB': '02', 'MAR': '03', 'APR': '04',
#     'MAY': '05', 'JUN': '06', 'JUL': '07', 'AUG': '08',
#     'SEP': '09', 'OCT': '10', 'NOV': '11', 'DEC': '12'
# }

# def make_pdf_searchable(input_pdf, output_pdf):
#     images = convert_from_path(input_pdf)
#     merger = PdfMerger()

#     for i, image in enumerate(images):
#         temp_img_path = f"temp_page_{i}.png"
#         image.save(temp_img_path)

#         pdf_bytes = pytesseract.image_to_pdf_or_hocr(temp_img_path, extension='pdf')
#         merger.append(io.BytesIO(pdf_bytes))
#         os.remove(temp_img_path)

#     with open(output_pdf, 'wb') as f:
#         merger.write(f)
#     merger.close()


# # def extract_total_consumption(text):
    
# #     patterns = [
 
# #         r'\d{4,5}\s+\d{4,5}\s+\d{2}\s+(\d+)\s+\d+\s+\1',


# #         r'Not Available\s+\d+\s+\d+\s+(\d+)\s+\d+\s+\1',
        
        
# #     ]
    
# #     for pattern in patterns:
# #         match = re.search(pattern, text)
# #         if match:
# #             return f"{match.group(1)}"  
    
# #     return "Not Found" 
# def extract_total_consumption(text):
#     current = re.search(r'Current\s+Reading\s*[:\-]?\s*(\d+)', text, re.IGNORECASE)
#     previous = re.search(r'Previous\s+Reading\s*[:\-]?\s*(\d+)', text, re.IGNORECASE)
#     if current and previous:
#         return str(int(current.group(1)) - int(previous.group(1)))
#     return "Not Found"

# def extract(pdf_path):
#     details = {}

#     searchable_path = f"searchable_{os.path.basename(pdf_path)}"
#     make_pdf_searchable(pdf_path, searchable_path)

#     with pdfplumber.open(searchable_path) as pdf:
#         text = "\n".join(page.extract_text() for page in pdf.pages if page.extract_text())

#     # Extraction Logic
#     details['Consumer Number'] = re.search(r'Consumer No:\s*(\d+)', text).group(1) if re.search(r'Consumer No:\s*(\d+)', text) else None
#     details['KWH Consumption'] = extract_total_consumption(text)

#     due_date = re.search(r'Due Date:\s*(\d{2})-([A-Z]{3})-(\d{2})', text)
#     details['Due Date'] = f"{due_date.group(1)}/{month_map.get(due_date.group(2), '00')}/20{due_date.group(3)}" if due_date else None

#     bill_date = re.search(r'Bill Date:\s*(\d{2})-([A-Z]{3})-(\d{2})', text)
#     details['Bill Date'] = f"{bill_date.group(1)}/{month_map.get(bill_date.group(2), '00')}/20{bill_date.group(3)}" if bill_date else None

#     details['Total Amount Payable'] = re.search(r'Bill Amount Rs:\s*([\d,]+\.\d+)', text).group(1) if re.search(r'Bill Amount Rs:\s*([\d,]+\.\d+)', text) else None
#     details['Delay Amount'] = re.search(r'If Paid After Due Date:\s*([\d,]+\.\d+)', text).group(1) if re.search(r'If Paid After Due Date:\s*([\d,]+\.\d+)', text) else None
#     details['Bill Number'] = re.search(r'BILL NO.\(GGN\):\s*(\d+)', text).group(1) if re.search(r'BILL NO.\(GGN\):\s*(\d+)', text) else None
#     details['Fixed Charges'] = re.search(r'Fixed Charges\s*([\d,]+\.\d+)', text).group(1) if re.search(r'Fixed Charges\s*([\d,]+\.\d+)', text) else None
#     details['Energy Charges'] = re.search(r'Energy Charges\s*([\d,]+\.\d+)', text).group(1) if re.search(r'Energy Charges\s*([\d,]+\.\d+)', text) else None
#     details['Wheeling Charges'] = re.search(r'Wheeling Charges\s*[\d.]+/ Unit\s*([\d,]+\.\d+)', text).group(1) if re.search(r'Wheeling Charges\s*[\d.]+/ Unit\s*([\d,]+\.\d+)', text) else None
#     details['F.A.C.'] = re.search(r'F\.A\.C\.\s*([\d,]+\.\d+)', text).group(1) if re.search(r'F\.A\.C\.\s*([\d,]+\.\d+)', text) else None
#     details['Taxes and Fees'] = re.search(r'Tax on Sale\s*[\d.]+/ Unit\s*([\d,]+\.\d+)', text).group(1) if re.search(r'Tax on Sale\s*[\d.]+/ Unit\s*([\d,]+\.\d+)', text) else None
#     details['Sanction Load (KW)'] = re.search(r'Sanct\. Load:\s*([\d.]+)\s?', text).group(1) if re.search(r'Sanct\. Load:\s*([\d.]+)\s?', text) else None

#     # Defaults
#     details['Rewards'] = "0"
#     details['Power Factor'] = "0"
#     details['Unit Rate'] = "0"
#     details['penalty'] = "0"

#     return details
# import os # it is working Code
# import re
# import io
# import pdfplumber
# from PyPDF2 import PdfMerger
# from pdf2image import convert_from_path
# import pytesseract
# from datetime import datetime

# month_map = {
#     'JAN': '01', 'FEB': '02', 'MAR': '03', 'APR': '04',
#     'MAY': '05', 'JUN': '06', 'JUL': '07', 'AUG': '08',
#     'SEP': '09', 'OCT': '10', 'NOV': '11', 'DEC': '12'
# }

# def make_pdf_searchable(input_pdf, output_pdf):
#     images = convert_from_path(input_pdf)
#     merger = PdfMerger()

#     for i, image in enumerate(images):
#         temp_img_path = f"temp_page_{i}.png"
#         image.save(temp_img_path)

#         pdf_bytes = pytesseract.image_to_pdf_or_hocr(temp_img_path, extension='pdf')
#         merger.append(io.BytesIO(pdf_bytes))
#         os.remove(temp_img_path)

#     with open(output_pdf, 'wb') as f:
#         merger.write(f)
#     merger.close()

# def extract_total_consumption(text):
    
#     patterns = [
 
#         r'\d{4,5}\s+\d{4,5}\s+\d{2}\s+(\d+)\s+\d+\s+\1',


#         r'Not Available\s+\d+\s+\d+\s+(\d+)\s+\d+\s+\1',
#         r'\b\d{4,5}\s+\d{4,5}\s+\d{1,2}\s+(\d{1,5})\s+\d{1,5}\s+\1\b'
        
        
#     ]
    
#     for pattern in patterns:
#         match = re.search(pattern, text)
#         if match:
#             return f"{match.group(1)}"  
    
#     return "Not Found"  

# def extract(pdf_path):
#     details = {}

#     searchable_path = f"searchable_{os.path.basename(pdf_path)}"
#     make_pdf_searchable(pdf_path, searchable_path)

#     with pdfplumber.open(searchable_path) as pdf:
#         text = "\n".join(page.extract_text() for page in pdf.pages if page.extract_text())

#     # Extraction Logic
#     details['Consumer Number'] = re.search(r'Consumer No:\s*(\d+)', text).group(1) if re.search(r'Consumer No:\s*(\d+)', text) else None
#     details['KWH Consumption'] = extract_total_consumption(text)

#     due_date = re.search(r'Due Date:\s*(\d{2})-([A-Z]{3})-(\d{2})', text)
#     details['Due Date'] = f"{due_date.group(1)}/{month_map.get(due_date.group(2), '00')}/20{due_date.group(3)}" if due_date else None

#     bill_date = re.search(r'Bill Date:\s*(\d{2})-([A-Z]{3})-(\d{2})', text)
#     details['Bill Date'] = f"{bill_date.group(1)}/{month_map.get(bill_date.group(2), '00')}/20{bill_date.group(3)}" if bill_date else None

#     details['Total Amount Payable'] = re.search(r'Bill Amount Rs:\s*([\d,]+\.\d+)', text)
#     details['Total Amount Payable'] = details['Total Amount Payable'].group(1) if details['Total Amount Payable'] else None

#     details['Delay Amount'] = re.search(r'If Paid After Due Date:\s*([\d,]+\.\d+)', text)
#     details['Delay Amount'] = details['Delay Amount'].group(1) if details['Delay Amount'] else None

#     details['Bill Number'] = re.search(r'BILL NO.\(GGN\):\s*(\d+)', text)
#     details['Bill Number'] = details['Bill Number'].group(1) if details['Bill Number'] else None

#     details['Fixed Charges'] = re.search(r'Fixed Charges\s*([\d,]+\.\d+)', text)
#     details['Fixed Charges'] = details['Fixed Charges'].group(1) if details['Fixed Charges'] else None

#     details['Energy Charges'] = re.search(r'Energy Charges\s*([\d,]+\.\d+)', text)
#     details['Energy Charges'] = details['Energy Charges'].group(1) if details['Energy Charges'] else None

#     details['Wheeling Charges'] = re.search(r'Wheeling Charges\s*[\d.]+/ Unit\s*([\d,]+\.\d+)', text)
#     details['Wheeling Charges'] = details['Wheeling Charges'].group(1) if details['Wheeling Charges'] else None

#     details['F.A.C.'] = re.search(r'F\.A\.C\.?\s*([\d,]+\.\d+)', text)
#     details['F.A.C.'] = details['F.A.C.'].group(1) if details['F.A.C.'] else None

#     details['Taxes and Fees'] = re.search(r'Tax on Sale\s*[\d.]+/ Unit\s*([\d,]+\.\d+)', text)
#     details['Taxes and Fees'] = details['Taxes and Fees'].group(1) if details['Taxes and Fees'] else None

#     details['Sanction Load (KW)'] = re.search(r'Sanct\. Load:\s*([\d.]+)\s?', text)
#     details['Sanction Load (KW)'] = details['Sanction Load (KW)'].group(1) if details['Sanction Load (KW)'] else None

#     # Defaults
#     details['Rewards'] = "0"
#     details['Power Factor'] = "0"
#     details['Unit Rate'] = "0"
#     details['penalty'] = "0"

#     return details
import os
import re
import io
import pdfplumber
from PyPDF2 import PdfMerger
from pdf2image import convert_from_path
import pytesseract
from datetime import datetime

month_map = {
    'JAN': '01', 'FEB': '02', 'MAR': '03', 'APR': '04',
    'MAY': '05', 'JUN': '06', 'JUL': '07', 'AUG': '08',
    'SEP': '09', 'OCT': '10', 'NOV': '11', 'DEC': '12'
}

def make_pdf_searchable(input_pdf, output_pdf):
    images = convert_from_path(input_pdf)
    merger = PdfMerger()
    for i, image in enumerate(images):
        temp_img_path = f"temp_page_{i}.png"
        image.save(temp_img_path)
        pdf_bytes = pytesseract.image_to_pdf_or_hocr(temp_img_path, extension='pdf')
        merger.append(io.BytesIO(pdf_bytes))
        os.remove(temp_img_path)
    with open(output_pdf, 'wb') as f:
        merger.write(f)
    merger.close()

def extract_total_consumption(text):
    patterns = [
        r'\d{4,5}\s+\d{4,5}\s+\d{2}\s+(\d+)\s+\d+\s+\1',
        r'Not Available\s+\d+\s+\d+\s+(\d+)\s+\d+\s+\1',
        r'\b\d{4,5}\s+\d{4,5}\s+\d{1,2}\s+(\d{1,5})\s+\d{1,5}\s+\1\b'
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return f"{match.group(1)}"
    return "Not Found"

def detect_bill_format(text):
    if "HT_LTIP" in text or "HT Consumer" in text:
        return "multimeter"
    elif "LT E-Bill" in text or "Reading Group" in text:
        return "simple"
    else:
        return "unknown"

def extract_simple_bill(text):
    details = {}
    details['Consumer Number'] = re.search(r'Consumer No:\s*(\d+)', text).group(1) if re.search(r'Consumer No:\s*(\d+)', text) else None
    details['KWH Consumption'] = extract_total_consumption(text)

    due_date = re.search(r'Due Date:\s*(\d{2})-([A-Z]{3})-(\d{2})', text)
    details['Due Date'] = f"{due_date.group(1)}/{month_map.get(due_date.group(2), '00')}/20{due_date.group(3)}" if due_date else None

    bill_date = re.search(r'Bill Date:\s*(\d{2})-([A-Z]{3})-(\d{2})', text)
    details['Bill Date'] = f"{bill_date.group(1)}/{month_map.get(bill_date.group(2), '00')}/20{bill_date.group(3)}" if bill_date else None

    details['Total Amount Payable'] = re.search(r'Bill Amount Rs:\s*([\d,]+\.\d+)', text)
    details['Total Amount Payable'] = details['Total Amount Payable'].group(1) if details['Total Amount Payable'] else None

    details['Delay Amount'] = re.search(r'If Paid After Due Date:\s*([\d,]+\.\d+)', text)
    details['Delay Amount'] = details['Delay Amount'].group(1) if details['Delay Amount'] else None

    details['Bill Number'] = re.search(r'BILL NO.\(GGN\):\s*(\d+)', text)
    details['Bill Number'] = details['Bill Number'].group(1) if details['Bill Number'] else None

    details['Fixed Charges'] = re.search(r'Fixed Charges\s*([\d,]+\.\d+)', text)
    details['Fixed Charges'] = details['Fixed Charges'].group(1) if details['Fixed Charges'] else None

    details['Energy Charges'] = re.search(r'Energy Charges\s*([\d,]+\.\d+)', text)
    details['Energy Charges'] = details['Energy Charges'].group(1) if details['Energy Charges'] else None

    details['Wheeling Charges'] = re.search(r'Wheeling Charges\s*[\d.]+/ Unit\s*([\d,]+\.\d+)', text)
    details['Wheeling Charges'] = details['Wheeling Charges'].group(1) if details['Wheeling Charges'] else None

    details['F.A.C.'] = re.search(r'F\.A\.C\.?\s*([\d,]+\.\d+)', text)
    details['F.A.C.'] = details['F.A.C.'].group(1) if details['F.A.C.'] else None

    details['Taxes and Fees'] = re.search(r'Tax on Sale\s*[\d.]+/ Unit\s*([\d,]+\.\d+)', text)
    details['Taxes and Fees'] = details['Taxes and Fees'].group(1) if details['Taxes and Fees'] else None

    details['Sanction Load (KW)'] = re.search(r'Sanct\. Load:\s*([\d.]+)\s?', text)
    details['Sanction Load (KW)'] = details['Sanction Load (KW)'].group(1) if details['Sanction Load (KW)'] else None

    # Defaults
    details['Rewards'] = "0"
    details['Power Factor'] = "0"
    details['Unit Rate'] = "0"
    details['penalty'] = "0"
    return details

def extract_multimeter_bill(text):
    details = {}
    details['Consumer Number'] = re.search(r'Consumer\s*No\.?\s*:\s*(\d+)', text).group(1) if re.search(r'Consumer\s*No\.?\s*:\s*(\d+)', text) else None
    details['Bill Date'] = re.search(r'BILL DATE\s+(\d{2}-\d{2}-\d{4})', text).group(1) if re.search(r'BILL DATE\s+(\d{2}-\d{2}-\d{4})', text) else None
    details['Due Date'] = re.search(r'DUE DATE\s+(\d{2}-\d{2}-\d{4})', text).group(1) if re.search(r'DUE DATE\s+(\d{2}-\d{2}-\d{4})', text) else None
    match_kwh = re.search(r'Total\s+Consumption\s*[:\-]?\s*(\d{1,5}(?:\.\d{1,2})?)', text)
    details['KWH Consumption'] = match_kwh.group(1) + " KWh" if match_kwh else "Not Found"
    due_amt = re.search(r'TOTAL\s+CURRENT\s+BILL\s*[:\-]?\s*(\d{1,3}(?:,\d{3})*\.\d{2})', text)
    details['Total Amount Payable'] = due_amt.group(1) if due_amt else "Not Found"
    details['Due Amount'] = details['Total Amount Payable']  # optional alias

    match = re.search(r'IF PAID AFTER\s+(\d{2}-\d{2}-\d{4})\s+(\d{1,3}(?:,\d{3})*\.\d{2})', text)
    details['Delay Amount'] = match.group(2) if match else None

    details['Energy Charges'] = re.search(r'Energy Charges\s+(\d+,?\d+\.\d+)', text).group(1) if re.search(r'Energy Charges\s+(\d+,?\d+\.\d+)', text) else None
    details['Fixed Charges'] = re.search(r'Demand Charges\s+(\d+,?\d+\.\d+)', text).group(1) if re.search(r'Demand Charges\s+(\d+,?\d+\.\d+)', text) else None
    details['Wheeling Charges'] = re.search(r'Wheeling Charge.*?\s+(\d+,?\d+\.\d+)', text).group(1) if re.search(r'Wheeling Charge.*?\s+(\d+,?\d+\.\d+)', text) else None
    details['Taxes and Fees'] = re.search(r'Electricity Duty.*?\s+(\d+,?\d+\.\d+)', text).group(1) if re.search(r'Electricity Duty.*?\s+(\d+,?\d+\.\d+)', text) else None
    details['penalty'] = re.search(r'Delayed Payment Charges\s+Rs\.\s+(\d+,?\d+\.\d+)', text).group(1) if re.search(r'Delayed Payment Charges\s+Rs\.\s+(\d+,?\d+\.\d+)', text) else None

    # Defaults
    details['Rewards'] = "0"
    details['Power Factor'] = "0"
    details['Unit Rate'] = "0"
# 1. Bill Number (try alternatives)
    details['Bill Number'] = re.search(r'BILL NO.\(GGN\):\s*(\d+)', text)
    details['Bill Number'] = details['Bill Number'].group(1) if details['Bill Number'] else None

    # 2. Sanction Load (multiple naming variations)
    load = re.search(r'(?:Sanctioned|Contract)\s+Load\s*[:\-]?\s*(\d+\.?\d*)', text)
    details['Sanction Load (KW)'] = load.group(1) if load else "Not Found"
    # 3. Total Amount Payable (try "NET AMOUNT PAYABLE" or "NET BILL")
    total_amount = (
        re.search(r'NET\s+(?:AMOUNT|BILL).*?(\d{1,3}(?:,\d{3})*\.\d{2})', text) or
        re.search(r'Total\s+Payable\s+Amount.*?(\d{1,3}(?:,\d{3})*\.\d{2})', text)
    )
    details['Total Amount Payable'] = total_amount.group(1) if total_amount else None

    return details

def extract(pdf_path):
    searchable_path = f"searchable_{os.path.basename(pdf_path)}"
    make_pdf_searchable(pdf_path, searchable_path)

    with pdfplumber.open(searchable_path) as pdf:
        text = "\n".join(page.extract_text() for page in pdf.pages if page.extract_text())

    bill_type = detect_bill_format(text)

    if bill_type == "simple":
        return extract_simple_bill(text)
    elif bill_type == "multimeter":
        return extract_multimeter_bill(text)
    else:
        return {"error": "Unsupported bill format"}
