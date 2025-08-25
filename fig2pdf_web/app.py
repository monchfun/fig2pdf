import os
from flask import Flask, request, render_template, send_from_directory
from werkzeug.utils import secure_filename
from process_pdf import process_pdf_files # Assuming this is still needed
import uuid

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024 # 100MB max upload size

# Ensure the upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # Check if the post request has the file part
        if 'pdf_file' not in request.files or 'json_file' not in request.files:
            return render_template('index.html', message='请选择PDF文件和JSON文件')

        pdf_file = request.files['pdf_file']
        json_file = request.files['json_file']

        # If user does not select file, browser also submits an empty part without filename
        if pdf_file.filename == '' or json_file.filename == '':
            return render_template('index.html', message='请选择PDF文件和JSON文件')

        if pdf_file and json_file:
            upload_id = str(uuid.uuid4())
            upload_dir = os.path.join(app.config['UPLOAD_FOLDER'], upload_id)
            os.makedirs(upload_dir, exist_ok=True)

            pdf_filename = secure_filename(pdf_file.filename)
            json_filename = secure_filename(json_file.filename)

            pdf_path = os.path.join(upload_dir, pdf_filename)
            json_path = os.path.join(upload_dir, json_filename)

            pdf_file.save(pdf_path)
            json_file.save(json_path)

            # Process the PDF files
            processing_result = process_pdf_files(pdf_path, json_path, upload_dir, convert_text_to_curves=True)

            if processing_result["success"]:
                result_message = "✅ 处理成功！\n\n" + processing_result['message']
                output_files = []
                if processing_result["output_cmyk_pdf"]:
                    output_files.append(os.path.basename(processing_result["output_cmyk_pdf"]))
                if processing_result["output_final_pdf"]:
                    output_files.append(os.path.basename(processing_result["output_final_pdf"]))
                
                return render_template('index.html', message=result_message, output_files=output_files, upload_id=upload_id)
            else:
                return render_template('index.html', message=f"❌ 处理失败！\n\n{processing_result['message']}")
    
    return render_template('index.html')

@app.route('/downloads/<upload_id>/<filename>')
def download_file(upload_id, filename):
    return send_from_directory(os.path.join(app.config['UPLOAD_FOLDER'], upload_id), filename, as_attachment=True)

if __name__ == '__main__':
    # Get the port from environment variable or use a default
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
