#!/usr/bin/env python3
"""
Demo script to show file-based authentication (NO DATABASE)
This creates sample users and shows how the JSON storage works
"""
import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

from app import create_app
from app.user import User
from app.storage import get_storage

# Create app context
app = create_app()

with app.app_context():
    storage = get_storage()
    
    print("=" * 60)
    print("🚀 OptiHire - File-Based Authentication Demo")
    print("=" * 60)
    print("\n📁 Storage Type: JSON Files (NO DATABASE)\n")
    
    # Check if users already exist
    existing_recruiter = User.get_by_email('recruiter@example.com')
    existing_candidate = User.get_by_email('candidate@example.com')
    
    if existing_recruiter:
        print("✅ Sample users already exist!\n")
        print(f"👤 Recruiter: recruiter@example.com")
        print(f"   ID: {existing_recruiter.id}")
        print(f"   Name: {existing_recruiter.full_name}")
        print(f"   Type: {existing_recruiter.user_type}\n")
        
        print(f"👤 Candidate: candidate@example.com")
        print(f"   ID: {existing_candidate.id}")
        print(f"   Name: {existing_candidate.full_name}")
        print(f"   Type: {existing_candidate.user_type}\n")
    else:
        print("📝 Creating sample users...\n")
        
        # Create recruiter
        recruiter = User.create(
            username='recruiter1',
            email='recruiter@example.com',
            full_name='John Recruiter',
            password='password123',
            user_type='recruiter'
        )
        print(f"✅ Created Recruiter: {recruiter.email} (ID: {recruiter.id})")
        
        # Create candidate
        candidate = User.create(
            username='candidate1',
            email='candidate@example.com',
            full_name='Jane Candidate',
            password='password123',
            user_type='candidate'
        )
        print(f"✅ Created Candidate: {candidate.email} (ID: {candidate.id})")
    
    print("\n" + "=" * 60)
    print("📊 Storage Location:")
    print("=" * 60)
    print(f"📂 Data folder: {app.config['DATA_DIR']}")
    print(f"📄 Users file: data/users.json")
    print(f"📄 Jobs file: data/jobs.json")
    print(f"📄 Resumes file: data/resumes.json")
    print(f"📄 Applications file: data/applications.json")
    
    print("\n" + "=" * 60)
    print("🔐 Test Login Credentials:")
    print("=" * 60)
    print("\n🏢 RECRUITER LOGIN:")
    print("   Email: recruiter@example.com")
    print("   Password: password123")
    print("   Dashboard: /dashboard/recruiter")
    
    print("\n👨‍💼 CANDIDATE LOGIN:")
    print("   Email: candidate@example.com")
    print("   Password: password123")
    print("   Dashboard: /dashboard/candidate")
    
    print("\n" + "=" * 60)
    print("🚀 Start the application:")
    print("=" * 60)
    print("   python run.py")
    print("   Then visit: http://localhost:5000/auth/login")
    print("=" * 60)
    
    print("\n✅ All data saved to JSON files - NO DATABASE USED!\n")
