import logging

from app.models.contact_submission import ContactSubmission

logger = logging.getLogger(__name__)


def sync_to_google_sheet(submission: ContactSubmission) -> None:
    """TODO: sync new contact submissions to a Google Sheet.

    Not wired up yet — no Google service account credentials configured.
    To enable this later:
      1. Create a Google Cloud service account with Sheets API access.
      2. Share the target spreadsheet with that service account's email.
      3. Set GOOGLE_SERVICE_ACCOUNT_JSON (the service account's JSON key,
         as a single-line string or file path) and GOOGLE_SHEET_ID in .env.
      4. Implement the append-row call here using google-api-python-client
         or gspread, keyed off those two settings.
    """
    logger.info("sync_to_google_sheet: not configured, skipping (submission id=%s)", submission.id)
