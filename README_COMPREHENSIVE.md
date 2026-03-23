# 🎯 OptiHire - AI-Powered Recruitment Platform

**Comprehensive Technical Documentation**

> An enterprise-grade recruitment management system combining AI-driven candidate matching, live interview rooms, and intelligent resume parsing—all powered by Flask with zero database overhead.

---

## 📋 Table of Contents

1. [Executive Summary](#executive-summary)
2. [System Architecture](#system-architecture)
3. [Key Features](#key-features)
4. [Technology Stack](#technology-stack)
5. [Installation & Setup](#installation--setup)
6. [Project Structure](#project-structure)
7. [Core Modules](#core-modules)
8. [API Reference](#api-reference)
9. [Data Storage](#data-storage)
10. [User Workflows](#user-workflows)
11. [Live Interview Room](#live-interview-room)
12. [Testing & Demo](#testing--demo)
13. [Deployment Guide](#deployment-guide)
14. [Security & Best Practices](#security--best-practices)
15. [Troubleshooting](#troubleshooting)

---

## Executive Summary

**OptiHire** is a full-stack AI-powered recruitment platform built with Python/Flask that eliminates the need for traditional databases by leveraging file-based JSON storage. The system provides:

- **Smart Resume Parsing**: Automatic extraction of skills, experience, and qualifications using spaCy NER
- **Semantic Job Matching**: AI-driven candidate-to-job matching using Sentence-BERT (0-100% similarity scores)
- **Live Interview Rooms**: Real-time video conferencing with collaborative code editing and instant code execution
- **AI Interview Generation**: Automatic technical interview question generation using Google Gemini API
- **Intelligent Ranking**: Auto-ranked candidate lists based on AI matching scores
- **Complete ATS**: Full Application Tracking System with recruiter dashboards and candidate management

**Perfect for**: Startups, small companies, hackathons, and developers who need a production-ready recruitment system without database infrastructure.

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                       FRONTEND LAYER                             │
│  Web UI (Jinja2) | CodeMirror Editor | Jitsi Video | Dashboard   │
└──────────────────────────┬──────────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────────┐
│                    FLASK API LAYER                               │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │ Route Blueprints                                        │    │
│  │ • auth.py (Login/Register)                              │    │
│  │ • jobs.py (Job CRUD)                                    │    │
│  │ • candidates.py (Resume Upload & Job Apply)            │    │
│  │ • interviews.py (Interview Slot Scheduling)            │    │
│  │ • interview_room.py (Live Interview & Feedback)        │    │
│  │ • dashboard.py (Recruiter & Candidate Dashboards)      │    │
│  │ • analytics.py (Recruitment Analytics)                 │    │
│  │ • profile.py (User Profile Management)                 │    │
│  │ • main.py (Home & Navigation)                           │    │
│  └─────────────────────────────────────────────────────────┘    │
└──────────────────────────┬──────────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────────┐
│                    SERVICE LAYER                                 │
│  ┌─────────────┬──────────────┬──────────┬──────────┬──────┐    │
│  │Resume Parser│Semantic Match│AI Interv │  Email   │Cal  │    │
│  │  spaCy NER  │  S-BERT      │ Gemini   │  SMTP    │Sched│    │
│  └─────────────┴──────────────┴──────────┴──────────┴──────┘    │
└──────────────────────────┬──────────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────────┐
│                   STORAGE LAYER                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │           File-Based JSON Storage (storage.py)           │   │
│  └──────────────────────────────────────────────────────────┘   │
│  • data/users.json          (User accounts & credentials)      │
│  • data/jobs.json           (Job postings & descriptions)      │
│  • data/resumes.json        (Parsed resume data)               │
│  • data/applications.json   (Applications & interview state)   │
│  • data/notifications.json  (User notifications)               │
└──────────────────────────┬──────────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────────┐
│              EXTERNAL APIs & SERVICES                            │
│  ┌────────────┬─────────┬──────────┬──────────┐                 │
│  │Google      │Piston   │Jitsi     │Gmail     │                 │
│  │Gemini LLM  │Code Exec│Video     │SMTP      │                 │
│  │(Interview) │(Python/ │(Meetings)│(Email)   │                 │
│  │            │JS/Java) │          │          │                 │
│  └────────────┴─────────┴──────────┴──────────┘                 │
└──────────────────────────────────────────────────────────────────┘
```

---

## Key Features

### 🔐 **Authentication & Authorization**
- Secure login/registration with role-based access control
- Dual user types: **Recruiters** and **Candidates**
- Password hashing with Werkzeug PBKDF2
- Session management via Flask-Login
- Protected routes with @login_required decorators

### 📄 **Resume Management**
- Resume upload with file validation
- **Automatic Skill Extraction** using spaCy NER (Named Entity Recognition)
- Extracted skills stored and indexed for quick lookup
- Resume preview with formatted text display
- Support for TXT, PDF (text layer), and DOCX formats

### 🤖 **AI-Powered Job Matching**
- **Semantic Similarity Matching** using Sentence-BERT (all-MiniLM-L6-v2)
- Compares resume content against job descriptions
- Produces explainable match percentages (0-100%)
- **Match Breakdown** showing:
  - Required skills match rate
  - Experience level alignment
  - Role compatibility score
  - Confidence threshold indicators

### 🎥 **Live Interview Rooms**
- **Full-Screen Interview Platform** with real-time features
- **Jitsi Meet Integration** for HD video conferencing (no account setup needed)
- **Collaborative Code Editor** (CodeMirror 5) supporting 8 languages:
  - Python, JavaScript, TypeScript, Java, C++, Go, Rust, SQL
- **Real-Time Code Sync** via AJAX polling (2-second intervals)
- **Instant Code Execution** via Piston API (Python, JS, Java, C++, Go, Rust)
- **Interview Questions Panel** showing AI-generated technical questions
- **Recruiter's Notes** with auto-save (1-second debounce)
- **Output Terminal** showing code execution results with color coding

### 🎯 **AI Interview Generation**
- Automatic technical question generation using Google Gemini API
- Questions tailored to job requirements and skills
- Difficulty levels (Beginner, Intermediate, Advanced)
- Follow-up feedback generation based on candidate performance
- Role-specific interview patterns

### 📊 **Interview Scheduling**
- Calendar-based slot selection interface
- Recruiter sends candidate multiple time options
- Candidate confirms preferred slot
- Automatic email notifications for both parties
- Interview duration customization

### ⭐ **Recruiter Feedback & Scoring**
- Post-interview star rating system (1-5 stars)
- Detailed feedback textarea with character limits
- Hiring decision options: **Hire**, **Reject**, or **Pending**
- Automatic candidate notification on decision
- Feedback stored with interview data

### 📈 **Analytics & Reporting**
- Recruiter dashboard with key metrics:
  - Total job postings
  - Applications received
  - Interview conversion rates
  - Average matching scores
- Candidate dashboard showing:
  - Applied positions
  - Match scores
  - Application status
  - Interview availability

### 🔔 **Smart Notifications**
- Email notifications for application updates
- Recruiter alerts on new applications
- Candidate notifications on interview invitations
- Automatic status update messages
- Real-time in-app notifications

---

## Technology Stack

| Category | Technology | Purpose |
|----------|-----------|---------|
| **Backend Framework** | Flask 3.0.0 | Web application server |
| **Python Version** | 3.8+ | Core language |
| **Web Server** | Werkzeug (Flask built-in) | HTTP server |
| **Authentication** | Flask-Login + Werkzeug | User sessions & password hashing |
| **Frontend** | Jinja2 + Tailwind CSS | HTML templates & styling |
| **Storage** | JSON Files (No Database) | Data persistence |
| **NLP/ML** | spaCy (en_core_web_sm) | Resume parsing & skill extraction |
| **AI Matching** | Sentence-BERT (all-MiniLM-L6-v2) | Semantic similarity scoring |
| **LLM Integration** | Google Gemini API | Interview question generation |
| **Code Execution** | Piston API | Execute user code (Python/JS/Java/C++) |
| **Video Conferencing** | Jitsi Meet External API | Live interview video |
| **Code Editor** | CodeMirror 5 | Real-time collaborative editing |
| **Email Service** | Gmail SMTP | Email notifications |
| **Rate Limiting** | Flask-Limiter | API rate protection |

---

## Installation & Setup

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- Git (for version control)
- Gmail account (for SMTP email notifications - optional)
- Google Gemini API key (for interview AI - optional)

### Step-by-Step Installation

#### 1. **Clone/Download the Project**
```bash
cd /path/to/project
# or unzip the downloaded file
```

#### 2. **Create Virtual Environment**
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# macOS/Linux
python3 -m venv .venv
source .venv/bin/activate
```

#### 3. **Install Dependencies**
```bash
pip install -r requirements.txt
```

**Key packages installed:**
- Flask==3.0.0
- Flask-Login==0.6.3
- spacy==3.7.2
- sentence-transformers==3.0.1
- Google-generativeai (for Gemini API)
- python-dotenv (for environment variables)

#### 4. **Download spaCy Language Model**
```bash
python -m spacy download en_core_web_sm
```

This ~40MB model enables resume parsing and NER extraction.

#### 5. **Configure Environment (Optional)**
```bash
# Copy example configuration
cp .env.example .env

# Edit .env and add your API keys:
# GEMINI_API_KEY=your_key_here
# EMAIL_PASSWORD=your_gmail_password
```

#### 6. **Create Sample Data**
```bash
python test_auth.py
```

This generates:
- 2 sample users (recruiter + candidate)
- 5 sample job postings
- 3 demo resumes
- Resume parsing demonstrations

#### 7. **Run the Application**
```bash
python run.py
```

Server starts at **http://127.0.0.1:5000**

#### 8. **Access the Application**
- Open browser: `http://localhost:5000`
- Login page loads automatically
- Use demo credentials (see [Testing & Demo](#testing--demo) section)

---

## Project Structure

```
tax/
├── app/
│   ├── __init__.py                # Flask app factory & blueprint registration
│   ├── models.py                  # User & Resume data models
│   ├── storage.py                 # File I/O manager (JSON operations)
│   ├── user.py                    # User model for Flask-Login
│   │
│   ├── routes/                    # Blueprints (business logic)
│   │   ├── __init__.py
│   │   ├── auth.py                # Login/Register (26 routes)
│   │   ├── main.py                # Homepage (1 route)
│   │   ├── jobs.py                # Job CRUD (8 routes)
│   │   ├── candidates.py          # Resume upload, job apply (6 routes)
│   │   ├── dashboard.py           # Recruiter/candidate dashboards (6 routes)
│   │   ├── interviews.py          # Interview slot booking (4 routes)
│   │   ├── interview_room.py      # Live interview rooms (5 routes)
│   │   ├── profile.py             # User profile management (4 routes)
│   │   └── analytics.py           # Analytics & reporting (2 routes)
│   │
│   ├── services/                  # Business logic & external integrations
│   │   ├── __init__.py
│   │   ├── resume_parser.py       # spaCy NER for skill extraction
│   │   ├── semantic_matcher.py    # Sentence-BERT matching (0-100%)
│   │   ├── ai_interviewer.py      # Google Gemini interview Q&A
│   │   ├── email_service.py       # Gmail SMTP notifications
│   │   └── calendar_service.py    # Interview scheduling
│   │
│   └── templates/                 # HTML views (Jinja2)
│       ├── base.html              # Base template with theme support
│       ├── index.html             # Homepage
│       ├── about.html             # About page
│       ├── how_it_works.html      # Feature explanation
│       ├── auth/
│       │   ├── login.html         # Login form
│       │   └── register.html      # Signup form
│       ├── jobs/
│       │   ├── list.html          # Browse jobs
│       │   ├── view.html          # Job details
│       │   ├── create.html        # Create job (recruiter)
│       │   └── edit.html          # Edit job (recruiter)
│       ├── candidates/
│       │   ├── upload_resume.html # Resume upload
│       │   ├── view_resume.html   # Resume preview
│       │   ├── apply.html         # Apply to job
│       │   ├── my_applications.html  # My applications
│       │   └── view_application.html # Application details
│       ├── dashboard/
│       │   ├── recruiter.html     # Recruiter dashboard
│       │   ├── candidate.html     # Candidate dashboard
│       │   └── job_applications.html # Applications list
│       ├── interview/
│       │   ├── room.html          # Live interview room (full-screen)
│       │   └── feedback.html      # Post-interview feedback form
│       ├── profile/
│       │   ├── edit.html          # Edit profile
│       │   └── notifications.html # Notification center
│       └── analytics/
│           └── recruiter_analytics.html # Analytics dashboard
│
├── data/                          # File-based storage (no database!)
│   ├── users.json                 # All user accounts
│   ├── jobs.json                  # All job postings
│   ├── resumes.json               # All resumes (parsed)
│   ├── applications.json          # All job applications
│   └── notifications.json         # All notifications
│
├── uploads/                       # Resume file uploads
│   └── [resume_files].txt/.pdf/.docx
│
├── logs/                          # Application logs
│
├── config.py                      # Flask configuration
├── run.py                         # Application entry point
├── test_auth.py                   # Sample data generator
│
├── requirements.txt               # Python dependencies
├── .env.example                   # Environment variables template
├── .gitignore                     # Git ignore rules
│
├── README.md                      # Quick start guide
├── GUIDE.md                       # Detailed user guide
├── TESTING.md                     # Testing procedures
├── DEPLOYMENT.md                  # Production deployment
└── DEMO_CREDENTIALS.md            # Demo login credentials
```

---

## Core Modules

### 🔐 **app/__init__.py** - Flask Application Factory
**Responsibility**: Initialize Flask app, register blueprints, configure settings

**Key Components**:
- Creates Flask application instance
- Loads configuration from `config.py`
- Registers all route blueprints
- Sets up Flask-Login manager
- Configures error handlers (404, 500)
- Initializes rate limiter

**Code Pattern**:
```python
def create_app():
    app = Flask(__name__)
    app.config.from_object(config)
    
    # Register blueprints
    from app.routes import auth, jobs, candidates, ...
    app.register_blueprint(auth.bp)
    app.register_blueprint(jobs.bp)
    # ... more blueprints
    
    return app
```

---

### 💾 **app/storage.py** - File I/O Manager
**Responsibility**: All JSON read/write operations for data persistence

**Key Methods**:
- `get_user_by_id()` - Retrieve user by ID
- `get_job_by_id()` - Retrieve job posting
- `get_application_by_id()` - Fetch application
- `update_application()` - Update application status/interview data
- `create_notification()` - Add notification
- Thread-safe file locking prevents corruption

**Data Files**:
- `data/users.json` → User accounts (passwords hashed)
- `data/jobs.json` → Job postings with descriptions
- `data/resumes.json` → Parsed resume content
- `data/applications.json` → Application records
- `data/notifications.json` → User notifications

---

### 📄 **app/services/resume_parser.py** - NLP Resume Parsing
**Responsibility**: Extract structured data from resumes

**Features**:
- Uses spaCy `en_core_web_sm` for Named Entity Recognition
- Extracts: **skills**, **experience**, **education**, **contact info**
- Custom skill database with ~500+ technical skills
- Normalizes extracted text
- Stores results in `data/resumes.json`

**Example**:
```python
from app.services.resume_parser import parse_resume

text = "Python developer with 5 years Django experience..."
result = parse_resume(text)
# result['skills'] = ['Python', 'Django', '...']
# result['experience_years'] = 5
```

---

### 🤖 **app/services/semantic_matcher.py** - AI Job Matching
**Responsibility**: Score candidate-to-job fit via embeddings

**Algorithm**:
1. Converts resume into embedding vector (Sentence-BERT)
2. Converts job description into embedding vector
3. Computes cosine similarity (0.0 → 1.0)
4. Scales to percentage (0% → 100%)
5. Generates **match breakdown**:
   - Required skills match
   - Experience alignment
   - Role compatibility

**Performance**: Matches 100+ resumes in <5 seconds

---

### 🎓 **app/services/ai_interviewer.py** - Interview Generation
**Responsibility**: Generate interview questions and feedback using LLM

**Uses Google Gemini API**:
- Reads job description & candidate resume
- Generates 5-10 technical interview questions
- Customizes difficulty based on experience level
- After interview: generates feedback from code & notes

---

### 📧 **app/services/email_service.py** - Notification System
**Responsibility**: Send emails via Gmail SMTP

**Email Types**:
- Application received confirmation
- Interview invitation with slot options
- Interview slot confirmed notification
- Hiring decision (Hired/Rejected)
- Status updates

---

### 📅 **app/services/calendar_service.py** - Interview Scheduling
**Responsibility**: Manage interview slot scheduling

**Features**:
- Recruiter proposes multiple time slots
- Candidate selects preferred slot
- Automatic conflict detection
- Duration customization
- Notification on confirmation

---

## API Reference

### Base URL
```
http://localhost:5000
```

### Authentication Routes (`/auth`)

#### Register
```
POST /auth/register
Content-Type: application/json

{
  "full_name": "John Doe",
  "username": "johndoe",
  "email": "john@example.com",
  "password": "securepass",
  "user_type": "candidate"  // or "recruiter"
}

Response: 302 (redirect to login)
```

#### Login
```
POST /auth/login
Content-Type: application/json

{
  "username": "johndoe",
  "password": "securepass",
  "remember_me": true
}

Response: 302 (redirect to dashboard)
```

#### Logout
```
GET /auth/logout

Response: 302 (redirect to homepage)
```

---

### Job Routes (`/jobs`)

#### List Jobs
```
GET /jobs/list
Response: HTML page with all jobs, ranked by match score (if logged in as candidate)
```

#### Create Job (Recruiter Only)
```
POST /jobs/create
{
  "title": "Senior Python Developer",
  "description": "Required: 5+ years Python...",
  "location": "San Francisco, CA",
  "salary_min": 120000,
  "salary_max": 180000,
  "skills_required": ["Python", "Django", "AWS"]
}

Response: 302 (redirect to job view)
```

#### View Job
```
GET /jobs/view/<job_id>
Response: HTML page showing job details + apply button (for candidates)
```

---

### Candidate Routes (`/candidates`)

#### Upload Resume
```
POST /candidates/upload-resume
Content-Type: multipart/form-data

file: <resume.pdf or .txt or .docx>

Response: Parsed resume data + extracted skills
```

#### Apply for Job
```
POST /candidates/apply/<job_id>
Response: Application created, match score calculated
```

#### View Application
```
GET /candidates/view-application/<application_id>
Response: Application details, match breakdown, interview status
```

---

### Interview Routes (`/interviews`)

#### Choose Slot
```
GET /interviews/choose-slot/<application_id>?token=<slot_token>
Response: Slot picker calendar interface
```

#### Select Slot (Candidate)
```
POST /interviews/select-slot/<application_id>
{
  "chosen_slot": "2026-03-25 10:00 AM"
}

Response: Confirmation + notification sent
```

---

### Interview Room Routes (`/interview`)

#### Enter Interview Room
```
GET /interview/room/<application_id>
Response: Full-screen live interview room (Jitsi + CodeMirror)
```

#### Poll Room State (AJAX)
```
GET /interview/room/<application_id>/state
Response: {
  "code": "print('hello')",
  "language": "python",
  "ended": false
}
```

#### Save Code (AJAX)
```
POST /interview/room/<application_id>/state
{
  "code": "print('hello')",
  "language": "python",
  "notes": "Good problem-solving..."
}

Response: { "ok": true, "saved_at": "..." }
```

#### End Interview (Recruiter)
```
POST /interview/room/<application_id>/end
Response: 302 (redirect to feedback form)
```

#### Submit Feedback
```
POST /interview/room/<application_id>/feedback
{
  "overall_score": 4,
  "final_feedback": "Strong candidate...",
  "decision": "hired"  // or "rejected" or "pending"
}

Response: Email sent, application updated
```

---

### Dashboard Routes (`/dashboard`)

#### Recruiter Dashboard
```
GET /dashboard/recruiter
Response: Job listings, applications, analytics
```

#### Candidate Dashboard
```
GET /dashboard/candidate
Response: Applied jobs, match scores, notifications
```

---

### Analytics Routes (`/analytics`)

#### Recruiter Analytics
```
GET /analytics/recruiter
Response: Dashboard with charts and metrics
```

---

## Data Storage

### Why No Database?

**Advantages**:
- ✅ **Zero Setup**: No PostgreSQL/MongoDB/MySQL needed
- ✅ **Easy Debugging**: Open JSON files in any text editor
- ✅ **Simple Deployment**: Just copy files
- ✅ **Cost Effective**: No database server costs
- ✅ **Perfect for MVP**: Quick prototyping

**Limitations**:
- Not ideal for 100K+ concurrent users
- No built-in query optimization
- All data fits in memory for each request

**Best For**: <1000 active users, internal tools, MVPs, demos

---

### JSON Schema

#### users.json
```json
{
  "id": "uuid-123",
  "username": "johndoe",
  "email": "john@example.com",
  "full_name": "John Doe",
  "password_hash": "pbkdf2:sha256:...",
  "user_type": "candidate",
  "created_at": "2026-03-20T10:30:00",
  "updated_at": "2026-03-20T10:30:00"
}
```

#### jobs.json
```json
{
  "id": "job-456",
  "title": "Senior Python Developer",
  "description": "We are hiring a senior...",
  "recruiter_id": "uuid-123",
  "location": "San Francisco, CA",
  "salary_min": 120000,
  "salary_max": 180000,
  "skills_required": ["Python", "Django", "AWS"],
  "created_at": "2026-03-20T10:30:00"
}
```

#### resumes.json
```json
{
  "id": "resume-789",
  "candidate_id": "uuid-456",
  "filename": "john_resume.pdf",
  "text": "John Doe. Senior Software Engineer...",
  "skills": ["Python", "JavaScript", "Django"],
  "experience_years": 5,
  "parsed_at": "2026-03-20T10:30:00"
}
```

#### applications.json
```json
{
  "id": "app-001",
  "candidate_id": "uuid-456",
  "job_id": "job-456",
  "resume_id": "resume-789",
  "status": "interview",
  "similarity_score": 0.87,
  "match_breakdown": {
    "skills_match": 0.92,
    "experience_match": 0.85,
    "role_fit": 0.80
  },
  "chosen_slot": "2026-03-25 10:00 AM",
  "interview_duration": 60,
  "room_opened_at": "2026-03-25T10:00:00",
  "room_code": "print('hello')",
  "room_language": "python",
  "interview_overall_score": 4,
  "interview_final_feedback": "Strong candidate...",
  "created_at": "2026-03-20T10:30:00"
}
```

---

## User Workflows

### 👨‍💼 Recruiter Workflow

```
1. REGISTER & LOGIN
   ├── Create account (recruiter type)
   └── Login to recruiter dashboard

2. POST A JOB
   ├── Fill job details (title, description, salary)
   ├── Specify required skills
   └── Job appears on platform

3. REVIEW APPLICATIONS
   ├── View job applications (auto-ranked by AI score)
   ├── Click on application
   └── See candidate resume & match breakdown

4. SCHEDULE INTERVIEW
   ├── Select "Schedule Interview"
   ├── Send multiple time slot options
   └── Candidate receives email with choices

5. CONDUCT INTERVIEW
   ├── Open interview room at scheduled time
   ├── Agree with candidate in Jitsi video
   ├── Ask technical questions
   ├── Watch candidate code
   └── Take notes in notes panel

6. PROVIDE FEEDBACK
   ├── Click "End Interview"
   ├── Rate performance (1-5 stars)
   ├── Write detailed feedback
   ├── Select hiring decision (Hire/Reject/Pending)
   └── Candidate receives notification
```

---

### 👨‍💻 Candidate Workflow

```
1. REGISTER & LOGIN
   ├── Create account (candidate type)
   └── Login to candidate dashboard

2. UPLOAD RESUME
   ├── Click "Upload Resume"
   ├── Select PDF/TXT/DOCX file
   ├── Skills auto-extracted
   └── Resume appears on profile

3. BROWSE & APPLY FOR JOBS
   ├── Go to "Browse Jobs"
   ├── See jobs ranked by match score
   ├── Click "Apply" for job
   └── Application submitted

4. RECEIVE INTERVIEW INVITATION
   ├── Get email with interview slot options
   ├── Click "Choose My Slot"
   ├── Select preferred time
   └── Confirm selection

5. TAKE INTERVIEW
   ├── Open interview room
   ├── Join Jitsi video call
   ├── See interview questions
   ├── Write code in editor
   ├── Click "Run" to execute
   └── See output in terminal

6. RECEIVE DECISION
   ├── Interview ends
   ├── Get notification with feedback
   ├── See recruiter's notes
   └── View hiring decision
```

---

## Live Interview Room

### Features

**Real-Time Collaboration**:
- **Jitsi Meet Video**: HD video conferencing (no account needed)
- **CodeMirror Editor**: Syntax-highlighted code editing
- **Live Code Sync**: Changes propagate to both users in ~2 seconds
- **Code Execution**: Run Python, JavaScript, Java, C++, Go, Rust instantly
- **Interview Questions**: Display technical questions on screen

**Recruiter Tools**:
- 📝 **Notes Panel**: Write observations (auto-save)
- ⏱️ **Timer**: Track interview duration
- ⏹️ **End Button**: Conclude interview session
- 🖥️ **Full Screen**: Maximize focus on conversation

**Candidate Experience**:
- Clean, distraction-free interface
- Can ask questions via chat
- See interview questions while coding
- Receive real-time code execution results

---

## Testing & Demo

### Demo Credentials

**Recruiter Account** (Full Access):
```
Email:    recruiter@example.com
Password: password123
```

**Candidate Account** (Candidate Features):
```
Email:    candidate@example.com
Password: password123
```

### Generate Sample Data

```bash
python test_auth.py
```

Creates:
- 2 user accounts (recruiter + candidate)
- 5 sample job postings
- 3 demo resumes with parsed skills
- Sample applications with match scores

### Testing Checklist

#### Authentication ✅
- [ ] Register new user
- [ ] Login with valid credentials
- [ ] Reject invalid password
- [ ] Logout successfully

#### Job Management ✅
- [ ] Create job posting (recruiter)
- [ ] Browse all jobs (candidate)
- [ ] View detailed job page
- [ ] Search & filter jobs

#### Resume & Skill Extraction ✅
- [ ] Upload resume (PDF/TXT)
- [ ] Verify skills extracted correctly
- [ ] View resume preview
- [ ] Check parsed data in backend

#### Job Application ✅
- [ ] Apply for job (candidate)
- [ ] See match score & breakdown
- [ ] View application status
- [ ] Check notifications

#### Interview Scheduling ✅
- [ ] Send interview slots (recruiter)
- [ ] Confirm slot selection (candidate)
- [ ] Verify email notification
- [ ] Check status updated

#### Live Interview ✅
- [ ] Open interview room (both users)
- [ ] Start Jitsi video call
- [ ] Change programming language
- [ ] Type and sync code between windows
- [ ] Execute code and see output
- [ ] Save recruiter notes
- [ ] View interview questions

#### Feedback ✅
- [ ] End interview (recruiter)
- [ ] Submit star rating & feedback
- [ ] Select hiring decision
- [ ] Verify candidate notified
- [ ] Check application updated

### Testing in Two Browsers/Tabs

**To test simultaneously with recruiter & candidate**:

1. **Normal Window** (Recruiter):
   ```
   Login: recruiter@example.com / password123
   Navigate to interview room
   ```

2. **Incognito/InPrivate Window** (Candidate):
   ```
   Login: candidate@example.com / password123
   Navigate to same interview room
   ```

3. **Both windows** now at `http://127.0.0.1:5000/interview/room/<app-id>`
4. **Code changes** sync in real-time (2-second delay)
5. **Video** works in both windows simultaneously
6. **Run code** executes for both users

---

## Deployment Guide

### Local Development
```bash
python run.py
```
Runs on `http://127.0.0.1:5000` with auto-reload on file changes

### Production Deployment

#### Option 1: Heroku
```bash
# Create Procfile
web: gunicorn run:app

# Deploy
heroku create your-app-name
git push heroku main
```

#### Option 2: AWS/DigitalOcean
```bash
# Install Gunicorn
pip install gunicorn

# Run with Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 run:app
```

#### Option 3: Docker
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
RUN python -m spacy download en_core_web_sm

COPY . .
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "run:app"]
```

---

## Security & Best Practices

### 🔒 Authentication Security
- ✅ Passwords hashed with Werkzeug PBKDF2 (not plaintext)
- ✅ Session tokens regenerated on login
- ✅ CSRF protection on forms
- ✅ Secure cookie flags (HttpOnly, SameSite)

### 🔐 Data Security
- ✅ Files stored in `data/` (should be .gitignore'd)
- ✅ Uploads stored in `uploads/` with validation
- ✅ Sensitive data never logged
- ✅ API keys stored in `.env` (not committed)

### ⚠️ Production Checklist
- [ ] Set `SECRET_KEY` to random 32-character string
- [ ] Set `DEBUG = False` in config
- [ ] Add HTTPS/SSL certificate
- [ ] Backup `data/` directory regularly
- [ ] Monitor disk space (JSON files grow over time)
- [ ] Set up log rotation
- [ ] Enable rate limiting

### 🔑 Environment Variables (.env)
```
SECRET_KEY=your-32-char-random-key
DEBUG=False
DATABASE_URL=sqlite:///app.db  # Future use
GEMINI_API_KEY=your-api-key
EMAIL_USER=your-email@gmail.com
EMAIL_PASSWORD=your-app-password
```

---

## Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'spacy'"

**Solution**:
```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

---

### Issue: Resume parsing not extracting skills

**Causes**:
- Resume text is image-based (scanned PDF)
- Skills not in standard format

**Solution**:
- Use TXT or text-based PDF
- Ensure skills listed explicitly
- Check `data/resumes.json` for extracted data

---

### Issue: Interview room video not loading

**Causes**:
- Jitsi Meet API unreachable
- Browser blocked camera/mic
- Network connectivity issue

**Solution**:
1. Ensure internet connection active
2. Click allow when browser asks for camera/mic
3. Try different browser (Chrome/Edge/Firefox)
4. Check console for errors (F12)
5. Try opening Jitsi directly: https://meet.jit.si

---

### Issue: Code not syncing between windows

**Causes**:
- AJAX polling disabled
- Network latency >5 seconds
- Browser cache issues

**Solution**:
1. Clear browser cache (Ctrl+Shift+Delete)
2. Hard refresh (Ctrl+Shift+R)
3. Check network tab in DevTools (F12)
4. Ensure both windows loading from same URL
5. Try different browser

---

### Issue: Emails not sending

**Causes**:
- Gmail credentials incorrect
- Less Secure App Access disabled
- Network blocked SMTP port 587

**Solution**:
1. Test Gmail login:
   ```bash
   python -c "import smtplib; s = smtplib.SMTP('smtp.gmail.com', 587); s.starttls(); s.login('email', 'password')"
   ```
2. Enable "Less Secure App Access": https://myaccount.google.com/lesssecureapps
3. Check firewall/network for port 587 blocking

---

### Issue: Large JSON files getting slow

**When**: >10,000 applications stored

**Solution**:
- Implement JSON indexing (separate index file)
- Migrate to SQLite (drop-in replacement for storage.py)
- Archive old applications to separate files
- Consider database migration (PostgreSQL)

---

## Contributing

### Development Workflow
```bash
# Create feature branch
git checkout -b feature/your-feature

# Make changes & test
python run.py

# Commit with descriptive messages
git commit -m "Add interview question caching"

# Push and create pull request
git push origin feature/your-feature
```

### Code Style
- Follow PEP 8 for Python
- Use meaningful variable names
- Add docstrings to functions
- Comment complex logic

### Testing
- Test manually in browser
- Test with both user roles (recruiter/candidate)
- Check console for JavaScript errors (F12)
- Verify JSON data after operations

---

## License & Credits

**MIT License** - Use freely for personal & commercial projects

**Frameworks & Libraries**:
- Flask (web framework)
- spaCy (NLP)
- Sentence-BERT (AI matching)
- Google Gemini (Interview AI)
- Jitsi Meet (Video conferencing)
- CodeMirror (Code editor)

---

## Support & Contact

For bugs, feature requests, or questions:
1. Check [TESTING.md](./TESTING.md) for test procedures
2. Review [GUIDE.md](./GUIDE.md) for detailed workflows
3. Check console logs (F12) for error messages
4. Compare with [DEMO_CREDENTIALS.md](./DEMO_CREDENTIALS.md)

---

## Quick Reference

| Task | Command |
|------|---------|
| **Install** | `pip install -r requirements.txt` |
| **Download NLP model** | `python -m spacy download en_core_web_sm` |
| **Generate sample data** | `python test_auth.py` |
| **Run development server** | `python run.py` |
| **Run production server** | `gunicorn -w 4 run:app` |
| **Create new user** | Via web interface at `/auth/register` |

---

**Last Updated**: March 23, 2026
**Version**: 2.0.0 (Interview Room Edition)

---

*This document provides comprehensive technical documentation for the OptiHire AI-Powered Recruitment Platform. For additional help, refer to the individual documentation files linked throughout.*
