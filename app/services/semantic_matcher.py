"""
Semantic Matching Service using all-MiniLM-L6-v2
Implements cosine similarity for resume-job matching as described in the paper
"""
from sentence_transformers import SentenceTransformer
import numpy as np
from typing import Dict, List, Tuple
import json

class SemanticMatcher:
    """
    Semantic matching engine using all-MiniLM-L6-v2
    Model: sentence-transformers/all-MiniLM-L6-v2
    - Converts text to 384-dimensional dense vectors
    - Fast and efficient for semantic similarity tasks
    - Computes cosine similarity for matching
    """
    
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        """
        Initialize all-MiniLM-L6-v2 model
        This model maps sentences to a 384-dimensional dense vector space
        Optimized for semantic search and similarity tasks
        """
        print(f"Loading all-MiniLM model: {model_name}")
        self.model = SentenceTransformer(model_name)
        print("all-MiniLM model loaded successfully")
    
    def cosine_similarity(self, vec_a: np.ndarray, vec_b: np.ndarray) -> float:
        """
        Calculate cosine similarity between two vectors
        Formula: cos(θ) = (A · B) / (||A|| × ||B||)
        """
        dot_product = np.dot(vec_a, vec_b)
        norm_a = np.linalg.norm(vec_a)
        norm_b = np.linalg.norm(vec_b)
        
        if norm_a == 0 or norm_b == 0:
            return 0.0
        
        similarity = dot_product / (norm_a * norm_b)
        return float(similarity)
    
    def prepare_resume_text(self, parsed_resume: Dict) -> str:
        """
        Convert parsed resume JSON to coherent text for embedding
        """
        text_parts = []

        # Add skills
        if parsed_resume.get('skills'):
            skills = parsed_resume['skills']
            if isinstance(skills, list):
                skills_list = [str(s) for s in skills if s]
                if skills_list:
                    skills_text = "Skills: " + ", ".join(skills_list)
                    text_parts.append(skills_text)

        # Add experience
        exp_years = parsed_resume.get('experience_years')
        if exp_years:
            try:
                exp_text = f"Experience: {int(exp_years)} years"
                text_parts.append(exp_text)
            except (ValueError, TypeError):
                pass

        # Add education
        if parsed_resume.get('education'):
            edu_list = []
            education = parsed_resume['education']
            if isinstance(education, list):
                for edu in education:
                    if isinstance(edu, dict):
                        degree = edu.get('degree', '')
                        field = edu.get('field', '')
                        if degree or field:
                            edu_list.append(f"{degree} in {field}".strip())
                    else:
                        edu_list.append(str(edu))
            if edu_list:
                text_parts.append("Education: " + ", ".join(edu_list))

        # Add certifications
        if parsed_resume.get('certifications'):
            certifications = parsed_resume['certifications']
            if isinstance(certifications, list):
                cert_list = [str(c) for c in certifications[:3] if c]
                if cert_list:
                    cert_text = "Certifications: " + ", ".join(cert_list)
                    text_parts.append(cert_text)

        # Combine all parts
        resume_text = ". ".join(text_parts)
        return resume_text if resume_text else "Resume data"

    
    def prepare_job_text(self, job_data: Dict) -> str:
        """
        Convert job posting to coherent text for embedding
        """
        text_parts = []

        # Job title and company
        if job_data.get('title'):
            text_parts.append(f"Position: {job_data['title']}")

        if job_data.get('company'):
            text_parts.append(f"Company: {job_data['company']}")

        # Requirements
        if job_data.get('requirements'):
            text_parts.append(f"Requirements: {job_data['requirements']}")

        # Skills required
        if job_data.get('skills_required'):
            try:
                skills = job_data['skills_required']
                if isinstance(skills, str):
                    skills = json.loads(skills)
                if isinstance(skills, list):
                    skills_list = [str(s) for s in skills if s]
                    if skills_list:
                        skills_text = "Required Skills: " + ", ".join(skills_list)
                        text_parts.append(skills_text)
            except Exception:
                pass

        # Experience level
        if job_data.get('experience_level'):
            text_parts.append(f"Experience Level: {job_data['experience_level']}")

        # Description
        if job_data.get('description'):
            desc = str(job_data['description'])[:500]  # Limit description length
            text_parts.append(desc)

        job_text = ". ".join(text_parts)
        return job_text if job_text else "Job posting"
    
    def calculate_match_score(self, resume_data: Dict, job_data: Dict) -> Tuple[float, Dict]:
        """
        Calculate semantic match score between resume and job
        Returns: (similarity_score, breakdown_dict)
        """
        try:
            # Prepare texts
            resume_text = self.prepare_resume_text(resume_data)
            job_text = self.prepare_job_text(job_data)

            # Validate text is not empty
            if not resume_text or not resume_text.strip():
                resume_text = "Resume"
            if not job_text or not job_text.strip():
                job_text = "Job"

            # Generate embeddings
            resume_embedding = self.model.encode(resume_text)
            job_embedding = self.model.encode(job_text)

            # Calculate overall similarity
            overall_score = self.cosine_similarity(resume_embedding, job_embedding)

            # Calculate component-wise scores
            breakdown = self._calculate_breakdown(resume_data, job_data)

            return overall_score, breakdown
        except Exception as e:
            import traceback
            print(f"Error in calculate_match_score: {str(e)}")
            print(traceback.format_exc())
            # Return safe defaults on error
            return 0.5, {
                'skills_match': 0.0,
                'experience_match': 0.0,
                'education_match': 0.0,
                'matched_skills': [],
                'missing_skills': [],
                'recommendations': []
            }

    
    def _calculate_breakdown(self, resume_data: Dict, job_data: Dict) -> Dict:
        """
        Calculate detailed breakdown of matching components
        For Explainable AI (XAI)
        """
        breakdown = {
            'skills_match': 0.0,
            'experience_match': 0.0,
            'education_match': 0.0,
            'matched_skills': [],
            'missing_skills': [],
            'recommendations': []
        }

        try:
            # Skills matching
            resume_skills = resume_data.get('skills', [])
            if isinstance(resume_skills, str):
                try:
                    resume_skills = json.loads(resume_skills)
                except:
                    resume_skills = []
            resume_skills = set(str(s).lower() for s in resume_skills if s)

            try:
                job_skills_raw = job_data.get('skills_required', '[]')
                job_skills = json.loads(job_skills_raw) if isinstance(job_skills_raw, str) else job_skills_raw
                job_skills = set(str(s).lower() for s in job_skills if s) if isinstance(job_skills, list) else set()
            except Exception:
                job_skills = set()

            if job_skills:
                matched = resume_skills.intersection(job_skills)
                missing = job_skills - resume_skills

                breakdown['matched_skills'] = list(matched)
                breakdown['missing_skills'] = list(missing)
                breakdown['skills_match'] = len(matched) / len(job_skills) if job_skills else 0.0
            else:
                breakdown['skills_match'] = 0.5  # Neutral score if no job skills specified

            # Experience matching
            resume_exp = resume_data.get('experience_years', 0)
            try:
                resume_exp = int(resume_exp) if resume_exp else 0
            except (ValueError, TypeError):
                resume_exp = 0

            job_exp_level = str(job_data.get('experience_level', '')).lower()

            exp_mapping = {
                'entry': (0, 2),
                'junior': (0, 3),
                'mid': (3, 5),
                'senior': (5, 100)
            }

            for level, (min_exp, max_exp) in exp_mapping.items():
                if level in job_exp_level:
                    if min_exp <= resume_exp <= max_exp:
                        breakdown['experience_match'] = 1.0
                    elif resume_exp < min_exp:
                        breakdown['experience_match'] = resume_exp / min_exp if min_exp > 0 else 0.5
                    else:
                        breakdown['experience_match'] = 0.8  # Overqualified
                    break

            # Education matching (simplified)
            if resume_data.get('education'):
                edu = resume_data['education']
                if isinstance(edu, list) and len(edu) > 0:
                    breakdown['education_match'] = 0.8  # Base match if has degree
                elif edu:
                    breakdown['education_match'] = 0.8

            # Generate recommendations
            if breakdown['missing_skills']:
                missing_list = list(breakdown['missing_skills'])[:5]
                breakdown['recommendations'].append(
                    f"Consider learning: {', '.join(missing_list)}"
                )

            if breakdown['experience_match'] < 1.0 and resume_exp < 3:
                breakdown['recommendations'].append(
                    "Gain more experience through internships or projects"
                )

        except Exception as e:
            import traceback
            print(f"Error in _calculate_breakdown: {str(e)}")
            print(traceback.format_exc())

        return breakdown

    
    def batch_match(self, resume_data: Dict, job_list: List[Dict]) -> List[Dict]:
        """
        Match one resume against multiple jobs
        Returns sorted list by match score
        """
        results = []
        
        for job in job_list:
            score, breakdown = self.calculate_match_score(resume_data, job)
            results.append({
                'job_id': job.get('id'),
                'job_title': job.get('title'),
                'score': score,
                'breakdown': breakdown
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

# Singleton instance
_matcher_instance = None

def get_semantic_matcher():
    """Get or create semantic matcher instance"""
    global _matcher_instance
    if _matcher_instance is None:
        _matcher_instance = SemanticMatcher()
    return _matcher_instance
