"""
Interview Preparation Chatbot Service using Google Gemini
Helps candidates prepare for interviews with job-specific Q&A
"""
import os
import json
from typing import List, Dict, Optional

try:
    from google import genai
    from google.genai import types as genai_types
    _GENAI_NEW_SDK = True
except ImportError:
    try:
        import google.generativeai as genai
        genai_types = None
        _GENAI_NEW_SDK = False
    except ImportError:
        genai = None
        genai_types = None
        _GENAI_NEW_SDK = False


class InterviewPrepChatbot:
    """AI-powered interview preparation assistant"""

    def __init__(self):
        """Initialize Gemini API"""
        self.api_key = os.environ.get('GEMINI_API_KEY')

        if genai and self.api_key:
            if _GENAI_NEW_SDK:
                self.client = genai.Client(api_key=self.api_key)
                self.model_name = 'gemini-2.0-flash'
            else:
                genai.configure(api_key=self.api_key)
                try:
                    self.model = genai.GenerativeModel('gemini-1.5-flash')
                except Exception:
                    self.model = genai.GenerativeModel('gemini-pro')
                self.client = None
            self.enabled = True
        else:
            self.enabled = False
            print("Gemini API not configured. Using fallback responses.")

    def _generate_response(self, prompt: str) -> str:
        """Generate a response from Gemini"""
        try:
            if _GENAI_NEW_SDK and self.client:
                response = self.client.models.generate_content(
                    model=self.model_name, contents=prompt
                )
                return response.text
            else:
                response = self.model.generate_content(prompt)
                return response.text
        except Exception as e:
            print(f"Error generating response: {e}")
            return None

    def chat(self, user_message: str, job_data: Dict, chat_history: List[Dict] = None) -> str:
        """
        Process user message and generate a helpful response about interview prep
        """
        if not self.enabled:
            return self._fallback_response(user_message, job_data)

        # Build context from job data
        job_context = self._build_job_context(job_data)

        # Build chat history context
        history_context = ""
        if chat_history:
            for msg in chat_history[-6:]:  # Last 6 messages for context
                role = "Candidate" if msg.get('role') == 'user' else "Assistant"
                history_context += f"{role}: {msg.get('content', '')}\n"

        prompt = f"""You are an expert interview coach helping a candidate prepare for a job interview.

Job Details:
{job_context}

Previous conversation:
{history_context}

The candidate asks: {user_message}

Provide a helpful, encouraging response that:
1. Directly addresses their question
2. Gives practical interview tips specific to this job
3. If they ask for practice questions, provide relevant technical or behavioral questions
4. If they ask about the company/role, explain based on the job description
5. Keep responses concise but informative (2-4 paragraphs max)
6. Use bullet points for lists
7. Be supportive and build their confidence

Response:"""

        response = self._generate_response(prompt)

        if response:
            return response
        return self._fallback_response(user_message, job_data)

    def _build_job_context(self, job_data: Dict) -> str:
        """Build job context string for the prompt"""
        title = job_data.get('title', 'Unknown Position')
        company = job_data.get('company', 'Unknown Company')
        description = job_data.get('description', '')[:500]
        requirements = job_data.get('requirements', '')[:500]

        skills = job_data.get('skills_required', [])
        if isinstance(skills, str):
            try:
                skills = json.loads(skills)
            except:
                skills = [s.strip() for s in skills.split(',')]

        experience_level = job_data.get('experience_level', 'Not specified')
        location = job_data.get('location', 'Not specified')
        job_type = job_data.get('job_type', 'Full-time')

        return f"""
Position: {title}
Company: {company}
Location: {location}
Job Type: {job_type}
Experience Level: {experience_level}
Required Skills: {', '.join(skills) if skills else 'Not specified'}

Job Description:
{description}

Requirements:
{requirements}
"""

    def generate_practice_questions(self, job_data: Dict, question_type: str = 'mixed') -> List[Dict]:
        """Generate practice interview questions for the job"""
        if not self.enabled:
            return self._fallback_questions(job_data, question_type)

        job_context = self._build_job_context(job_data)

        type_instruction = {
            'technical': 'Focus only on technical questions testing coding skills and system knowledge.',
            'behavioral': 'Focus only on behavioral questions using STAR method (Situation, Task, Action, Result).',
            'problem-solving': 'Focus on problem-solving and algorithmic thinking questions.',
            'mixed': 'Include a mix of technical, behavioral, and problem-solving questions.'
        }.get(question_type, 'Include a mix of technical, behavioral, and problem-solving questions.')

        prompt = f"""Generate 5 interview practice questions for this job:

{job_context}

{type_instruction}

For each question, provide:
1. The question
2. Key points the candidate should cover in their answer
3. A sample ideal answer outline

Format as JSON array with objects having keys: "question", "key_points" (array), "sample_answer"
"""

        response = self._generate_response(prompt)

        if response:
            try:
                start_idx = response.find('[')
                end_idx = response.rfind(']') + 1
                if start_idx != -1 and end_idx > start_idx:
                    questions = json.loads(response[start_idx:end_idx])
                    return questions
            except:
                pass

        return self._fallback_questions(job_data, question_type)

    def get_job_insights(self, job_data: Dict) -> Dict:
        """Get AI-generated insights about the job for preparation"""
        if not self.enabled:
            return self._fallback_insights(job_data)

        job_context = self._build_job_context(job_data)

        prompt = f"""Analyze this job posting and provide preparation insights:

{job_context}

Provide insights in this JSON format:
{{
    "key_responsibilities": ["list of 3-4 main responsibilities"],
    "must_have_skills": ["critical skills to demonstrate"],
    "nice_to_have_skills": ["additional skills that would stand out"],
    "expected_questions": ["3-4 likely interview questions"],
    "preparation_tips": ["4-5 specific preparation tips"],
    "red_flags_to_avoid": ["common mistakes to avoid"],
    "questions_to_ask": ["3-4 good questions candidate should ask interviewer"]
}}
"""

        response = self._generate_response(prompt)

        if response:
            try:
                start_idx = response.find('{')
                end_idx = response.rfind('}') + 1
                if start_idx != -1 and end_idx > start_idx:
                    return json.loads(response[start_idx:end_idx])
            except:
                pass

        return self._fallback_insights(job_data)

    def _fallback_response(self, user_message: str, job_data: Dict) -> str:
        """Provide fallback response when API is unavailable"""
        title = job_data.get('title', 'this position')
        company = job_data.get('company', 'the company')
        skills = job_data.get('skills_required', [])
        if isinstance(skills, str):
            try:
                skills = json.loads(skills)
            except:
                skills = []

        msg_lower = user_message.lower()

        if 'question' in msg_lower or 'practice' in msg_lower:
            return f"""Here are some practice questions for {title}:

**Technical Questions:**
- How would you approach a complex problem using {skills[0] if skills else 'your technical skills'}?
- Describe your experience with {skills[1] if len(skills) > 1 else 'relevant technologies'}.

**Behavioral Questions:**
- Tell me about a challenging project you worked on. What was your role?
- How do you handle tight deadlines and competing priorities?

**Tips:**
- Use the STAR method (Situation, Task, Action, Result) for behavioral questions
- Prepare specific examples from your experience
- Practice explaining your thought process out loud"""

        elif 'tip' in msg_lower or 'advice' in msg_lower or 'prepare' in msg_lower:
            return f"""**Interview Preparation Tips for {title} at {company}:**

1. **Research the Company**: Learn about their products, culture, and recent news
2. **Review Required Skills**: Brush up on {', '.join(skills[:3]) if skills else 'relevant technologies'}
3. **Prepare Examples**: Have 3-5 STAR stories ready
4. **Practice Coding**: If technical, practice algorithms and system design
5. **Prepare Questions**: Have thoughtful questions ready for the interviewer
6. **Rest Well**: Get good sleep before the interview

You've got this! Preparation is key to confidence."""

        elif 'skill' in msg_lower or 'requirement' in msg_lower:
            skills_list = ', '.join(skills) if skills else 'Check the job description for specific requirements'
            return f"""**Key Skills for {title}:**

{skills_list}

**How to Demonstrate These:**
- Prepare specific examples where you used each skill
- Be ready to discuss projects in detail
- Show enthusiasm for learning and growth
- Connect your experience to their requirements"""

        else:
            return f"""I'm here to help you prepare for your interview for **{title}** at **{company}**!

I can help you with:
- **Practice Questions**: Ask me for technical, behavioral, or mixed questions
- **Preparation Tips**: Get advice on how to prepare
- **Job Insights**: Learn about what to expect
- **Skill Review**: Understand key requirements

What would you like to focus on?"""

    def _fallback_questions(self, job_data: Dict, question_type: str) -> List[Dict]:
        """Generate fallback questions"""
        skills = job_data.get('skills_required', [])
        if isinstance(skills, str):
            try:
                skills = json.loads(skills)
            except:
                skills = []

        questions = [
            {
                "question": f"Tell me about your experience with {skills[0] if skills else 'relevant technologies'}.",
                "key_points": ["Specific projects", "Challenges overcome", "Results achieved"],
                "sample_answer": "Describe a specific project where you used this skill, the challenges you faced, and the positive outcome."
            },
            {
                "question": "Describe a time when you had to solve a complex problem under pressure.",
                "key_points": ["Problem description", "Your approach", "Collaboration", "Outcome"],
                "sample_answer": "Use STAR method: Explain the situation, your specific task, actions taken, and results."
            },
            {
                "question": "How do you stay updated with the latest industry trends and technologies?",
                "key_points": ["Learning resources", "Practical application", "Continuous improvement"],
                "sample_answer": "Mention specific resources (courses, blogs, conferences) and how you've applied new knowledge."
            },
            {
                "question": "Where do you see yourself in 5 years?",
                "key_points": ["Career growth", "Alignment with company", "Realistic goals"],
                "sample_answer": "Show ambition while demonstrating commitment to growing within the company."
            },
            {
                "question": "Why are you interested in this role?",
                "key_points": ["Company research", "Role alignment", "Enthusiasm"],
                "sample_answer": "Connect your skills and career goals to what the company offers."
            }
        ]

        return questions

    def _fallback_insights(self, job_data: Dict) -> Dict:
        """Generate fallback insights"""
        skills = job_data.get('skills_required', [])
        if isinstance(skills, str):
            try:
                skills = json.loads(skills)
            except:
                skills = []

        return {
            "key_responsibilities": [
                "Developing and maintaining software solutions",
                "Collaborating with cross-functional teams",
                "Contributing to technical design decisions"
            ],
            "must_have_skills": skills[:4] if skills else ["Technical proficiency", "Problem-solving", "Communication"],
            "nice_to_have_skills": ["Leadership experience", "Open source contributions", "Industry certifications"],
            "expected_questions": [
                "Tell me about yourself",
                "Why do you want this role?",
                "Describe a challenging project",
                "How do you handle disagreements?"
            ],
            "preparation_tips": [
                "Research the company thoroughly",
                "Prepare STAR method stories",
                "Review technical fundamentals",
                "Practice explaining your experience",
                "Prepare thoughtful questions to ask"
            ],
            "red_flags_to_avoid": [
                "Speaking negatively about past employers",
                "Being unprepared for basic questions",
                "Not asking any questions",
                "Arriving late or looking unkempt"
            ],
            "questions_to_ask": [
                "What does success look like in this role?",
                "What's the team culture like?",
                "What are the biggest challenges facing the team?",
                "What opportunities for growth are available?"
            ]
        }


# Singleton instance
_chatbot_instance = None

def get_prep_chatbot():
    """Get or create chatbot instance"""
    global _chatbot_instance
    if _chatbot_instance is None:
        _chatbot_instance = InterviewPrepChatbot()
    return _chatbot_instance
