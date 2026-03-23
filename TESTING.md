# OptiHire - Testing Guide

This guide provides comprehensive instructions for testing all functionalities of the OptiHire AI recruitment platform.

## Table of Contents
1. [Setup & Prerequisites](#setup--prerequisites)
2. [Test Accounts](#test-accounts)
3. [Testing Workflow](#testing-workflow)
4. [Feature Testing Guide](#feature-testing-guide)
5. [API Testing](#api-testing)
6. [Troubleshooting](#troubleshooting)

---

## Setup & Prerequisites

### Initial Setup

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   python -m spacy download en_core_web_sm
   ```

2. **Configure Environment**
   - Copy `.env.example` to `.env`
   - Add your Google Gemini API key:
     ```
     GEMINI_API_KEY=your_key_here
     ```

3. **Create Test Data**
   ```bash
   python create_test_data.py
   ```

4. **Run the Application**
   ```bash
   python run.py
   ```
   
   The app will be available at: `http://localhost:5000`

---

## Test Accounts

The `create_test_data.py` script creates the following test accounts:

### Recruiter Account
- **Email**: `recruiter@optihire.com`
- **Password**: `recruiter123`
- **Role**: Recruiter
- **Purpose**: Post jobs, review applications, manage hiring pipeline

### Candidate Accounts

#### Candidate 1 - Full Stack Focus
- **Email**: `john.doe@email.com`
- **Password**: `candidate123`
- **Skills**: Python, JavaScript, React, Node.js, PostgreSQL, AWS, Docker
- **Experience**: 6 years
- **Best Match**: Senior Software Engineer role

#### Candidate 2 - ML/AI Focus
- **Email**: `jane.smith@email.com`
- **Password**: `candidate123`
- **Skills**: Python, Machine Learning, TensorFlow, PyTorch, NLP, Deep Learning
- **Experience**: 4 years
- **Best Match**: Machine Learning Engineer role

---

## Testing Workflow

### Complete End-to-End Test Scenario

Follow this workflow to test the entire application:

1. **Recruiter Flow** → Post jobs, manage postings
2. **Candidate Flow** → Upload resume, browse jobs, apply
3. **AI Processing** → Semantic matching, interview questions
4. **Application Management** → Review applications, update status

---

## Feature Testing Guide

### 1. Authentication & User Management

#### Registration
1. Navigate to `http://localhost:5000`
2. Click "Sign Up"
3. Test both recruiter and candidate registration
4. Verify email validation
5. Test password strength requirements

#### Login
1. Test login with created accounts
2. Verify incorrect password handling
3. Test "Remember me" functionality
4. Verify redirect to appropriate dashboard

#### Logout
1. Click profile dropdown → Logout
2. Verify session is terminated
3. Verify protected routes redirect to login

---

### 2. Recruiter Functionalities

#### Dashboard Access
1. Login as: `recruiter@optihire.com`
2. Navigate to Dashboard
3. **Verify Stats Display**:
   - Total jobs posted
   - Active job count
   - Total applications
   - Pending applications

#### Job Posting
1. Click "Post Job" button
2. Fill out job form with:
   - Job title
   - Company name
   - Description
   - Requirements
   - Skills (comma-separated)
   - Location, job type, experience level
   - Salary range
3. Submit and verify job creation
4. Check job appears in job listings

**Test Jobs Created**:
- Senior Software Engineer - Full Stack
- Machine Learning Engineer
- Frontend Developer - React
- DevOps Engineer
- Data Analyst

#### Managing Jobs
1. **View Job**:
   - Click on a job from dashboard
   - Verify all details display correctly
   
2. **Edit Job**:
   - Click "Edit" on job detail page
   - Modify job description
   - Update skills list
   - Save and verify changes

3. **Delete Job**:
   - Click "Delete" button
   - Confirm deletion
   - Verify job marked as inactive

#### Viewing Applications
1. From dashboard, click "View Applications" on a job
2. Verify you can see:
   - Candidate name and email
   - Match score (AI-generated)
   - Match breakdown (skills, experience, semantic similarity)
   - Application date
   - Current status

3. **Application Details**:
   - Click "View Full Details"
   - Review AI match analysis
   - Check interview questions generated
   - View candidate resume
   - Read cover letter (if provided)

#### Managing Application Status
1. Open an application
2. Test status updates:
   - Mark as "Shortlisted"
   - Schedule for "Interview"
   - Mark as "Hired"
   - Mark as "Rejected"
3. Verify candidate receives notifications

---

### 3. Candidate Functionalities

#### Dashboard Access
1. Login as: `john.doe@email.com`
2. Navigate to Dashboard
3. **Verify Display**:
   - Application statistics
   - Recent applications
   - Job recommendations
   - Notifications
   - Resume count

#### Resume Upload
1. Click "Upload Resume" in nav bar
2. **Test Upload**:
   - Try uploading PDF file
   - Try uploading DOCX file
   - Test file size validation
   - Verify error handling for invalid formats

3. **After Upload**:
   - Verify resume parsed successfully
   - Check extracted information:
     * Skills
     * Experience years
     * Education
     * Certifications
     * Contact information

#### Browsing Jobs
1. Click "Browse Jobs"
2. **Test Features**:
   - View all jobs
   - Use search functionality
   - Filter by keywords
   - Pagination (if many jobs)

3. **Job Detail View**:
   - Click on any job
   - Verify complete job details
   - Check required skills display
   - View salary range and location

#### Applying for Jobs
1. Select a job (e.g., "Machine Learning Engineer")
2. Click "Apply for this Position"
3. **Application Process**:
   - Select resume from list
   - Write optional cover letter
   - Submit application

4. **Verification**:
   - Application submitted successfully
   - Redirect to application details
   - AI match score calculated
   - Match breakdown displayed
   - Interview questions generated

#### Viewing Applications
1. Navigate to "Dashboard" → "My Applications"
2. **Verify Display**:
   - All submitted applications
   - Application status for each
   - Match scores
   - Date applied
   - Quick stats overview

3. **Application Details**:
   - Click on an application
   - Review full match analysis
   - Study AI-generated interview questions
   - Prepare responses

---

### 4. AI Features Testing

#### Resume Parsing (NER)
1. Upload a resume
2. **Verify Extraction**:
   - Name, email, phone
   - Technical skills
   - Years of experience
   - Education details
   - Certifications

**Expected Behavior**:
- Skills should be extracted as array
- Experience years calculated
- Education formatted properly

#### Semantic Matching (Sentence-BERT)
1. Apply to a job
2. **Verify Match Score**:
   - Overall similarity score (0-100%)
   - Match breakdown:
     * Skills match
     * Experience match
     * Semantic similarity
   - Match rating (Excellent/Good/ Fair)

**Test Scenarios**:
- High match: ML candidate → ML Engineer job (expect 80%+)
- Medium match: Full-stack → Frontend job (expect 60-80%)
- Low match: Frontend → ML job (expect <60%)

#### AI Interview Questions
1. View an application
2. **Review Generated Questions**:
   - Should be relevant to job role
   - Should consider candidate background
   - Should be technical and behavioral mix
   - Typically 5-10 questions generated

**Sample Expected Questions**:
- Technical skills specific to role
- Experience-based scenarios
- Problem-solving challenges
- Cultural fit questions

---

### 5. General Features

#### Navigation
Test all navigation links:
- Home page
- Browse Jobs
- How It Works
- About page
- Dashboard
- Profile dropdown

#### Responsive Design
Test on different screen sizes:
- Desktop (1920x1080)
- Tablet (768x1024)
- Mobile (375x667)

#### Flash Messages
Verify flash messages appear for:
- Successful actions (green)
- Errors (red)
- Warnings (yellow)
- Info messages (blue)

#### Page Accessibility
1. Test "How It Works" page
2. Test "About" page
3. Verify:
   - Content loads correctly
   - Images/icons display
   - Links work
   - No Jinja template errors

---

## API Testing

### Test Resume Upload API
```bash
curl -X POST http://localhost:5000/candidates/upload-resume \
  -F "resume=@path/to/resume.pdf" \
  -H "Cookie: session=YOUR_SESSION_COOKIE"
```

### Test Job Creation API
```bash
curl -X POST http://localhost:5000/jobs/create \
  -d "title=Test Job" \
  -d "company=Test  Company" \
  -d "description=Test Description" \
  -d "requirements=Test Requirements" \
  -H "Cookie: session=YOUR_SESSION_COOKIE"
```

---

## Common Test Scenarios

### Scenario 1: New Recruiter Posting First Job
1. Register new recruiter account
2. Login
3. Navigate to "Post Job"
4. Create comprehensive job posting
5. Verify job appears in listings
6. Share job link

### Scenario 2: Candidate Complete Journey
1. Register candidate account
2. Upload resume (PDF)
3. Browse available jobs
4. Find best matching job
5. Apply with cover letter
6. Check application status
7. Review interview questions
8. Prepare for interview

### Scenario 3: Application Management
1. Recruiter receives application
2. Reviews candidate resume
3. Checks AI match score
4. Reviews match breakdown
5. Updates status to "Shortlisted"
6. Candidate receives notification
7. Recruiter schedules interview
8. Final hiring decision

---

## Troubleshooting

### Common Issues

#### 1. Template Not Found Errors
**Error**: `jinja2.exceptions.TemplateNotFound`
**Solution**: 
- Verify all templates created
- Check template paths in routes
- Restart the application

#### 2. Jinja2 Filter Errors
**Error**: `No filter named 'from_json'`
**Solution**:
- Verify `from_json` filter in `app/__init__.py`
- Restart Flask application

#### 3. Resume Upload Fails
**Possible Causes**:
- File size too large
- Invalid file type
- Missing upload folder
**Solution**:
- Check `uploads/` directory exists
- Verify file is PDF or DOCX
- Check file size < 10MB

#### 4. AI Features Not Working
**Issue**: Match scores not calculating
**Check**:
- Gemini API key configured
- sentence-transformers installed
- spaCy model downloaded

#### 5. No Jobs Showing
**Solution**:
- Run `python create_test_data.py`
- Check job `is_active` status
- Verify recruiter_id set

---

## Testing Checklist

Use this checklist to ensure comprehensive testing:

### Authentication ✓
- [ ] Register recruiter
- [ ] Register candidate
- [ ] Login
- [ ] Logout
- [ ] Password validation
- [ ] Email validation

### Recruiter Features ✓
- [ ] View dashboard
- [ ] Post new job
- [ ] Edit job
- [ ] Delete job
- [ ] View applications
- [ ] Update application status
- [ ] View candidate resumes

### Candidate Features ✓
- [ ] Upload resume (PDF)
- [ ] Upload resume (DOCX)
- [ ] View parsed resume
- [ ] Browse jobs
- [ ] Search jobs
- [ ] Apply to job
- [ ] View applications
- [ ] Check match scores

### AI Features ✓
- [ ] Resume parsing works
- [ ] Skills extracted correctly
- [ ] Match score calculated
- [ ] Match breakdown shown
- [ ] Interview questions generated
- [ ] Recommendations working

### General ✓
- [ ] How It Works page
- [ ] About page
- [ ] Navigation works
- [ ] Flash messages display
- [ ] Mobile responsive
- [ ] No 404 errors
- [ ] No template errors

---

## Performance Testing

### Load Test
1. Create 10+ jobs
2. Create 5+ candidate accounts
3. Upload multiple resumes
4. Submit 20+ applications
5. Monitor performance

### Metrics to Check
- Page load times
- AI processing time
- Database query performance
- Resume parsing speed

---

## Sample Test Data Summary

### Jobs Available (5)
1. **Senior Software Engineer** - TechCorp ($130k-$180k)
2. **Machine Learning Engineer** - AI Innovations ($140k-$200k)
3. **Frontend Developer** - StartupXYZ ($90k-$130k)
4. **DevOps Engineer** - CloudScale ($120k-$160k)
5. **Data Analyst** - DataDriven ($75k-$95k)

### Candidate Profiles (2)
1. **John Doe** - Full Stack (6 years)
2. **Jane Smith** - ML/AI (4 years)

---

## Presentation Demo Flow

For a polished presentation, follow this sequence:

1. **Introduction** (2 min)
   - Show homepage
   - Explain platform purpose
   - Highlight AI features

2. **Recruiter Demo** (5 min)
   - Login as recruiter
   - Show dashboard
   - Post a new job
   - Review applications
   - Show AI match scores

3. **Candidate Demo** (5 min)
   - Login as candidate
   - Upload resume
   - Show resume parsing (AI NER)
   - Browse and apply to job
   - Show match score & interview questions

4. **AI Showcase** (3 min)
   - Highlight semantic matching
   - Show match breakdown
   - Display interview questions
   - Explain recommendation system

5. **Q&A** (5 min)
   - Address questions
   - Show additional features
   - Discuss technology stack

---

## Support

For issues or questions:
- Check this testing guide
- Review `GUIDE.md`
- Check `README.md`
- Review error logs in console

---

**Last Updated**: January 2026  
**Version**: 1.0  
**Platform**: OptiHire AI Recruitment System
