import re
import pdfplumber
import fitz  # PyMuPDF
from pdf2image import convert_from_path
import pytesseract

month_map = {
    'JAN': '01',
    'FEB': '02',
    'MAR': '03',
    'APR': '04',
    'MAY': '05',
    'JUN': '06',
    'JUL': '07',
    'AUG': '08',
    'SEP': '09',
    'OCT': '10',
    'NOV': '11',
    'DEC': '12'
}
def extract_text_from_pdf(pdf_path):
    text = ""
    try:
        doc = fitz.open(pdf_path)
        for page in doc:
            text += page.get_text("text") + "\n"

        if not text.strip():
            images = convert_from_path(pdf_path)
            text = " ".join([pytesseract.image_to_string(img) for img in images])
    except Exception as e:
        print(f"Error extracting text from {pdf_path}: {e}")
    return text
def clean_date(raw_date):
    return re.sub(r"\s*-\s*", "/", raw_date.strip())




def extract(pdf_path):
    text = extract_text_from_pdf(pdf_path)
    
    Consumer_No= re.search(r"(\d{10,12})\s+\d+/\d+\s+[A-Z-]+,\d{2}", text, re.IGNORECASE)
    Total_Consumption = re.search(r"Total Consumption\s(\d+)", text, re.IGNORECASE)
    # Sanction_Load = re.search(r"H\.P\.\/K\.W\.\s+([\d\.]+)", text, re.IGNORECASE)
    Sanction_Load = re.search(r'NRGP\s+A\s+(\d+\.\d+)', text, re.IGNORECASE)
    bill_no_match = re.search(r"Bill\s*No[:\-]?\s*([\d/]+)", text, re.IGNORECASE)
    bill_date_match = re.search(r"Bill\s*Date[:\-]?\s*([\d\-]+)", text, re.IGNORECASE)
    due_date_match = re.search(r"Due\s*Date[:\-]?\s*([\d\-]+)", text, re.IGNORECASE)
    amount_due_match = re.search(r"(?:Amount Due|ભરવાપાત્ર રકમ)\s*[:\-]?\s*Rs\.?\s*([\d,]+\.\d+)", text, re.IGNORECASE)
    penalty_match = re.search(r"Delayed Payment Charges\s([\d,.]+)", text, re.IGNORECASE)
    Charges = re.search(r"Fixed Charges\s([\d,.]+)|Energy Charges\s([\d,.]+)|Fuel Charges @ [\d,.]+\s([\d,.]+)", text, re.IGNORECASE)
    bill_date = bill_date_match.group(1).strip() if bill_date_match else "Unknown"
    Due_date = due_date_match.group(1).strip() if due_date_match else "Not found"

    bill_details = {
        "Bill Number": bill_no_match.group(1).strip() if bill_no_match else "Not found",
        "Bill_date" : clean_date(bill_date_match.group(1)) if bill_date_match else "Unknown",
        "Due_date" : clean_date(due_date_match.group(1)) if due_date_match else "Not found",
        "Total Amount Payable": amount_due_match.group(1).replace(",", "").strip() if amount_due_match else "Not found",
        "Consumer Number": Consumer_No.group(1).strip() if Consumer_No else "Not found",  
        "Sanction Load (KW)": Sanction_Load.group(1).strip() if Sanction_Load else "Not found", 
        "KWH Consumption": Total_Consumption.group(1).strip() if Total_Consumption else "Not found",  
        "Penalty": penalty_match.group(1).replace(",", "").strip() if penalty_match else "Not found",
        "Charges": Charges.group(1).replace(",", "").strip() if Charges else "Not found",
        "Rewards": 0,
        "Taxes and Fees": 0,
        "Unit Rate": 0,
        "Power Factor": 0
    }

    return bill_details