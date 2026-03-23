"""
Analytics routes — Score distribution, recruiter stats, candidate progress
"""
from flask import Blueprint, render_template, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app.storage import get_storage

bp = Blueprint('analytics', __name__, url_prefix='/analytics')


@bp.route('/recruiter')
@login_required
def recruiter_analytics():
    """Recruiter analytics dashboard"""
    if current_user.user_type != 'recruiter':
        flash('Access denied.', 'error')
        return redirect(url_for('dashboard.recruiter_dashboard'))

    storage = get_storage()
    summary = storage.analytics_summary(recruiter_id=current_user.id)

    # Get all applications for this recruiter's jobs with enriched data
    all_jobs = storage.get_jobs_by_recruiter(current_user.id)
    all_applications = []
    for job in all_jobs:
        apps = storage.get_applications_by_job(job['id'])
        for app in apps:
            app['job_title'] = job.get('title', 'Unknown')
        all_applications.extend(apps)

    return render_template('analytics/recruiter_analytics.html',
                           summary=summary,
                           applications=all_applications,
                           jobs=all_jobs)


@bp.route('/candidate')
@login_required
def candidate_analytics():
    """Candidate analytics — score trend, skill gaps"""
    if current_user.user_type != 'candidate':
        flash('Access denied.', 'error')
        return redirect(url_for('dashboard.candidate_dashboard'))

    storage = get_storage()
    applications = storage.get_applications_by_candidate(current_user.id)
    applications = sorted(applications, key=lambda x: x.get('applied_at', ''))

    # Enrich with job info
    for app in applications:
        app['job'] = storage.get_job_by_id(app.get('job_id', ''))

    # Build score timeline data
    labels = []
    scores = []
    for app in applications:
        job = app.get('job')
        labels.append(job.get('title', 'Job') if job else 'Job')
        scores.append(round((app.get('similarity_score', 0) or 0) * 100, 1))

    # Aggregate skill gaps across all applications
    all_missing = {}
    all_matched = {}
    for app in applications:
        breakdown = app.get('match_breakdown') or {}
        for skill in breakdown.get('missing_skills', []):
            all_missing[skill] = all_missing.get(skill, 0) + 1
        for skill in breakdown.get('matched_skills', []):
            all_matched[skill] = all_matched.get(skill, 0) + 1

    top_missing = sorted(all_missing.items(), key=lambda x: x[1], reverse=True)[:8]
    top_matched = sorted(all_matched.items(), key=lambda x: x[1], reverse=True)[:8]

    return render_template('analytics/candidate_analytics.html',
                           applications=applications,
                           score_labels=labels,
                           score_data=scores,
                           top_missing=top_missing,
                           top_matched=top_matched)


@bp.route('/api/recruiter-summary')
@login_required
def api_recruiter_summary():
    """JSON API for recruiter analytics charts"""
    if current_user.user_type != 'recruiter':
        return jsonify({'error': 'Access denied'}), 403
    storage = get_storage()
    return jsonify(storage.analytics_summary(recruiter_id=current_user.id))
