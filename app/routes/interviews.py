"""
Interview slot-selection blueprint.

Provides a token-protected, login-free page for shortlisted candidates to
pick their preferred interview slot.  The recruiter sends emails (via the
Auto-Shortlist Agent in dashboard.py) that contain a signed URL to this view.
"""
import hmac
import hashlib
from flask import Blueprint, render_template, request, current_app, abort
from app.storage import get_storage

bp = Blueprint('interviews', __name__, url_prefix='/interviews')


# ──────────────────────────────────────────────────────────────────────────────
# Token helpers
# ──────────────────────────────────────────────────────────────────────────────

def make_slot_token(application_id: str, secret_key: str) -> str:
    """Generate a 32-char HMAC-SHA256 token for slot-selection URL signing."""
    h = hmac.new(
        secret_key.encode('utf-8'),
        application_id.encode('utf-8'),
        hashlib.sha256,
    )
    return h.hexdigest()[:32]


def verify_slot_token(application_id: str, token: str, secret_key: str) -> bool:
    expected = make_slot_token(application_id, secret_key)
    return hmac.compare_digest(expected, token)


# ──────────────────────────────────────────────────────────────────────────────
# Routes
# ──────────────────────────────────────────────────────────────────────────────

@bp.route('/choose-slot/<application_id>', methods=['GET', 'POST'])
def choose_slot(application_id):
    """
    Candidate-facing slot selection page.

    GET  — show available slots
    POST — persist chosen slot, advance status to 'interview'
    """
    storage = get_storage()
    application = storage.get_application_by_id(application_id)
    if not application:
        abort(404)

    # Verify HMAC token from querystring
    token = request.args.get('token', '')
    if not verify_slot_token(application_id, token, current_app.config['SECRET_KEY']):
        abort(403)

    job       = storage.get_job_by_id(application.get('job_id', ''))
    candidate = storage.get_user_by_id(application.get('candidate_id', ''))

    # Already picked a slot — show confirmation
    if application.get('chosen_slot'):
        return render_template(
            'interviews/slot_confirmed.html',
            already_done=True,
            chosen_slot=application['chosen_slot'],
            job=job,
            candidate=candidate,
        )

    slots = application.get('interview_slots') or []
    if not slots:
        return render_template('interviews/choose_slot.html',
                               no_slots=True, job=job, candidate=candidate,
                               slots=[], token=token,
                               application_id=application_id, error=None)

    error = None
    if request.method == 'POST':
        chosen = request.form.get('slot', '').strip()
        if not chosen or chosen not in slots:
            error = 'Please select one of the available slots below.'
        else:
            # Save chosen slot + advance to interview
            storage.update_application(application_id, {
                'chosen_slot': chosen,
                'status':      'interview',
            })

            # Notify recruiter in-app
            if job:
                cand_name = candidate.get('full_name', 'A candidate') if candidate else 'A candidate'
                storage.create_notification({
                    'user_id':           job['recruiter_id'],
                    'application_id':    application_id,
                    'title':             f'Interview Slot Selected — {job["title"]}',
                    'message':           f'{cand_name} chose the slot: {chosen}',
                    'notification_type': 'success',
                })

            # Confirmation email to candidate
            if candidate:
                try:
                    from app.services.email_service import send_slot_confirmation_email
                    send_slot_confirmation_email(
                        candidate_email=candidate.get('email', ''),
                        candidate_name=candidate.get('full_name', 'Candidate'),
                        job_title=job.get('title', 'the position') if job else 'the position',
                        company=job.get('company', '') if job else '',
                        chosen_slot=chosen,
                    )
                except Exception as e:
                    current_app.logger.warning(f'Slot confirmation email failed: {e}')

            return render_template(
                'interviews/slot_confirmed.html',
                already_done=False,
                chosen_slot=chosen,
                job=job,
                candidate=candidate,
            )

    return render_template(
        'interviews/choose_slot.html',
        slots=slots,
        job=job,
        candidate=candidate,
        token=token,
        application_id=application_id,
        no_slots=False,
        error=error,
    )
