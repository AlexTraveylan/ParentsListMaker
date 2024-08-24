import resend

from app.settings import CONFIRMATION_URL, DOMAIN_EMAIL


def send_contact_message(subject: str, html: str, *, to: str) -> dict:
    payload = {
        "from": DOMAIN_EMAIL,
        "to": [to],
        "subject": subject,
        "html": html,
    }

    return resend.Emails.send(payload)


def html_wrapper_for_confirmation_email_with_token(token: str) -> str:
    html = f"""
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Email Confirmation</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 600px;
                margin: 0 auto;
                padding: 20px;
            }}
            .btn {{
                display: inline-block;
                padding: 10px 20px;
                background-color: #007bff;
                color: #ffffff;
                text-decoration: none;
                border-radius: 5px;
                margin-top: 20px;
            }}
            .btn:hover {{
                background-color: #0056b3;
            }}
            .copy-link {{
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 5px;
                padding: 10px;
                margin-top: 20px;
                word-break: break-all;
            }}
        </style>
    </head>
    <body>
        <h1>Confirmez votre email</h1>
        <p>Vous avez renseigné un email ! Veuillez confirmer votre adresse email en cliquant sur le bouton ci-dessous :</p>
        <a href="{CONFIRMATION_URL}/{token}" class="btn">Confirmer mon email</a>
        <p>Si le bouton ne fonctionne pas, vous pouvez copier et coller le lien suivant dans votre navigateur :</p>
        <p class="copy-link">{CONFIRMATION_URL}/{token}</p>
        <p>Votre email sera encodé dans notre base de données et ne sera pas accessible aux autres utilisateurs. Notre application servira d'intermédiaire pour communiquer. Si vous souhaitez transmettre votre email dans ces communications, ce sera à vous de le partager directement.</p>
    </body>
    </html>
    """

    return html
