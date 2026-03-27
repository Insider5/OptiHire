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
                   redirect, url_for, flash, current_app)
from flask_login import login_required, current_user
from flask_socketio import emit, join_room, leave_room
from app.storage import get_storage
from app.services.email_service import send_status_email
from app import socketio
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
            # Send hire notification email to candidate
            send_status_email(
                candidate_email=candidate.get('email', ''),
                candidate_name=candidate.get('full_name', candidate.get('username', 'Candidate')),
                job_title=job.get('title', 'the role'),
                company=job.get('company', ''),
                new_status='hired',
                application_id=application_id
            )
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
            # Send rejection notification email to candidate
            send_status_email(
                candidate_email=candidate.get('email', ''),
                candidate_name=candidate.get('full_name', candidate.get('username', 'Candidate')),
                job_title=job.get('title', 'the role'),
                company=job.get('company', ''),
                new_status='rejected',
                application_id=application_id
            )

        flash('Interview feedback saved! ✅', 'success')
        return redirect(url_for('candidates.view_application',
                                application_id=application_id))

    return render_template(
        'interview/feedback.html',
        application=application,
        job=job,
        candidate=candidate,
    )


@bp.route('/room/<application_id>/candidate-feedback', methods=['GET', 'POST'])
@login_required
def candidate_feedback(application_id):
    """Post-interview feedback form for candidates to rate their experience."""
    storage = get_storage()
    application, job, role = _authorize(application_id)

    if not application or role != 'candidate':
        flash('Access denied.', 'error')
        return redirect(url_for('main.index'))

    # Check if interview has ended
    if not application.get('room_ended_at'):
        flash('Interview has not ended yet.', 'warning')
        return redirect(url_for('interview_room.room',
                                application_id=application_id))

    # Check if already submitted
    if application.get('candidate_feedback_submitted'):
        flash('You have already submitted feedback for this interview.', 'info')
        return redirect(url_for('candidates.view_application',
                                application_id=application_id))

    recruiter = storage.get_user_by_id(job.get('recruiter_id', '')) if job else None

    if request.method == 'POST':
        experience_rating = request.form.get('experience_rating', '').strip()
        interviewer_rating = request.form.get('interviewer_rating', '').strip()
        platform_rating = request.form.get('platform_rating', '').strip()
        feedback_text = request.form.get('feedback_text', '').strip()
        would_recommend = request.form.get('would_recommend', '').strip()

        updates = {
            'candidate_feedback_submitted': True,
            'candidate_feedback_at': datetime.now().isoformat(),
            'candidate_feedback_text': feedback_text[:2_000],
            'candidate_would_recommend': would_recommend == 'yes',
        }

        try:
            exp = int(experience_rating)
            if 1 <= exp <= 5:
                updates['candidate_experience_rating'] = exp
        except (ValueError, TypeError):
            pass

        try:
            inter = int(interviewer_rating)
            if 1 <= inter <= 5:
                updates['candidate_interviewer_rating'] = inter
        except (ValueError, TypeError):
            pass

        try:
            plat = int(platform_rating)
            if 1 <= plat <= 5:
                updates['candidate_platform_rating'] = plat
        except (ValueError, TypeError):
            pass

        storage.update_application(application_id, updates)

        # Notify recruiter about candidate feedback
        if job:
            storage.create_notification({
                'user_id':           job.get('recruiter_id'),
                'application_id':    application_id,
                'title':             'Candidate Submitted Interview Feedback',
                'message':           (
                    f'{current_user.full_name or current_user.username} has '
                    f'submitted feedback for the {job.get("title", "interview")} interview.'
                ),
                'notification_type': 'info',
            })

        flash('Thank you for your feedback! 🙏', 'success')
        return redirect(url_for('candidates.view_application',
                                application_id=application_id))

    return render_template(
        'interview/candidate_feedback.html',
        application=application,
        job=job,
        recruiter=recruiter,
    )


# ─────────────────────────────────────────
# WebSocket Event Handlers (Real-time Sync)
# ─────────────────────────────────────────

@socketio.on('join_interview')
@login_required
def handle_join_interview(data):
    """Handle user joining interview room"""
    application_id = data.get('application_id')
    room = f'interview_{application_id}'
    join_room(room)
    emit('user_joined', {
        'user': current_user.full_name or current_user.username,
        'timestamp': datetime.now().isoformat()
    }, room=room)


@socketio.on('leave_interview')
@login_required
def handle_leave_interview(data):
    """Handle user leaving interview room"""
    application_id = data.get('application_id')
    room = f'interview_{application_id}'
    leave_room(room)
    emit('user_left', {
        'user': current_user.full_name or current_user.username,
        'timestamp': datetime.now().isoformat()
    }, room=room)


@socketio.on('code_change')
@login_required
def handle_code_change(data):
    """Handle real-time code changes"""
    application_id = data.get('application_id')
    code = data.get('code', '')
    room = f'interview_{application_id}'

    # Broadcast to all users in this room
    emit('code_update', {
        'code': code,
        'user': current_user.id,
        'timestamp': datetime.now().isoformat()
    }, room=room, skip_sid=request.sid)


@socketio.on('language_change')
@login_required
def handle_language_change(data):
    """Handle real-time language changes"""
    application_id = data.get('application_id')
    language = data.get('language', 'python')
    room = f'interview_{application_id}'

    # Broadcast to all users in this room
    emit('language_update', {
        'language': language,
        'user': current_user.id,
        'timestamp': datetime.now().isoformat()
    }, room=room, skip_sid=request.sid)


@socketio.on('notes_change')
@login_required
def handle_notes_change(data):
    """Handle real-time recruiter notes changes"""
    application_id = data.get('application_id')
    notes = data.get('notes', '')
    room = f'interview_{application_id}'

    # Broadcast to all users in this room
    emit('notes_update', {
        'notes': notes,
        'user': current_user.id,
        'timestamp': datetime.now().isoformat()
    }, room=room, skip_sid=request.sid)


@socketio.on('code_execute')
@login_required
def handle_code_execute(data):
    """Handle code execution output broadcasting"""
    application_id = data.get('application_id')
    language = data.get('language', 'python')
    code = data.get('code', '')
    stdout = data.get('stdout', '')
    stderr = data.get('stderr', '')
    exit_code = data.get('exit_code', 0)

    room = f'interview_{application_id}'

    # Broadcast code execution output to all users in this room
    emit('code_executed', {
        'language': language,
        'code': code,
        'stdout': stdout,
        'stderr': stderr,
        'exit_code': exit_code,
        'user': current_user.id,
        'timestamp': datetime.now().isoformat()
    }, room=room)


# ─────────────────────────────────────────
# Code Execution Endpoint
# ─────────────────────────────────────────

@bp.route('/room/<application_id>/execute', methods=['POST'])
@login_required
def execute_code(application_id):
    """Execute code via local execution or Piston API"""
    import requests
    import subprocess

    application, _, _ = _authorize(application_id)
    if not application:
        return jsonify({'error': 'Not found'}), 404

    try:
        payload = request.get_json() or {}
        language = payload.get('language', 'python')
        version = payload.get('version', '3.10.0')
        code = payload.get('code', '')

        if not code.strip():
            return jsonify({'error': 'Code is empty'}), 400

        # For Python, use local execution (most reliable)
        if language == 'python':
            try:
                result = subprocess.run(
                    ['python', '-c', code],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                return jsonify({
                    'run': {
                        'stdout': result.stdout,
                        'stderr': result.stderr,
                        'code': result.returncode
                    }
                }), 200
            except subprocess.TimeoutExpired:
                return jsonify({'run': {'stdout': '', 'stderr': 'Code execution timed out (>10s)', 'code': 1}}), 200
            except Exception as e:
                return jsonify({'run': {'stdout': '', 'stderr': f'Execution error: {str(e)[:200]}', 'code': 1}}), 200

        # For other languages, try local execution
        # Supported: JavaScript (Node.js), Java, C++, Go, Rust, TypeScript

        import tempfile
        import os as os_module

        # Map language to execution method
        language_exec = {
            'javascript': ('node', lambda code: code, None),
            'typescript': ('node', lambda code: code, None),  # Need ts-node or compile first
            'java': ('java', None, 'Java'),  # Needs compilation
            'c++': ('g++', None, 'C++'),  # Needs compilation
            'go': ('go', None, 'Go'),  # go run
            'rust': ('rustc', None, 'Rust'),  # Needs compilation
        }

        if language not in language_exec:
            # Unsupported language
            return jsonify({
                'run': {
                    'stdout': '',
                    'stderr': f'Code execution for {language} is not available.\nSupported: Python, JavaScript, Java, C++, Go, Rust',
                    'code': 1
                }
            }), 200

        executor_cmd, code_wrapper, lang_name = language_exec[language]

        # Try JavaScript/TypeScript with Node.js
        if language in ['javascript', 'typescript']:
            try:
                result = subprocess.run(
                    ['node', '-e', code],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                return jsonify({
                    'run': {
                        'stdout': result.stdout,
                        'stderr': result.stderr,
                        'code': result.returncode
                    }
                }), 200
            except FileNotFoundError:
                pass
            except subprocess.TimeoutExpired:
                return jsonify({'run': {'stdout': '', 'stderr': 'Timeout: Code took longer than 10s', 'code': 1}}), 200
            except Exception as e:
                current_app.logger.warning(f'{language} local execution failed: {e}')

        # Try Java
        elif language == 'java':
            try:
                with tempfile.TemporaryDirectory() as tmpdir:
                    # For simplicity, wrap code in a main class
                    if 'class ' not in code or 'public static void main' not in code:
                        # Wrap user code in a simple main
                        wrapped = f'public class Solution {{\n    public static void main(String[] args) {{\n        {code}\n    }}\n}}'
                        java_file = os_module.path.join(tmpdir, 'Solution.java')
                    else:
                        wrapped = code
                        java_file = os_module.path.join(tmpdir, 'Main.java')

                    with open(java_file, 'w') as f:
                        f.write(wrapped)

                    # Compile
                    compile_result = subprocess.run(
                        ['javac', java_file],
                        capture_output=True,
                        text=True,
                        timeout=15
                    )

                    if compile_result.returncode != 0:
                        return jsonify({'run': {'stdout': '', 'stderr': compile_result.stderr, 'code': 1}}), 200

                    # Run
                    class_name = 'Solution' if 'Solution' in wrapped else 'Main'
                    result = subprocess.run(
                        ['java', '-cp', tmpdir, class_name],
                        capture_output=True,
                        text=True,
                        timeout=10
                    )

                    return jsonify({
                        'run': {
                            'stdout': result.stdout,
                            'stderr': result.stderr,
                            'code': result.returncode
                        }
                    }), 200
            except FileNotFoundError:
                pass
            except subprocess.TimeoutExpired:
                return jsonify({'run': {'stdout': '', 'stderr': 'Timeout: Code took longer than 10s', 'code': 1}}), 200
            except Exception as e:
                current_app.logger.warning(f'Java execution failed: {e}')

        # Try C++
        elif language == 'c++':
            try:
                with tempfile.TemporaryDirectory() as tmpdir:
                    cpp_file = os_module.path.join(tmpdir, 'solution.cpp')
                    exe_file = os_module.path.join(tmpdir, 'solution')

                    with open(cpp_file, 'w') as f:
                        f.write(code)

                    # Compile
                    compile_result = subprocess.run(
                        ['g++', '-o', exe_file, cpp_file],
                        capture_output=True,
                        text=True,
                        timeout=15
                    )

                    if compile_result.returncode != 0:
                        return jsonify({'run': {'stdout': '', 'stderr': compile_result.stderr, 'code': 1}}), 200

                    # Run
                    result = subprocess.run(
                        [exe_file],
                        capture_output=True,
                        text=True,
                        timeout=10
                    )

                    return jsonify({
                        'run': {
                            'stdout': result.stdout,
                            'stderr': result.stderr,
                            'code': result.returncode
                        }
                    }), 200
            except FileNotFoundError:
                pass
            except subprocess.TimeoutExpired:
                return jsonify({'run': {'stdout': '', 'stderr': 'Timeout: Code took longer than 10s', 'code': 1}}), 200
            except Exception as e:
                current_app.logger.warning(f'C++ execution failed: {e}')

        # Try Go
        elif language == 'go':
            try:
                with tempfile.TemporaryDirectory() as tmpdir:
                    go_file = os_module.path.join(tmpdir, 'solution.go')
                    exe_file = os_module.path.join(tmpdir, 'solution')

                    with open(go_file, 'w') as f:
                        f.write(code)

                    # Compile
                    compile_result = subprocess.run(
                        ['go', 'build', '-o', exe_file, go_file],
                        capture_output=True,
                        text=True,
                        timeout=15,
                        cwd=tmpdir
                    )

                    if compile_result.returncode != 0:
                        return jsonify({'run': {'stdout': '', 'stderr': compile_result.stderr, 'code': 1}}), 200

                    # Run
                    result = subprocess.run(
                        [exe_file],
                        capture_output=True,
                        text=True,
                        timeout=10
                    )

                    return jsonify({
                        'run': {
                            'stdout': result.stdout,
                            'stderr': result.stderr,
                            'code': result.returncode
                        }
                    }), 200
            except FileNotFoundError:
                pass
            except subprocess.TimeoutExpired:
                return jsonify({'run': {'stdout': '', 'stderr': 'Timeout: Code took longer than 10s', 'code': 1}}), 200
            except Exception as e:
                current_app.logger.warning(f'Go execution failed: {e}')

        # Try Rust
        elif language == 'rust':
            try:
                with tempfile.TemporaryDirectory() as tmpdir:
                    rs_file = os_module.path.join(tmpdir, 'solution.rs')
                    exe_file = os_module.path.join(tmpdir, 'solution')

                    with open(rs_file, 'w') as f:
                        f.write(code)

                    # Compile
                    compile_result = subprocess.run(
                        ['rustc', '-o', exe_file, rs_file],
                        capture_output=True,
                        text=True,
                        timeout=30
                    )

                    if compile_result.returncode != 0:
                        return jsonify({'run': {'stdout': '', 'stderr': compile_result.stderr, 'code': 1}}), 200

                    # Run
                    result = subprocess.run(
                        [exe_file],
                        capture_output=True,
                        text=True,
                        timeout=10
                    )

                    return jsonify({
                        'run': {
                            'stdout': result.stdout,
                            'stderr': result.stderr,
                            'code': result.returncode
                        }
                    }), 200
            except FileNotFoundError:
                pass
            except subprocess.TimeoutExpired:
                return jsonify({'run': {'stdout': '', 'stderr': 'Timeout: Code took longer than 10s', 'code': 1}}), 200
            except Exception as e:
                current_app.logger.warning(f'Rust execution failed: {e}')

        # If we get here, the required executor was not found
        return jsonify({
            'run': {
                'stdout': '',
                'stderr': f'⚠ {language.upper()} execution requires {executor_cmd} to be installed.\n\n✓ Fully supported:\n  • Python w/ any version\n\n✓ If tools are installed:\n  • JavaScript/TypeScript (requires Node.js)\n  • Java (requires JDK javac)\n  • C++ (requires g++ compiler)\n  • Go (requires go compiler)\n  • Rust (requires rustc compiler)\n\nPlease use Python to complete the interview or install the required tools.',
                'code': 1
            }
        }), 200

    except Exception as e:
        current_app.logger.error(f'Execute endpoint error: {e}')
        return jsonify({'run': {'stdout': '', 'stderr': f'Error: {str(e)[:150]}', 'code': 1}}), 200

