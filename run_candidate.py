"""
Candidate portal entry point - runs on port 5001 with separate session
"""
import os
from app import create_app
from app.user import User
from app.storage import get_storage

# Create app with different session cookie name to avoid conflicts
app = create_app(os.getenv('FLASK_ENV', 'development'))
app.config['SESSION_COOKIE_NAME'] = 'session_candidate'

@app.shell_context_processor
def make_shell_context():
    """Make storage and user model available in flask shell"""
    return {
        'storage': get_storage(),
        'User': User
    }

if __name__ == '__main__':
    print("Starting Candidate Portal on port 5001...")
    app.run(debug=True, host='0.0.0.0', port=5001)
