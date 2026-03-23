"""
Profile routes — Edit profile, view notifications, mark as read
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.storage import get_storage
from app.user import User
from datetime import datetime

bp = Blueprint('profile', __name__, url_prefix='/profile')


@bp.route('/edit', methods=['GET', 'POST'])
@login_required
def edit():
    """Edit user profile"""
    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        email = request.form.get('email', '').strip()
        new_password = request.form.get('new_password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()

        errors = []

        if not full_name:
            errors.append('Full name is required.')
        if not email:
            errors.append('Email is required.')

        # Check email uniqueness (skip if same)
        if email and email.lower() != current_user.email.lower():
            storage = get_storage()
            existing = storage.get_user_by_email(email)
            if existing and existing['id'] != current_user.id:
                errors.append('That email is already registered to another account.')

        # Password change (optional)
        if new_password:
            if len(new_password) < 6:
                errors.append('New password must be at least 6 characters.')
            elif new_password != confirm_password:
                errors.append('Passwords do not match.')

        if errors:
            for err in errors:
                flash(err, 'error')
            return render_template('profile/edit.html')

        # Apply updates
        user_obj = User.get_by_id(current_user.id)
        user_obj.update_profile(full_name=full_name, email=email)
        if new_password:
            user_obj.change_password(new_password)
            flash('Profile and password updated successfully! ✅', 'success')
        else:
            flash('Profile updated successfully! ✅', 'success')

        return redirect(url_for('profile.edit'))

    return render_template('profile/edit.html')


@bp.route('/notifications')
@login_required
def notifications():
    """View all notifications"""
    storage = get_storage()
    all_notifs = storage.get_notifications_by_user(current_user.id, unread_only=False)

    # Sort newest first and parse dates
    all_notifs = sorted(all_notifs, key=lambda n: n.get('created_at', ''), reverse=True)
    for n in all_notifs:
        raw = n.get('created_at')
        if isinstance(raw, str):
            try:
                n['created_at_obj'] = datetime.fromisoformat(raw)
            except Exception:
                n['created_at_obj'] = datetime.now()
        else:
            n['created_at_obj'] = datetime.now()

    # Attach application / job info
    for n in all_notifs:
        app_id = n.get('application_id')
        if app_id:
            app = storage.get_application_by_id(app_id)
            if app:
                n['job'] = storage.get_job_by_id(app.get('job_id', ''))

    return render_template('profile/notifications.html', notifications=all_notifs)


@bp.route('/notifications/<notif_id>/read', methods=['POST'])
@login_required
def mark_read(notif_id):
    """Mark a single notification as read"""
    storage = get_storage()
    storage.mark_notification_read(notif_id)
    return redirect(url_for('profile.notifications'))


@bp.route('/notifications/mark-all-read', methods=['POST'])
@login_required
def mark_all_read():
    """Mark all notifications as read"""
    storage = get_storage()
    count = storage.mark_all_notifications_read(current_user.id)
    flash(f'Marked {count} notification(s) as read.', 'success')
    return redirect(url_for('profile.notifications'))
