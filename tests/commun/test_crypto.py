from app.commun.crypto import decrypt, encrypt


def test_encryt_and_decrypt_email(key: bytes):
    email = "alextraveylan@gmail.com"

    encrypted_email = encrypt(email, key)

    assert email == decrypt(encrypted_email, key)
