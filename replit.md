# Overview

Smart Resume Reviewer is an AI-powered web application that helps job seekers optimize their resumes for specific job roles. The application uses Google Gemini AI to analyze uploaded resumes and provide comprehensive feedback including missing skills, section-wise recommendations, and an improved version of the resume tailored to the target position.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Frontend Architecture
- **Framework**: Flask with Jinja2 templating
- **Styling**: Bootstrap with dark theme for modern, responsive UI
- **JavaScript**: Vanilla JS for file handling, form validation, and user interactions
- **File Upload**: Supports both PDF and text file uploads with drag-and-drop functionality
- **Responsive Design**: Mobile-first approach using Bootstrap grid system

## Backend Architecture
- **Framework**: Flask web framework with modular route handling
- **PDF Processing**: PyMuPDF (fitz) for extracting text content from PDF files
- **AI Integration**: Google Gemini 2.5 Flash model for resume analysis and improvement
- **File Management**: Secure file upload handling with size limits (16MB) and type validation
- **Session Management**: Flask sessions with configurable secret keys

## Data Flow
- **Input Processing**: Users can upload PDF/text files or paste resume content directly
- **Text Extraction**: PDF files are processed to extract plain text using PyMuPDF
- **AI Analysis**: Extracted content is sent to Gemini API with structured prompts for analysis
- **Result Generation**: AI provides feedback on missing skills, improvements, and generates optimized resume
- **Output Delivery**: Results displayed in web interface with PDF download option for improved resume

## Security and Configuration
- **Environment Variables**: API keys stored securely using environment variables
- **File Security**: Secure filename handling and upload directory management
- **Proxy Support**: ProxyFix middleware for proper header handling in hosted environments
- **Error Handling**: Comprehensive logging and user-friendly error messages

# External Dependencies

## AI Services
- **Google Gemini API**: Primary AI service using the 2.5 Flash model for resume analysis and content generation
- **API Client**: google-generativeai Python SDK for Gemini integration

## File Processing
- **PyMuPDF (fitz)**: PDF text extraction and processing
- **ReportLab**: PDF generation for improved resume downloads

## Web Framework
- **Flask**: Core web framework with Werkzeug utilities
- **Bootstrap**: Frontend CSS framework with dark theme integration
- **Feather Icons**: Icon library for UI elements

## Development Tools
- **Python Logging**: Built-in logging for debugging and monitoring
- **Werkzeug**: WSGI utilities for file handling and security

## Hosting Platform
- **Replit**: Designed specifically for Replit's free tier hosting environment
- **Environment**: Configured for 0.0.0.0:5000 hosting with debug mode