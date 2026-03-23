#!/usr/bin/env python3
"""
Script to populate the OptiHire database with example test data
Run this after the application is set up to create sample users, jobs, resumes, and applications
"""

import os
import sys
import json
from datetime import datetime, timedelta

# Add the project directory to the path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app import create_app, bcrypt
from app.storage import get_storage
from app.user import User

def create_test_data():
    """Create comprehensive test data for the application"""
    
    app = create_app()
    storage = get_storage()
    
    print("Creating test data for OptiHire...")
    print("=" * 60)
    
    # Create test users
    print("\n1. Creating test users...")
    
    # Recruiter user
    recruiter_data = {
        'username': 'recruiter1',
        'email': 'recruiter@optihire.com',
        'password': bcrypt.generate_password_hash('recruiter123').decode('utf-8'),
        'full_name': 'Sarah Johnson',
        'user_type': 'recruiter',
        'is_active': True
    }
    
    try:
        recruiter = User.create_user(recruiter_data)
        print(f"✓ Created recruiter: {recruiter.email}")
    except Exception as e:
        print(f"✗ Recruiter already exists or error: {e}")
        recruiter = User.get_by_email('recruiter@optihire.com')
    
    # Candidate users
    candidates_data = [
        {
            'username': 'candidate1',
            'email': 'john.doe@email.com',
            'password': bcrypt.generate_password_hash('candidate123').decode('utf-8'),
            'full_name': 'John Doe',
            'user_type': 'candidate',
            'is_active': True
        },
        {
            'username': 'candidate2',
            'email': 'jane.smith@email.com',
            'password': bcrypt.generate_password_hash('candidate123').decode('utf-8'),
            'full_name': 'Jane Smith',
            'user_type': 'candidate',
            'is_active': True
        }
    ]
    
    candidates = []
    for cand_data in candidates_data:
        try:
            cand = User.create_user(cand_data)
            candidates.append(cand)
            print(f"✓ Created candidate: {cand.email}")
        except Exception as e:
            print(f"✗ Candidate {cand_data['email']} already exists or error: {e}")
            cand = User.get_by_email(cand_data['email'])
            if cand:
                candidates.append(cand)
    
    # Create example jobs
    print("\n2. Creating example job postings...")
    
    jobs_data = [
        {
            'title': 'Senior Software Engineer - Full Stack',
            'company': 'TechCorp Solutions',
            'description': '''We are seeking an experienced Full Stack Software Engineer to join our growing team. 

In this role, you will:
• Design and develop scalable web applications using modern technologies
• Collaborate with cross-functional teams to define and ship new features
• Write clean, maintainable code and conduct code reviews
• Mentor junior developers and contribute to technical decisions
• Participate in agile development processes

Our tech stack includes React, Node.js, Python, AWS, and PostgreSQL. You'll work on challenging problems that impact millions of users worldwide.''',
            'requirements': '''Required Qualifications:
• 5+ years of professional software development experience
• Strong proficiency in JavaScript/TypeScript, React, and Node.js
• Experience with Python and backend development
• Solid understanding of RESTful APIs and microservices architecture
• Experience with SQL and NoSQL databases
• Familiarity with cloud platforms (AWS, GCP, or Azure)
• Bachelor's degree in Computer Science or equivalent experience

Preferred Qualifications:
• Experience with containerization (Docker, Kubernetes)
• Knowledge of CI/CD pipelines
• Contributions to open-source projects
• Experience with agile methodologies''',
            'skills_required': json.dumps(['Python', 'JavaScript', 'React', 'Node.js', 'AWS', 'PostgreSQL', 'TypeScript', 'Docker', 'REST API', 'Git']),
            'location': 'San Francisco, CA / Remote',
            'job_type': 'Full-time',
            'experience_level': 'Senior Level',
            'salary_range': '$130,000 - $180,000',
            'recruiter_id': recruiter.id if recruiter else None
        },
        {
            'title': 'Machine Learning Engineer',
            'company': 'AI Innovations Inc',
            'description': '''Join our AI team to build cutting-edge machine learning solutions!

Responsibilities:
• Develop and deploy machine learning models at scale
• Work with large datasets to extract insights and patterns
• Collaborate with data scientists and engineers to implement AI solutions
• Optimize model performance and accuracy
• Stay current with latest ML research and best practices

You'll work on exciting projects in computer vision, NLP, and recommendation systems.''',
            'requirements': '''Requirements:
• Master's degree or PhD in Computer Science, ML, or related field
• 3+ years of experience in machine learning and deep learning
• Strong programming skills in Python
• Experience with TensorFlow, PyTorch, or similar frameworks
• Knowledge of statistical analysis and data mining
• Understanding of MLOps and model deployment
• Experience with cloud ML platforms (AWS SageMaker, GCP AI Platform)

Nice to have:
• Publications in top ML conferences
• Experience with large language models
• Knowledge of reinforcement learning''',
            'skills_required': json.dumps(['Python', 'Machine Learning', 'TensorFlow', 'PyTorch', 'Deep Learning', 'NLP', 'Computer Vision', 'AWS', 'Data Science', 'MLOps']),
            'location': 'Remote',
            'job_type': 'Full-time',
            'experience_level': 'Mid Level',
            'salary_range': '$140,000 - $200,000',
            'recruiter_id': recruiter.id if recruiter else None
        },
        {
            'title': 'Frontend Developer - React',
            'company': 'StartupXYZ',
            'description': '''We're looking for a talented Frontend Developer to create amazing user experiences!

What you'll do:
• Build responsive and intuitive web applications using React
• Implement pixel-perfect designs from Figma
• Optimize application performance and loading times
• Write unit and integration tests
• Collaborate with designers and backend developers

Join our fast-paced startup environment and make a real impact!''',
            'requirements': '''Required:
• 2+ years of frontend development experience
• Expert knowledge of React and modern JavaScript (ES6+)
• Proficiency in HTML5, CSS3, and responsive design
• Experience with state management (Redux, Context API)
• Understanding of RESTful APIs and async programming
• Familiarity with Git and version control

Preferred:
• Experience with Next.js or Gatsby
• Knowledge of TypeScript
• Experience with testing frameworks (Jest, React Testing Library)
• Understanding of web performance optimization
• Design sense and attention to detail''',
            'skills_required': json.dumps(['React', 'JavaScript', 'HTML', 'CSS', 'TypeScript', 'Redux', 'Next.js', 'Git', 'REST API', 'Responsive Design']),
            'location': 'Austin, TX',
            'job_type': 'Full-time',
            'experience_level': 'Mid Level',
            'salary_range': '$90,000 - $130,000',
            'recruiter_id': recruiter.id if recruiter else None
        },
        {
            'title': 'DevOps Engineer',
            'company': 'CloudScale Systems',
            'description': '''Looking for a DevOps Engineer to help us scale our infrastructure!

Your responsibilities:
• Design and maintain CI/CD pipelines
• Manage cloud infrastructure on AWS/GCP
• Implement monitoring and logging solutions
• Automate deployment processes
• Ensure system reliability and uptime
• Implement security best practices

Work with cutting-edge DevOps tools and technologies.''',
            'requirements': '''Qualifications:
• 3+ years of DevOps or Site Reliability Engineering experience
• Strong knowledge of AWS or GCP services
• Experience with Infrastructure as Code (Terraform, CloudFormation)
• Proficiency in containerization (Docker, Kubernetes)
• Experience with CI/CD tools (Jenkins, GitLab CI, GitHub Actions)
• Strong Linux/Unix administration skills
• Scripting skills in Python, Bash, or similar

Bonus skills:
• Experience with monitoring tools (Prometheus, Grafana, ELK)
• Knowledge of security and compliance standards
• Experience with database administration''',
            'skills_required': json.dumps(['AWS', 'Kubernetes', 'Docker', 'Terraform', 'CI/CD', 'Linux', 'Python', 'Jenkins', 'Monitoring', 'DevOps']),
            'location': 'Seattle, WA / Remote',
            'job_type': 'Full-time',
            'experience_level': 'Mid Level',
            'salary_range': '$120,000 - $160,000',
            'recruiter_id': recruiter.id if recruiter else None
        },
        {
            'title': 'Data Analyst',
            'company': 'DataDriven Co',
            'description': '''Join our analytics team to turn data into actionable insights!

What you'll do:
• Analyze large datasets to identify trends and patterns
• Create dashboards and visualizations
• Work with stakeholders to understand business needs
• Develop and maintain data pipelines
• Present findings to leadership
• Support data-driven decision making

Great opportunity for someone passionate about data!''',
            'requirements': '''Requirements:
• 2+ years of experience in data analysis
• Strong SQL skills and database knowledge
• Experience with data visualization tools (Tableau, Power BI, or similar)
• Proficiency in Python or R for data analysis
• Understanding of statistical analysis methods
• Excellent communication and presentation skills
• Bachelor's degree in a quantitative field

Preferred:
• Experience with ETL processes
• Knowledge of machine learning concepts
• Experience with big data technologies (Spark, Hadoop)
• Business acumen and problem-solving skills''',
            'skills_required': json.dumps(['SQL', 'Python', 'Tableau', 'Data Analysis', 'Statistics', 'Excel', 'Power BI', 'ETL', 'Data Visualization']),
            'location': 'New York, NY',
            'job_type': 'Full-time',
            'experience_level': 'Entry Level',
            'salary_range': '$75,000 - $95,000',
            'recruiter_id': recruiter.id if recruiter else None
        }
    ]
    
    created_jobs = []
    for job_data in jobs_data:
        try:
            job = storage.create_job(job_data)
            created_jobs.append(job)
            print(f"✓ Created job: {job['title']}")
        except Exception as e:
            print(f"✗ Error creating job: {e}")
    
    # Create example resumes/parsed data
    print("\n3. Creating example resumes...")
    
    resumes_data = [
        {
            'user_id': candidates[0].id if len(candidates) > 0 else None,
            'filename': 'john_doe_resume.pdf',
            'file_path': 'uploads/sample_john_doe_resume.pdf',
            'parsed_data': {
                'name': 'John Doe',
                'email': 'john.doe@email.com',
                'phone': '+1 (555) 123-4567',
                'location': 'San Francisco, CA',
                'skills': ['Python', 'JavaScript', 'React', 'Node.js', 'PostgreSQL', 'AWS', 'Docker', 'Git', 'REST API', 'Agile'],
                'experience_years': 6,
                'education': [
                    'Bachelor of Science in Computer Science - Stanford University (2017)',
                    'Online Certification in Cloud Architecture - AWS (2020)'
                ],
                'certifications': [
                    'AWS Certified Solutions Architect',
                    'Google Cloud Professional Developer'
                ]
            },
            'skills': json.dumps(['Python', 'JavaScript', 'React', 'Node.js', 'PostgreSQL', 'AWS', 'Docker', 'Git', 'REST API', 'Agile']),
            'experience_years': 6,
            'education': json.dumps(['Bachelor of Science in Computer Science - Stanford University (2017)', 'Online Certification in Cloud Architecture - AWS (2020)']),
            'certifications': json.dumps(['AWS Certified Solutions Architect', 'Google Cloud Professional Developer'])
        },
        {
            'user_id': candidates[1].id if len(candidates) > 1 else None,
            'filename': 'jane_smith_resume.pdf',
            'file_path': 'uploads/sample_jane_smith_resume.pdf',
            'parsed_data': {
                'name': 'Jane Smith',
                'email': 'jane.smith@email.com',
                'phone': '+1 (555) 987-6543',
                'location': 'Remote',
                'skills': ['Python', 'Machine Learning', 'TensorFlow', 'PyTorch', 'NLP', 'Deep Learning', 'Data Science', 'SQL', 'Pandas', 'Scikit-learn'],
                'experience_years': 4,
                'education': [
                    'Master of Science in Artificial Intelligence - MIT (2020)',
                    'Bachelor of Science in Mathematics - UC Berkeley (2018)'
                ],
                'certifications': [
                    'TensorFlow Developer Certificate',
                    'Deep Learning Specialization - Coursera'
                ]
            },
            'skills': json.dumps(['Python', 'Machine Learning', 'TensorFlow', 'PyTorch', 'NLP', 'Deep Learning', 'Data Science', 'SQL', 'Pandas', 'Scikit-learn']),
            'experience_years': 4,
            'education': json.dumps(['Master of Science in Artificial Intelligence - MIT (2020)', 'Bachelor of Science in Mathematics - UC Berkeley (2018)']),
            'certifications': json.dumps(['TensorFlow Developer Certificate', 'Deep Learning Specialization - Coursera'])
        }
    ]
    
    created_resumes = []
    for resume_data in resumes_data:
        if resume_data['user_id']:
            try:
                resume = storage.create_resume(resume_data)
                created_resumes.append(resume)
                print(f"✓ Created resume: {resume['filename']}")
            except Exception as e:
                print(f"✗ Error creating resume: {e}")
    
    print("\n" + "=" * 60)
    print("Test data creation complete!")
    print("\n📋 Test Accounts Created:")
    print(f"  Recruiter: recruiter@optihire.com / recruiter123")
    print(f"  Candidate 1: john.doe@email.com / candidate123")
    print(f"  Candidate 2: jane.smith@email.com / candidate123")
    print(f"\n📊 Created:")
    print(f"  • {len(created_jobs)} job postings")
    print(f"  • {len(created_resumes)} resumes")
    print("\n✨ You can now test the application with these accounts!")
    print("=" * 60)

if __name__ == '__main__':
    create_test_data()
