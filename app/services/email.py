import logging

import resend

from app.core.config import Settings, get_settings
from app.models.contact_submission import ContactSubmission
from app.models.job_application import JobApplication

logger = logging.getLogger(__name__)


def _client(settings: Settings) -> None:
    resend.api_key = settings.resend_api_key


def send_contact_notification(submission: ContactSubmission, settings: Settings | None = None) -> None:
    settings = settings or get_settings()
    _client(settings)
    try:
        resend.Emails.send(
            {
                "from": settings.resend_from_email,
                "to": [settings.team_notification_email],
                "subject": f"New contact form submission from {submission.name}",
                "html": (
                    f"<p><strong>Name:</strong> {submission.name}</p>"
                    f"<p><strong>Email:</strong> {submission.email}</p>"
                    f"<p><strong>Company:</strong> {submission.company or '-'}</p>"
                    f"<p><strong>Message:</strong></p><p>{submission.message}</p>"
                ),
            }
        )
    except Exception:
        logger.exception("Failed to send contact notification email")


def send_application_notification(
    application: JobApplication, job_title: str, settings: Settings | None = None
) -> None:
    settings = settings or get_settings()
    _client(settings)
    try:
        resend.Emails.send(
            {
                "from": settings.resend_from_email,
                "to": [settings.team_notification_email],
                "subject": f"New application for {job_title}: {application.applicant_name}",
                "html": (
                    f"<p><strong>Applicant:</strong> {application.applicant_name}</p>"
                    f"<p><strong>Email:</strong> {application.email}</p>"
                    f"<p><strong>Phone:</strong> {application.phone or '-'}</p>"
                    f"<p><strong>Position:</strong> {job_title}</p>"
                ),
            }
        )
    except Exception:
        logger.exception("Failed to send application notification email")
