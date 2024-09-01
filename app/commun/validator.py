import re


def validate_password(value: str) -> str:
    if len(value) < 8:
        raise ValueError("Password must be at least 8 characters long")

    if not re.search(r"[a-z]", value):
        raise ValueError("Password must contain at least one lowercase letter")

    if not re.search(r"[A-Z]", value):
        raise ValueError("Password must contain at least one uppercase letter")

    if not re.search(r"\d", value):
        raise ValueError("Password must contain at least one digit")

    return value


def validate_email(value: str) -> str:
    value = value.strip()

    if not value:
        raise ValueError("Email cannot be empty.")

    email_regex = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"

    if not re.match(email_regex, value):
        raise ValueError("Invalid email format.")

    if len(value) > 254:
        raise ValueError("Email is too long. Maximum length is 254 characters.")

    return value


def validate_string(value: str) -> str:
    value = value.strip()

    if len(value) < 2:
        raise ValueError("Username must be at least 2 characters long")

    if len(value) > 64:
        raise ValueError("Username is too long. Maximum length is 64 characters.")

    return value


def validate_code(value: str) -> str:
    value = value.strip()

    if not (len(value) == 8 and value.isupper() and value.isalnum()):
        raise ValueError(
            "Code must be 8 characters long, composed of uppercase letters and numbers."
        )
    return value

    return value
