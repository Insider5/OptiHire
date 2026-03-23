# OptiHire - AI-Powered Recruitment Platform

> **File-Based Storage • No Database Required • Complete Backend Authentication**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0.0-green.svg)](https://flask.palletsprojects.com/)
[![Status](https://img.shields.io/badge/Status-Ready-success.svg)]()

---

## 🚀 Quick Start

```bash
# 1. Activate virtual environment
source venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Download spaCy model
python -m spacy download en_core_web_sm

# 4. Create sample users
python test_auth.py

# 5. Run the application
python run.py
```

**Visit**: http://localhost:5000

---

## 🔐 Test Login Credentials

After running `python test_auth.py`:

| User Type | Email | Password | Dashboard |
|-----------|-------|----------|-----------|
| **Recruiter** | recruiter@example.com | password123 | `/dashboard/recruiter` |
| **Candidate** | candidate@example.com | password123 | `/dashboard/candidate` |

---

## ✨ Key Features

- ✅ **No Database** - Pure JSON file storage
- ✅ **Complete Authentication** - Secure login system for recruiters & candidates
- ✅ **Smart Resume Parsing** - spaCy NER extraction
- ✅ **Semantic Matching** - Sentence-BERT AI matching (0-100% scores)
- ✅ **AI Interview Questions** - Google Gemini API integration
- ✅ **Explainable AI** - Transparent score breakdowns
- ✅ **ATS Features** - Application tracking system

---

## 📚 Complete Documentation

**👉 Read the full guide**: [GUIDE.md](./GUIDE.md)

The comprehensive guide includes:
- Backend authentication system details
- Step-by-step usage instructions
- API endpoint reference
- Troubleshooting guide
- Security best practices
- Testing procedures

---

## 📁 Storage Architecture

### File-Based (No Database)

All data stored in JSON files:

```
data/
├── users.json          # User accounts
├── jobs.json           # Job postings  
├── resumes.json        # Uploaded resumes
├── applications.json   # Job applications
└── notifications.json  # User notifications
```

**Benefits**:
- No database setup required
- Easy to inspect and debug
- Perfect for development
- Simple deployment

---

## 🎯 User Workflows

### For Candidates

1. Register → Login → Upload Resume
2. Browse jobs → Apply
3. View match score & breakdown
4. Check application status
5. Get AI recommendations

### For Recruiters

1. Register → Login → Post Job
2. View applications (auto-ranked by AI score)
3. Review candidate matches
4. Update application status
5. Manage job postings

---

## 🛠️ Technology Stack

| Component | Technology |
|-----------|------------|
| **Backend** | Flask 3.0 |
| **Storage** | JSON Files (no database) |
| **Auth** | Flask-Login + Werkzeug |
| **NLP** | spaCy (en_core_web_sm) |
| **AI Matching** | Sentence-BERT (all-MiniLM-L6-v2) |
| **Interview AI** | Google Gemini API |
| **Frontend** | Jinja2 + Tailwind CSS |

---

## 📊 Project Structure

```
tax/
├── app/
│   ├── routes/           # Auth, jobs, candidates, dashboards
│   ├── services/         # AI/ML services (parsing, matching)
│   ├── templates/        # HTML templates
│   ├── storage.py        # JSON file storage
│   └── user.py          # User model
├── data/                # JSON database files
├── uploads/             # Resume files
├── test_auth.py         # Create sample users
├── run.py              # Start application
└── GUIDE.md            # 📚 Complete documentation
```

---

## 🧪 Testing

```bash
# Create sample data
python test_auth.py

# Start app
python run.py

# Visit in browser
http://localhost:5000/auth/login
```

Login with:
- Recruiter: `recruiter@example.com` / `password123`
- Candidate: `candidate@example.com` / `password123`

---

## 🔒 Security

- ✅ Password hashing (PBKDF2-SHA256)
- ✅ Session management (Flask-Login)
- ✅ Role-based access control
- ✅ CSRF protection
- ✅ File validation
- ✅ Duplicate prevention

---

## 🐛 Common Issues

### "Module not found"
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### "spaCy model not found"
```bash
python -m spacy download en_core_web_sm
```

### "Port 5000 in use"
```bash
lsof -ti:5000 | xargs kill -9
```

---

## 📖 Learn More

For complete documentation including:
- **Backend authentication system** architecture
- **API endpoints** reference
- **File storage** details
- **Security** best practices
- **Troubleshooting** guide

**👉 See [GUIDE.md](./GUIDE.md)**

---

## 🎓 Based On

Research paper: **"OptiHire: An AI Powered Platform for Optimizing Talent Acquisition and Simplifying Recruitment"**

Authors:
- P. Purushotham
- Nimmagadda Narendra  
- Penikelapati Tej Pavan
- Chenoori Abhinay
- Malige Nethranand

MLR Institute of Technology, Hyderabad

---

## 📧 Support

For detailed help, check [GUIDE.md](./GUIDE.md) or inspect the code files.

---

**Made with ❤️ using Flask, spaCy, Sentence-BERT, and Gemini AI**

🚀 **Ready to start? Run:** `python test_auth.py && python run.py`
