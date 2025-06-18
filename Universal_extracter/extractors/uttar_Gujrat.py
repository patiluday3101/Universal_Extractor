import pytesseract
from pdf2image import convert_from_path
import re
import json

def pdf_to_images(pdf_path):
    """Convert PDF pages to images."""
    return convert_from_path(pdf_path, dpi=300)  # Higher DPI improves OCR accuracy

def ocr_image_to_text(image):
    """Extract text from an image using Tesseract OCR."""
    return pytesseract.image_to_string(image)

def extract_bill_details(text):
    """Parse text to extract bill details."""
    data = {
        "consumer_details": {},
        "billing_info": {},
        "consumption": {},
        "charges": {},
        "payment": {}
    }

    # Consumer Details
    data["consumer_details"]["name"] = re.search(r"ASHWAMEGH INFRA", text).group(0) if re.search(r"ASHWAMEGH INFRA", text) else ""
    data["consumer_details"]["address"] = re.search(r"SHOP NO-FF-.*?,(.*?),", text).group(1).strip() if re.search(r"SHOP NO-FF-.*?,(.*?),", text) else ""
    data["consumer_details"]["consumer_no"] = re.search(r"Consumer No: (\d+)", text).group(1) if re.search(r"Consumer No: (\d+)", text) else ""
    data["consumer_details"]["meter_no"] = re.search(r"Meter No: (.*?)\n", text).group(1).strip() if re.search(r"Meter No: (.*?)\n", text) else ""

    # Billing Info
    data["billing_info"]["bill_no"] = re.search(r"Bill No: (.*?)\n", text).group(1).strip() if re.search(r"Bill No: (.*?)\n", text) else ""
    data["billing_info"]["bill_date"] = re.search(r"Bill Date: (.*?)\n", text).group(1).strip() if re.search(r"Bill Date: (.*?)\n", text) else ""
    data["billing_info"]["due_date"] = re.search(r"Last Date For Payment: (.*?)\n", text).group(1).strip() if re.search(r"Last Date For Payment: (.*?)\n", text) else ""

    # Consumption
    prev_reading = re.search(r"Past\s*\|\s*(\d+)", text).group(1) if re.search(r"Past\s*\|\s*(\d+)", text) else ""
    curr_reading = re.search(r"Present\s*\|\s*(\d+)", text).group(1) if re.search(r"Present\s*\|\s*(\d+)", text) else ""
    data["consumption"]["units_used"] = str(int(curr_reading) - int(prev_reading)) if prev_reading and curr_reading else ""

    # Charges
    data["charges"]["fixed_charge"] = re.search(r"1\s*\|\s*Fixed Chg\s*\|\s*\|\s*(\d+)", text).group(1) if re.search(r"1\s*\|\s*Fixed Chg\s*\|\s*\|\s*(\d+)", text) else ""
    data["charges"]["energy_charge"] = re.search(r"2\s*\|\s*Energy Chg\s*\|\s*\|\s*(\d+)", text).group(1) if re.search(r"2\s*\|\s*Energy Chg\s*\|\s*\|\s*(\d+)", text) else ""
    data["charges"]["total_amount"] = re.search(r"Net Bill Amount.*?(\d+,\d+)", text).group(1).replace(",", "") if re.search(r"Net Bill Amount.*?(\d+,\d+)", text) else ""

    return data

def save_to_json(data, filename="bill_data.json"):
    """Save extracted data to JSON."""
    with open(filename, "w") as f:
        json.dump(data, f, indent=4)

# Main Execution
pdf_path = r"C:\Users\Computer Point\OneDrive\Desktop\Universal_extracter\20605121435_02-06-2025.pdf"  # Replace with your PDF path
images = pdf_to_images(pdf_path)
full_text = ""

for img in images:
    full_text += ocr_image_to_text(img)

bill_data = extract_bill_details(full_text)
save_to_json(bill_data)

print("✅ Data extracted and saved to bill_data.json")