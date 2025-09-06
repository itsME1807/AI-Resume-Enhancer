import logging
import fitz  # PyMuPDF
import os

class PDFParser:
    def __init__(self):
        pass
    
    def extract_text_from_pdf(self, pdf_path):
        """
        Extract text content from PDF file using PyMuPDF
        """
        try:
            if not os.path.exists(pdf_path):
                raise FileNotFoundError(f"PDF file not found: {pdf_path}")
            
            # Open PDF document
            doc = fitz.open(pdf_path)
            
            if doc.page_count == 0:
                raise ValueError("PDF file contains no pages")
            
            text_content = ""
            
            # Extract text from each page
            for page_num in range(doc.page_count):
                page = doc.load_page(page_num)
                page_text = page.get_text()
                text_content += page_text + "\n"
            
            # Close document
            doc.close()
            
            # Clean up extracted text
            text_content = self._clean_extracted_text(text_content)
            
            if not text_content.strip():
                raise ValueError("No text content could be extracted from the PDF")
            
            logging.info(f"Successfully extracted {len(text_content)} characters from PDF")
            return text_content
            
        except Exception as e:
            logging.error(f"Error extracting text from PDF {pdf_path}: {e}")
            raise Exception(f"Failed to extract text from PDF: {str(e)}")
    
    def _clean_extracted_text(self, text):
        """
        Clean and normalize extracted text
        """
        if not text:
            return ""
        
        # Replace multiple consecutive newlines with double newlines
        import re
        text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)
        
        # Remove excessive whitespace while preserving structure
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            # Strip whitespace from each line
            cleaned_line = line.strip()
            if cleaned_line:
                cleaned_lines.append(cleaned_line)
            elif cleaned_lines and cleaned_lines[-1]:  # Preserve single empty lines for structure
                cleaned_lines.append('')
        
        return '\n'.join(cleaned_lines)
    
    def validate_pdf(self, pdf_path):
        """
        Validate if the file is a valid PDF and can be processed
        """
        try:
            doc = fitz.open(pdf_path)
            page_count = doc.page_count
            doc.close()
            
            return {
                'valid': True,
                'page_count': page_count,
                'message': f'Valid PDF with {page_count} page(s)'
            }
            
        except Exception as e:
            return {
                'valid': False,
                'page_count': 0,
                'message': f'Invalid PDF: {str(e)}'
            }
