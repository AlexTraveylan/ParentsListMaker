import resend

from app.settings import DOMAIN_EMAIL


def send_contact_message(subject: str, html: str, *, to: str) -> dict:
    payload = {
        "from": DOMAIN_EMAIL,
        "to": [to],
        "subject": subject,
        "html": html,
    }

    return resend.Emails.send(payload)
