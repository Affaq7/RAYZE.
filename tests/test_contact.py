from unittest.mock import patch


def test_contact_honeypot_short_circuits_without_touching_db(client_no_db):
    with patch("app.api.v1.contact.send_contact_notification") as mock_email, patch(
        "app.api.v1.contact.sync_to_google_sheet"
    ) as mock_sheet:
        response = client_no_db.post(
            "/api/v1/contact",
            json={
                "name": "Bot",
                "email": "bot@example.com",
                "message": "hello",
                "website": "http://spam.example.com",
            },
        )

    assert response.status_code == 201
    mock_email.assert_not_called()
    mock_sheet.assert_not_called()


def test_contact_rejects_overlong_message(client_no_db):
    response = client_no_db.post(
        "/api/v1/contact",
        json={
            "name": "Real User",
            "email": "user@example.com",
            "message": "x" * 6000,
        },
    )
    assert response.status_code == 422


def test_contact_rejects_invalid_email(client_no_db):
    response = client_no_db.post(
        "/api/v1/contact",
        json={
            "name": "Real User",
            "email": "not-an-email",
            "message": "hello there",
        },
    )
    assert response.status_code == 422
