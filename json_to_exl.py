import os
import shutil
import json
import re
import pandas as pd
from datetime import datetime

# Step 1: Gather all JSON files into a single folder
source_root = r'C:\Users\Computer Point\OneDrive\Desktop\Universal_extracter\extracted_jsons_20250610_173003'
destination_folder = 'all_jsons'
os.makedirs(destination_folder, exist_ok=True)

for root, dirs, files in os.walk(source_root):
    for file in files:
        if file.lower().endswith('.json'):
            source_file_path = os.path.join(root, file)
            destination_file_path = os.path.join(destination_folder, file)
            if not os.path.exists(destination_file_path):
                shutil.copy2(source_file_path, destination_file_path)
                print(f"✅ Moved: {source_file_path} → {destination_file_path}")
            else:
                print(f"⚠️ Skipped (already exists): {destination_file_path}")

# Step 2: Transform JSON files and store data
INPUT_FOLDER = destination_folder
OUTPUT_FOLDER = 'database_jsons'
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

excel_data = []  # List to hold all rows for Excel

def to_numeric(val):
    try:
        if val == "" or val is None:
            return 0
        if isinstance(val, (int, float)):
            return val
        if isinstance(val, str) and val.strip() == "":
            return 0
        return int(val.strip())
    except Exception:
        try:
            return float(val)
        except Exception:
            return 0

def to_double(val):
    try:
        if val == "" or val is None:
            return 0.0
        return float(val)
    except Exception:
        return 0.0

def to_str(val):
    if val is None:
        return ""
    return str(val)

def transform_json(data):
    key_map = {k.lower(): k for k in data.keys()}
    
    def get_value(preferred_keys):
        for key in preferred_keys:
            if key in data:
                return data[key]
            key_lower = key.lower()
            if key_lower in key_map:
                return data[key_map[key_lower]]
        return ""
    
    return {
        "consumer_number": to_numeric(get_value(["Consumer Number", "consumer number", "Consumer_Number", "consumer_number"])),
        "power_factor": to_double(get_value(["Power Factor", "power factor", "Power_Factor", "power_factor"])),
        "amount": to_double(get_value(["Total Amount Payable", "Total Payment Amount", "total amount payable", "total payment amount", "Amount", "amount"])),
        "power_kwh": to_str(get_value(["KWH Consumption", "KWH_Consumtion", "kwh consumption", "kwh_consumption", "KWH_Consumption"])),
        "rewards": to_double(get_value(["Rewards", "rewards", "Reward", "reward"])),
        "unit_rate": to_double(get_value(["Unit Rate", "unit rate", "Unit_Rate", "unit_rate"])),
        "taxes_and_fees": to_double(get_value(["Taxes and Fees", "taxes and fees", "Taxes_and_Fees", "taxes_and_fees"])),
        "penalty": to_double(get_value(["panelty", "Penalty", "penalty", "Panelty"])),
        "bill_number": to_str(get_value(["Bill Number", "bill number", "Bill_Number", "bill_number"])),
        "bill_date": to_str(get_value(["Bill Date", "bill date", "Bill_Date", "bill_date"])),
        "due_date": to_str(get_value(["Due Date", "due date", "Due_Date", "due_date"])),
        "sanctioned_load": to_double(get_value(["Sanction Load (KW)", "Sanction Load", "Sanction Load(kW)", "sanction load (kw)", "sanction load", "sanction load(kw)", "Sanctioned Load", "sanctioned load"]))
    }


for filename in os.listdir(INPUT_FOLDER):
    if not filename.endswith(".json"):
        continue
    input_path = os.path.join(INPUT_FOLDER, filename)
    try:
        with open(input_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"Skipping {filename}: Error reading JSON - {e}")
        continue


    transformed = transform_json(data)
    excel_data.append(transformed)  # Collect for Excel
    output_path = os.path.join(OUTPUT_FOLDER, filename)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(transformed, f, indent=4)
    print(f"Processed and saved: {output_path}")

# Step 3: Write all collected data to Excel
excel_output_path = "final_data.xlsx"
df = pd.DataFrame(excel_data)
df.to_excel(excel_output_path, index=False)
print(f"✅ All data written to Excel: {excel_output_path}")
