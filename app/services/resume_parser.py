"""
NLP Service for Resume Parsing and Named Entity Recognition (NER)
Uses spaCy and BERT-based models for extracting structured data from resumes
"""
import sys
import spacy
import re
import json
from typing import Dict, List, Any
import PyPDF2
from docx import Document as DocxDocument

class ResumeParser:
    """Parse resumes and extract entities using NER"""

    # ── Domain keyword map ───────────────────────────────────
    DOMAIN_SKILLS: Dict[str, List[str]] = {
        'Backend':   ['Python', 'Java', 'Node.js', 'Django', 'Flask', 'Spring', 'FastAPI',
                      'REST API', 'GraphQL', 'Microservices', 'PostgreSQL', 'MySQL'],
        'Frontend':  ['React', 'Angular', 'Vue.js', 'HTML', 'CSS', 'TypeScript', 'JavaScript',
                      'Next.js', 'Svelte', 'Tailwind'],
        'ML/AI':     ['Machine Learning', 'Deep Learning', 'TensorFlow', 'PyTorch', 'Keras',
                      'scikit-learn', 'NLP', 'Computer Vision', 'BERT', 'GPT', 'OpenCV',
                      'Data Science'],
        'DevOps':    ['Docker', 'Kubernetes', 'Terraform', 'Ansible', 'CI/CD', 'Jenkins',
                      'AWS', 'Azure', 'GCP', 'Linux', 'DevOps'],
        'Database':  ['SQL', 'MySQL', 'PostgreSQL', 'MongoDB', 'Redis', 'Cassandra',
                      'Oracle', 'DynamoDB', 'Firebase'],
        'Mobile':    ['Android', 'iOS', 'Swift', 'Kotlin', 'React Native', 'Flutter'],
    }

    def __init__(self):
        """Initialize spaCy model"""
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            print("Downloading spaCy model...")
            import subprocess
            subprocess.run([sys.executable, "-m", "spacy", "download", "en_core_web_sm"],
                           check=True)
            self.nlp = spacy.load("en_core_web_sm")

        # Common technical skills database
        self.common_skills = {
            'programming': ['Python', 'Java', 'JavaScript', 'C++', 'C#', 'Ruby', 'Go', 'Rust',
                           'TypeScript', 'PHP', 'Swift', 'Kotlin', 'Scala', 'R'],
            'web': ['HTML', 'CSS', 'React', 'Angular', 'Vue.js', 'Node.js', 'Django', 'Flask',
                   'Spring', 'Express.js', 'FastAPI', 'Next.js', 'Svelte'],
            'database': ['SQL', 'MySQL', 'PostgreSQL', 'MongoDB', 'Redis', 'Cassandra',
                        'Oracle', 'SQLite', 'DynamoDB', 'Firebase'],
            'cloud': ['AWS', 'Azure', 'GCP', 'Docker', 'Kubernetes', 'Terraform', 'Ansible'],
            'ml_ai': ['Machine Learning', 'Deep Learning', 'TensorFlow', 'PyTorch', 'Keras',
                     'scikit-learn', 'NLP', 'Computer Vision', 'BERT', 'GPT', 'OpenCV'],
            'tools': ['Git', 'GitHub', 'GitLab', 'Jira', 'Jenkins', 'CI/CD', 'Agile', 'Scrum'],
            'other': ['Linux', 'REST API', 'GraphQL', 'Microservices', 'Testing', 'DevOps']
        }

        # Flatten all skills for matching
        self.all_skills = []
        for category in self.common_skills.values():
            self.all_skills.extend(category)
    
    def extract_text_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF file"""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
                return text
        except Exception as e:
            print(f"Error extracting PDF: {e}")
            return ""
    
    def extract_text_from_docx(self, file_path: str) -> str:
        """Extract text from DOCX file"""
        try:
            doc = DocxDocument(file_path)
            text = "\n".join([para.text for para in doc.paragraphs])
            return text
        except Exception as e:
            print(f"Error extracting DOCX: {e}")
            return ""
    
    def extract_text(self, file_path: str) -> str:
        """Extract text based on file extension"""
        if file_path.endswith('.pdf'):
            return self.extract_text_from_pdf(file_path)
        elif file_path.endswith('.docx'):
            return self.extract_text_from_docx(file_path)
        else:
            return ""
    
    def extract_email(self, text: str) -> str:
        """Extract email address from text"""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        return emails[0] if emails else ""

    def extract_phone(self, text: str) -> str:
        """Extract phone number from text"""
        phone_pattern = r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
        phones = re.findall(phone_pattern, text)
        return phones[0] if phones else ""

    def extract_linkedin(self, text: str) -> str:
        """Extract LinkedIn profile URL"""
        pattern = r'(?:https?://)?(?:www\.)?linkedin\.com/in/[\w\-]+'
        match = re.search(pattern, text, re.IGNORECASE)
        return match.group(0) if match else ""

    def extract_github(self, text: str) -> str:
        """Extract GitHub profile URL"""
        pattern = r'(?:https?://)?(?:www\.)?github\.com/[\w\-]+'
        match = re.search(pattern, text, re.IGNORECASE)
        return match.group(0) if match else ""

    def predict_domain(self, skills: List[str]) -> str:
        """
        Predict the primary domain/track of a candidate based on their skills.
        Returns the domain with the most skill matches.
        """
        if not skills:
            return 'General'
        skill_set = {s.lower() for s in skills}
        domain_scores: Dict[str, int] = {}
        for domain, domain_skill_list in self.DOMAIN_SKILLS.items():
            matches = sum(1 for s in domain_skill_list if s.lower() in skill_set)
            domain_scores[domain] = matches
        best = max(domain_scores, key=lambda d: domain_scores[d])
        return best if domain_scores[best] > 0 else 'General'
    
    def extract_skills(self, text: str) -> List[str]:
        """Extract technical skills from text"""
        found_skills = set()
        text_lower = text.lower()
        
        for skill in self.all_skills:
            # Case-insensitive matching with word boundaries
            pattern = r'\b' + re.escape(skill.lower()) + r'\b'
            if re.search(pattern, text_lower):
                found_skills.add(skill)
        
        return list(found_skills)
    
    def extract_experience_years(self, text: str) -> float:
        """Extract years of experience from text using multiple patterns"""
        patterns = [
            r'(\d+)\+?\s*years?\s+(?:of\s+)?(?:professional\s+)?experience',
            r'experience\s*:?\s*(\d+)\+?\s*years?',
            r'(\d+)\+?\s*yrs?\s+(?:of\s+)?experience',
            r'(\d+)\+?\s*years?\s+in\s+(?:the\s+)?(?:industry|field|software)',
        ]
        for pattern in patterns:
            match = re.search(pattern, text.lower())
            if match:
                val = float(match.group(1))
                if 0 < val <= 40:  # sanity clamp
                    return val

        # Fallback: count year spans like "2018 - 2023" or "2019 – Present"
        year_spans = re.findall(r'(20\d\d|19\d\d)\s*[-–]\s*(20\d\d|present)', text, re.IGNORECASE)
        total = 0.0
        for start_y, end_y in year_spans:
            end = 2026 if end_y.lower() == 'present' else int(end_y)
            total += max(0, end - int(start_y))
        if total > 0:
            return min(total, 40.0)

        return 0.0
    
    def extract_education(self, text: str) -> List[Dict[str, str]]:
        """Extract education information"""
        education = []
        doc = self.nlp(text)
        
        # Common degree patterns
        degree_patterns = [
            r'\b(B\.?Tech|Bachelor|B\.?E\.?|B\.?S\.?|B\.?A\.?)\b',
            r'\b(M\.?Tech|Master|M\.?E\.?|M\.?S\.?|M\.?A\.?|MBA)\b',
            r'\b(Ph\.?D\.?|Doctorate)\b'
        ]
        
        for pattern in degree_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                education.append({
                    'degree': match.group(0),
                    'field': self._extract_field_of_study(text, match.start())
                })
        
        return education
    
    def _extract_field_of_study(self, text: str, degree_position: int) -> str:
        """Extract field of study near degree mention"""
        # Common fields
        fields = ['Computer Science', 'Engineering', 'Information Technology', 
                 'Software Engineering', 'Data Science', 'Artificial Intelligence']
        
        # Check text around degree mention
        context = text[max(0, degree_position-100):degree_position+100].lower()
        
        for field in fields:
            if field.lower() in context:
                return field
        
        return "Unknown"
    
    def extract_certifications(self, text: str) -> List[str]:
        """Extract certifications"""
        certifications = []
        
        # Common certification keywords
        cert_keywords = ['certified', 'certification', 'certificate']
        
        lines = text.split('\n')
        for line in lines:
            line_lower = line.lower()
            if any(keyword in line_lower for keyword in cert_keywords):
                certifications.append(line.strip())
        
        return certifications
    
    def extract_name(self, text: str) -> str:
        """Extract candidate name (typically first few lines of resume)"""
        # Common technical terms that should NOT be considered names
        tech_terms = {
            'java', 'python', 'javascript', 'typescript', 'react', 'angular', 'vue',
            'node', 'express', 'django', 'flask', 'spring', 'docker', 'kubernetes',
            'aws', 'azure', 'gcp', 'linux', 'git', 'github', 'sql', 'mongodb',
            'redis', 'tensorflow', 'pytorch', 'keras', 'machine', 'learning',
            'deep', 'data', 'science', 'engineer', 'developer', 'software',
            'senior', 'junior', 'lead', 'manager', 'analyst', 'architect',
            'full', 'stack', 'frontend', 'backend', 'devops', 'resume', 'cv',
            'curriculum', 'vitae', 'profile', 'summary', 'objective', 'experience',
            'education', 'skills', 'projects', 'contact', 'phone', 'email',
            'address', 'linkedin', 'github', 'portfolio', 'website', 'html', 'css',
            'c++', 'c#', 'ruby', 'go', 'rust', 'swift', 'kotlin', 'scala', 'php',
            'mysql', 'postgresql', 'oracle', 'firebase', 'graphql', 'rest', 'api',
            'agile', 'scrum', 'jira', 'jenkins', 'ci', 'cd', 'terraform', 'ansible'
        }

        # Get first 10 lines where name typically appears
        lines = [line.strip() for line in text.split('\n') if line.strip()][:10]
        first_section = '\n'.join(lines[:5])  # Focus on first 5 lines for NER

        doc = self.nlp(first_section)

        # Try to find PERSON entities in first few lines
        for ent in doc.ents:
            if ent.label_ == "PERSON":
                name_candidate = ent.text.strip()
                # Filter out technical terms and single words that might be misidentified
                words = name_candidate.lower().split()
                # Check if any word is a tech term
                if not any(word in tech_terms for word in words):
                    # Valid name should have at least 2 characters and not be all uppercase single word
                    if len(name_candidate) >= 2:
                        # Avoid single uppercase words like "JAVA", "PYTHON"
                        if not (len(words) == 1 and name_candidate.isupper()):
                            return name_candidate

        # Fallback: Look for name pattern in first few lines
        # Names are typically on their own line, proper case, 2-4 words
        for line in lines[:5]:
            # Skip lines with common non-name indicators
            line_lower = line.lower()
            if any(indicator in line_lower for indicator in ['@', 'http', 'www', 'phone', 'email', 'address', 'resume', 'cv', 'objective', 'summary', '|', ':', '+91', '+1']):
                continue

            # Skip lines that are too long (likely not a name)
            if len(line) > 50:
                continue

            # Skip lines that are all tech terms
            words = line.split()
            if len(words) >= 2 and len(words) <= 4:
                # Check if looks like a name (proper case, no tech terms)
                if not any(word.lower() in tech_terms for word in words):
                    # Should have proper capitalization
                    if any(word[0].isupper() for word in words if word):
                        return line

        # Last fallback: first non-empty line that's not a tech term
        for line in lines[:3]:
            if line.lower() not in tech_terms and len(line) > 1 and len(line) < 50:
                return line

        return "Unknown"
    
    def parse_resume(self, file_path: str) -> Dict[str, Any]:
        """
        Main method to parse resume and extract all entities.
        Returns a structured JSON dict with all extracted information.
        """
        # Extract text
        text = self.extract_text(file_path)

        if not text:
            return {"error": "Could not extract text from file"}

        skills = self.extract_skills(text)

        # Extract all entities
        parsed_data = {
            "name": self.extract_name(text),
            "email": self.extract_email(text),
            "phone": self.extract_phone(text),
            "linkedin": self.extract_linkedin(text),
            "github": self.extract_github(text),
            "skills": skills,
            "experience_years": self.extract_experience_years(text),
            "education": self.extract_education(text),
            "certifications": self.extract_certifications(text),
            "domain": self.predict_domain(skills),
            "raw_text": text[:500] + "..." if len(text) > 500 else text
        }

        return parsed_data

# Singleton instance
_parser_instance = None

def get_resume_parser():
    """Get or create resume parser instance"""
    global _parser_instance
    if _parser_instance is None:
        _parser_instance = ResumeParser()
    return _parser_instance
