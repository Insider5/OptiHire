"""
Interview Preparation Routes
Provides chatbot interface for candidates to prepare for interviews
"""
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user
from app.storage import get_storage
from app.services.interview_prep_service import get_prep_chatbot
import json

bp = Blueprint('interview_prep', __name__, url_prefix='/interview-prep')


@bp.route('/<job_id>')
@login_required
def preparation_page(job_id):
    """Main interview preparation page with chatbot"""
    if current_user.user_type != 'candidate':
        flash('This feature is for candidates only.', 'error')
        return redirect(url_for('dashboard.index'))

    storage = get_storage()
    job = storage.get_job_by_id(job_id)

    if not job:
        flash('Job not found.', 'error')
        return redirect(url_for('jobs.list_jobs'))

    # Get job insights for initial display
    chatbot = get_prep_chatbot()
    insights = chatbot.get_job_insights(job)

    # Check if candidate has applied
    applications = storage.get_applications_by_candidate(current_user.id)
    has_applied = any(app.get('job_id') == job_id for app in applications)

    # Get the application if exists
    application = None
    for app in applications:
        if app.get('job_id') == job_id:
            application = app
            break

    return render_template(
        'interview/preparation.html',
        job=job,
        insights=insights,
        has_applied=has_applied,
        application=application
    )


@bp.route('/<job_id>/chat', methods=['POST'])
@login_required
def chat(job_id):
    """Handle chat messages from the candidate"""
    if current_user.user_type != 'candidate':
        return jsonify({'error': 'Access denied'}), 403

    storage = get_storage()
    job = storage.get_job_by_id(job_id)

    if not job:
        return jsonify({'error': 'Job not found'}), 404

    data = request.get_json()
    message = data.get('message', '').strip()
    chat_history = data.get('history', [])

    if not message:
        return jsonify({'error': 'Message is required'}), 400

    chatbot = get_prep_chatbot()
    response = chatbot.chat(message, job, chat_history)

    return jsonify({
        'response': response,
        'success': True
    })


@bp.route('/<job_id>/questions', methods=['GET'])
@login_required
def get_practice_questions(job_id):
    """Get practice questions for a job"""
    if current_user.user_type != 'candidate':
        return jsonify({'error': 'Access denied'}), 403

    storage = get_storage()
    job = storage.get_job_by_id(job_id)

    if not job:
        return jsonify({'error': 'Job not found'}), 404

    question_type = request.args.get('type', 'mixed')

    chatbot = get_prep_chatbot()
    questions = chatbot.generate_practice_questions(job, question_type)

    return jsonify({
        'questions': questions,
        'success': True
    })


@bp.route('/<job_id>/insights', methods=['GET'])
@login_required
def get_insights(job_id):
    """Get AI insights about the job"""
    if current_user.user_type != 'candidate':
        return jsonify({'error': 'Access denied'}), 403

    storage = get_storage()
    job = storage.get_job_by_id(job_id)

    if not job:
        return jsonify({'error': 'Job not found'}), 404

    chatbot = get_prep_chatbot()
    insights = chatbot.get_job_insights(job)

    return jsonify({
        'insights': insights,
        'success': True
    })
