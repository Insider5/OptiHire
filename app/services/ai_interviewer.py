"""
AI Interview Question Generator using Google Gemini
Generates role-specific technical questions based on candidate profile
"""
import os
import re
from typing import List, Dict
import json

try:
    from google import genai
    from google.genai import types as genai_types
    _GENAI_NEW_SDK = True
except ImportError:
    try:
        import google.generativeai as genai  # type: ignore[no-redef]
        genai_types = None
        _GENAI_NEW_SDK = False
    except ImportError:
        genai = None
        genai_types = None
        _GENAI_NEW_SDK = False

class InterviewQuestionGenerator:
    """Generate AI-powered interview questions using Gemini"""
    
    def __init__(self):
        """Initialize Gemini API"""
        self.api_key = os.environ.get('GEMINI_API_KEY')

        if genai and self.api_key:
            if _GENAI_NEW_SDK:
                # New google-genai SDK
                self.client = genai.Client(api_key=self.api_key)
                self.model_name = 'gemini-2.0-flash'
            else:
                # Legacy google-generativeai SDK
                genai.configure(api_key=self.api_key)
                try:
                    self.model = genai.GenerativeModel('gemini-1.5-flash')
                except Exception:
                    self.model = genai.GenerativeModel('gemini-pro')
                self.client = None
            self.enabled = True
        else:
            self.enabled = False
            print("Gemini API not configured. Using built-in fallback question generator.")
    
    def generate_questions(self, 
                          resume_data: Dict, 
                          job_data: Dict, 
                          num_questions: int = 5) -> List[Dict]:
        """
        Generate interview questions based on candidate profile and job requirements
        """
        if not self.enabled:
            return self._generate_fallback_questions(resume_data, job_data, num_questions)
        
        try:
            # Build prompt
            prompt = self._build_generation_prompt(resume_data, job_data, num_questions)

            # Generate response (new SDK or legacy)
            if _GENAI_NEW_SDK and self.client:
                response = self.client.models.generate_content(
                    model=self.model_name, contents=prompt
                )
                response_text = response.text
            else:
                response = self.model.generate_content(prompt)
                response_text = response.text

            # Parse response
            questions = self._parse_questions(response_text)

            # Validate: ensure we have real question objects
            valid = [
                q for q in questions
                if isinstance(q, dict) and q.get('question') and len(q['question']) > 15
            ]

            if valid:
                return valid[:num_questions]

            # Fall through to fallback if AI returned garbage
            return self._generate_fallback_questions(resume_data, job_data, num_questions)

        except Exception as e:
            print(f"Error generating questions: {e}")
            return self._generate_fallback_questions(resume_data, job_data, num_questions)
    
    def _build_generation_prompt(self, resume_data: Dict, job_data: Dict, num_questions: int) -> str:
        """Build prompt for Gemini"""
        
        # Extract relevant info
        skills = resume_data.get('skills', [])
        experience = resume_data.get('experience_years', 0)
        job_title = job_data.get('title', 'Software Engineer')
        job_requirements = job_data.get('requirements', '')
        experience_level = job_data.get('experience_level', 'Mid-level')
        
        prompt = f"""
You are an expert technical interviewer. Generate {num_questions} interview questions for the following candidate profile:

Job Position: {job_title}
Experience Level: {experience_level}
Required Skills: {', '.join(skills[:10]) if skills else 'General programming'}
Candidate Experience: {experience} years
Job Requirements: {job_requirements[:300]}

Generate questions that:
1. Match the candidate's experience level ({experience_level})
2. Test their knowledge of the required skills
3. Include a mix of technical and scenario-based questions
4. Are specific and relevant to the job role

For each question, provide:
- The question text
- Question type (technical, behavioral, problem-solving, or system-design)
- Difficulty level (easy, medium, hard)

Format your response as a JSON array of objects with keys: "question", "type", "difficulty"
"""
        
        return prompt
    
    def _parse_questions(self, response_text: str) -> List[Dict]:
        """Parse Gemini response to extract questions"""
        
        try:
            # Try to extract JSON from response
            # Look for JSON array in the text
            start_idx = response_text.find('[')
            end_idx = response_text.rfind(']') + 1
            
            if start_idx != -1 and end_idx > start_idx:
                json_str = response_text[start_idx:end_idx]
                questions = json.loads(json_str)
                return questions
        except:
            pass
        
        # Fallback: parse line by line
        questions = []
        lines = response_text.split('\n')
        
        for line in lines:
            line = line.strip()
            if line and any(char.isalpha() for char in line):
                # Remove numbering
                line = re.sub(r'^\d+[\.\)]\s*', '', line)
                if len(line) > 20:  # Reasonable question length
                    questions.append({
                        'question': line,
                        'type': 'technical',
                        'difficulty': 'medium'
                    })
        
        return questions[:5]  # Return max 5
    
    def _generate_fallback_questions(self, resume_data: Dict, job_data: Dict, num_questions: int) -> List[Dict]:
        """Generate fallback questions if API is unavailable"""
        
        skills = resume_data.get('skills', [])
        experience = resume_data.get('experience_years', 0)
        job_title = job_data.get('title', 'Software Engineer')
        
        questions = []
        
        # General technical questions
        if 'Python' in skills:
            questions.append({
                'question': 'Explain the difference between list and tuple in Python. When would you use each?',
                'type': 'technical',
                'difficulty': 'easy'
            })
        
        if 'JavaScript' in skills or 'React' in skills:
            questions.append({
                'question': 'What are React hooks and how do useState and useEffect work?',
                'type': 'technical',
                'difficulty': 'medium'
            })
        
        if 'Database' in str(skills) or 'SQL' in skills:
            questions.append({
                'question': 'Explain database normalization and denormalization. When would you use each approach?',
                'type': 'technical',
                'difficulty': 'medium'
            })
        
        # Experience-based questions
        if experience >= 3:
            questions.append({
                'question': 'Describe a challenging technical problem you solved. What was your approach?',
                'type': 'behavioral',
                'difficulty': 'medium'
            })
            questions.append({
                'question': 'How do you design a scalable system? Walk me through your approach.',
                'type': 'system-design',
                'difficulty': 'hard'
            })
        else:
            questions.append({
                'question': 'Tell me about a project you\'re most proud of and what you learned.',
                'type': 'behavioral',
                'difficulty': 'easy'
            })
            questions.append({
                'question': 'How would you approach learning a new technology or framework?',
                'type': 'behavioral',
                'difficulty': 'easy'
            })
        
        # Generic algorithm question
        questions.append({
            'question': 'Write a function to reverse a linked list. Explain your approach and time complexity.',
            'type': 'problem-solving',
            'difficulty': 'medium'
        })
        
        return questions[:num_questions]
    
    def generate_feedback(self, application_data: Dict) -> str:
        """
        Generate personalized feedback for candidates
        """
        if not self.enabled:
            return self._generate_fallback_feedback(application_data)
        
        try:
            score = application_data.get('similarity_score', 0)
            breakdown = application_data.get('match_breakdown', {})
            
            prompt = f"""
Generate constructive feedback for a job application with the following details:

Overall Match Score: {score * 100:.1f}%
Skills Match: {breakdown.get('skills_match', 0) * 100:.1f}%
Matched Skills: {', '.join(breakdown.get('matched_skills', []))}
Missing Skills: {', '.join(breakdown.get('missing_skills', []))}

Provide encouraging, actionable feedback that:
1. Acknowledges their strengths
2. Identifies improvement areas
3. Suggests specific learning resources or actions
4. Maintains a positive, supportive tone

Keep it concise (3-4 paragraphs).
"""
            
            response = self.model.generate_content(prompt)
            return response.text
            
        except Exception as e:
            print(f"Error generating feedback: {e}")
            return self._generate_fallback_feedback(application_data)
    
    def _generate_fallback_feedback(self, application_data: Dict) -> str:
        """Fallback feedback when API unavailable"""
        score = application_data.get('similarity_score', 0)
        breakdown = application_data.get('match_breakdown', {})
        
        feedback = f"""
Thank you for your application. Based on our analysis, your profile shows a {score * 100:.1f}% match with this position.

Strengths:
"""
        
        matched_skills = breakdown.get('matched_skills', [])
        if matched_skills:
            feedback += f"- You possess key skills: {', '.join(matched_skills[:5])}\n"
        
        feedback += "\nAreas for Improvement:\n"
        
        missing_skills = breakdown.get('missing_skills', [])
        if missing_skills:
            feedback += f"- Consider gaining experience in: {', '.join(missing_skills[:5])}\n"
        
        feedback += "\nWe encourage you to continue developing your skills and applying to relevant positions."
        
        return feedback

# Singleton
_generator_instance = None

def get_question_generator():
    """Get or create question generator instance"""
    global _generator_instance
    if _generator_instance is None:
        _generator_instance = InterviewQuestionGenerator()
    return _generator_instance
