import os
import json
import datetime
import shutil
from flask import Flask, request, render_template, send_from_directory, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
from process_pdf import process_pdf_files
from pdf_color_analyzer import extract_unique_colors
import uuid
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Database Configuration
db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'project.db')
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"
db = SQLAlchemy(app)

with app.app_context():
    db.create_all()

class UploadHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    upload_id = db.Column(db.String(36), unique=True, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.now)
    original_pdf = db.Column(db.String(255))
    json_mapping = db.Column(db.String(255))
    cmyk_pdf = db.Column(db.String(255))
    final_pdf = db.Column(db.String(255))

    def to_dict(self):
        return {
            "upload_id": self.upload_id,
            "timestamp": self.timestamp.strftime('%Y-%m-%d %H:%M:%S') if self.timestamp else None,
            "original_pdf": self.original_pdf,
            "json_mapping": self.json_mapping, # Stored as filename
            "cmyk_pdf": self.cmyk_pdf, # Stored as filename
            "final_pdf": self.final_pdf # Stored as filename
        }

def _get_history_data():
    """Helper function to get history data as a list of dicts from the database."""
    history_records = UploadHistory.query.order_by(UploadHistory.timestamp.desc()).all()
    return [record.to_dict() for record in history_records]

# Serve Vue.js static files
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_vue_app(path):
    if path != "" and os.path.exists(app.static_folder + '/' + path):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')

# Set the static folder to the Vue.js build output
app.static_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'vue-app', 'dist'))

@app.route('/process', methods=['POST'])
def process_files():
    """API endpoint for processing PDF files with AJAX"""
    try:
        if 'pdf_file' not in request.files or 'json_file' not in request.files:
            return jsonify({"success": False, "message": "请选择PDF文件和JSON文件"})

        pdf_file = request.files['pdf_file']
        json_file = request.files['json_file']

        if pdf_file.filename == '' or json_file.filename == '':
            return jsonify({"success": False, "message": "请选择PDF文件和JSON文件"})

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

            convert_text_to_curves = request.form.get('convert_text', 'false').lower() == 'true'
            processing_result = process_pdf_files(pdf_path, json_path, upload_dir, convert_text_to_curves=convert_text_to_curves)

            if processing_result["success"]:
                cmyk_pdf_filename = os.path.basename(processing_result["output_cmyk_pdf"]) if processing_result.get("output_cmyk_pdf") else None
                final_pdf_filename = os.path.basename(processing_result["output_final_pdf"]) if processing_result.get("output_final_pdf") else None
                
                # Save to database
                new_history_entry = UploadHistory(
                    upload_id=upload_id,
                    original_pdf=pdf_filename,
                    json_mapping=json_filename,
                    cmyk_pdf=cmyk_pdf_filename,
                    final_pdf=final_pdf_filename
                )
                db.session.add(new_history_entry)
                db.session.commit()

                # Get updated history
                updated_history = _get_history_data()

                return jsonify({
                    "success": True,
                    "message": processing_result["message"],
                    "upload_id": upload_id,
                    "cmyk_pdf_filename": cmyk_pdf_filename,
                    "final_pdf_filename": final_pdf_filename,
                    "history": updated_history  # Return updated history
                })
            else:
                return jsonify({
                    "success": False,
                    "message": processing_result["message"]
                })
    
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"服务器错误: {str(e)}"
        })

@app.route('/download/<upload_id>/<filename>')
def download_file(upload_id, filename):
    """Download endpoint for processed files"""
    return send_from_directory(os.path.join(app.config['UPLOAD_FOLDER'], upload_id), filename, as_attachment=True)

@app.route('/api/color-mapping', methods=['GET'])
def get_color_mapping():
    """获取默认颜色映射"""
    try:
        # Try to open the default mapping first
        with open('default_color_mapping.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        return jsonify(data)
    except FileNotFoundError:
        # If it doesn't exist, try to load the initial one
        try:
            with open('initial_default_color_mapping.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
            return jsonify(data)
        except Exception as e:
            print(f"FATAL: Could not read initial_default_color_mapping.json. {e}")
            return jsonify({"error": str(e)}), 500
    except Exception as e:
        # For other errors like JSON decoding
        print(f"Error reading default_color_mapping.json. {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/color-mapping', methods=['POST'])
def save_color_mapping():
    """保存颜色映射到默认文件"""
    try:
        data = request.get_json()
        with open('default_color_mapping.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return jsonify({"success": True, "message": "颜色映射已保存"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/original-color-mapping', methods=['GET'])
def get_original_color_mapping():
    """获取原始默认颜色映射"""
    try:
        with open('initial_default_color_mapping.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/analyze-colors', methods=['POST'])
def analyze_colors_endpoint():
    """Analyzes the dominant colors in an uploaded PDF file."""
    if 'pdf_file' not in request.files:
        return jsonify({"success": False, "message": "No PDF file provided."}), 400

    pdf_file = request.files['pdf_file']
    if pdf_file.filename == '':
        return jsonify({"success": False, "message": "No selected file."}), 400

    if pdf_file:
        upload_id = str(uuid.uuid4())
        upload_dir = os.path.join(app.config['UPLOAD_FOLDER'], upload_id)
        os.makedirs(upload_dir, exist_ok=True)

        pdf_filename = secure_filename(pdf_file.filename)
        pdf_path = os.path.join(upload_dir, pdf_filename)
        pdf_file.save(pdf_path)

        try:
            # Perform the color analysis
            unique_colors = extract_unique_colors(pdf_path)
            
            # The temporary file and directory will be cleaned up later by other processes
            # or a dedicated cleanup service. For now, we leave it.

            return jsonify({
                "success": True,
                "colors": unique_colors
            })
        except Exception as e:
            # Log the exception for debugging
            print(f"[ERROR] in color analysis for {pdf_path}: {e}")
            return jsonify({
                "success": False,
                "message": f"An error occurred during color analysis: {str(e)}"
            }), 500
    
    return jsonify({"success": False, "message": "Invalid file."}), 400

@app.route('/api/upload-pdf', methods=['POST'])
def upload_pdf():
    """上传PDF文件"""
    try:
        if 'pdf_file' not in request.files:
            return jsonify({"success": False, "message": "请选择PDF文件"})

        pdf_file = request.files['pdf_file']
        if pdf_file.filename == '':
            return jsonify({"success": False, "message": "请选择PDF文件"})

        upload_id = str(uuid.uuid4())
        upload_dir = os.path.join(app.config['UPLOAD_FOLDER'], upload_id)
        os.makedirs(upload_dir, exist_ok=True)

        pdf_filename = secure_filename(pdf_file.filename)
        pdf_path = os.path.join(upload_dir, pdf_filename)
        pdf_file.save(pdf_path)

        return jsonify({
            "success": True,
            "upload_id": upload_id,
            "filename": pdf_filename,
            "file_path": pdf_path
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"上传失败: {str(e)}"
        })

@app.route('/api/history', methods=['GET'])
def get_history():
    """获取处理历史记录"""
    return jsonify(_get_history_data())

@app.route('/api/clear-history', methods=['POST'])
def clear_history():
    """清空所有上传和处理的历史记录"""
    uploads_dir = app.config['UPLOAD_FOLDER']
    try:
        # Clear file system uploads
        for item in os.listdir(uploads_dir):
            item_path = os.path.join(uploads_dir, item)
            if os.path.isdir(item_path):
                shutil.rmtree(item_path)
            elif os.path.isfile(item_path):
                os.remove(item_path)
        
        os.makedirs(uploads_dir, exist_ok=True)

        # Clear database history
        db.session.query(UploadHistory).delete()
        db.session.commit()

        return jsonify({"success": True, "message": "历史记录已清空"})
    except Exception as e:
        return jsonify({"success": False, "message": f"清空历史记录失败: {str(e)}"})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    port = int(os.environ.get("PORT", 5001))
    app.run(host='0.0.0.0', port=port)