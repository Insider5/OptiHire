"""
Live Interview Room
───────────────────
URL prefix : /interview

Routes
------
GET  /interview/room/<app_id>           → render full-screen interview room
GET  /interview/room/<app_id>/state     → AJAX: fetch current code / language
POST /interview/room/<app_id>/state     → AJAX: save code / language / notes
POST /interview/room/<app_id>/end       → recruiter ends the interview
GET  /interview/room/<app_id>/feedback  → post-interview scoring form (recruiter)
POST /interview/room/<app_id>/feedback  → submit scores + hire decision
"""
from flask import (Blueprint, render_template, request, jsonify,
                   redirect, url_for, flash)
from flask_login import login_required, current_user
from app.storage import get_storage
from datetime import datetime
import json

bp = Blueprint('interview_room', __name__, url_prefix='/interview')

# ── Starter code per language ─────────────────────────────────────────────────
STARTER = {
    'python': (
        '# Python 3\n'
        'def solution():\n'
        '    # Write your solution here\n'
        '    pass\n\n'
        'print(solution())\n'
    ),
    'javascript': (
        '// JavaScript (Node.js)\n'
        'function solution() {\n'
        '    // Write your solution here\n'
        '    return null;\n'
        '}\n\n'
        'console.log(solution());\n'
    ),
    'java': (
        '// Java\n'
        'public class Solution {\n'
        '    public static void main(String[] args) {\n'
        '        // Write your solution here\n'
        '        System.out.println("Output: ");\n'
        '    }\n'
        '}\n'
    ),
    'cpp': (
        '// C++\n'
        '#include <iostream>\n'
        'using namespace std;\n\n'
        'int main() {\n'
        '    // Write your solution here\n'
        '    cout << "Output: " << endl;\n'
        '    return 0;\n'
        '}\n'
    ),
    'sql': (
        '-- SQL\n'
        'SELECT column1, column2\n'
        'FROM table_name\n'
        'WHERE condition = true\n'
        'ORDER BY column1;\n'
    ),
    'typescript': (
        '// TypeScript\n'
        'function solution(): string {\n'
        '    // Write your solution here\n'
        '    return "";\n'
        '}\n\n'
        'console.log(solution());\n'
    ),
    'go': (
        '// Go\n'
        'package main\n\n'
        'import "fmt"\n\n'
        'func main() {\n'
        '    // Write your solution here\n'
        '    fmt.Println("Output: ")\n'
        '}\n'
    ),
    'rust': (
        '// Rust\n'
        'fn main() {\n'
        '    // Write your solution here\n'
        '    println!("Output: ");\n'
        '}\n'
    ),
}

LANG_NAMES = {
    'python': 'Python 3',
    'javascript': 'JavaScript',
    'java': 'Java',
    'cpp': 'C++',
    'sql': 'SQL',
    'typescript': 'TypeScript',
    'go': 'Go',
    'rust': 'Rust',
}


# ── Authorization helper ──────────────────────────────────────────────────────
def _authorize(application_id):
    """Return (application, job, role) or (None, None, None) if unauthorized."""
    storage = get_storage()
    app = storage.get_application_by_id(application_id)
    if not app:
        return None, None, None
    job = storage.get_job_by_id(app.get('job_id', ''))
    is_cand = app.get('candidate_id') == current_user.id
    is_rec  = (
        current_user.user_type == 'recruiter' and
        job and job.get('recruiter_id') == current_user.id
    )
    if not is_cand and not is_rec:
        return None, None, None
    return app, job, ('recruiter' if is_rec else 'candidate')


# ── Routes ────────────────────────────────────────────────────────────────────
@bp.route('/room/<application_id>')
@login_required
def room(application_id):
    """Render the full-screen live interview room."""
    storage = get_storage()
    application, job, role = _authorize(application_id)

    if not application:
        flash('Access denied or application not found.', 'error')
        return redirect(url_for('main.index'))

    if not application.get('chosen_slot'):
        flash('Interview slot has not been confirmed yet.', 'warning')
        return redirect(url_for('candidates.view_application',
                                application_id=application_id))

    # Seed room state on first open
    if not application.get('room_opened_at'):
        storage.update_application(application_id, {
            'room_opened_at': datetime.now().isoformat(),
            'room_code':      STARTER['python'],
            'room_language':  'python',
        })
        application = storage.get_application_by_id(application_id)

    candidate = storage.get_user_by_id(application.get('candidate_id', ''))
    resume    = storage.get_resume_by_id(application.get('resume_id', ''))

    skills = []
    if resume:
        raw = resume.get('skills', '[]')
        try:
            skills = json.loads(raw) if isinstance(raw, str) else (raw or [])
        except Exception:
            pass

    iq = application.get('interview_questions', [])
    if isinstance(iq, str):
        try:
            iq = json.loads(iq)
        except Exception:
            iq = []

    mb = application.get('match_breakdown', {})
    if isinstance(mb, str):
        try:
            mb = json.loads(mb)
        except Exception:
            mb = {}

    return render_template(
        'interview/room.html',
        application=application,
        job=job,
        candidate=candidate,
        skills=skills[:10],
        interview_questions=iq,
        match_breakdown=mb,
        role=role,
        room_ended=bool(application.get('room_ended_at')),
        starter_codes=STARTER,
        lang_names=LANG_NAMES,
        current_language=application.get('room_language', 'python'),
        current_code=application.get('room_code', STARTER['python']),
    )


@bp.route('/room/<application_id>/state')
@login_required
def get_state(application_id):
    """AJAX – return current code + language + ended flag for polling."""
    application, _, _ = _authorize(application_id)
    if not application:
        return jsonify({'error': 'Not found'}), 404
    return jsonify({
        'code':     application.get('room_code', ''),
        'language': application.get('room_language', 'python'),
        'code_at':  application.get('room_code_at', ''),
        'ended':    bool(application.get('room_ended_at')),
    })


@bp.route('/room/<application_id>/state', methods=['POST'])
@login_required
def save_state(application_id):
    """AJAX – save code / language / recruiter notes."""
    application, _, _ = _authorize(application_id)
    if not application:
        return jsonify({'error': 'Not found'}), 404
    if application.get('room_ended_at'):
        return jsonify({'error': 'Room ended', 'ended': True}), 400

    data = request.get_json(silent=True) or {}
    updates = {'room_code_at': datetime.now().isoformat()}

    if 'code' in data:
        updates['room_code'] = str(data['code'])[:50_000]
    if 'language' in data and data['language'] in STARTER:
        updates['room_language'] = data['language']
    if 'notes' in data and current_user.user_type == 'recruiter':
        updates['room_recruiter_notes'] = str(data['notes'])[:5_000]

    get_storage().update_application(application_id, updates)
    return jsonify({'ok': True, 'saved_at': updates['room_code_at']})


@bp.route('/room/<application_id>/end', methods=['POST'])
@login_required
def end_room(application_id):
    """Recruiter ends the live interview room."""
    application, _, role = _authorize(application_id)
    if not application or role != 'recruiter':
        flash('Only the recruiter can end the interview.', 'error')
        return redirect(url_for('interview_room.room',
                                application_id=application_id))

    if not application.get('room_ended_at'):
        get_storage().update_application(application_id, {
            'room_ended_at': datetime.now().isoformat()
        })

    return redirect(url_for('interview_room.feedback',
                            application_id=application_id))


@bp.route('/room/<application_id>/feedback', methods=['GET', 'POST'])
@login_required
def feedback(application_id):
    """Post-interview scoring + hiring decision form (recruiter only)."""
    storage = get_storage()
    application, job, role = _authorize(application_id)

    if not application or role != 'recruiter':
        flash('Access denied.', 'error')
        return redirect(url_for('main.index'))

    candidate = storage.get_user_by_id(application.get('candidate_id', ''))

    if request.method == 'POST':
        raw_score = request.form.get('overall_score', '').strip()
        final_fb  = request.form.get('final_feedback', '').strip()
        decision  = request.form.get('decision', '').strip()

        updates = {'interview_final_feedback': final_fb[:2_000]}
        try:
            s = int(raw_score)
            if 1 <= s <= 5:
                updates['interview_overall_score'] = s
        except (ValueError, TypeError):
            pass

        if decision in ('hired', 'rejected', 'pending'):
            updates['status'] = decision

        storage.update_application(application_id, updates)

        if decision == 'hired':
            storage.create_notification({
                'user_id':           application.get('candidate_id'),
                'application_id':    application_id,
                'title':             "🎉 Congratulations — You've been hired!",
                'message':           (
                    f'The recruiter has decided to move forward with you for '
                    f'{job.get("title", "the role")} at {job.get("company", "")}.'
                ),
                'notification_type': 'success',
            })
        elif decision == 'rejected':
            storage.create_notification({
                'user_id':           application.get('candidate_id'),
                'application_id':    application_id,
                'title':             'Application Status Update',
                'message':           (
                    f'Thank you for interviewing for {job.get("title", "the role")} '
                    f'at {job.get("company", "")}. After careful consideration, '
                    f'we have decided not to move forward at this time.'
                ),
                'notification_type': 'info',
            })

        flash('Interview feedback saved! ✅', 'success')
        return redirect(url_for('candidates.view_application',
                                application_id=application_id))

    return render_template(
        'interview/feedback.html',
        application=application,
        job=job,
        candidate=candidate,
    )
