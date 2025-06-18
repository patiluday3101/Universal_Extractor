#main.py
import json
from utils.download_pdf import download_pdf
# from extractors import DGujrat,TPNODL,TPSODL,TPWODL,APEPDCL,TPCODL,West_bangal,Mahavitaran,TSSPDCL,TGNPDCL,Bescom,Jaipur,jharkhand
# from extractors import up,MESCOM,HESCOM,GESCOM,CHESCOM,North_bihar, South_bihar,Noida,KSEB,MP_Madhya,MP_Pachim,APCPDCL,APSPDCL,Madhya_Gujrat,Utter_hariyana
from extractors import TPNODL, TPSODL, TPWODL, TPCODL,Mahavitaran,DGujrat,Jaipur,Bescom,TSSPDCL,TGNPDCL,Uttar_hariyana,West_bangal,APEPDCL,APSPDCL,CHESCOM,MESCOM,TNEB,HESCOM,GESCOM, Madhya_Gujrat,jharkhand,Dakshin_Hariyana,South_bihar,North_bihar,Tata,up,kanpur,APCPDCL,Panjab,Noida,Goa,Jammu,Pondicherry,Adani,KSEB,Ajmer # Import only the necessary extractors

# Router dictionary
BOARD_FUNCTIONS = {
    "Dakshin Gujarat Vij Company Limited (DGVCL)": DGujrat.extract,
    "TP Northern Odisha Distribution Limited": TPNODL.extract,
    "TP Southern Odisha Distribution Limited": TPSODL.extract,
    "TP Western Odisha Distribution Limited": TPWODL.extract,
    "APEPDCL": APEPDCL.extract,
    "TP Central Odisha Distribution Ltd.": TPCODL.extract,
    "West Bengal Electricity": West_bangal.extract,
    "Maharashtra State Electricity Distbn Co Ltd": Mahavitaran.extract,
    "TSSPDCL": TSSPDCL.extract,
    "TGNPDCL": TGNPDCL.extract,
    "Bangalore Electricity Supply Co. Ltd (BESCOM)": Bescom.extract,
    "Jaipur Vidyut Vitran Nigam (JVVNL)": Jaipur.extract,
    "Tamil Nadu Electricity Board (TNEB)": TNEB.extract,
    "Jharkhand Bijli Vitran Nigam Limited (JBVNL)": jharkhand.extract,
    "Madhyanchal Vidyut Vitran Nigam Limited (MVVNL)(Postpaid and Smart Prepaid Meter Recharge)": up.extract,
    "Dakshinanchal Vidyut Vitran Nigam Limited (DVVNL)(Postpaid and Smart Prepaid Meter Recharge)": up.extract,
    "Purvanchal Vidyut Vitran Nigam Limited(PUVVNL)(Postpaid and Smart Prepaid Meter Recharge)": up.extract,
    "Paschimanchal Vidyut Vitran Nigam Limited (PVVNL)(Postpaid and Smart Prepaid Meter Recharge)": up.extract,
    "Kanpur Electricity Supply Company": kanpur.extract,
    "Mangalore Electricity Supply Co. Ltd (MESCOM) - RAPDR": MESCOM.extract,
    "Hubli Electricity Supply Company Ltd (HESCOM)": HESCOM.extract,
    "Gulbarga Electricity Supply Company Limited": GESCOM.extract,
    "Chamundeshwari Electricity Supply Corp Ltd (CESCOM)": CHESCOM.extract,
    "Dakshin Haryana Bijli Vitran Nigam (DHBVN)": Dakshin_Hariyana.extract,
    "North Bihar Power Distribution Company Ltd.": North_bihar.extract,
    "South Bihar Power Distribution Company Ltd.": South_bihar.extract,
    "Punjab State Power Corporation Ltd (PSPCL)": Panjab.extract,
    "Noida": Noida.extract,
    "Goa Electricity Department": Goa.extract,
    "Jammu and Kashmir Power Development Department": Jammu.extract,
    "Puducherry Electricity Department": Pondicherry.extract,
    "Adani Electricity Mumbai Limited": Adani.extract,
    "Kerala State Electricity Board Ltd. (KSEBL)": KSEB.extract,
    "Ajmer Vidyut Vitran Nigam Limited (AVVNL)": Ajmer.extract,
    ""
    # "MP_Madhya": MP_Madhya.extract,
    # "MP_Pachim": MP_Pachim.extract,
    "Andhra Pradesh Central Power Distribution Corporation Limited": APCPDCL.extract,
    "Tata Power - Mumbai": Tata.extract,
    "APSPDCL": APSPDCL.extract,
    "Madhya Gujarat Vij Company Limited (MGVCL)": Madhya_Gujrat.extract,
    "Uttar Haryana Bijli Vitran Nigam (UHBVN)": Uttar_hariyana.extract,
    
    
    
    
    
    
}

def extract_bill(pdf_url: str, board_name: str):
    try:
        pdf_path = download_pdf(pdf_url)
    except Exception as e:
        raise RuntimeError(f"Failed to download PDF: {e}")

    if board_name not in BOARD_FUNCTIONS:
        raise ValueError("Unsupported electricity board.")

    print("Received board_name:", board_name)
    print("Available boards:", list(BOARD_FUNCTIONS.keys()))

    extract_func = BOARD_FUNCTIONS[board_name]
    extracted_data = extract_func(pdf_path)

    with open("output.json", "w") as f:
        json.dump(extracted_data, f, indent=2)

    return extracted_data
