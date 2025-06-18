from flask import Flask, render_template, request, redirect, url_for
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Limit upload size to 16 MB

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

@app.route('/')
def index():
    return render_template('single.html')

@app.route('/process', methods=['POST'])
def process():
    eb_board = request.form['ebBoard']
    pdf_file = request.files['pdfFile']

    if pdf_file and pdf_file.filename.endswith('.pdf'):
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], pdf_file.filename)
        pdf_file.save(file_path)
        
        # Here you would add your PDF processing logic
        # For example, extracting data from the PDF

        return render_template('single_processing.html', eb_board=eb_board, filename=pdf_file.filename)
    else:
        return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)