import os
import zipfile
import io
from flask import Flask, render_template, request, send_file, jsonify
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from services.vision_service import analyze_image
from services.tia_generator import generate_excel, generate_scl

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route('/')
def index():
    # Check if API KEY exists in env
    api_key_configured = bool(os.getenv('GEMINI_API_KEY'))
    return render_template('index.html', api_key_configured=api_key_configured)

@app.route('/process', methods=['POST'])
def process():
    if 'image' not in request.files:
        return jsonify({'error': 'No image part'}), 400
    
    file = request.files['image']
    
    # Get API key from request map OR environment
    api_key = request.form.get('api_key')
    if not api_key:
        api_key = os.getenv('GEMINI_API_KEY')
    
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
        
    if not api_key:
        return jsonify({'error': 'API Key is required'}), 400

    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    try:
        # 1. Analyze Image
        analysis_result = analyze_image(filepath, api_key)
        
        # 2. Generate Files
        excel_buffer = generate_excel(analysis_result['tags'])
        scl_buffer = generate_scl(analysis_result)
        
        # Get raw SCL text for preview
        scl_raw = scl_buffer.getvalue().decode('utf-8-sig', errors='ignore')

        # 3. Create ZIP
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            zip_file.writestr('PLC_Tags.xlsx', excel_buffer.getvalue())
            zip_file.writestr('Block.scl', scl_buffer.getvalue())
        
        zip_buffer.seek(0)
        
        import base64
        zip_base64 = base64.b64encode(zip_buffer.getvalue()).decode('utf-8')
        
        return jsonify({
            'success': True,
            'zip_base64': zip_base64,
            'scl_raw': scl_raw,
            'block_name': analysis_result.get('block_name', 'GeneratedBlock')
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500
    finally:
        if os.path.exists(filepath):
            os.remove(filepath)

if __name__ == '__main__':
    app.run(debug=True)
