"""
Main routes - Home page and general pages (File-based storage)
"""
from flask import Blueprint, render_template, redirect, url_for
from flask_login import current_user
from app.storage import get_storage

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    """Home page - redirect candidates to their dashboard"""
    # Redirect authenticated candidates to their dashboard
    if current_user.is_authenticated and current_user.user_type == 'candidate':
        return redirect(url_for('dashboard.candidate_dashboard'))

    # Get recent job posts for homepage
    storage = get_storage()
    all_jobs = storage.get_all_jobs(active_only=True)
    # Sort by created_at and get first 6
    recent_jobs = sorted(all_jobs, key=lambda x: x.get('created_at', ''), reverse=True)[:6]

    return render_template('index.html', jobs=recent_jobs)

@bp.route('/about')
def about():
    """About page"""
    return render_template('about.html')

@bp.route('/how-it-works')
def how_it_works():
    """How it works page"""
    return render_template('how_it_works.html')
