"""
Job posting routes - Create, view, manage jobs (File-based storage)
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from app.storage import get_storage
import json

bp = Blueprint('jobs', __name__, url_prefix='/jobs')

@bp.route('/')
def list_jobs():
    """List all active jobs with optional search + domain filter"""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    domain = request.args.get('domain', '')
    
    storage = get_storage()
    
    if search:
        jobs = storage.search_jobs(search)
    else:
        jobs = storage.get_all_jobs(active_only=True)
    
    # Domain filter (client-selectable)
    if domain:
        domain_lower = domain.lower().replace(' / ', ' ').replace('/', ' ')
        filtered = []
        for job in jobs:
            title_desc = (job.get('title', '') + ' ' + job.get('description', '')).lower()
            # Map domain keywords
            domain_keywords = {
                'backend': ['backend', 'back-end', 'back end', 'django', 'flask', 'node', 'spring', 'rails', 'api', 'server'],
                'frontend': ['frontend', 'front-end', 'front end', 'react', 'vue', 'angular', 'ui', 'ux', 'css', 'html'],
                'ml ai': ['machine learning', 'ml', 'ai', 'deep learning', 'nlp', 'data scientist', 'tensorflow', 'pytorch'],
                'devops': ['devops', 'dev ops', 'docker', 'kubernetes', 'ci/cd', 'jenkins', 'infrastructure', 'aws', 'cloud'],
                'mobile': ['mobile', 'ios', 'android', 'flutter', 'react native', 'swift', 'kotlin'],
                'data science': ['data science', 'data analyst', 'analytics', 'pandas', 'numpy', 'sql', 'tableau', 'bi'],
                'cybersecurity': ['security', 'cybersecurity', 'penetration', 'firewall', 'soc', 'siem'],
                'cloud': ['cloud', 'aws', 'azure', 'gcp', 'terraform', 'serverless'],
            }
            keywords = domain_keywords.get(domain_lower, [domain_lower])
            if any(kw in title_desc for kw in keywords):
                filtered.append(job)
        jobs = filtered
    
    # Sort by created_at descending
    jobs = sorted(jobs, key=lambda x: x.get('created_at', ''), reverse=True)
    
    # Simple pagination
    per_page = 12
    total = len(jobs)
    start = (page - 1) * per_page
    end = start + per_page
    jobs_page = jobs[start:end]
    
    # Pagination info
    pagination = {
        'items': jobs_page,
        'page': page,
        'pages': (total + per_page - 1) // per_page,
        'total': total,
        'has_prev': page > 1,
        'has_next': end < total,
        'prev_num': page - 1,
        'next_num': page + 1
    }
    
    return render_template('jobs/list.html', jobs=pagination, search=search)

@bp.route('/<job_id>')
def view_job(job_id):
    """View single job details"""
    storage = get_storage()
    job = storage.get_job_by_id(job_id)
    
    if not job:
        flash('Job not found', 'error')
        return redirect(url_for('jobs.list_jobs'))
    
    # Parse skills if JSON string
    skills = []
    if job.get('skills_required'):
        try:
            skills = json.loads(job['skills_required']) if isinstance(job['skills_required'], str) else job['skills_required']
        except:
            skills = []
    
    return render_template('jobs/view.html', job=job, skills=skills)

@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_job():
    """Create new job posting (recruiters only)"""
    if current_user.user_type != 'recruiter':
        flash('Only recruiters can create job postings', 'error')
        return redirect(url_for('jobs.list_jobs'))
    
    if request.method == 'POST':
        title = request.form.get('title')
        company = request.form.get('company')
        description = request.form.get('description')
        requirements = request.form.get('requirements')
        skills_required = request.form.get('skills_required', '')
        location = request.form.get('location')
        job_type = request.form.get('job_type')
        experience_level = request.form.get('experience_level')
        salary_range = request.form.get('salary_range')
        
        # Validation
        if not all([title, company, description, requirements]):
            flash('Please fill all required fields', 'error')
            return render_template('jobs/create.html')
        
        # Parse skills (comma-separated to JSON array)
        skills_list = [s.strip() for s in skills_required.split(',') if s.strip()]
        
        storage = get_storage()
        job = storage.create_job({
            'title': title,
            'company': company,
            'description': description,
            'requirements': requirements,
            'skills_required': json.dumps(skills_list),
            'location': location,
            'job_type': job_type,
            'experience_level': experience_level,
            'salary_range': salary_range,
            'recruiter_id': current_user.id
        })
        
        flash('Job posted successfully!', 'success')
        return redirect(url_for('jobs.view_job', job_id=job['id']))
    
    return render_template('jobs/create.html')

@bp.route('/<job_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_job(job_id):
    """Edit job posting"""
    storage = get_storage()
    job = storage.get_job_by_id(job_id)
    
    if not job:
        flash('Job not found', 'error')
        return redirect(url_for('jobs.list_jobs'))
    
    # Check ownership
    if job['recruiter_id'] != current_user.id:
        flash('You can only edit your own job postings', 'error')
        return redirect(url_for('jobs.view_job', job_id=job_id))
    
    if request.method == 'POST':
        title = request.form.get('title')
        company = request.form.get('company')
        description = request.form.get('description')
        requirements = request.form.get('requirements')
        skills_required = request.form.get('skills_required', '')
        location = request.form.get('location')
        job_type = request.form.get('job_type')
        experience_level = request.form.get('experience_level')
        salary_range = request.form.get('salary_range')
        
        # Parse skills
        skills_list = [s.strip() for s in skills_required.split(',') if s.strip()]
        
        storage.update_job(job_id, {
            'title': title,
            'company': company,
            'description': description,
            'requirements': requirements,
            'skills_required': json.dumps(skills_list),
            'location': location,
            'job_type': job_type,
            'experience_level': experience_level,
            'salary_range': salary_range
        })
        
        flash('Job updated successfully!', 'success')
        return redirect(url_for('jobs.view_job', job_id=job_id))
    
    # Parse skills for editing
    skills_str = ''
    if job.get('skills_required'):
        try:
            skills_list = json.loads(job['skills_required']) if isinstance(job['skills_required'], str) else job['skills_required']
            skills_str = ', '.join(skills_list)
        except:
            skills_str = ''
    
    return render_template('jobs/edit.html', job=job, skills_str=skills_str)

@bp.route('/<job_id>/delete', methods=['POST'])
@login_required
def delete_job(job_id):
    """Delete/deactivate job posting"""
    storage = get_storage()
    job = storage.get_job_by_id(job_id)
    
    if not job:
        flash('Job not found', 'error')
        return redirect(url_for('jobs.list_jobs'))
    
    if job['recruiter_id'] != current_user.id:
        flash('You can only delete your own job postings', 'error')
        return redirect(url_for('jobs.view_job', job_id=job_id))
    
    # Soft delete - just mark as inactive
    storage.delete_job(job_id)
    
    flash('Job posting deactivated successfully', 'success')
    return redirect(url_for('dashboard.recruiter_dashboard'))
