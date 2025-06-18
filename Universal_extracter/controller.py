# from main import extract_bill

# url = "https://buildintsnaps.s3.ap-south-1.amazonaws.com/09801313471_23-04-2025.pdf"
# board = "Madhya Gujarat Vij Company Limited (MGVCL)" 

# json_data = extract_bill(url, board)
# print(json_data)
# import pandas as pd
# from main import extract_bill

# def process_bills(input_excel_path, output_excel_path):
#     df = pd.read_excel(input_excel_path)
#     results = []

#     for idx, row in df.iterrows():
#         board = row['board_name'].strip()
#         pdf_url = row['pdf_url']
#         print(f"Processing {idx+1}/{len(df)}: Board={board}, URL={pdf_url}")

#         try:
#             data = extract_bill(pdf_url, board)
#             data['board_name'] = board
#             data['pdf_url'] = pdf_url
#             results.append(data)
#         except Exception as e:
#             print(f"Error processing row {idx+1}: {e}")
#             results.append({
#                 'board_name': board,
#                 'pdf_url': pdf_url,
#                 'error': str(e)
#             })

#     output_df = pd.DataFrame(results)
#     output_df.to_excel(output_excel_path, index=False)
#     print(f"Results saved to {output_excel_path}")

# if __name__ == "__main__":
#     input_file = r"C:\Users\Computer Point\OneDrive\Desktop\Universal_extracter\Data.xlsx"  # Your input Excel file path
#     output_file = "extracted_bills.xlsx"  # Desired output file path
#     process_bills(input_file, output_file)
import os
import json
import pandas as pd
from datetime import datetime
from main import extract_bill

def process_bills(input_excel_path, output_excel_path):
    df = pd.read_excel(input_excel_path)
    results = []

    # Create a dynamic folder for JSONs (e.g., "extracted_jsons_20250608_1530")
    folder_name = f"extracted_jsons_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    os.makedirs(folder_name, exist_ok=True)

    for idx, row in df.iterrows():
        board = row['board_name'].strip()
        pdf_url = row['pdf_url']
        print(f"Processing {idx+1}/{len(df)}: Board={board}, URL={pdf_url}")

        try:
            data = extract_bill(pdf_url, board)
            data['board_name'] = board
            data['pdf_url'] = pdf_url
            results.append(data)

            # Save each JSON to the dynamic folder
            json_filename = f"{idx+1}_{board}.json"
            json_path = os.path.join(folder_name, json_filename)
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)

        except Exception as e:
            print(f"Error processing row {idx+1}: {e}")
            error_data = {
                'board_name': board,
                'pdf_url': pdf_url,
                'error': str(e)
            }
            results.append(error_data)

            # Save error JSON as well
            json_filename = f"{idx+1}_{board}_error.json"
            json_path = os.path.join(folder_name, json_filename)
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(error_data, f, ensure_ascii=False, indent=4)

    output_df = pd.DataFrame(results)
    output_df.to_excel(output_excel_path, index=False)
    print(f"Results saved to {output_excel_path}")
    print(f"All JSONs saved in folder: {folder_name}")

if __name__ == "__main__":
    input_file = r"C:\Users\Computer Point\OneDrive\Desktop\Universal_extracter\Data.xlsx"  # Your input Excel file path
    output_file = "extracted_bills.xlsx"  # Desired output file path
    process_bills(input_file, output_file)