from flask import Flask, request, render_template_string, send_from_directory, redirect, url_for
import os
from datetime import datetime
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Configuration - uses /app/storage for persistent data
STORAGE_PATH = os.environ.get('STORAGE_PATH', '/app/storage')
UPLOAD_FOLDER = os.path.join(STORAGE_PATH, 'uploads')
DB_FILE = os.path.join(STORAGE_PATH, 'visits.txt')

# Create directories if they don't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(os.path.dirname(DB_FILE), exist_ok=True)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'txt'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def log_visit():
    """Log each visit with timestamp"""
    with open(DB_FILE, 'a') as f:
        f.write(f"{datetime.now().isoformat()}\n")

def get_visit_count():
    """Get total visit count"""
    try:
        with open(DB_FILE, 'r') as f:
            return len(f.readlines())
    except FileNotFoundError:
        return 0

def get_uploaded_files():
    """Get list of uploaded files"""
    try:
        return os.listdir(UPLOAD_FOLDER)
    except FileNotFoundError:
        return []

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Storage Test App</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 50px auto;
            padding: 20px;
            background: #f5f5f5;
        }
        .container {
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 { color: #333; }
        .info-box {
            background: #e3f2fd;
            padding: 15px;
            border-radius: 5px;
            margin: 20px 0;
            border-left: 4px solid #2196F3;
        }
        .success {
            background: #c8e6c9;
            border-left-color: #4CAF50;
        }
        .upload-section {
            margin: 30px 0;
            padding: 20px;
            border: 2px dashed #ccc;
            border-radius: 5px;
        }
        .file-list {
            margin: 20px 0;
        }
        .file-item {
            padding: 10px;
            margin: 5px 0;
            background: #f9f9f9;
            border-radius: 3px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        button, input[type="submit"] {
            background: #2196F3;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 14px;
        }
        button:hover, input[type="submit"]:hover {
            background: #1976D2;
        }
        input[type="file"] {
            margin: 10px 0;
        }
        .stats {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin: 20px 0;
        }
        .stat-box {
            padding: 20px;
            background: #f5f5f5;
            border-radius: 5px;
            text-align: center;
        }
        .stat-number {
            font-size: 36px;
            font-weight: bold;
            color: #2196F3;
        }
        .paths {
            font-family: monospace;
            font-size: 12px;
            color: #666;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🧪 Storage Persistence Test</h1>

        <div class="info-box">
            <strong>Test Instructions:</strong>
            <ol>
                <li>Upload some files</li>
                <li>Note the visit count</li>
                <li>Redeploy/update your app</li>
                <li>Check if files and visit count persist</li>
            </ol>
        </div>

        {% if message %}
        <div class="info-box success">
            {{ message }}
        </div>
        {% endif %}

        <div class="stats">
            <div class="stat-box">
                <div class="stat-number">{{ visit_count }}</div>
                <div>Total Visits</div>
            </div>
            <div class="stat-box">
                <div class="stat-number">{{ file_count }}</div>
                <div>Uploaded Files</div>
            </div>
        </div>

        <div class="upload-section">
            <h2>📤 Upload a File</h2>
            <form method="POST" enctype="multipart/form-data" action="/upload">
                <input type="file" name="file" required>
                <br>
                <input type="submit" value="Upload File">
            </form>
            <p style="color: #666; font-size: 12px;">
                Allowed: PNG, JPG, GIF, PDF, TXT
            </p>
        </div>

        <div class="file-list">
            <h2>📁 Uploaded Files ({{ file_count }})</h2>
            {% if files %}
                {% for file in files %}
                <div class="file-item">
                    <span>{{ file }}</span>
                    <a href="/download/{{ file }}">
                        <button>Download</button>
                    </a>
                </div>
                {% endfor %}
            {% else %}
                <p style="color: #999;">No files uploaded yet</p>
            {% endif %}
        </div>

        <div class="info-box" style="margin-top: 30px;">
            <strong>Storage Paths:</strong>
            <div class="paths">
                <div>STORAGE_PATH: {{ storage_path }}</div>
                <div>UPLOAD_FOLDER: {{ upload_folder }}</div>
                <div>DB_FILE: {{ db_file }}</div>
            </div>
        </div>
    </div>
</body>
</html>
'''

@app.route('/')
def index():
    log_visit()
    files = get_uploaded_files()
    return render_template_string(
        HTML_TEMPLATE,
        visit_count=get_visit_count(),
        file_count=len(files),
        files=files,
        storage_path=STORAGE_PATH,
        upload_folder=UPLOAD_FOLDER,
        db_file=DB_FILE,
        message=request.args.get('message')
    )

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(url_for('index', message='No file selected'))

    file = request.files['file']

    if file.filename == '':
        return redirect(url_for('index', message='No file selected'))

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        # Add timestamp to avoid overwrites
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{timestamp}_{filename}"
        file.save(os.path.join(UPLOAD_FOLDER, filename))
        return redirect(url_for('index', message=f'File {filename} uploaded successfully!'))

    return redirect(url_for('index', message='File type not allowed'))

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename, as_attachment=True)

@app.route('/health')
def health():
    return {'status': 'healthy', 'visits': get_visit_count(), 'files': len(get_uploaded_files())}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=False)
