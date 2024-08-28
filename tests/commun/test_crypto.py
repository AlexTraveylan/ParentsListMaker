import pytest

from app.commun.crypto import decrypt, encrypt, generate_password
from app.commun.validator import validate_password


def test_encryt_and_decrypt_email(key: bytes):
    email = "alextraveylan@gmail.com"

    encrypted_email = encrypt(email, key)

    assert email == decrypt(encrypted_email, key)


@pytest.mark.parametrize("_", range(50))
def test_generate_password(_):
    password = generate_password()

    assert validate_password(password) == password
