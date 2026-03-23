"""
User model for Flask-Login (file-based storage)
"""
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app.storage import get_storage


class User(UserMixin):
    """User class for Flask-Login"""

    def __init__(self, user_data: dict):
        """Initialize user from dict"""
        self.id = user_data.get('id')
        self.email = user_data.get('email')
        self.username = user_data.get('username')
        self.password_hash = user_data.get('password_hash')
        self.full_name = user_data.get('full_name')
        self.user_type = user_data.get('user_type', 'candidate')
        self._is_active = user_data.get('is_active', True)

    @property
    def is_active(self):
        """Get is_active status"""
        return self._is_active

    @is_active.setter
    def is_active(self, value):
        """Set is_active status"""
        self._is_active = value

    def check_password(self, password: str) -> bool:
        """Check if password matches hash"""
        return check_password_hash(self.password_hash, password)

    def update_profile(self, full_name: str = None, email: str = None) -> bool:
        """Update user profile fields in storage"""
        updates = {}
        if full_name and full_name.strip():
            updates['full_name'] = full_name.strip()
        if email and email.strip():
            updates['email'] = email.strip()
        if not updates:
            return False
        storage = get_storage()
        result = storage.update_user(self.id, updates)
        if result:
            if 'full_name' in updates:
                self.full_name = updates['full_name']
            if 'email' in updates:
                self.email = updates['email']
        return result

    def change_password(self, new_password: str) -> bool:
        """Hash a new password and persist it"""
        if len(new_password) < 6:
            return False
        new_hash = generate_password_hash(new_password)
        storage = get_storage()
        result = storage.update_user(self.id, {'password_hash': new_hash})
        if result:
            self.password_hash = new_hash
        return result

    @staticmethod
    def create(username, email, password, full_name, user_type='candidate'):
        """Create new user"""
        storage = get_storage()
        user_data = {
            'username': username,
            'email': email,
            'password_hash': generate_password_hash(password),
            'full_name': full_name,
            'user_type': user_type
        }
        created_user = storage.create_user(user_data)
        return User(created_user)

    @staticmethod
    def get_by_id(user_id):
        """Get user by ID"""
        storage = get_storage()
        user_data = storage.get_user_by_id(user_id)
        if user_data:
            return User(user_data)
        return None

    @staticmethod
    def get_by_email(email):
        """Get user by email"""
        storage = get_storage()
        user_data = storage.get_user_by_email(email)
        if user_data:
            return User(user_data)
        return None

    @staticmethod
    def get_by_username(username):
        """Get user by username"""
        storage = get_storage()
        user_data = storage.get_user_by_username(username)
        if user_data:
            return User(user_data)
        return None

    def __repr__(self):
        return f'<User {self.username} ({self.user_type})>'


def load_user(user_id):
    """Load user for Flask-Login"""
    return User.get_by_id(user_id)
