import os
import logging
import json
from google import genai
from google.genai import types

class GeminiResumeAnalyzer:
    def __init__(self):
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set")
        
        self.client = genai.Client(api_key=api_key)
        self.model = "gemini-2.5-flash"
    
    def analyze_resume(self, resume_content, job_role, job_description=""):
        """
        Analyze resume and provide comprehensive feedback
        """
        try:
            # Create comprehensive prompt for analysis
            prompt = self._create_analysis_prompt(resume_content, job_role, job_description)
            
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt
            )
            
            if not response.text:
                raise Exception("Empty response from Gemini API")
            
            # Parse the structured response
            analysis = self._parse_analysis_response(response.text)
            
            # Generate improved resume
            improved_resume = self._generate_improved_resume(resume_content, job_role, job_description, analysis)
            analysis['improved_resume'] = improved_resume
            
            return analysis
            
        except Exception as e:
            logging.error(f"Error in Gemini analysis: {e}")
            raise Exception(f"Failed to analyze resume: {str(e)}")
    
    def _create_analysis_prompt(self, resume_content, job_role, job_description):
        """Create structured prompt for resume analysis"""
        prompt = f"""
You are an expert resume reviewer and career consultant. Analyze the following resume for a {job_role} position.

RESUME CONTENT:
{resume_content}

TARGET JOB ROLE: {job_role}

JOB DESCRIPTION: {job_description if job_description else "Not provided"}

Please provide a comprehensive analysis in the following structured format:

## MISSING SKILLS & KEYWORDS
- List 5-8 specific skills, keywords, or qualifications that are missing but would be valuable for this role
- Focus on technical skills, certifications, tools, and industry-specific terms

## SECTION-WISE FEEDBACK

### Education
- Specific feedback on education section relevance and presentation
- Suggestions for improvement

### Experience  
- Analysis of work experience relevance to the target role
- Feedback on accomplishment descriptions and quantification
- Suggestions for better positioning

### Skills
- Review of technical and soft skills listed
- Recommendations for skills to add or reframe
- Suggestions for better organization

### Overall Structure
- Feedback on resume format, organization, and flow
- Professional presentation assessment

## REDUNDANT/VAGUE LANGUAGE
- Identify specific phrases, buzzwords, or descriptions that are overused or unclear
- Provide alternatives for weak language

## FORMATTING & CLARITY RECOMMENDATIONS
- Specific suggestions for improving visual presentation
- Recommendations for better information hierarchy
- Tips for enhancing readability

Provide detailed, actionable feedback that would help a job seeker improve their resume specifically for the {job_role} position.
"""
        return prompt
    
    def _parse_analysis_response(self, response_text):
        """Parse the structured response from Gemini"""
        analysis = {
            'missing_skills': [],
            'section_feedback': {},
            'redundant_language': [],
            'formatting_recommendations': []
        }
        
        try:
            # Simple parsing based on headers
            sections = response_text.split('##')
            
            for section in sections:
                section = section.strip()
                if not section:
                    continue
                    
                if section.upper().startswith('MISSING SKILLS'):
                    analysis['missing_skills'] = self._extract_list_items(section)
                elif section.upper().startswith('SECTION-WISE FEEDBACK'):
                    analysis['section_feedback'] = self._extract_section_feedback(section)
                elif section.upper().startswith('REDUNDANT/VAGUE LANGUAGE'):
                    analysis['redundant_language'] = self._extract_list_items(section)
                elif section.upper().startswith('FORMATTING & CLARITY'):
                    analysis['formatting_recommendations'] = self._extract_list_items(section)
            
            # Store raw response for fallback
            analysis['raw_response'] = response_text
            
        except Exception as e:
            logging.warning(f"Error parsing analysis response: {e}")
            analysis['raw_response'] = response_text
        
        return analysis
    
    def _extract_list_items(self, section_text):
        """Extract list items from a section"""
        items = []
        lines = section_text.split('\n')
        
        for line in lines:
            line = line.strip()
            if line.startswith('- ') or line.startswith('• '):
                items.append(line[2:].strip())
            elif line.startswith('* '):
                items.append(line[2:].strip())
        
        return items
    
    def _extract_section_feedback(self, section_text):
        """Extract section-wise feedback"""
        feedback = {}
        current_subsection = None
        current_content = []
        
        lines = section_text.split('\n')
        
        for line in lines:
            line = line.strip()
            if line.startswith('### '):
                # Save previous subsection
                if current_subsection and current_content:
                    feedback[current_subsection] = '\n'.join(current_content)
                
                # Start new subsection
                current_subsection = line[4:].strip()
                current_content = []
            elif line and current_subsection:
                current_content.append(line)
        
        # Save last subsection
        if current_subsection and current_content:
            feedback[current_subsection] = '\n'.join(current_content)
        
        return feedback
    
    def _generate_improved_resume(self, resume_content, job_role, job_description, analysis):
        """Generate an improved version of the resume"""
        try:
            prompt = f"""
Based on the following resume analysis, create an improved version of the resume that addresses the feedback and is optimized for a {job_role} position.

ORIGINAL RESUME:
{resume_content}

TARGET JOB ROLE: {job_role}

JOB DESCRIPTION: {job_description if job_description else "Not provided"}

ANALYSIS FEEDBACK:
- Missing Skills: {', '.join(analysis.get('missing_skills', []))}
- Key areas for improvement based on the detailed analysis provided

Please create an improved resume that:
1. Incorporates relevant missing skills and keywords naturally
2. Improves weak or vague language with specific, quantified achievements
3. Reorganizes content for better flow and impact
4. Maintains the person's authentic experience while optimizing presentation
5. Uses action verbs and quantified results where possible

Format the improved resume professionally with clear sections and bullet points. Make it ATS-friendly and tailored for the {job_role} position.

IMPROVED RESUME:
"""
            
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt
            )
            
            return response.text if response.text else "Unable to generate improved resume."
            
        except Exception as e:
            logging.error(f"Error generating improved resume: {e}")
            return "Error generating improved resume. Please try again."
