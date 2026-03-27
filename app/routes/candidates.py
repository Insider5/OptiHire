"""
Candidate routes - Resume upload, job application, viewing results (File-based storage)
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, jsonify
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app.storage import get_storage
from app.services.resume_parser import get_resume_parser
from app.services.semantic_matcher import get_semantic_matcher
from app.services.ai_interviewer import get_question_generator
import os
import json
from datetime import datetime

bp = Blueprint('candidates', __name__, url_prefix='/candidates')


@bp.route('/preview-match/<job_id>/<resume_id>')
@login_required
def preview_match_score(job_id, resume_id):
    """Calculate and return match score preview for a resume against a job"""
    if current_user.user_type != 'candidate':
        return jsonify({'success': False, 'error': 'Access denied'}), 403

    storage = get_storage()

    try:
        job = storage.get_job_by_id(job_id)
        resume = storage.get_resume_by_id(resume_id)

        if not job:
            current_app.logger.error(f'Job not found: {job_id}')
            return jsonify({'success': False, 'error': 'Job not found'}), 404

        if not resume:
            current_app.logger.error(f'Resume not found: {resume_id}')
            return jsonify({'success': False, 'error': 'Resume not found'}), 404

        if resume.get('user_id') != current_user.id:
            current_app.logger.error(f'Access denied - resume user: {resume.get("user_id")}, current user: {current_user.id}')
            return jsonify({'success': False, 'error': 'Access denied'}), 403

        # Parse resume data
        parsed_data = resume.get('parsed_data') or {}
        if isinstance(parsed_data, str):
            try:
                parsed_data = json.loads(parsed_data)
            except Exception as e:
                current_app.logger.error(f'Failed to parse resume data: {str(e)}')
                parsed_data = {}

        # Ensure skills is a list
        if isinstance(parsed_data.get('skills'), str):
            try:
                parsed_data['skills'] = json.loads(parsed_data['skills'])
            except:
                parsed_data['skills'] = []

        if not isinstance(parsed_data.get('skills'), list):
            parsed_data['skills'] = []

        current_app.logger.info(f'Parsed data: {parsed_data}')

        matcher = get_semantic_matcher()

        job_data = {
            'id': job['id'],
            'title': job.get('title', ''),
            'company': job.get('company', ''),
            'description': job.get('description', ''),
            'requirements': job.get('requirements', ''),
            'skills_required': job.get('skills_required', '[]'),
            'experience_level': job.get('experience_level', 'Mid')
        }

        current_app.logger.info(f'Job data: {job_data}')

        similarity_score, match_breakdown = matcher.calculate_match_score(
            parsed_data, job_data
        )
        similarity_score = max(0.0, min(1.0, float(similarity_score)))

        # Get matching and missing skills
        resume_skills = parsed_data.get('skills', [])
        job_skills = job.get('skills_required', [])

        if isinstance(job_skills, str):
            try:
                job_skills = json.loads(job_skills)
            except Exception as e:
                current_app.logger.error(f'Failed to parse job skills: {str(e)}')
                job_skills = []

        if not isinstance(job_skills, list):
            job_skills = []

        resume_skills_lower = {str(s).lower() for s in resume_skills if s}
        matching_skills = [s for s in job_skills if str(s).lower() in resume_skills_lower]
        missing_skills = [s for s in job_skills if str(s).lower() not in resume_skills_lower]

        return jsonify({
            'success': True,
            'score': round(similarity_score * 100),
            'breakdown': {
                'skills_match': round((match_breakdown.get('skills_match', 0)) * 100),
                'experience_match': round((match_breakdown.get('experience_match', 0)) * 100),
                'education_match': round((match_breakdown.get('education_match', 0)) * 100)
            },
            'matching_skills': matching_skills[:5],
            'missing_skills': missing_skills[:5],
            'recommendation': 'Strong match!' if similarity_score >= 0.7 else 'Good match' if similarity_score >= 0.5 else 'Consider improving your resume'
        })

    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        current_app.logger.error(f'Error calculating preview score: {str(e)}\n{error_trace}')
        return jsonify({'success': False, 'error': f'Server error: {str(e)}'}), 500


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']


@bp.route('/onboarding')
@login_required
def onboarding():
    """3-step onboarding wizard for new candidates after registration"""
    if current_user.user_type != 'candidate':
        return redirect(url_for('dashboard.recruiter_dashboard'))
    storage = get_storage()
    has_resume = bool(storage.get_resumes_by_user(current_user.id))
    jobs = storage.get_all_jobs()
    return render_template('candidates/onboarding.html',
                           has_resume=has_resume,
                           jobs=jobs[:6])


@bp.route('/upload-resume', methods=['GET', 'POST'])
@login_required
def upload_resume():
    """Upload and parse resume"""
    if current_user.user_type != 'candidate':
        flash('Only candidates can upload resumes.', 'error')
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        if 'resume' not in request.files:
            flash('No file uploaded.', 'error')
            return render_template('candidates/upload_resume.html')

        file = request.files['resume']

        if not file or file.filename == '':
            flash('No file selected.', 'error')
            return render_template('candidates/upload_resume.html')

        if not allowed_file(file.filename):
            flash('Only PDF and DOCX files are allowed.', 'error')
            return render_template('candidates/upload_resume.html')

        # Save file
        filename = secure_filename(file.filename)
        unique_filename = f"{current_user.id}_{filename}"
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)

        try:
            file.save(filepath)
        except Exception as e:
            flash(f'Error saving file: {str(e)}', 'error')
            return render_template('candidates/upload_resume.html')

        # Parse resume
        try:
            parser = get_resume_parser()
            parsed_data = parser.parse_resume(filepath)

            if not parsed_data or 'error' in parsed_data:
                flash(f"Could not parse resume. Please ensure it is a valid PDF or DOCX.", 'error')
                if os.path.exists(filepath):
                    os.remove(filepath)
                return render_template('candidates/upload_resume.html')

            # Guard against completely empty parsed data
            if not parsed_data.get('skills') and not parsed_data.get('name'):
                flash('Resume parsed but no content could be extracted. Try a different file.', 'warning')

            # Save to storage
            storage = get_storage()
            resume = storage.create_resume({
                'user_id': current_user.id,
                'filename': filename,
                'file_path': filepath,
                'parsed_data': parsed_data,
                'skills': json.dumps(parsed_data.get('skills', [])),
                'experience_years': parsed_data.get('experience_years', 0),
                'education': json.dumps(parsed_data.get('education', [])),
                'certifications': json.dumps(parsed_data.get('certifications', []))
            })

            flash('Resume uploaded and parsed successfully! ✅', 'success')
            return redirect(url_for('candidates.view_resume', resume_id=resume['id']))

        except Exception as e:
            flash(f'Error processing resume: {str(e)}', 'error')
            if os.path.exists(filepath):
                os.remove(filepath)
            return render_template('candidates/upload_resume.html')

    return render_template('candidates/upload_resume.html')


@bp.route('/resume/<resume_id>')
@login_required
def view_resume(resume_id):
    """View parsed resume data"""
    storage = get_storage()
    resume = storage.get_resume_by_id(resume_id)

    if not resume:
        flash('Resume not found.', 'error')
        return redirect(url_for('main.index'))

    if resume.get('user_id') != current_user.id:
        flash('Access denied.', 'error')
        return redirect(url_for('main.index'))

    # Ensure parsed_data is a dict
    parsed_data = resume.get('parsed_data') or {}
    if isinstance(parsed_data, str):
        try:
            parsed_data = json.loads(parsed_data)
        except Exception:
            parsed_data = {}
    resume['parsed_data'] = parsed_data

    return render_template('candidates/view_resume.html', resume=resume)


@bp.route('/apply/<job_id>', methods=['GET', 'POST'])
@login_required
def apply_job(job_id):
    """Apply to a job"""
    if current_user.user_type != 'candidate':
        flash('Only candidates can apply to jobs.', 'error')
        return redirect(url_for('jobs.view_job', job_id=job_id))

    storage = get_storage()
    job = storage.get_job_by_id(job_id)

    if not job:
        flash('Job not found or no longer active.', 'error')
        return redirect(url_for('jobs.list_jobs'))

    if not job.get('is_active', True):
        flash('This job is no longer accepting applications.', 'warning')
        return redirect(url_for('jobs.list_jobs'))

    # Check if already applied
    existing_application = storage.get_existing_application(job_id, current_user.id)
    if existing_application:
        flash('You have already applied to this job.', 'info')
        return redirect(url_for('candidates.view_application',
                                application_id=existing_application['id']))

    # Get user's resumes
    resumes = storage.get_resumes_by_user(current_user.id)

    if not resumes:
        flash('Please upload a resume before applying.', 'warning')
        return redirect(url_for('candidates.upload_resume'))

    if request.method == 'POST':
        resume_id = request.form.get('resume_id')
        cover_letter = request.form.get('cover_letter', '').strip()

        if not resume_id:
            flash('Please select a resume.', 'error')
            return render_template('candidates/apply.html', job=job, resumes=resumes)

        resume = storage.get_resume_by_id(resume_id)

        if not resume or resume.get('user_id') != current_user.id:
            flash('Invalid resume selected.', 'error')
            return render_template('candidates/apply.html', job=job, resumes=resumes)

        # Ensure parsed_data is a dict
        parsed_data = resume.get('parsed_data') or {}
        if isinstance(parsed_data, str):
            try:
                parsed_data = json.loads(parsed_data)
            except Exception:
                parsed_data = {}

        try:
            # Calculate semantic match score
            matcher = get_semantic_matcher()

            job_data = {
                'id': job['id'],
                'title': job.get('title', ''),
                'company': job.get('company', ''),
                'description': job.get('description', ''),
                'requirements': job.get('requirements', ''),
                'skills_required': job.get('skills_required', '[]'),
                'experience_level': job.get('experience_level', 'Mid')
            }

            similarity_score, match_breakdown = matcher.calculate_match_score(
                parsed_data, job_data
            )

            # Clamp score to [0, 1]
            similarity_score = max(0.0, min(1.0, float(similarity_score)))

            # Generate interview questions
            question_gen = get_question_generator()
            interview_questions = question_gen.generate_questions(
                parsed_data, job_data, num_questions=5
            )

            # Create application
            application = storage.create_application({
                'job_id': job_id,
                'candidate_id': current_user.id,
                'resume_id': resume_id,
                'similarity_score': similarity_score,
                'match_breakdown': match_breakdown,
                'cover_letter': cover_letter,
                'interview_questions': interview_questions,
                'status': 'pending'
            })

            # Notify candidate
            score_pct = f"{similarity_score * 100:.1f}"
            storage.create_notification({
                'user_id': current_user.id,
                'application_id': application['id'],
                'title': 'Application Submitted ✅',
                'message': (
                    f'Your application for {job.get("title")} at {job.get("company")} '
                    f'was submitted with a match score of {score_pct}%.'
                ),
                'notification_type': 'success'
            })

            flash('Application submitted successfully! 🎉', 'success')
            return redirect(url_for('candidates.view_application',
                                    application_id=application['id']))

        except Exception as e:
            current_app.logger.error(f'Error submitting application: {str(e)}')
            flash(f'Error submitting application: {str(e)}', 'error')
            return render_template('candidates/apply.html', job=job, resumes=resumes)

    return render_template('candidates/apply.html', job=job, resumes=resumes)


@bp.route('/application/<application_id>')
@login_required
def view_application(application_id):
    """View application details with scores and breakdown"""
    storage = get_storage()
    application = storage.get_application_by_id(application_id)

    if not application:
        flash('Application not found.', 'error')
        return redirect(url_for('main.index'))

    # Safely fetch job (may have been soft-deleted)
    job = storage.get_job_by_id(application.get('job_id', ''))

    # Access control
    is_owner = application.get('candidate_id') == current_user.id
    is_recruiter_owner = (
        current_user.user_type == 'recruiter' and
        job and job.get('recruiter_id') == current_user.id
    )
    if not is_owner and not is_recruiter_owner:
        flash('Access denied.', 'error')
        return redirect(url_for('main.index'))

    resume = storage.get_resume_by_id(application.get('resume_id', ''))

    # Safely decode match_breakdown if stored as a string
    match_breakdown = application.get('match_breakdown', {})
    if isinstance(match_breakdown, str):
        try:
            match_breakdown = json.loads(match_breakdown)
        except Exception:
            match_breakdown = {}
    application['match_breakdown'] = match_breakdown

    # Safely decode interview_questions
    interview_questions = application.get('interview_questions', [])
    if isinstance(interview_questions, str):
        try:
            interview_questions = json.loads(interview_questions)
        except Exception:
            interview_questions = []
    application['interview_questions'] = interview_questions

    application['job'] = job
    application['resume'] = resume

    # Fetch candidate info so recruiter view can display name in confirmation dialog
    candidate = storage.get_user_by_id(application.get('candidate_id', ''))
    application['candidate'] = candidate

    # Parse applied_at for template formatting
    applied_at = application.get('applied_at')
    if isinstance(applied_at, str):
        try:
            application['applied_at_obj'] = datetime.fromisoformat(applied_at)
        except Exception:
            application['applied_at_obj'] = datetime.now()

    return render_template('candidates/view_application.html', application=application,
                           now_date=datetime.now().strftime('%Y-%m-%d'))


@bp.route('/my-applications')
@login_required
def my_applications():
    """View all applications submitted by candidate"""
    if current_user.user_type != 'candidate':
        flash('Access denied.', 'error')
        return redirect(url_for('main.index'))

    storage = get_storage()
    applications = storage.get_applications_by_candidate(current_user.id)
    applications = sorted(applications, key=lambda x: x.get('applied_at', ''), reverse=True)

    now = datetime.now()
    for app in applications:
        app['job'] = storage.get_job_by_id(app.get('job_id', ''))

        # Flag apps whose status was changed after they were submitted
        applied_at = app.get('applied_at', '')
        updated_at = app.get('updated_at', '')
        app['is_recently_updated'] = False
        if updated_at and updated_at != applied_at:
            try:
                updated_dt = datetime.fromisoformat(updated_at)
                app['is_recently_updated'] = (now - updated_dt).days <= 7
                app['updated_at_obj'] = updated_dt
            except (ValueError, TypeError):
                pass

    # Fetch unread status-change notifications to show as a banner
    unread_notifications = storage.get_notifications_by_user(current_user.id, unread_only=True)
    unread_notifications = sorted(
        unread_notifications,
        key=lambda x: x.get('created_at', ''),
        reverse=True
    )[:5]

    return render_template(
        'candidates/my_applications.html',
        applications=applications,
        unread_notifications=unread_notifications
    )


@bp.route('/application/<application_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_application(application_id):
    """Edit an existing application (cover letter and resume)"""
    if current_user.user_type != 'candidate':
        flash('Only candidates can edit applications.', 'error')
        return redirect(url_for('main.index'))

    storage = get_storage()
    application = storage.get_application_by_id(application_id)

    if not application:
        flash('Application not found.', 'error')
        return redirect(url_for('candidates.my_applications'))

    # Check ownership
    if application.get('candidate_id') != current_user.id:
        flash('Access denied.', 'error')
        return redirect(url_for('candidates.my_applications'))

    # Get job details
    job = storage.get_job_by_id(application.get('job_id', ''))
    if not job:
        flash('Job no longer exists.', 'error')
        return redirect(url_for('candidates.my_applications'))

    # Get user's resumes
    resumes = storage.get_resumes_by_user(current_user.id)

    if request.method == 'POST':
        resume_id = request.form.get('resume_id')
        cover_letter = request.form.get('cover_letter', '').strip()

        if not resume_id:
            flash('Please select a resume.', 'error')
            return render_template('candidates/edit_application.html',
                                   application=application, job=job, resumes=resumes)

        resume = storage.get_resume_by_id(resume_id)
        if not resume or resume.get('user_id') != current_user.id:
            flash('Invalid resume selected.', 'error')
            return render_template('candidates/edit_application.html',
                                   application=application, job=job, resumes=resumes)

        # Ensure parsed_data is a dict
        parsed_data = resume.get('parsed_data') or {}
        if isinstance(parsed_data, str):
            try:
                parsed_data = json.loads(parsed_data)
            except Exception:
                parsed_data = {}

        try:
            # Recalculate match score with new resume
            matcher = get_semantic_matcher()

            job_data = {
                'id': job['id'],
                'title': job.get('title', ''),
                'company': job.get('company', ''),
                'description': job.get('description', ''),
                'requirements': job.get('requirements', ''),
                'skills_required': job.get('skills_required', '[]'),
                'experience_level': job.get('experience_level', 'Mid')
            }

            similarity_score, match_breakdown = matcher.calculate_match_score(
                parsed_data, job_data
            )
            similarity_score = max(0.0, min(1.0, float(similarity_score)))

            # Regenerate interview questions
            question_gen = get_question_generator()
            interview_questions = question_gen.generate_questions(
                parsed_data, job_data, num_questions=5
            )

            # Update application
            storage.update_application(application_id, {
                'resume_id': resume_id,
                'cover_letter': cover_letter,
                'similarity_score': similarity_score,
                'match_breakdown': match_breakdown,
                'interview_questions': interview_questions,
                'updated_at': datetime.now().isoformat()
            })

            flash('Application updated successfully! ✅', 'success')
            return redirect(url_for('candidates.view_application', application_id=application_id))

        except Exception as e:
            current_app.logger.error(f'Error updating application: {str(e)}')
            flash(f'Error updating application: {str(e)}', 'error')
            return render_template('candidates/edit_application.html',
                                   application=application, job=job, resumes=resumes)

    return render_template('candidates/edit_application.html',
                           application=application, job=job, resumes=resumes)


@bp.route('/application/<application_id>/delete', methods=['POST'])
@login_required
def delete_application(application_id):
    """Delete an application"""
    if current_user.user_type != 'candidate':
        flash('Only candidates can delete applications.', 'error')
        return redirect(url_for('main.index'))

    storage = get_storage()
    application = storage.get_application_by_id(application_id)

    if not application:
        flash('Application not found.', 'error')
        return redirect(url_for('candidates.my_applications'))

    # Check ownership
    if application.get('candidate_id') != current_user.id:
        flash('Access denied.', 'error')
        return redirect(url_for('candidates.my_applications'))

    # Get job details for flash message
    job = storage.get_job_by_id(application.get('job_id', ''))
    job_title = job.get('title', 'Unknown Job') if job else 'Unknown Job'

    try:
        # Delete the application
        storage.delete_application(application_id)

        flash(f'Application for "{job_title}" deleted successfully.', 'success')
        return redirect(url_for('candidates.my_applications'))

    except Exception as e:
        current_app.logger.error(f'Error deleting application: {str(e)}')
        flash(f'Error deleting application: {str(e)}', 'error')
        return redirect(url_for('candidates.my_applications'))
