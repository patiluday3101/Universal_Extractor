from flask import Flask, render_template, request, send_file, flash, redirect, url_for
import os
from werkzeug.utils import secure_filename
import uuid
import json

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Needed for flashing messages

# Configuration
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['RESULT_FOLDER'] = 'results'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['RESULT_FOLDER'], exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/single')
def single():
    return render_template('single.html')

@app.route('/extract-single', methods=['POST'])
def extract_single():
    eb_board = request.form.get('ebBoard')
    pdf = request.files.get('pdfFile')

    if not eb_board or not pdf or pdf.filename == '':
        flash('Please provide all required fields and a PDF file.')
        return redirect(url_for('single'))

    filename = secure_filename(pdf.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    pdf.save(file_path)

    # Dummy extracted data (replace with actual extraction logic)
    extracted_data = {
        "EB Board": eb_board,
        "Filename": filename,
        "Consumer Number": "1234567890",
        "Bill Date": "2025-06-02",
        "Due Date": "2025-06-12",
        "Amount": "₹560"
    }

    output_filename = f"{uuid.uuid4()}.json"
    output_path = os.path.join(app.config['RESULT_FOLDER'], output_filename)

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(extracted_data, f, indent=4, ensure_ascii=False)

    return send_file(output_path, as_attachment=True, download_name=output_filename)