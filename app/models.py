"""
OptiHire Data Models (Reference / Documentation Only)
-------------------------------------------------------
NOTE: This project uses file-based JSON storage (app/storage.py + app/user.py).
      These classes are plain Python dataclasses for documentation purposes only 
      and are NOT connected to any database.  Do NOT import SQLAlchemy here.
"""
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime


@dataclass
class UserModel:
    """Represents a user (recruiter or candidate)"""
    id: str                          # 8-char UUID fragment
    username: str
    email: str
    password_hash: str
    full_name: str
    user_type: str                   # 'recruiter' | 'candidate'
    created_at: str                  # ISO datetime string
    is_active: bool = True


@dataclass
class JobModel:
    """Represents a job posting created by a recruiter"""
    id: str
    title: str
    company: str
    description: str
    requirements: str
    recruiter_id: str
    skills_required: str = "[]"      # JSON-encoded list of skill strings
    location: str = ""
    job_type: str = "Full-time"      # Full-time | Part-time | Contract
    experience_level: str = "Mid"    # Entry | Junior | Mid | Senior
    salary_range: str = ""
    created_at: str = ""
    updated_at: str = ""
    is_active: bool = True


@dataclass
class ResumeModel:
    """Represents a parsed resume uploaded by a candidate"""
    id: str
    user_id: str
    filename: str
    file_path: str
    parsed_data: Dict[str, Any] = field(default_factory=dict)
    # Parsed fields cached from parsed_data for quick access
    skills: str = "[]"              # JSON-encoded list
    experience_years: float = 0.0
    education: str = "[]"           # JSON-encoded list
    certifications: str = "[]"      # JSON-encoded list
    created_at: str = ""
    updated_at: str = ""


@dataclass
class ApplicationModel:
    """Represents a job application submitted by a candidate"""
    id: str
    job_id: str
    candidate_id: str
    resume_id: str
    similarity_score: float = 0.0   # 0.0 – 1.0 (cosine similarity via S-BERT)
    match_breakdown: Dict = field(default_factory=dict)
    # Keys: skills_match, experience_match, education_match,
    #       matched_skills, missing_skills, recommendations
    status: str = "pending"         # pending | shortlisted | interview | hired | rejected
    cover_letter: str = ""
    interview_questions: List[Dict] = field(default_factory=list)
    interview_feedback: str = ""
    applied_at: str = ""
    updated_at: str = ""


@dataclass
class NotificationModel:
    """Represents a notification sent to a user"""
    id: str
    user_id: str
    title: str
    message: str
    notification_type: str = "info"  # info | success | warning | rejection
    application_id: Optional[str] = None
    is_read: bool = False
    created_at: str = ""


@dataclass
class ScoreBreakdownModel:
    """Explainable AI (XAI) detailed scoring breakdown — embedded in ApplicationModel"""
    skills_match_score: float = 0.0
    experience_match_score: float = 0.0
    education_match_score: float = 0.0
    overall_semantic_score: float = 0.0
    matched_skills: List[str] = field(default_factory=list)
    missing_skills: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
