import secrets


def generate_confirmation_token() -> str:
    return secrets.token_urlsafe(nbytes=32)
