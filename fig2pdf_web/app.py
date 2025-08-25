import os
from flask import Flask, request, render_template, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename
import subprocess
import json
from process_pdf import process_pdf_files # Import the function
import uuid # Import uuid

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'pdf', 'json'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'pdf_file' not in request.files or 'json_file' not in request.files:
        return render_template('index.html', error="Please select both PDF and JSON files.")

    pdf_file = request.files['pdf_file']
    json_file = request.files['json_file']

    if pdf_file.filename == '' or json_file.filename == '':
        return render_template('index.html', error="Please select both PDF and JSON files.")

    if pdf_file and allowed_file(pdf_file.filename) and json_file and allowed_file(json_file.filename):
        pdf_filename = secure_filename(pdf_file.filename)
        json_filename = secure_filename(json_file.filename)

        # Create a unique subdirectory for each upload to avoid conflicts
        upload_id = str(uuid.uuid4())
        upload_dir = os.path.join(app.config['UPLOAD_FOLDER'], upload_id)
        os.makedirs(upload_dir, exist_ok=True)

        pdf_path = os.path.join(upload_dir, pdf_filename)
        json_path = os.path.join(upload_dir, json_filename)

        pdf_file.save(pdf_path)
        json_file.save(json_path)

        # Call the PDF processing function
        processing_result = process_pdf_files(pdf_path, json_path, upload_dir)

        if processing_result["success"]:
            return render_template(
                'result.html',
                message=processing_result["message"],
                output_cmyk_pdf=os.path.basename(processing_result["output_cmyk_pdf"]) if processing_result["output_cmyk_pdf"] else None,
                output_final_pdf=os.path.basename(processing_result["output_final_pdf"]) if processing_result["output_final_pdf"] else None,
                upload_id=upload_id
            )
        else:
            return render_template(
                'result.html',
                message=processing_result["message"],
                error=True,
                upload_id=upload_id # Still pass upload_id for potential debugging/cleanup
            )
    return render_template('index.html', error="Invalid file type. Only PDF and JSON are allowed.")

@app.route('/download/<upload_id>/<filename>')
def download_file(upload_id, filename):
    return send_from_directory(os.path.join(app.config['UPLOAD_FOLDER'], upload_id), filename, as_attachment=True)

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(debug=True)