"""
Dashboard routes for recruiters and candidates (File-based storage)
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from datetime import datetime
from flask_login import login_required, current_user
from app.storage import get_storage
from app.services.semantic_matcher import get_semantic_matcher
from app.services.email_service import send_status_email
from app.services.calendar_service import schedule_interview as calendar_schedule

bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')

@bp.route('/')
@login_required
def index():
    """Redirect to appropriate dashboard based on user type"""
    if current_user.user_type == 'recruiter':
        return redirect(url_for('dashboard.recruiter_dashboard'))
    else:
        return redirect(url_for('dashboard.candidate_dashboard'))

@bp.route('/recruiter')
@login_required
def recruiter_dashboard():
    """Recruiter dashboard - view jobs and applications"""
    if current_user.user_type != 'recruiter':
        flash('Access denied', 'error')
        return redirect(url_for('main.index'))
    
    storage = get_storage()
    
    # Get recruiter's job posts
    jobs = storage.get_jobs_by_recruiter(current_user.id)
    
    # Sort by created_at descending
    jobs = sorted(jobs, key=lambda x: x.get('created_at', ''), reverse=True)
    
    # Get statistics
    total_jobs = len(jobs)
    active_jobs = sum(1 for job in jobs if job.get('is_active', True))
    
    # Get all applications for recruiter's jobs
    job_ids = [job['id'] for job in jobs]
    all_applications = []
    for job_id in job_ids:
        apps = storage.get_applications_by_job(job_id)
        all_applications.extend(apps)
    
    total_applications = len(all_applications)
    pending_applications = sum(1 for app in all_applications if app.get('status') == 'pending')
    
    # Get recent applications with job data
    recent_applications = sorted(all_applications, key=lambda x: x.get('applied_at', ''), reverse=True)[:10]
    
    # Attach job data to applications
    for app in recent_applications:
        app['job'] = storage.get_job_by_id(app['job_id'])
        # Get candidate info
        from app.user import User
        candidate = User.get_by_id(app['candidate_id'])
        if candidate:
            app['candidate'] = {
                'id': candidate.id,
                'full_name': candidate.full_name,
                'email': candidate.email
            }
    
    stats = {
        'total_jobs': total_jobs,
        'active_jobs': active_jobs,
        'total_applications': total_applications,
        'pending_applications': pending_applications
    }
    
    # ── Interview Calendar data ───────────────────────────────────────
    from datetime import datetime as _dt
    interview_events = []
    for app in all_applications:
        chosen = app.get('chosen_slot')
        if chosen and app.get('status') == 'interview':
            try:
                slot_clean = chosen.replace(' IST', '').strip()
                dt = _dt.strptime(slot_clean, '%d %b %Y at %I:%M %p')
                date_key = dt.strftime('%Y-%m-%d')
                time_str = dt.strftime('%I:%M %p')
            except ValueError:
                continue
            job_item = storage.get_job_by_id(app['job_id'])
            cand_data = storage.get_user_by_id(app['candidate_id'])
            resume_data = storage.get_resume_by_id(app['resume_id']) if app.get('resume_id') else None
            skills, exp_years = [], 0
            if resume_data and resume_data.get('parsed_data'):
                pd = resume_data['parsed_data']
                skills = pd.get('skills', [])[:8]
                exp_years = round(float(pd.get('experience_years') or 0), 1)
            interview_events.append({
                'date': date_key,
                'time': time_str,
                'candidate_name':  cand_data.get('full_name', 'Unknown') if cand_data else 'Unknown',
                'candidate_email': cand_data.get('email', '') if cand_data else '',
                'job_title':       job_item.get('title', '') if job_item else '',
                'company':         job_item.get('company', '') if job_item else '',
                'similarity_score': int(round(app.get('similarity_score', 0) * 100)),
                'interview_duration': app.get('interview_duration', 60),
                'interview_notes':    app.get('interview_notes', ''),
                'application_id':  app['id'],
                'resume_id':       app.get('resume_id', ''),
                'skills':          skills,
                'exp_years':       exp_years,
            })
    interview_events.sort(key=lambda x: (x['date'], x['time']))

    return render_template('dashboard/recruiter.html',
                         jobs=jobs,
                         stats=stats,
                         recent_applications=recent_applications,
                         interview_events=interview_events)

@bp.route('/candidate')
@login_required
def candidate_dashboard():
    """Candidate dashboard - view applications and recommendations"""
    if current_user.user_type != 'candidate':
        flash('Access denied', 'error')
        return redirect(url_for('main.index'))
    
    storage = get_storage()
    
    # Get candidate's applications
    applications = storage.get_applications_by_candidate(current_user.id)
    
    # Sort by applied_at descending
    applications = sorted(applications, key=lambda x: x.get('applied_at', ''), reverse=True)
    
    # Attach job data to applications and convert dates
    for app in applications:
        if isinstance(app.get('applied_at'), str):
            try:
                app['applied_at'] = datetime.fromisoformat(app['applied_at'])
            except ValueError:
                pass
        app['job'] = storage.get_job_by_id(app['job_id'])
    
    # Get candidate's resumes
    resumes = storage.get_resumes_by_user(current_user.id)
    
    # Get statistics
    total_applications = len(applications)
    pending = sum(1 for app in applications if app.get('status') == 'pending')
    shortlisted = sum(1 for app in applications if app.get('status') == 'shortlisted')
    rejected = sum(1 for app in applications if app.get('status') == 'rejected')
    
    # Calculate average match score
    avg_score = 0
    if applications:
        scores = [app['similarity_score'] for app in applications if app.get('similarity_score')]
        if scores:
            avg_score = sum(scores) / len(scores) * 100
    
    # Get notifications
    notifications = storage.get_notifications_by_user(current_user.id, unread_only=True)
    
    # Sort notifications by created_at descending
    notifications = sorted(notifications, key=lambda x: x.get('created_at', ''), reverse=True)[:5]

    # Convert notification dates strings to datetime objects for template formatting
    for notif in notifications:
        if isinstance(notif.get('created_at'), str):
            try:
                notif['created_at'] = datetime.fromisoformat(notif['created_at'])
            except ValueError:
                pass
    
    # Get recommended jobs based on resume
    recommended_jobs = []
    if resumes:
        # Get all active jobs
        all_jobs = storage.get_all_jobs(active_only=True)
        
        # Get latest resume
        latest_resume = sorted(resumes, key=lambda x: x.get('created_at', ''), reverse=True)[0]
        
        # Get semantic matcher
        matcher = get_semantic_matcher()
        
        # Prepare job data list
        job_data_list = []
        for job in all_jobs[:20]:  # Limit to 20 jobs for performance
            # Skip if already applied
            if storage.get_existing_application(job['id'], current_user.id):
                continue
            
            job_data_list.append({
                'id': job['id'],
                'title': job['title'],
                'company': job['company'],
                'description': job['description'],
                'requirements': job['requirements'],
                'skills_required': job.get('skills_required'),
                'experience_level': job.get('experience_level'),
                'location': job.get('location')
            })
        
        if job_data_list:
            try:
                # Batch match
                matches = matcher.batch_match(latest_resume['parsed_data'], job_data_list)
                
                # Get top 5 matches
                top_matches = matches[:5]
                
                for match in top_matches:
                    job = storage.get_job_by_id(match['job_id'])
                    if job:
                        recommended_jobs.append({
                            'job': job,
                            'score': match['score']
                        })
            except Exception as e:
                print(f"Error generating recommendations: {e}")
    
    stats = {
        'total_applications': total_applications,
        'pending': pending,
        'shortlisted': shortlisted,
        'rejected': rejected,
        'avg_score': avg_score,
        'total_resumes': len(resumes)
    }
    
    return render_template('dashboard/candidate.html',
                         applications=applications,
                         resumes=resumes,
                         stats=stats,
                         notifications=notifications,
                         recommended_jobs=recommended_jobs)

@bp.route('/job/<job_id>/applications')
@login_required
def view_job_applications(job_id):
    """View all applications for a specific job"""
    storage = get_storage()
    job = storage.get_job_by_id(job_id)
    
    if not job:
        flash('Job not found', 'error')
        return redirect(url_for('dashboard.recruiter_dashboard'))
    
    # Check ownership
    if job['recruiter_id'] != current_user.id:
        flash('Access denied', 'error')
        return redirect(url_for('dashboard.recruiter_dashboard'))
    
    # Get applications
    applications = storage.get_applications_by_job(job_id)
    
    # Sort by similarity_score descending
    applications = sorted(applications, key=lambda x: x.get('similarity_score', 0), reverse=True)
    
    # Attach candidate and resume data
    for app in applications:
        from app.user import User
        candidate = User.get_by_id(app['candidate_id'])
        if candidate:
            app['candidate'] = {
                'id': candidate.id,
                'full_name': candidate.full_name,
                'email': candidate.email
            }
        app['resume'] = storage.get_resume_by_id(app['resume_id'])
    
    return render_template('dashboard/job_applications.html', job=job, applications=applications)

@bp.route('/application/<application_id>/update-status', methods=['POST'])
@login_required
def update_application_status(application_id):
    """Update application status (recruiter only)"""
    storage = get_storage()
    application = storage.get_application_by_id(application_id)
    
    if not application:
        flash('Application not found', 'error')
        return redirect(url_for('dashboard.recruiter_dashboard'))
    
    # Get job to check ownership
    job = storage.get_job_by_id(application['job_id'])
    
    # Check if recruiter owns the job
    if job['recruiter_id'] != current_user.id:
        flash('Access denied', 'error')
        return redirect(url_for('dashboard.recruiter_dashboard'))
    
    new_status = request.form.get('status')
    
    if new_status not in ['pending', 'shortlisted', 'rejected', 'interview', 'hired']:
        flash('Invalid status', 'error')
        return redirect(url_for('candidates.view_application', application_id=application_id))
    
    # Update status
    storage.update_application(application_id, {'status': new_status})

    # Send email notification to candidate
    candidate = storage.get_user_by_id(application['candidate_id'])
    email_sent = False
    if candidate:
        try:
            email_sent = send_status_email(
                candidate_email=candidate.get('email', ''),
                candidate_name=candidate.get('full_name', 'Candidate'),
                job_title=job.get('title', 'the position'),
                company=job.get('company', ''),
                new_status=new_status,
                application_id=application_id
            )
        except Exception as e:
            current_app.logger.error(f'Email notification failed: {e}')
            email_sent = False
    
    # Create notification for candidate
    status_messages = {
        'shortlisted': 'Congratulations! You have been shortlisted.',
        'rejected': 'Thank you for applying. Unfortunately, we have decided to move forward with other candidates.',
        'interview': 'You have been selected for an interview!',
        'hired': 'Congratulations! You have been selected for the position!'
    }
    
    if new_status in status_messages:
        storage.create_notification({
            'user_id': application['candidate_id'],
            'application_id': application_id,
            'title': f'Application Update - {job["title"]}',
            'message': status_messages[new_status],
            'notification_type': 'success' if new_status in ['shortlisted', 'interview', 'hired'] else 'warning'
        })
    
    if email_sent:
        flash(f'Status updated to {new_status}. Email notification sent to candidate.', 'success')
    else:
        flash(f'Status updated to {new_status}. ⚠️ Email could not be sent — check SMTP settings in .env.', 'warning')
    return redirect(url_for('candidates.view_application', application_id=application_id))


@bp.route('/application/<application_id>/schedule-interview', methods=['POST'])
@login_required
def schedule_interview(application_id):
    """Schedule an interview for an application (recruiter only)."""
    from flask import send_file
    import io

    storage = get_storage()
    application = storage.get_application_by_id(application_id)

    if not application:
        flash('Application not found', 'error')
        return redirect(url_for('dashboard.recruiter_dashboard'))

    job = storage.get_job_by_id(application['job_id'])
    if not job or job['recruiter_id'] != current_user.id:
        flash('Access denied', 'error')
        return redirect(url_for('dashboard.recruiter_dashboard'))

    # Parse up to 3 slot options provided by the recruiter
    from app.services.email_service import send_slot_selection_email
    from app.routes.interviews import make_slot_token
    from datetime import datetime as _dt

    slots = []
    for i in range(1, 4):
        d = request.form.get(f'slot_{i}_date', '').strip()
        t = request.form.get(f'slot_{i}_time', '').strip()
        if d and t:
            try:
                readable = _dt.strptime(f'{d} {t}', '%Y-%m-%d %H:%M').strftime('%d %b %Y at %I:%M %p IST')
            except ValueError:
                readable = f'{d} at {t}'
            slots.append(readable)

    if not slots:
        flash('Please add at least one interview slot option.', 'error')
        return redirect(url_for('candidates.view_application', application_id=application_id))

    notes = request.form.get('notes', '').strip()
    try:
        duration_minutes = int(request.form.get('duration', '60').strip())
    except ValueError:
        duration_minutes = 60

    candidate = storage.get_user_by_id(application['candidate_id'])
    if not candidate:
        flash('Candidate not found', 'error')
        return redirect(url_for('candidates.view_application', application_id=application_id))

    # Generate HMAC token for the candidate's slot-selection URL
    token = make_slot_token(application_id, current_app.config['SECRET_KEY'])

    # Persist slots on the application; clear any previous choice
    storage.update_application(application_id, {
        'interview_slots':    slots,
        'interview_duration': duration_minutes,
        'interview_notes':    notes,
        'slot_token':         token,
        'chosen_slot':        None,
    })

    # Email candidate with slot options + secure selection link
    base_url = current_app.config.get('APPLICATION_BASE_URL', 'http://localhost:5000')
    slot_url = f"{base_url}/interviews/choose-slot/{application_id}?token={token}"

    sent = send_slot_selection_email(
        candidate_email=candidate.get('email', ''),
        candidate_name=candidate.get('full_name', 'Candidate'),
        job_title=job.get('title', 'the position'),
        company=job.get('company', ''),
        slots=slots,
        slot_selection_url=slot_url,
    )

    # In-app notification for candidate
    storage.create_notification({
        'user_id':           application['candidate_id'],
        'application_id':    application_id,
        'title':             f'Interview Slot Options — {job["title"]}',
        'message':           f'The recruiter has offered {len(slots)} interview slot(s). Check your email to pick your preferred time.',
        'notification_type': 'info',
    })

    if sent:
        flash(
            f'✅ Interview slot options sent to {candidate.get("email")}. '
            f'The candidate will choose their preferred slot.',
            'success'
        )
    else:
        flash(
            f'Slot options saved. ⚠️ Email could not be sent — check SMTP settings in .env.',
            'warning'
        )
    return redirect(url_for('candidates.view_application', application_id=application_id))


# ─── Auto-Shortlist Agent ─────────────────────────────────────────────────────

@bp.route('/job/<job_id>/auto-shortlist', methods=['POST'])
@login_required
def auto_shortlist(job_id):
    """
    Auto-Shortlist Agent (recruiter only).

    1. Reads a match-score threshold from the form.
    2. Shortlists all pending candidates above the threshold.
    3. Sends each shortlisted candidate a slot-selection email with
       the recruiter-defined interview time options.
    """
    from app.services.email_service import send_slot_selection_email
    from app.routes.interviews import make_slot_token

    storage = get_storage()
    job = storage.get_job_by_id(job_id)

    if not job or job['recruiter_id'] != current_user.id:
        flash('Access denied.', 'error')
        return redirect(url_for('dashboard.recruiter_dashboard'))

    # ── Read form values ────────────────────────────────────────
    try:
        threshold = max(0, min(100, int(request.form.get('threshold', 70))))
    except ValueError:
        threshold = 70

    slots = []
    for i in range(1, 4):
        d = request.form.get(f'slot_{i}_date', '').strip()
        t = request.form.get(f'slot_{i}_time', '').strip()
        if d and t:
            try:
                from datetime import datetime as _dt
                readable = _dt.strptime(f'{d} {t}', '%Y-%m-%d %H:%M').strftime('%d %b %Y at %I:%M %p IST')
            except ValueError:
                readable = f'{d} at {t}'
            slots.append(readable)

    if not slots:
        flash('Please provide at least one interview slot before running the agent.', 'error')
        return redirect(url_for('dashboard.view_job_applications', job_id=job_id))

    # ── Find candidates above threshold with pending status ─────
    applications   = storage.get_applications_by_job(job_id)
    base_url       = current_app.config.get('APPLICATION_BASE_URL', 'http://localhost:5000')
    shortlisted_n  = 0
    emailed_n      = 0

    for app in applications:
        score_pct = round((app.get('similarity_score') or 0) * 100)
        if app.get('status') != 'pending' or score_pct < threshold:
            continue

        app_id = app['id']
        token  = make_slot_token(app_id, current_app.config['SECRET_KEY'])

        # Update application: shortlisted + store slots for candidate to choose
        storage.update_application(app_id, {
            'status':          'shortlisted',
            'interview_slots': slots,
            'slot_token':      token,
        })
        shortlisted_n += 1

        candidate = storage.get_user_by_id(app['candidate_id'])
        if not candidate:
            continue

        # In-app notification for candidate
        storage.create_notification({
            'user_id':           app['candidate_id'],
            'application_id':    app_id,
            'title':             f"You've been shortlisted! — {job['title']}",
            'message':           'Congratulations! Check your email to choose your interview slot.',
            'notification_type': 'success',
        })

        # Email with slot-selection link
        slot_url = f"{base_url}/interviews/choose-slot/{app_id}?token={token}"
        sent = send_slot_selection_email(
            candidate_email=candidate.get('email', ''),
            candidate_name=candidate.get('full_name', 'Candidate'),
            job_title=job.get('title', 'the position'),
            company=job.get('company', ''),
            slots=slots,
            slot_selection_url=slot_url,
        )
        if sent:
            emailed_n += 1

    if shortlisted_n == 0:
        flash(
            f'No pending candidates met the {threshold}% threshold. '
            f'Try lowering it or check that there are pending applications.',
            'warning',
        )
    else:
        flash(
            f'✅ Auto-Shortlist Agent complete: {shortlisted_n} candidate(s) shortlisted above {threshold}% match. '
            f'Slot-selection emails sent to {emailed_n} candidate(s).',
            'success',
        )

    return redirect(url_for('dashboard.view_job_applications', job_id=job_id))

