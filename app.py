import os
import secrets
from pathlib import Path
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from werkzeug.utils import secure_filename
from werkzeug.security import check_password_hash, generate_password_hash
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', secrets.token_hex(32))

# Configuration
UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', '/paperless-consume')
ALLOWED_EXTENSIONS = set(os.getenv('ALLOWED_EXTENSIONS', 'pdf,png,jpg,jpeg,gif,tiff,txt,doc,docx').split(','))
MAX_FILE_SIZE = int(os.getenv('MAX_FILE_SIZE', 50 * 1024 * 1024))  # Default 50MB

# Handle PASSWORD_HASH - convert $$ to $ if needed (Docker Compose escaping)
password_hash_env = os.getenv('PASSWORD_HASH', generate_password_hash('changeme'))
PASSWORD_HASH = password_hash_env.replace('$$', '$') if '$$' in password_hash_env else password_hash_env

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# Rate limiting configuration
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def login_required(f):
    """Decorator to require login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/login', methods=['GET', 'POST'])
@limiter.limit("10 per minute")
def login():
    """Login page with rate limiting"""
    if request.method == 'POST':
        password = request.form.get('password', '')

        if check_password_hash(PASSWORD_HASH, password):
            session['logged_in'] = True
            flash('Successfully logged in!', 'success')
            return redirect(url_for('upload_file'))
        else:
            flash('Invalid password. Please try again.', 'error')

    return render_template('login.html')

@app.route('/logout')
def logout():
    """Logout endpoint"""
    session.pop('logged_in', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/', methods=['GET', 'POST'])
@login_required
@limiter.limit("20 per minute")
def upload_file():
    """Main upload page"""
    if request.method == 'POST':
        # Check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part in the request', 'error')
            return redirect(request.url)

        files = request.files.getlist('file')

        if not files or files[0].filename == '':
            flash('No file selected', 'error')
            return redirect(request.url)

        uploaded_files = []
        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)

                # Create upload folder if it doesn't exist
                Path(app.config['UPLOAD_FOLDER']).mkdir(parents=True, exist_ok=True)

                # Save the file
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                uploaded_files.append(filename)
            else:
                flash(f'File {file.filename} has an invalid extension', 'warning')

        if uploaded_files:
            flash(f'Successfully uploaded {len(uploaded_files)} file(s): {", ".join(uploaded_files)}', 'success')

        return redirect(url_for('upload_file'))

    return render_template('upload.html', allowed_extensions=ALLOWED_EXTENSIONS)

@app.route('/health')
def health():
    """Health check endpoint"""
    return {'status': 'healthy'}, 200

if __name__ == '__main__':
    # Only for development
    app.run(host='0.0.0.0', port=5000, debug=False)
