# PDF Page Extractor

A web-based PDF page extraction tool that allows you to extract specific pages from PDF files through a modern drag-and-drop interface.

## Features

- **Drag & Drop Interface**: Simply drag and drop your PDF files or browse to select them
- **Page Range Selection**: Extract specific pages by specifying start and end page numbers
- **Modern UI**: Clean, responsive design with real-time feedback
- **File Validation**: Automatic PDF validation and page count detection
- **Direct Download**: Extracted pages are automatically downloaded as a new PDF
- **Error Handling**: Comprehensive error handling with user-friendly messages
- **Automatic Cleanup**: Files are automatically cleaned up after extraction or within 24 hours
- **Memory Management**: Prevents storage bloat with intelligent file management

## Installation

### Prerequisites

- Python 3.7 or higher
- pip (Python package installer)

### Setup

1. **Clone or download the project files**
   ```bash
   # If you have git
   git clone <repository-url>
   cd pdf-extractor
   
   # Or simply navigate to the project directory
   cd pdf-extractor
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   python app.py
   ```

4. **Open your browser**
   Navigate to `http://localhost:5000` to use the application

## Usage

### Step 1: Upload PDF
- Drag and drop a PDF file onto the upload area, or
- Click "Browse Files" to select a PDF from your device

### Step 2: Select Page Range
- After successful upload, you'll see the file information including total pages
- Enter the page range you want to extract:
  - **From**: Starting page number (e.g., 1)
  - **To**: Ending page number (e.g., 5)

### Step 3: Extract Pages
- Click "Extract Pages" to process your request
- The extracted PDF will automatically download to your default download folder

### Step 4: Extract More Pages (Optional)
- Want to extract different pages from the same PDF? Just change the page range and click "Extract Pages" again
- The same file remains available for 10 minutes, allowing multiple extractions without re-uploading

### Step 5: Start Over (Optional)
- Click "Upload New File" to process another PDF

## File Structure

```
pdf-extractor/
├── app.py              # Flask web application
├── pdf_processor.py    # PDF processing logic
├── file_manager.py     # File cleanup and management
├── requirements.txt    # Python dependencies
├── README.md          # This file
├── templates/
│   └── index.html     # Web interface
└── uploads/           # Temporary file storage
```

## File Management & Cleanup

The application includes an intelligent file management system that prevents storage bloat:

### Automatic Cleanup Strategies

1. **Post-Extraction Cleanup**: Files remain available for 10 minutes after extraction (allowing multiple extractions from the same PDF), then automatically cleaned up
2. **Age-Based Cleanup**: Unused files older than 24 hours are automatically removed
3. **Periodic Cleanup**: Background thread runs every 5 minutes to clean up old files
4. **Startup Cleanup**: Any leftover files from previous sessions are cleaned up on app startup
5. **Shutdown Cleanup**: All files are cleaned up when the application shuts down

### File Tracking

- Each uploaded file is registered with a timestamp
- Files are tracked throughout their lifecycle
- Statistics are available via the `/stats` endpoint

### User Experience Benefits

- ✅ **No Storage Bloat**: Files are cleaned up automatically
- ✅ **Multiple Extractions**: Extract different page ranges from the same PDF without re-uploading
- ✅ **Smart Cleanup**: Files remain available for 10 minutes after extraction, then auto-cleanup
- ✅ **Failsafe**: Even if cleanup fails, periodic cleanup catches orphaned files
- ✅ **Resource Efficient**: Background cleanup doesn't impact user experience
- ✅ **Configurable**: Easy to adjust cleanup intervals and file age limits

## API Endpoints

The application provides the following REST API endpoints:

- `GET /` - Main page
- `POST /upload` - Upload PDF file
- `POST /extract` - Extract pages and download
- `POST /cleanup` - Clean up uploaded files
- `GET /stats` - Get file management statistics

## Configuration

You can modify the following settings in `app.py`:

- `MAX_CONTENT_LENGTH`: Maximum file size (default: 16MB)
- `UPLOAD_FOLDER`: Directory for temporary files (default: 'uploads')
- `SECRET_KEY`: Change this for production use

## Troubleshooting

### Common Issues

1. **"Invalid PDF file" error**
   - Ensure your file is a valid PDF
   - Try with a different PDF file

2. **"File too large" error**
   - The file exceeds the 16MB limit
   - Try compressing the PDF or increase the limit in `app.py`

3. **"Page numbers cannot exceed total pages" error**
   - Check that your page range is within the document's page count

4. **Server won't start**
   - Ensure all dependencies are installed: `pip install -r requirements.txt`
   - Check that port 5000 is available

### Development

To run in development mode:
```bash
export FLASK_ENV=development
python app.py
```

## Security Notes

- Files are temporarily stored in the `uploads/` directory
- Consider implementing file cleanup for production use
- Change the secret key in `app.py` for production deployment
- The application runs on all interfaces (0.0.0.0) - restrict this for production

## Dependencies

- **Flask 2.3.3**: Web framework
- **PyPDF2 3.0.1**: PDF processing library
- **Werkzeug 2.3.7**: WSGI utilities

## License

This project is open source and available under the MIT License.

## Contributing

Feel free to submit issues and enhancement requests!

---

**Note**: This application is designed for local use. For production deployment, consider adding authentication, rate limiting, and other security measures. 