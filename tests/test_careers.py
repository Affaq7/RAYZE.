import io
import uuid
from unittest.mock import patch


def test_apply_honeypot_short_circuits_without_touching_db_or_storage(client_no_db):
    job_id = uuid.uuid4()
    with patch("app.api.v1.careers.upload_resume") as mock_upload, patch(
        "app.api.v1.careers.send_application_notification"
    ) as mock_email:
        response = client_no_db.post(
            f"/api/v1/careers/{job_id}/apply",
            data={
                "applicant_name": "Bot",
                "email": "bot@example.com",
                "website": "http://spam.example.com",
            },
            files={"resume": ("resume.pdf", io.BytesIO(b"%PDF-1.4 fake"), "application/pdf")},
        )

    assert response.status_code == 201
    mock_upload.assert_not_called()
    mock_email.assert_not_called()


def test_apply_rejects_missing_resume(client_no_db):
    job_id = uuid.uuid4()
    response = client_no_db.post(
        f"/api/v1/careers/{job_id}/apply",
        data={"applicant_name": "Real Applicant", "email": "user@example.com"},
    )
    assert response.status_code == 422
