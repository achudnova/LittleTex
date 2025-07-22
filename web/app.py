import os
import tempfile
import uuid
import zipfile
from pathlib import Path
from flask import (
    Flask, request, render_template, send_from_directory,
    url_for, flash, redirect, session
)
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

# Import your existing application components
from src.core.app import LittleTexApp
from src.pipeline.config import PipelineConfig

load_dotenv()

# Initialize the Flask app
app = Flask(__name__)

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'd08fb1b3ebd309b2563c17000923cdffba5f8275b8f661e55022df4b30bc28e0')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Set max upload size to 16MB

# Define the allowed file extensions
ALLOWED_EXTENSIONS = {'zip'}

def allowed_file(filename):
    """Check if the uploaded file has an allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    """Renders the main upload page."""
    return render_template('index.html')


@app.route('/convert', methods=['POST'])
def convert_file():
    """Handles the file upload and conversion logic."""
    # 1. Validate the file upload
    file = request.files.get('file')
    if not file or file.filename == '':
        flash('No file selected. Please choose a project .zip file.')
        return redirect(url_for('index'))

    if not allowed_file(file.filename):
        flash('Invalid file type. Please upload a .zip file.')
        return redirect(url_for('index'))

    # 2. Create a unique temporary directory for this conversion
    session_id = str(uuid.uuid4())
    session_dir = Path(tempfile.gettempdir()) / "littletex_web" / session_id
    session_dir.mkdir(parents=True, exist_ok=True)
    
    input_filename = secure_filename(file.filename)
    input_path = session_dir / input_filename
    file.save(input_path)
    
    try:
        with zipfile.ZipFile(input_path, 'r') as zip_ref:
            zip_ref.extractall(session_dir)
        
        md_files = list(session_dir.glob('**/*.md')) + list(session_dir.glob('**/*.markdown'))
        if not md_files:
            flash('No Markdown files found in the uploaded ZIP archive.')
        if len(md_files) > 1:
            flash(f"Warning: Multiple Markdown files found. Using the first one: {md_files[0].name}")
        
        input_path = md_files[0]
        
    except (zipfile.BadZipFile, ValueError) as e:
        flash(f'Error processing archive: {e}')
        return redirect(url_for('index'))

    # Store the original filename stem in the user's session for later use
    # session['filename_stem'] = input_path.stem

    # 3. Try to run the conversion pipeline
    try:
        output_path = session_dir / f"{input_path.stem}.tex"
        config = PipelineConfig(
            input_path=input_path,
            output_path=output_path,
            generate_pdf=True
        )
        littletex_app = LittleTexApp(config)
        final_pdf_path = littletex_app.run()
        
        if not final_pdf_path or not final_pdf_path.exists():
            flash('Conversion failed to produce a PDF file.')
            return redirect(url_for('index'))
        
        session['pdf_filename'] = final_pdf_path.name
        session['tex_filename'] = final_pdf_path.with_suffix('.tex').name
        
    except Exception as e:
        # If anything goes wrong in the pipeline, flash an error and redirect
        flash(f'An error occurred during conversion: {e}')
        return redirect(url_for('index'))

    # 4. If successful, redirect to the results page
    return redirect(url_for('results', session_id=session_id))


@app.route('/results/<session_id>')
def results(session_id):
    """Displays the download links after a successful conversion."""
    # Retrieve the filename stem we saved in the session
    # filename_stem = session.get('filename_stem', 'output')
    
    pdf_filename = session.get('pdf_filename', 'output.pdf')
    tex_filename = session.get('tex_filename', 'output.tex')
    
    # Generate the links for the results.html template
    tex_link = url_for('download_file', session_id=session_id, filename=tex_filename)
    pdf_link = url_for('download_file', session_id=session_id, filename=pdf_filename)
    
    return render_template('results.html', tex_link=tex_link, pdf_link=pdf_link)


@app.route('/downloads/<session_id>/<filename>')
def download_file(session_id: str, filename: str):
    """A dedicated route to safely serve the generated files for download."""
    directory = Path(tempfile.gettempdir()) / "littletex_web" / session_id
    return send_from_directory(directory, filename, as_attachment=True)