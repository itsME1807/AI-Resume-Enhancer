import os
import logging
from flask import render_template, request, flash, redirect, url_for, jsonify, send_file
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
from app import app
from gemini_service import GeminiResumeAnalyzer
from pdf_parser import PDFParser
import tempfile
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.units import inch

# Initialize services
gemini_analyzer = GeminiResumeAnalyzer()
pdf_parser = PDFParser()

ALLOWED_EXTENSIONS = {'pdf', 'txt'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze_resume():
    try:
        # Get form data
        job_role = request.form.get('job_role', '').strip()
        job_description = request.form.get('job_description', '').strip()
        resume_text = request.form.get('resume_text', '').strip()
        
        # Validate required fields
        if not job_role:
            flash('Please provide a target job role.', 'error')
            return redirect(url_for('index'))
        
        # Get resume content
        resume_content = ""
        
        # Check if file was uploaded
        if 'resume_file' in request.files:
            file = request.files['resume_file']
            if file and file.filename and allowed_file(file.filename):
                try:
                    filename = secure_filename(file.filename)
                    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    file.save(filepath)
                    
                    # Parse PDF or text file
                    if filename.lower().endswith('.pdf'):
                        resume_content = pdf_parser.extract_text_from_pdf(filepath)
                    else:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            resume_content = f.read()
                    
                    # Clean up uploaded file
                    os.remove(filepath)
                    
                except Exception as e:
                    logging.error(f"Error processing uploaded file: {e}")
                    flash('Error processing uploaded file. Please try again.', 'error')
                    return redirect(url_for('index'))
        
        # Use text input if no file uploaded or file processing failed
        if not resume_content and resume_text:
            resume_content = resume_text
        
        if not resume_content:
            flash('Please provide a resume either by uploading a file or pasting the text.', 'error')
            return redirect(url_for('index'))
        
        # Analyze resume with Gemini
        try:
            analysis = gemini_analyzer.analyze_resume(resume_content, job_role, job_description)
            
            return render_template('results.html', 
                                 analysis=analysis,
                                 job_role=job_role,
                                 original_resume=resume_content)
                                 
        except Exception as e:
            logging.error(f"Error analyzing resume with Gemini: {e}")
            flash('Error analyzing resume. Please check your API configuration and try again.', 'error')
            return redirect(url_for('index'))
    
    except Exception as e:
        logging.error(f"Unexpected error in analyze_resume: {e}")
        flash('An unexpected error occurred. Please try again.', 'error')
        return redirect(url_for('index'))

@app.route('/download_improved_resume', methods=['POST'])
def download_improved_resume():
    try:
        improved_resume = request.form.get('improved_resume', '')
        job_role = request.form.get('job_role', 'Professional')
        
        if not improved_resume:
            flash('No improved resume content available for download.', 'error')
            return redirect(url_for('index'))
        
        # Create PDF
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter,
                              rightMargin=72, leftMargin=72,
                              topMargin=72, bottomMargin=18)
        
        # Styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            spaceAfter=30,
            alignment=1  # Center alignment
        )
        
        # Build PDF content
        story = []
        story.append(Paragraph(f"Improved Resume - {job_role}", title_style))
        story.append(Spacer(1, 12))
        
        # Split improved resume into paragraphs and add to PDF
        paragraphs = improved_resume.split('\n\n')
        for para in paragraphs:
            if para.strip():
                story.append(Paragraph(para.strip(), styles['Normal']))
                story.append(Spacer(1, 12))
        
        doc.build(story)
        buffer.seek(0)
        
        return send_file(
            io.BytesIO(buffer.getvalue()),
            as_attachment=True,
            download_name=f'improved_resume_{job_role.replace(" ", "_").lower()}.pdf',
            mimetype='application/pdf'
        )
        
    except Exception as e:
        logging.error(f"Error generating PDF: {e}")
        flash('Error generating PDF. Please try again.', 'error')
        return redirect(url_for('index'))

@app.errorhandler(413)
def too_large(e):
    flash('File too large. Please upload a file smaller than 16MB.', 'error')
    return redirect(url_for('index'))

@app.errorhandler(404)
def not_found(e):
    return render_template('index.html'), 404

@app.errorhandler(500)
def internal_error(e):
    logging.error(f"Internal server error: {e}")
    flash('An internal error occurred. Please try again.', 'error')
    return redirect(url_for('index'))
