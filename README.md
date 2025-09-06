# Smart Resume Reviewer

An AI-powered web application that helps job seekers optimize their resumes for specific job roles using Google Gemini AI.

## Features

- Upload resumes (PDF/text) or paste content directly
- AI-powered analysis with comprehensive feedback
- Missing skills identification
- Section-wise recommendations
- Professional PDF download of improved resume
- Responsive Bootstrap UI with dark theme

## Render Deploy

### Prerequisites
- Python 3.11+
- Google Gemini API key

### Deployment Steps

1. **Clone/Upload your repository to Render**

2. **Configure Build Settings:**
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python3 main.py`
   - **Python Version:** 3.11 (set in Environment or use runtime.txt)

3. **Environment Variables:**
   Set the following environment variables in Render:
   ```
   GEMINI_API_KEY=your_gemini_api_key_here
   SESSION_SECRET=your_random_session_secret_here
   PORT=10000
   ```

4. **Required Files in Repository Root:**
   - `requirements.txt` - Python dependencies
   - `main.py` - Application entry point
   - All other project files

### Health Check
The application will be available at `https://your-app-name.onrender.com` and serves HTTP endpoints on the configured port.

### Build Command Details
```bash
pip install -r requirements.txt
```

### Start Command Details
```bash
python3 main.py
```

The application automatically binds to `0.0.0.0:$PORT` and is configured for production deployment.

## Local Development

1. Install dependencies: `pip install -r requirements.txt`
2. Set environment variables: `GEMINI_API_KEY`
3. Run: `python3 main.py`
4. Visit: `http://localhost:5000`

## Architecture

- **Backend:** Flask with gunicorn
- **AI:** Google Gemini 2.5 Flash
- **PDF Processing:** PyMuPDF
- **PDF Generation:** ReportLab
- **Frontend:** Bootstrap with responsive design