# 🎯 OptiHire - Demo Presentation Guide

## 🚀 Application is Running!

**URL**: http://localhost:5000

---

## 🔐 HARDCODED LOGIN CREDENTIALS

### 👔 Recruiter Account
- **Email**: `recruiter@example.com`
- **Password**: `password123`
- **Dashboard**: `/dashboard/recruiter`
- **Name**: John Recruiter

### 👨‍💼 Candidate Account
- **Email**: `candidate@example.com`
- **Password**: `password123`
- **Dashboard**: `/dashboard/candidate`
- **Name**: Jane Candidate

### 🏢 Additional Test Accounts (from create_test_data.py)
- **Recruiter**: `recruiter@optihire.com` / `recruiter123` (Sarah Johnson)
- **Candidate 1**: `john.doe@email.com` / `candidate123` (John Doe)
- **Candidate 2**: `jane.smith@email.com` / `candidate123` (Jane Smith)

---

## 📊 DEMO DATA AVAILABLE

### 5 Job Postings Created:
1. **Senior Software Engineer - Full Stack** @ TechCorp Solutions
   - Location: San Francisco, CA / Remote
   - Salary: $130,000 - $180,000
   - Skills: Python, JavaScript, React, Node.js, AWS, PostgreSQL, TypeScript, Docker

2. **Machine Learning Engineer** @ AI Innovations Inc
   - Location: Remote
   - Salary: $140,000 - $200,000
   - Skills: Python, Machine Learning, TensorFlow, PyTorch, Deep Learning, NLP

3. **Frontend Developer - React** @ StartupXYZ
   - Location: Austin, TX
   - Salary: $90,000 - $130,000
   - Skills: React, JavaScript, HTML, CSS, TypeScript, Redux, Next.js

4. **DevOps Engineer** @ CloudScale Systems
   - Location: Seattle, WA / Remote
   - Salary: $120,000 - $160,000
   - Skills: AWS, Kubernetes, Docker, Terraform, CI/CD, Linux, Python

5. **Data Analyst** @ DataDriven Co
   - Location: New York, NY
   - Salary: $75,000 - $95,000
   - Skills: SQL, Python, Tableau, Data Analysis, Statistics, Excel

---

## 🎬 PRESENTATION FLOW

### Demo 1: Recruiter Portal
1. **Login** as recruiter (`recruiter@example.com` / `password123`)
2. **View Dashboard** - See recruiter overview
3. **Browse Jobs** - View all 5 posted jobs
4. **Post New Job** - Demonstrate job posting functionality
5. **View Applications** - See candidate applications with AI match scores
6. **Manage Candidates** - Review candidate profiles and resumes

### Demo 2: Candidate Portal
1. **Login** as candidate (`candidate@example.com` / `password123`)
2. **View Dashboard** - See candidate overview
3. **Upload Resume** - Demonstrate resume parsing with AI
4. **Browse Jobs** - View available positions
5. **Apply to Jobs** - Submit applications
6. **View Match Scores** - See AI-powered compatibility scores
7. **Check Application Status** - Track application progress

### Demo 3: AI Features
1. **Resume Parsing** - Upload resume and see extracted skills, experience
2. **Semantic Matching** - View 0-100% match scores between resume and job
3. **AI Interview Questions** - Generate role-specific questions (Gemini API)
4. **Explainable AI** - See detailed score breakdowns

---

## 🌐 KEY URLS

- **Homepage**: http://localhost:5000
- **Login**: http://localhost:5000/auth/login
- **Register**: http://localhost:5000/auth/register
- **Recruiter Dashboard**: http://localhost:5000/dashboard/recruiter
- **Candidate Dashboard**: http://localhost:5000/dashboard/candidate
- **Jobs Listing**: http://localhost:5000/jobs
- **Post Job**: http://localhost:5000/jobs/post

---

## ✨ KEY FEATURES TO HIGHLIGHT

### 🎯 No Database Required
- All data stored in JSON files (`data/` folder)
- Easy to inspect: `users.json`, `jobs.json`, `resumes.json`, `applications.json`
- Perfect for demos and development

### 🔒 Complete Authentication
- Secure password hashing (PBKDF2-SHA256)
- Session management with Flask-Login
- Role-based access control (Recruiter vs Candidate)

### 🤖 AI-Powered Features
- **spaCy NER**: Resume parsing and skill extraction
- **Sentence-BERT**: Semantic similarity matching (0-100% scores)
- **Google Gemini**: AI-generated interview questions
- **Explainable AI**: Transparent score breakdowns

### 📱 User Workflows
- **Candidates**: Register → Upload Resume → Browse Jobs → Apply → Track Status
- **Recruiters**: Register → Post Jobs → Review Applications → Manage Candidates

---

## 🛠️ TECHNOLOGY STACK

| Component | Technology |
|-----------|------------|
| Backend | Flask 3.0 |
| Storage | JSON Files (no database) |
| Authentication | Flask-Login + Werkzeug |
| NLP | spaCy (en_core_web_sm) |
| AI Matching | Sentence-BERT (all-MiniLM-L6-v2) |
| Interview AI | Google Gemini API |
| Frontend | Jinja2 + Tailwind CSS |

---

## 📁 DATA STORAGE LOCATION

All demo data is stored in:
```
C:\Users\meom\OneDrive\Desktop\tax\data\
├── users.json          # All user accounts
├── jobs.json           # 5 job postings
├── resumes.json        # Uploaded resumes
├── applications.json   # Job applications
└── notifications.json  # User notifications
```

---

## 🎓 QUICK START COMMANDS

```bash
# Already completed:
✅ python test_auth.py      # Created demo users
✅ python create_test_data.py  # Created 5 jobs
✅ python run.py            # Server running on http://localhost:5000

# To stop server:
Press CTRL+C in terminal
```

---

## 💡 PRESENTATION TIPS

1. **Start with Recruiter Login** - Show job management features
2. **Switch to Candidate Login** - Demonstrate job search and application
3. **Highlight AI Features** - Upload a resume and show match scores
4. **Show Explainability** - Display how AI calculates compatibility
5. **Emphasize No Database** - Open `data/users.json` to show file-based storage

---

## 🎯 DEMO SCRIPT

### Opening (30 seconds)
"OptiHire is an AI-powered recruitment platform that simplifies hiring with intelligent matching, resume parsing, and automated candidate screening - all without requiring a database."

### Feature Demo (2-3 minutes)
1. Login as recruiter → View 5 posted jobs
2. Login as candidate → Upload resume → See AI parsing
3. Apply to job → Show 85% match score
4. View explainable AI breakdown

### Closing (30 seconds)
"Built with Flask, spaCy, Sentence-BERT, and Google Gemini - OptiHire makes recruitment smarter, faster, and more transparent."

---

## 📞 SUPPORT

- Full documentation: `GUIDE.md`
- Testing guide: `TESTING.md`
- Project README: `README.md`

---

**🚀 Ready for your presentation! Access the app at http://localhost:5000**
