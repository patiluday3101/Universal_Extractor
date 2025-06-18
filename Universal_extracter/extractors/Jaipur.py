import pymupdf  # PyMuPDF
import json
import re
import os
import csv

def extract(pdf_path):
    """Extracts details from a single bill PDF."""
    try:
        doc = pymupdf.Document(pdf_path)
        text = "\n".join([page.get_text("text") for page in doc])
        if not text.strip():
            print(f"Warning: No text extracted from {pdf_path}")
            return None

        details = {
            "File Name": os.path.basename(pdf_path),
            "Consumer Number": extract_value(text, r"ds-ua\s*:\s*(\d+)") or "N/A",
            "Bill Number": extract_value(text, r"fcy ua\s*:\s*(\d+)") or "N/A",
            "KWH Consumption": extract_value(text, r"TOD \(12PM to 4PM\)\s+0.0\s+\(KWH\)\s+(\d+\.\d+)") or "N/A",
            "Sanction Load": extract_value(text, r"dusDVsM yksM\D+(\d+\.\d+) \(KW\)") or "N/A",
            "Bill Date": extract_value(text, r"fcy tkjh djus dh frfFk\s*:\s*(\d{2}-\d{2}-\d{4})") or "N/A",
            "Due Date": extract_value(text, r"fu;r Hkqxrku frfFk\s*:\s*(\d{2}-\d{2}-\d{4})") or "N/A",
            # New fields for payment amounts
            "Amount Before Due Date": extract_amount_before_due_date(text) or "N/A",
            "Amount After Due Date": extract_amount_after_due_date(text) or "N/A",
            "Late Payment Surcharge": extract_late_payment_surcharge(text) or "N/A",
            "Current Bill Amount": extract_current_bill_amount(text) or "N/A",
            "Previous Outstanding": extract_previous_outstanding(text) or "N/A",
            "Power Factor": 0,
            "Taxes and Fees": 0,
            "Rewards": 0,
            "Unit Rate": 0
        }

        return details
    except Exception as e:
        print(f"Error processing {pdf_path}: {e}")
        return None

def extract_value(text, pattern):
    """Extracts the first matching value using regex."""
    match = re.search(pattern, text)
    return match.group(1) if match else None

def extract_amount_before_due_date(text):
    """Extracts the amount due before the due date."""
    # Look for the pattern in the payment summary table
    # The format is: previous_amount current_amount total_before_due late_charge total_after_due
    pattern = r"(\d+\.\d+)\s+(\d+\.\d+)\s+(\d+)\s+(\d+\.\d+)\s+(\d+)"
    match = re.search(pattern, text)
    if match:
        return match.group(3)  # Third number is the amount before due date
    return None

def extract_amount_after_due_date(text):
    """Extracts the amount due after the due date."""
    # Look for the pattern in the payment summary table
    # The format is: previous_amount current_amount total_before_due late_charge total_after_due
    pattern = r"(\d+\.\d+)\s+(\d+\.\d+)\s+(\d+)\s+(\d+\.\d+)\s+(\d+)"
    match = re.search(pattern, text)
    if match:
        return match.group(5)  # Fifth number is the amount after due date
    return None

def extract_late_payment_surcharge(text):
    """Extracts the late payment surcharge amount."""
    # Look for the surcharge in the payment summary table
    # The format is: previous_amount current_amount total_before_due late_charge total_after_due
    pattern = r"(\d+\.\d+)\s+(\d+\.\d+)\s+(\d+)\s+(\d+\.\d+)\s+(\d+)"
    match = re.search(pattern, text)
    if match:
        return match.group(4)  # Fourth number is the late payment surcharge
    return None

def extract_current_bill_amount(text):
    """Extracts the current bill amount."""
    # Look for the current bill amount in the payment summary table
    # The format is: previous_amount current_amount total_before_due late_charge total_after_due
    pattern = r"(\d+\.\d+)\s+(\d+\.\d+)\s+(\d+)\s+(\d+\.\d+)\s+(\d+)"
    match = re.search(pattern, text)
    if match:
        return match.group(2)  # Second number is the current bill amount
    return None

def extract_previous_outstanding(text):
    """Extracts the previous outstanding amount."""
    # Look for the previous outstanding in the payment summary table
    # The format is: previous_amount current_amount total_before_due late_charge total_after_due
    pattern = r"(\d+\.\d+)\s+(\d+\.\d+)\s+(\d+)\s+(\d+\.\d+)\s+(\d+)"
    match = re.search(pattern, text)
    if match:
        return match.group(1)  # First number is the previous outstanding
    return None

