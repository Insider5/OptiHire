"""
Authentication routes - Login, Register, Logout (File-based storage)
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, login_required, current_user
from app.user import User
from app import login_manager, limiter

bp = Blueprint('auth', __name__, url_prefix='/auth')

@login_manager.user_loader
def load_user(user_id):
    """Load user for Flask-Login"""
    return User.get_by_id(user_id)

@bp.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        full_name = request.form.get('full_name')
        user_type = request.form.get('user_type', 'candidate')
        
        # Validation
        if not all([username, email, password, confirm_password, full_name]):
            flash('All fields are required', 'error')
            return render_template('auth/register.html')
        
        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return render_template('auth/register.html')
        
        if len(password) < 8:
            flash('Password must be at least 8 characters', 'error')
            return render_template('auth/register.html')
        
        if not any(ch.isdigit() for ch in password):
            flash('Password must contain at least one number', 'error')
            return render_template('auth/register.html')
        
        # Check if user exists
        if User.get_by_email(email):
            flash('Email already registered', 'error')
            return render_template('auth/register.html')
        
        if User.get_by_username(username):
            flash('Username already taken', 'error')
            return render_template('auth/register.html')
        
        # Create new user
        user = User.create(
            username=username,
            email=email,
            password=password,
            full_name=full_name,
            user_type=user_type
        )
        
        # Auto-login and redirect to onboarding / dashboard
        login_user(user)
        flash(f'Welcome to OptiHire, {full_name}! 🎉', 'success')
        if user_type == 'recruiter':
            return redirect(url_for('dashboard.recruiter_dashboard'))
        else:
            return redirect(url_for('candidates.onboarding'))
    
    return render_template('auth/register.html')

@bp.route('/login', methods=['GET', 'POST'])
@limiter.limit("10 per minute", methods=["POST"])
def login():
    """User login"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = request.form.get('remember', False)
        
        if not email or not password:
            flash('Please provide email and password', 'error')
            return render_template('auth/login.html')
        
        user = User.get_by_email(email)
        
        if user is None or not user.check_password(password):
            flash('Invalid email or password', 'error')
            return render_template('auth/login.html')
        
        if not user.is_active:
            flash('Your account has been deactivated', 'error')
            return render_template('auth/login.html')
        
        login_user(user, remember=remember)
        
        # Redirect to appropriate dashboard
        next_page = request.args.get('next')
        if next_page:
            return redirect(next_page)
        
        if user.user_type == 'recruiter':
            return redirect(url_for('dashboard.recruiter_dashboard'))
        else:
            return redirect(url_for('dashboard.candidate_dashboard'))
    
    return render_template('auth/login.html')

@bp.route('/logout')
@login_required
def logout():
    """User logout"""
    logout_user()
    flash('You have been logged out successfully', 'info')
    return redirect(url_for('main.index'))
