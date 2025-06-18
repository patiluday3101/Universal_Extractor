# PDF Data Extractor

This project is a PDF Data Extractor built using Flask. It allows users to upload PDF bills and extract relevant data based on the selected EB board.

## Project Structure

```
pdf-extractor-flask
├── app.py
├── requirements.txt
├── templates
│   ├── single.html
│   └── single_processing.html
├── static
│   └── style.css
└── README.md
```

## Files Description

- **app.py**: The main Flask application that sets up the server, defines routes for rendering HTML templates, and handles file uploads and processing.

- **requirements.txt**: Lists the dependencies required for the project, such as Flask and any other libraries needed for PDF processing.

- **templates/single.html**: Contains the HTML code for the PDF data extractor form, including a dropdown for selecting an EB board, a file input for uploading a PDF bill, and a submit button.

- **templates/single_processing.html**: Displays the results after processing the uploaded PDF, showing extracted data or a confirmation message.

- **static/style.css**: Contains the CSS styles for the HTML templates, ensuring a visually appealing layout.

## Setup Instructions

1. **Clone the Repository**: 
   ```bash
   git clone <repository-url>
   cd pdf-extractor-flask
   ```

2. **Install Dependencies**: 
   Make sure you have Python and pip installed. Then run:
   ```bash
   pip install -r requirements.txt
   ```

3. **Create Uploads Directory**: 
   Ensure that the `uploads` directory exists in the project root to store uploaded PDF files. The application will create it automatically if it doesn't exist.

4. **Run the Application**: 
   Start the Flask server by running:
   ```bash
   python app.py
   ```

5. **Access the Application**: 
   Open your web browser and go to `http://127.0.0.1:5000/` to access the PDF Data Extractor.

## Usage

- Select the desired EB board from the dropdown menu.
- Upload your PDF bill using the file input.
- Click the "EXTRACT DATA" button to submit the form.
- The application will process the PDF and display the results on the next page.

## Note

Make sure to adjust the PDF processing logic in the `process` function of `app.py` as needed for your specific requirements.