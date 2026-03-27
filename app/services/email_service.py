"""
Email notification service for OptiHire.
Sends transactional emails on application status changes.
Gracefully no-ops if MAIL_USERNAME is not configured.
"""
from flask import current_app, render_template_string
from typing import Optional, List

# Status -> (subject, friendly label, colour)
STATUS_META = {
    'shortlisted': (
        "Great news - you've been shortlisted!",
        'Shortlisted',
        '#3b82f6',
    ),
    'interview': (
        'Interview invitation from OptiHire',
        'Interview Scheduled',
        '#8b5cf6',
    ),
    'hired': (
        "Congratulations - you've been hired!",
        'Hired',
        '#10b981',
    ),
    'rejected': (
        'Application update from OptiHire',
        'Not Selected',
        '#ef4444',
    ),
}

# Inline HTML email template (no external files needed)
_EMAIL_TEMPLATE = """
<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"></head>
<body style="margin:0;padding:0;background:#f1f5f9;font-family:Inter,Arial,sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="padding:40px 0;">
    <tr><td align="center">
      <table width="600" cellpadding="0" cellspacing="0"
             style="background:#fff;border-radius:12px;overflow:hidden;box-shadow:0 4px 24px rgba(0,0,0,.08);">
        <!-- Header -->
        <tr><td style="background:linear-gradient(135deg,#0ea5e9,#6366f1);padding:32px 40px;">
          <h1 style="color:#fff;margin:0;font-size:24px;font-weight:800;">OptiHire</h1>
          <p style="color:rgba(255,255,255,.8);margin:4px 0 0;">AI-Powered Recruitment Platform</p>
        </td></tr>
        <!-- Body -->
        <tr><td style="padding:36px 40px;">
          <p style="font-size:16px;color:#374151;">Hi <strong>{{ candidate_name }}</strong>,</p>
          <p style="font-size:15px;color:#374151;line-height:1.6;">{{ message|safe }}</p>
          <div style="margin:28px 0;padding:20px 24px;background:#f8fafc;border-left:4px solid {{ status_color }};border-radius:6px;">
            <p style="margin:0;font-size:13px;color:#6b7280;text-transform:uppercase;letter-spacing:.05em;">Application Status</p>
            <p style="margin:6px 0 0;font-size:22px;font-weight:800;color:{{ status_color }};">{{ status_label }}</p>
            <p style="margin:8px 0 0;font-size:14px;color:#374151;"><strong>Position:</strong> {{ job_title }}</p>
            <p style="margin:4px 0 0;font-size:14px;color:#374151;"><strong>Company:</strong> {{ company }}</p>
          </div>
          <a href="{{ app_url }}"
             style="display:inline-block;padding:12px 28px;background:linear-gradient(135deg,#0ea5e9,#6366f1);
                    color:#fff;text-decoration:none;border-radius:8px;font-weight:700;font-size:15px;">
            View Application →
          </a>
          <p style="margin-top:32px;font-size:13px;color:#9ca3af;">
            This email was sent by OptiHire on behalf of the recruiter.<br>
            You are receiving this because you applied through the platform.
          </p>
        </td></tr>
        <!-- Footer -->
        <tr><td style="padding:20px 40px;background:#f8fafc;border-top:1px solid #e5e7eb;">
          <p style="margin:0;font-size:12px;color:#9ca3af;">
            © 2026 OptiHire · AI-Powered Talent Acquisition
          </p>
        </td></tr>
      </table>
    </td></tr>
  </table>
</body>
</html>
"""


def send_status_email(
    candidate_email: str,
    candidate_name: str,
    job_title: str,
    company: str,
    new_status: str,
    application_id: str,
    custom_message: Optional[str] = None,
) -> bool:
    """
    Send a status-change notification email to a candidate.

    Returns True if sent successfully, False otherwise.
    Email is silently skipped if MAIL_ENABLED is False.
    """
    meta = STATUS_META.get(new_status)
    if not meta:
        return False

    subject, status_label, status_color = meta

    default_messages = {
        'shortlisted': (
            f'We are pleased to inform you that your application for '
            f'<strong>{job_title}</strong> at <strong>{company}</strong> has been shortlisted. '
            f'The recruiter will be in touch with next steps.'
        ),
        'interview': (
            f'Congratulations! You have been selected for an interview for '
            f'<strong>{job_title}</strong> at <strong>{company}</strong>. '
            f'Please check your application for interview preparation questions.'
        ),
        'hired': (
            f'We are thrilled to inform you that you have been selected for the position of '
            f'<strong>{job_title}</strong> at <strong>{company}</strong>. '
            f'Congratulations on this achievement!'
        ),
        'rejected': (
            f'Thank you for your interest in <strong>{job_title}</strong> at <strong>{company}</strong>. '
            f'After careful consideration, we have decided to move forward with other candidates. '
            f'We encourage you to apply to future openings.'
        ),
    }
    message = custom_message or default_messages.get(new_status, '')

    mail_enabled = current_app.config.get('MAIL_ENABLED', False)

    if not mail_enabled:
        # No SMTP configured — print the email to the console so it is visible during dev/demo
        border = '=' * 65
        plain_message = (
            message
            .replace('<strong>', '').replace('</strong>', '')
            .replace('<br>', '\n')
        )
        base_url = current_app.config.get('APPLICATION_BASE_URL', 'http://localhost:5000')
        app_url = f"{base_url}/candidates/application/{application_id}"
        print(f'\n{border}')
        print(f'  📧  EMAIL NOTIFICATION  (SMTP not configured — shown here)')
        print(border)
        print(f'  To      : {candidate_email}')
        print(f'  Subject : {subject}')
        print(f'  Status  : {status_label}')
        print(f'  Job     : {job_title}  @ {company}')
        print(f'  Message : {plain_message}')
        print(f'  Link    : {app_url}')
        print(f'{border}\n')
        current_app.logger.info(
            f'[DEV] Email (console) → {candidate_email} | {new_status} | {job_title}'
        )
        return True  # treat as success so callers know it was handled

    try:
        from flask_mail import Message
        from app import mail

        base_url = current_app.config.get('APPLICATION_BASE_URL', 'http://localhost:5000')
        app_url = f"{base_url}/candidates/application/{application_id}"

        html_body = render_template_string(
            _EMAIL_TEMPLATE,
            candidate_name=candidate_name,
            message=message,
            status_label=status_label,
            status_color=status_color,
            job_title=job_title,
            company=company,
            app_url=app_url,
        )

        msg = Message(
            subject=subject,
            recipients=[candidate_email],
            html=html_body,
        )
        mail.send(msg)
        current_app.logger.info(
            f'Status email sent → {candidate_email} ({new_status}) for {job_title}'
        )
        return True

    except Exception as e:
        border = '!' * 65
        print(f'\n{border}')
        print(f'  ❌  SMTP EMAIL FAILED — could not send to {candidate_email}')
        print(f'  Error : {e}')
        print(f'  Fix   : In .env set MAIL_PASSWORD to a Gmail App Password')
        print(f'          (16-char code from myaccount.google.com/apppasswords)')
        print(f'          NOT your regular Gmail password.')
        print(f'{border}\n')
        current_app.logger.error(f'Email send failed to {candidate_email}: {e}')
        return False

#  Slot-selection email templates 

_SLOT_SELECTION_TEMPLATE = """
<!DOCTYPE html>
<html><head><meta charset="UTF-8"></head>
<body style="margin:0;padding:0;background:#f1f5f9;font-family:Inter,Arial,sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="padding:40px 0;">
    <tr><td align="center">
      <table width="600" cellpadding="0" cellspacing="0"
             style="background:#fff;border-radius:12px;overflow:hidden;box-shadow:0 4px 24px rgba(0,0,0,.08);">
        <tr><td style="background:linear-gradient(135deg,#6366f1,#8b5cf6);padding:32px 40px;">
          <h1 style="color:#fff;margin:0;font-size:24px;font-weight:800;">OptiHire</h1>
          <p style="color:rgba(255,255,255,.8);margin:4px 0 0;">AI-Powered Recruitment Platform</p>
        </td></tr>
        <tr><td style="padding:36px 40px;">
          <p style="font-size:16px;color:#374151;">Hi <strong>{{ candidate_name }}</strong>,</p>
          <div style="margin:0 0 20px;padding:16px 20px;background:#f0fdf4;border-left:4px solid #22c55e;border-radius:6px;">
            <p style="margin:0;font-size:17px;font-weight:800;color:#15803d;">&#127881; You've been shortlisted!</p>
            <p style="margin:6px 0 0;font-size:14px;color:#166534;">
              <strong>{{ job_title }}</strong> at <strong>{{ company }}</strong>
            </p>
          </div>
          <p style="font-size:15px;color:#374151;line-height:1.6;">
            The recruiter would like to schedule an interview with you.
            Please click the button below to choose your preferred time slot:
          </p>
          <div style="margin:20px 0;padding:20px;background:#f5f3ff;border:1px solid #e0e7ff;border-radius:8px;">
            <p style="margin:0 0 12px;font-size:12px;font-weight:700;color:#4338ca;text-transform:uppercase;letter-spacing:.06em;">Available Interview Slots</p>
            {{ slots_html|safe }}
          </div>
          <div style="text-align:center;margin:28px 0;">
            <a href="{{ slot_selection_url }}"
               style="display:inline-block;padding:14px 36px;background:linear-gradient(135deg,#6366f1,#8b5cf6);
                      color:#fff;text-decoration:none;border-radius:8px;font-weight:700;font-size:16px;">
              &#128197; Choose My Interview Slot &#8594;
            </a>
          </div>
          <p style="font-size:13px;color:#9ca3af;margin-top:24px;">
            This invitation link is personal to you. Please do not share it.<br>
            This email was sent by OptiHire on behalf of {{ company }}.
          </p>
        </td></tr>
        <tr><td style="padding:20px 40px;background:#f8fafc;border-top:1px solid #e5e7eb;">
          <p style="margin:0;font-size:12px;color:#9ca3af;">&#169; 2026 OptiHire &middot; AI-Powered Talent Acquisition</p>
        </td></tr>
      </table>
    </td></tr>
  </table>
</body></html>
"""

_SLOT_CONFIRMATION_TEMPLATE = """
<!DOCTYPE html>
<html><head><meta charset="UTF-8"></head>
<body style="margin:0;padding:0;background:#f1f5f9;font-family:Inter,Arial,sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="padding:40px 0;">
    <tr><td align="center">
      <table width="600" cellpadding="0" cellspacing="0"
             style="background:#fff;border-radius:12px;overflow:hidden;box-shadow:0 4px 24px rgba(0,0,0,.08);">
        <tr><td style="background:linear-gradient(135deg,#059669,#10b981);padding:32px 40px;">
          <h1 style="color:#fff;margin:0;font-size:24px;font-weight:800;">OptiHire</h1>
          <p style="color:rgba(255,255,255,.8);margin:4px 0 0;">Interview Slot Confirmed!</p>
        </td></tr>
        <tr><td style="padding:36px 40px;">
          <p style="font-size:16px;color:#374151;">Hi <strong>{{ candidate_name }}</strong>,</p>
          <p style="font-size:15px;color:#374151;line-height:1.6;">
            Your interview slot has been confirmed. Here are the details:
          </p>
          <div style="margin:20px 0;padding:20px 24px;background:#f0fdf4;border-left:4px solid #22c55e;border-radius:6px;">
            <p style="margin:0;font-size:13px;color:#6b7280;text-transform:uppercase;letter-spacing:.05em;">Interview Details</p>
            <p style="margin:6px 0 0;font-size:20px;font-weight:800;color:#15803d;">&#128197; {{ chosen_slot }}</p>
            <p style="margin:8px 0 0;font-size:14px;color:#374151;"><strong>Position:</strong> {{ job_title }}</p>
            <p style="margin:4px 0 0;font-size:14px;color:#374151;"><strong>Company:</strong> {{ company }}</p>
          </div>
          <p style="font-size:14px;color:#374151;">
            The recruiter will send you joining details closer to the interview date.
            Please add this to your calendar and be available 5 minutes early.
          </p>
          <p style="font-size:13px;color:#9ca3af;margin-top:24px;">
            This email was sent by OptiHire on behalf of {{ company }}.
          </p>
        </td></tr>
        <tr><td style="padding:20px 40px;background:#f8fafc;border-top:1px solid #e5e7eb;">
          <p style="margin:0;font-size:12px;color:#9ca3af;">&#169; 2026 OptiHire &middot; AI-Powered Talent Acquisition</p>
        </td></tr>
      </table>
    </td></tr>
  </table>
</body></html>
"""


def send_slot_selection_email(
    candidate_email: str,
    candidate_name: str,
    job_title: str,
    company: str,
    slots: List[str],
    slot_selection_url: str,
) -> bool:
    """
    Send an interview slot-selection invitation to a shortlisted candidate.
    Returns True on success (or console-print in dev mode), False on error.
    """
    subject = f"You've been shortlisted for {job_title} at {company} — Choose your interview slot"
    slots_html = '\n'.join(
        f'<p style="margin:5px 0;font-size:15px;color:#4338ca;font-weight:600;">'
        f'&#8226; {slot}</p>'
        for slot in slots
    )

    mail_enabled = current_app.config.get('MAIL_ENABLED', False)

    if not mail_enabled:
        border = '=' * 65
        print(f'\n{border}')
        print(f'    SLOT-SELECTION EMAIL  (SMTP not configured — shown here)')
        print(border)
        print(f'  To      : {candidate_email}')
        print(f'  Subject : {subject}')
        print(f'  Job     : {job_title} @ {company}')
        print(f'  Slots   : {", ".join(slots)}')
        print(f'  Link    : {slot_selection_url}')
        print(f'{border}\n')
        current_app.logger.info(
            f'[DEV] Slot-selection email (console)  {candidate_email} | {job_title}'
        )
        return True

    try:
        from flask_mail import Message
        from app import mail

        html_body = render_template_string(
            _SLOT_SELECTION_TEMPLATE,
            candidate_name=candidate_name,
            job_title=job_title,
            company=company,
            slots_html=slots_html,
            slot_selection_url=slot_selection_url,
        )
        msg = Message(subject=subject, recipients=[candidate_email], html=html_body)
        mail.send(msg)
        current_app.logger.info(
            f'Slot-selection email sent  {candidate_email} | {job_title}'
        )
        return True
    except Exception as e:
        current_app.logger.error(f'Slot-selection email failed to {candidate_email}: {e}')
        print(f'   Slot-selection email FAILED  {candidate_email}: {e}')
        return False


def send_slot_confirmation_email(
    candidate_email: str,
    candidate_name: str,
    job_title: str,
    company: str,
    chosen_slot: str,
) -> bool:
    """
    Send a confirmation email after a candidate has chosen their interview slot.
    """
    subject = f"Interview confirmed — {job_title} at {company}"

    mail_enabled = current_app.config.get('MAIL_ENABLED', False)

    if not mail_enabled:
        border = '=' * 65
        print(f'\n{border}')
        print(f'    SLOT-CONFIRMATION EMAIL  (SMTP not configured — shown here)')
        print(border)
        print(f'  To      : {candidate_email}')
        print(f'  Subject : {subject}')
        print(f'  Slot    : {chosen_slot}')
        print(f'{border}\n')
        current_app.logger.info(
            f'[DEV] Slot-confirmation email (console)  {candidate_email}'
        )
        return True

    try:
        from flask_mail import Message
        from app import mail

        html_body = render_template_string(
            _SLOT_CONFIRMATION_TEMPLATE,
            candidate_name=candidate_name,
            job_title=job_title,
            company=company,
            chosen_slot=chosen_slot,
        )
        msg = Message(subject=subject, recipients=[candidate_email], html=html_body)
        mail.send(msg)
        current_app.logger.info(
            f'Slot-confirmation email sent  {candidate_email}'
        )
        return True
    except Exception as e:
        current_app.logger.error(f'Slot-confirmation email failed to {candidate_email}: {e}')
        return False
