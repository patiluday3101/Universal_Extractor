from flask import Flask, render_template, request, jsonify, send_file
from flask_wtf import FlaskForm, CSRFProtect
from wtforms import SelectField, FileField
from io import BytesIO
import os
import tempfile
import uuid
import logging
import pandas as pd
import requests
from werkzeug.utils import secure_filename
from PyPDF2 import PdfReader

# Import custom extractors
from extractors import (
    TPNODL, TPSODL, TPWODL, TPCODL, Mahavitaran, DGujrat, Jaipur, Bescom, TSSPDCL,
    TGNPDCL, Uttar_hariyana, West_bangal, APEPDCL, APSPDCL, CHESCOM, MESCOM, TNEB,
    HESCOM, GESCOM, Madhya_Gujrat, jharkhand, Dakshin_Hariyana, South_bihar,
    North_bihar, Tata, up, kanpur, APCPDCL, Panjab, Noida, Goa, Jammu, Pondicherry,
    Adani, KSEB, Ajmer
)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'  # Replace with a secure key
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB limit
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# CSRF protection
csrf = CSRFProtect(app)

# Extractor mapping
extractor_map = {
    "Dakshin Gujarat Vij Company Limited (DGVCL)": DGujrat.extract,
    "TP Northern Odisha Distribution Limited": TPNODL.extract,
    "TP Southern Odisha Distribution Limited": TPSODL.extract,
    "TP Western Odisha Distribution Limited": TPWODL.extract,
    "TP Central Odisha Distribution Limited": TPCODL.extract,
    "Maharashtra State Electricity Board (MSEB)": Mahavitaran.extract,
    "Jaipur Vidyut Vitran Nigam Limited": Jaipur.extract,
    "Bangalore Electricity Supply Company": Bescom.extract,
    "Telangana State Southern Power Distribution Company Limited": TSSPDCL.extract,
    "Telangana State Northern Power Distribution Company Limited": TGNPDCL.extract,
    "Uttar Haryana Bijli Vitran Nigam": Uttar_hariyana.extract,
    "West Bengal State Electricity Distribution Company Limited": West_bangal.extract,
    "Andhra Pradesh Eastern Power Distribution Company Limited": APEPDCL.extract,
    "Andhra Pradesh Southern Power Distribution Company Limited": APSPDCL.extract,
    "Chamundeshwari Electricity Supply Company": CHESCOM.extract,
    "Mangalore Electricity Supply Company": MESCOM.extract,
    "Tamil Nadu Electricity Board (TNEB)": TNEB.extract,
    "Hubli Electricity Supply Company": HESCOM.extract,
    "Gulbarga Electricity Supply Company": GESCOM.extract,
    "Madhya Gujarat Vij Company Limited": Madhya_Gujrat.extract,
    "Jharkhand Bijli Vitran Nigam": jharkhand.extract,
    "Dakshin Haryana Bijli Vitran Nigam": Dakshin_Hariyana.extract,
    "South Bihar Power Distribution Company": South_bihar.extract,
    "North Bihar Power Distribution Company": North_bihar.extract,
    "Tata Power": Tata.extract,
    "Uttar Pradesh Power Corporation": up.extract,
    "Kanpur Electricity Supply Company": kanpur.extract,
    "Andhra Pradesh Central Power Distribution Corporation Limited": APCPDCL.extract,
    "Punjab State Power Corporation": Panjab.extract,
    "Noida Power Company": Noida.extract,
    "Goa Electricity Department": Goa.extract,
    "Jammu Power Distribution Corporation": Jammu.extract,
    "Pondicherry Electricity Department": Pondicherry.extract,
    "Adani Electricity Mumbai Limited": Adani.extract,
    "Kerala State Electricity Board": KSEB.extract,
    "Ajmer Vidyut Vitran Nigam Limited (AVVNL)": Ajmer.extract,
}

# Form classes
class SingleForm(FlaskForm):
    eb_board = SelectField('EB Board', choices=[(k, k) for k in extractor_map.keys()])
    pdf_file = FileField('PDF File')

class BatchForm(FlaskForm):
    excel_file = FileField('Excel File')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/single')
def single():
    form = SingleForm()
    return render_template('single.html', form=form, boards=list(extractor_map.keys()))

@app.route('/batch')
def batch():
    form = BatchForm()
    return render_template('batch.html', form=form)

@app.route('/extract', methods=['POST'])
@csrf.exempt  # Temporarily exempt for testing; enable in production
def extract_single():
    board = request.form.get('eb_board')
    file = request.files.get('pdf_file')

    if not board or board not in extractor_map:
        return jsonify({"error": "Invalid board selected"}), 400
    if not file or not file.filename.lower().endswith('.pdf'):
        return jsonify({"error": "Invalid PDF file"}), 400

    try:
        with BytesIO(file.read()) as f:
            PdfReader(f)
        file.seek(0)

        filename = f"{uuid.uuid4()}_{secure_filename(file.filename)}"
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
            file.save(temp_file.name)
            file_path = temp_file.name

        logger.info(f"Processing single file: board={board}, file={filename}")

        extractor_function = extractor_map[board]
        extracted_data = extractor_function(file_path)

        json_data = jsonify(extracted_data).get_data(as_text=True)
        os.unlink(file_path)

        return send_file(
            BytesIO(json_data.encode('utf-8')),
            mimetype='application/json',
            as_attachment=True,
            download_name='extracted_data.json'
        )

    except (ValueError, IOError) as e:
        logger.error(f"Invalid PDF file: {str(e)}")
        return jsonify({"error": f"Invalid PDF file: {str(e)}"}), 400
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return jsonify({"error": f"Extraction failed: {str(e)}"}), 500

@app.route('/batch_extract', methods=['POST'])
@csrf.exempt  # Temporarily exempt for testing; enable in production
def batch_extract():
    file = request.files.get('excel_file')

    if not file or not file.filename.lower().endswith(('.xlsx', '.xls', '.csv')):
        return jsonify({"error": "Invalid Excel file"}), 400

    try:
        # Read Excel file
        if file.filename.endswith('.csv'):
            df = pd.read_csv(file)
        else:
            df = pd.read_excel(file)

        if not {'EB Board Name', 'PDF URL'}.issubset(df.columns):
            return jsonify({"error": "Excel file must contain 'EB Board Name' and 'PDF URL' columns"}), 400

        results = []
        for index, row in df.iterrows():
            board = row['EB Board Name']
            pdf_url = row['PDF URL']

            if not board or board not in extractor_map:
                results.append({"index": index, "error": "Invalid board name"})
                continue
            if not pdf_url or not isinstance(pdf_url, str):
                results.append({"index": index, "error": "Invalid PDF URL"})
                continue

            try:
                # Download PDF
                response = requests.get(pdf_url, timeout=10)
                response.raise_for_status()

                with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
                    temp_file.write(response.content)
                    file_path = temp_file.name

                # Validate PDF
                with open(file_path, 'rb') as f:
                    PdfReader(f)

                logger.info(f"Processing batch file: board={board}, url={pdf_url}")

                # Extract data
                extractor_function = extractor_map[board]
                extracted_data = extractor_function(file_path)
                extracted_data['EB Board Name'] = board
                extracted_data['PDF URL'] = pdf_url
                results.append(extracted_data)

                os.unlink(file_path)

            except requests.RequestException as e:
                results.append({"index": index, "error": f"Failed to download PDF: {str(e)}"})
            except (ValueError, IOError) as e:
                results.append({"index": index, "error": f"Invalid PDF: {str(e)}"})
            except Exception as e:
                results.append({"index": index, "error": f"Extraction failed: {str(e)}"})

        # Create Excel output
        output_df = pd.DataFrame([r for r in results if 'error' not in r])
        excel_buffer = BytesIO()
        output_df.to_excel(excel_buffer, index=False)
        excel_buffer.seek(0)

        # Create JSON output
        json_data = jsonify(results).get_data(as_text=True)

        # Save files temporarily for download
        excel_path = os.path.join(UPLOAD_FOLDER, f"batch_results_{uuid.uuid4()}.xlsx")
        json_path = os.path.join(UPLOAD_FOLDER, f"batch_results_{uuid.uuid4()}.json")
        with open(excel_path, 'wb') as f:
            f.write(excel_buffer.getvalue())
        with open(json_path, 'w') as f:
            f.write(json_data)

        return jsonify({
            "excel_url": f"/download/{os.path.basename(excel_path)}",
            "json_url": f"/download/{os.path.basename(json_path)}",
            "json_data": results
        })

    except Exception as e:
        logger.error(f"Batch processing error: {str(e)}")
        return jsonify({"error": f"Batch processing failed: {str(e)}"}), 500

@app.route('/download/<filename>')
def download_file(filename):
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    if os.path.exists(file_path):
        response = send_file(file_path, as_attachment=True)
        os.unlink(file_path)  # Delete after sending
        return response
    return jsonify({"error": "File not found"}), 404

@app.route('/sample_template')
def sample_template():
    # Create sample Excel template
    data = {
        "EB Board Name": ["Tamil Nadu Electricity Board (TNEB)", "Bangalore Electricity Supply Company"],
        "PDF URL": ["https://example.com/pdf1.pdf", "https://example.com/pdf2.pdf"]
    }
    df = pd.DataFrame(data)
    buffer = BytesIO()
    df.to_excel(buffer, index=False)
    buffer.seek(0)
    return send_file(
        buffer,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name='sample_template.xlsx'
    )

if __name__ == '__main__':
    app.run(debug=False)