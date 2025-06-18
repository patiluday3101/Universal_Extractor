import pdfplumber
import pytesseract
from PIL import Image
import os
import re

def extract(pdf_path):
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"{pdf_path} not found")

    data = {"File Name": os.path.basename(pdf_path)}
    full_text = ""

    # Extract text using OCR
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            img = page.to_image(resolution=300)
            pil_img = img.original.convert("L")
            text = pytesseract.image_to_string(pil_img)
            full_text += text + "\n"

    text = re.sub(r"\s+", " ", full_text)  # normalize whitespace

    # Main patterns
    patterns = {
        "Consumer Number": r"Consumer\s+No.*?(\d{10,})",
        "Due Date": r"Last Date For Payment[:\s]+(\d{2}-\d{2}-\d{4})",
        "Present Reading": r"Present Rdg\s+(\d+)",
        "Past Reading": r"Past Rdg\s+(\d+)",
        "Total Bill Amount": r"Tot Rs\.\s+([\d.]+)",
    }

    for key, pattern in patterns.items():
        match = re.search(pattern, text)
        data[key] = match.group(1).strip() if match else "0"


    # Calculate KWH
    try:
        present = int(data.get("Present Reading", "0"))
        past = int(data.get("Past Reading", "0"))
        data["KWH Consumption"] = str(present - past)
    except:
        data["KWH Consumption"] = "0"
    # Extract Bill Date
    bill_date_match = re.search(r"Bill\s*Date[:\s]*([0-9]{2}-[0-9]{2}-[0-9]{4})", text)
    data["Bill Date"] = bill_date_match.group(1) if bill_date_match else "0"

    # Extract Due Date
    due_date_match = re.search(r"Last\s*Date\s*For\s*Payment[:\s]*([0-9]{2}-[0-9]{2}-[0-9]{4})", text)
    data["Due Date"] = due_date_match.group(1) if due_date_match else "0"


    # Try extracting both dates from the line
    dates_match = re.search(
        r"Bill\s*Date[:\s]*Last\s*Date\s*For\s*Payment[:\s]*([0-9]{2}-[0-9]{2}-[0-9]{4})\s+([0-9]{2}-[0-9]{2}-[0-9]{4})",
        text
    )
    if dates_match:
        data["Bill Date"] = dates_match.group(1)
        data["Due Date"] = dates_match.group(2)
    else:
        # fallback to generic search for first two dates
        all_dates = re.findall(r"\d{2}-\d{2}-\d{4}", text)
        data["Bill Date"] = all_dates[0] if len(all_dates) > 0 else "0"
        data["Due Date"] = all_dates[1] if len(all_dates) > 1 else "0"


    # Unit Rate = Energy Charge / Billed Units
    energy_match = re.search(r"Energy Chg\s+([\d.]+)", text)
    try:
        billed_units = int(data.get("Billed Units", "0"))
        energy_charge = float(energy_match.group(1)) if energy_match else 0
        data["Unit Rate"] = f"{energy_charge / billed_units:.2f}" if billed_units > 0 else "0"
    except:
        data["Unit Rate"] = "0"

    # Taxes and Fees (Ed Charge)
    ed_match = re.search(r"Ed Chg @ .*?\s+([\d.]+)", text)
    data["Taxes and Fees"] = ed_match.group(1) if ed_match else "0"

    # Penalty (DPC)
    dpc_match = re.search(r"DPC\s+([\d.]+)", text)
    data["Penalty"] = dpc_match.group(1) if dpc_match else "0"

    # Reward (UJALA)
    reward_match = re.search(r"UJALA\s+([\d.]+)", text)
    data["Reward"] = reward_match.group(1) if reward_match else "0"
    Power_Factor = re.search(r"Power\s+Factor\s+([\d.]+)", text)
    data["Power Factor"] = Power_Factor.group(1) if Power_Factor else "0"
    data["Reward"] = reward_match.group(1) if reward_match else "0"

    # Bill Number: After 'Root Code Bill No', second code is the actual bill number
    # bill_no_match = re.search(
    #     r"Root\s*Code\s*Bill\s*No\s*[\n\s]*([0-9/]+)", text, re.IGNORECASE
    # )
    # data["Bill Number"] = bill_no_match.group(1) if bill_no_match else "0"

    # Sanction Load: It appears after 'Tariff Meter Code Load CD'
    sanction_load_match = re.search(r"Tariff\s+Meter\s+Code\s+[A-Z]+\s+([0-9.]+)", text)
    data["Sanction Load"] = sanction_load_match.group(1) if sanction_load_match else "0"

    return data

