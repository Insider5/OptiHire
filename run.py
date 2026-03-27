"""
Main entry point for OptiHire Flask application
File-based storage version (no database)
"""
import os
from app import create_app, socketio
from app.user import User
from app.storage import get_storage
import json

app = create_app(os.getenv('FLASK_ENV', 'development'))

@app.shell_context_processor
def make_shell_context():
    """Make storage and user model available in flask shell"""
    return {
        'storage': get_storage(),
        'User': User
    }

@app.cli.command()
def init_storage():
    """Initialize storage directories"""
    storage = get_storage()
    print("✅ Storage initialized!")
    print(f"   Data directory: {app.config['DATA_DIR']}")
    print(f"   Upload directory: {app.config['UPLOAD_FOLDER']}")

@app.cli.command()
def create_sample_data():
    """Create sample data for testing"""
    storage = get_storage()
    
    # Create a sample recruiter
    recruiter = User.create(
        username='recruiter1',
        email='recruiter@example.com',
        full_name='John Recruiter',
        password='password123',
        user_type='recruiter'
    )
    
    # Create a sample candidate
    candidate = User.create(
        username='candidate1',
        email='candidate@example.com',
        full_name='Jane Candidate',
        password='password123',
        user_type='candidate'
    )
    
    # Create sample jobs
    job1 = storage.create_job({
        'title': 'Senior Python Developer',
        'company': 'Tech Corp',
        'description': 'We are looking for an experienced Python developer to join our team.',
        'requirements': '5+ years of Python experience, knowledge of Flask/Django, experience with databases',
        'skills_required': json.dumps(['Python', 'Flask', 'PostgreSQL', 'Docker', 'REST API']),
        'location': 'Remote',
        'job_type': 'Full-time',
        'experience_level': 'Senior',
        'salary_range': '$100k - $150k',
        'recruiter_id': recruiter.id
    })
    
    job2 = storage.create_job({
        'title': 'Frontend Developer',
        'company': 'Startup Inc',
        'description': 'Join our team as a frontend developer working with React and modern web technologies.',
        'requirements': '3+ years of React experience, knowledge of TypeScript, responsive design',
        'skills_required': json.dumps(['React', 'JavaScript', 'TypeScript', 'CSS', 'HTML']),
        'location': 'San Francisco, CA',
        'job_type': 'Full-time',
        'experience_level': 'Mid',
        'salary_range': '$80k - $120k',
        'recruiter_id': recruiter.id
    })
    
    job3 = storage.create_job({
        'title': 'Machine Learning Engineer',
        'company': 'AI Solutions',
        'description': 'Work on cutting-edge ML projects using Python, TensorFlow, and PyTorch.',
        'requirements': '3+ years of ML experience, strong Python skills, knowledge of deep learning',
        'skills_required': json.dumps(['Python', 'TensorFlow', 'PyTorch', 'Machine Learning', 'NLP']),
        'location': 'New York, NY',
        'job_type': 'Full-time',
        'experience_level': 'Mid',
        'salary_range': '$120k - $160k',
        'recruiter_id': recruiter.id
    })
    
    print("✅ Sample data created!")
    print(f"   Recruiter: recruiter@example.com / password123 (ID: {recruiter.id})")
    print(f"   Candidate: candidate@example.com / password123 (ID: {candidate.id})")
    print(f"   Jobs created: {job1['id']}, {job2['id']}, {job3['id']}")

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)
