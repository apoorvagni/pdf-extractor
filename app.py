from flask import Flask, request, render_template, send_file, jsonify, flash
import os
import uuid
from werkzeug.utils import secure_filename
from pdf_processor import PDFProcessor
from file_manager import FileManager
import json
import atexit

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this'  # Change this in production
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf'}

# Initialize PDF processor and file manager
pdf_processor = PDFProcessor()
file_manager = FileManager(upload_folder=UPLOAD_FOLDER, max_file_age_hours=24, post_extraction_minutes=10)

# Clean up all files when app shuts down
atexit.register(file_manager.cleanup_all)

def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def generate_unique_filename(filename):
    """Generate a unique filename to avoid conflicts."""
    name, ext = os.path.splitext(filename)
    unique_name = f"{name}_{uuid.uuid4().hex}{ext}"
    return unique_name

@app.route('/')
def index():
    """Render the main page."""
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload and return file info."""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Only PDF files are allowed'}), 400
        
        # Save uploaded file
        original_filename = secure_filename(file.filename)
        unique_filename = generate_unique_filename(original_filename)
        file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
        file.save(file_path)
        
        # Validate PDF and get page count
        if not pdf_processor.validate_pdf(file_path):
            os.remove(file_path)  # Clean up invalid file
            return jsonify({'error': 'Invalid PDF file'}), 400
        
        page_count = pdf_processor.get_page_count(file_path)
        
        # Register file with file manager
        file_manager.register_file(unique_filename)
        
        return jsonify({
            'success': True,
            'filename': unique_filename,
            'original_filename': original_filename,
            'page_count': page_count,
            'message': f'PDF uploaded successfully. Total pages: {page_count}'
        })
        
    except Exception as e:
        return jsonify({'error': f'Upload failed: {str(e)}'}), 500

@app.route('/extract', methods=['POST'])
def extract_pages():
    """Extract specific pages from uploaded PDF."""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        filename = data.get('filename')
        start_page = data.get('start_page')
        end_page = data.get('end_page')
        
        if not all([filename, start_page, end_page]):
            return jsonify({'error': 'Missing required parameters'}), 400
        
        # Validate page numbers
        try:
            start_page = int(start_page)
            end_page = int(end_page)
        except ValueError:
            return jsonify({'error': 'Page numbers must be integers'}), 400
        
        if start_page < 1 or end_page < 1 or start_page > end_page:
            return jsonify({'error': 'Invalid page range'}), 400
        
        # Check if file exists
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        if not os.path.exists(file_path):
            return jsonify({'error': 'File not found'}), 404
        
        # Extract pages and return as downloadable file
        output_buffer = pdf_processor.extract_pages(file_path, start_page, end_page)
        
        # Generate output filename
        base_name = os.path.splitext(filename)[0]
        output_filename = f"{base_name}_pages_{start_page}-{end_page}.pdf"
        
        # Mark file as extracted (will be cleaned up after 10 minutes)
        file_manager.mark_extracted(filename)
        
        return send_file(
            output_buffer,
            as_attachment=True,
            download_name=output_filename,
            mimetype='application/pdf'
        )
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'Extraction failed: {str(e)}'}), 500

@app.route('/cleanup', methods=['POST'])
def cleanup_file():
    """Clean up uploaded file."""
    try:
        data = request.get_json()
        filename = data.get('filename')
        
        if not filename:
            return jsonify({'error': 'No filename provided'}), 400
        
        if file_manager.cleanup_file(filename):
            return jsonify({'success': True, 'message': 'File cleaned up successfully'})
        else:
            return jsonify({'error': 'File not found or cleanup failed'}), 404
            
    except Exception as e:
        return jsonify({'error': f'Cleanup failed: {str(e)}'}), 500

@app.route('/stats', methods=['GET'])
def get_stats():
    """Get file management statistics."""
    try:
        stats = file_manager.get_file_stats()
        return jsonify({
            'success': True,
            'stats': stats
        })
    except Exception as e:
        return jsonify({'error': f'Failed to get stats: {str(e)}'}), 500

@app.errorhandler(413)
def too_large(e):
    """Handle file too large error."""
    return jsonify({'error': 'File too large. Maximum size is 16MB.'}), 413

@app.errorhandler(500)
def internal_error(e):
    """Handle internal server errors."""
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 