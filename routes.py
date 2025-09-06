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

def is_section_header(line):
    """Determine if a line is a section header"""
    section_keywords = [
        'experience', 'education', 'skills', 'summary', 'objective',
        'projects', 'certifications', 'achievements', 'awards',
        'publications', 'languages', 'interests', 'references',
        'professional experience', 'work experience', 'employment history',
        'technical skills', 'core competencies', 'qualifications'
    ]
    
    line_lower = line.lower().strip()
    
    # Check if line contains section keywords and is relatively short
    if len(line.split()) <= 4:
        for keyword in section_keywords:
            if keyword in line_lower:
                return True
    
    # Check if line is all caps (common for section headers)
    if line.isupper() and len(line.split()) <= 3:
        return True
        
    return False

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
        
        # Create custom styles for resume formatting
        styles = getSampleStyleSheet()
        
        # Define custom styles
        name_style = ParagraphStyle(
            'NameStyle',
            parent=styles['Heading1'],
            fontSize=18,
            spaceAfter=12,
            alignment=1,  # Center alignment
        )
        
        section_header_style = ParagraphStyle(
            'SectionHeader',
            parent=styles['Heading2'],
            fontSize=14,
            spaceAfter=8,
            spaceBefore=16,
        )
        
        contact_style = ParagraphStyle(
            'ContactStyle',
            parent=styles['Normal'],
            fontSize=10,
            spaceAfter=12,
            alignment=1  # Center alignment
        )
        
        bullet_style = ParagraphStyle(
            'BulletStyle',
            parent=styles['Normal'],
            fontSize=10,
            leftIndent=20,
            spaceAfter=6,
        )
        
        # Parse and format resume content with enhanced logic
        story = []
        lines = improved_resume.split('\n')
        name_found = False
        current_section = None
        
        # Create additional styles for better formatting
        job_title_style = ParagraphStyle(
            'JobTitleStyle',
            parent=styles['Normal'],
            fontSize=12,
            spaceAfter=4,
            spaceBefore=6,
            textColor='black'
        )
        
        company_style = ParagraphStyle(
            'CompanyStyle',
            parent=styles['Normal'],
            fontSize=11,
            spaceAfter=2,
            textColor='black'
        )
        
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
                
            # Detect name (first significant non-contact line)
            if not name_found and len(line.split()) <= 5 and not any(keyword in line.lower() for keyword in ['email', 'phone', '@', 'linkedin', 'experience', 'education', 'skills', 'summary', 'objective']):
                story.append(Paragraph(f'<b>{line}</b>', name_style))
                name_found = True
                story.append(Spacer(1, 8))
                continue
            
            # Detect contact information
            if any(keyword in line.lower() for keyword in ['@', 'phone:', 'email:', 'linkedin', 'github', '+1', '(' in line and ')' in line]):
                story.append(Paragraph(line, contact_style))
                continue
                
            # Detect section headers
            if is_section_header(line):
                current_section = line.lower()
                story.append(Spacer(1, 16))
                story.append(Paragraph(f'<b>{line.upper()}</b>', section_header_style))
                story.append(Spacer(1, 8))
                continue
            
            # Enhanced bullet point detection
            if (line.startswith('•') or line.startswith('-') or line.startswith('*') or 
                line.startswith('\u2022') or line.startswith('\u2023') or line.startswith('\u25e6')):
                clean_line = line[1:].strip()
                story.append(Paragraph(f'• {clean_line}', bullet_style))
                continue
            
            # Detect job titles and companies (in experience section)
            if current_section and 'experience' in current_section:
                # Check if this looks like a job title or company
                next_line = lines[i + 1].strip() if i + 1 < len(lines) else ''
                
                # If line is short and next line has dates, this is likely a job title
                if (len(line.split()) <= 6 and 
                    any(date_pattern in next_line for date_pattern in ['2019', '2020', '2021', '2022', '2023', '2024', '2025', 'present', 'current', '-'])):
                    story.append(Paragraph(f'<b>{line}</b>', job_title_style))
                    continue
                
                # If line contains common company indicators
                if any(indicator in line.lower() for indicator in [', inc', ', llc', 'corporation', 'company', 'technologies', 'systems']):
                    story.append(Paragraph(f'<i>{line}</i>', company_style))
                    continue
            
            # Detect dates and duration
            if any(pattern in line for pattern in ['2019', '2020', '2021', '2022', '2023', '2024', '2025']) and ('-' in line or 'to' in line.lower() or 'present' in line.lower()):
                date_style = ParagraphStyle(
                    'DateStyle',
                    parent=styles['Normal'],
                    fontSize=10,
                    spaceAfter=8,
                    textColor='grey'
                )
                story.append(Paragraph(f'<i>{line}</i>', date_style))
                continue
            
            # Regular content with proper spacing
            if line:
                story.append(Paragraph(line, styles['Normal']))
                story.append(Spacer(1, 6))
        
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
