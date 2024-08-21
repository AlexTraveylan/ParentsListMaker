import pytest

from app.commun.validator import validate_email, validate_password


@pytest.mark.parametrize(
    "invalid_password",
    [
        "a",
        "azerty",
        "AZERTY",
        "azertyuioipoiopqidpoqsid",
        "AZERTYUIOPIPOIPOQSDPOQSID",
        "123456789",
        "123456789azerty",
        "aA1",
        "alkjhazdkljsASDKQSJFDKSLM",
        "1324564aadfsdsgsdgfs",
        "ALDFSJMGKLJS1654",
    ],
)
def test_validate_password_with_invalid_passwords(invalid_password):
    with pytest.raises(ValueError):
        validate_password(invalid_password)


@pytest.mark.parametrize(
    "valid_password", ["ValidPassword123*", 'ValidPassword123*"*', "ValidPassword1"]
)
def test_validate_password_with_valid_passwords(valid_password):
    assert validate_password(valid_password) == valid_password


@pytest.mark.parametrize(
    "invalid_email",
    [
        "not_an_email",
        "not_an_email@not_an_email",
        "not_an_email@notanemail",
        "@not_an_email.com",
        "not_an_email@",
        "not_an_email.com",
        "",
    ],
)
def test_validate_email_with_invalid_emails(invalid_email):
    with pytest.raises(ValueError):
        validate_email(invalid_email)


@pytest.mark.parametrize(
    "valid_email",
    [
        "valid_email@subdomain.validemail.com",
        "valid_email@sub.validemail.org",
        "user@subdomain.example.co.uk",
        "contact@support.store.example.com",
        "info@sub.mail.example.net",
        "name@sub.subdomain.domain.edu",
    ],
)
def test_validate_email_with_valid_emails(valid_email):
    assert validate_email(valid_email) == valid_email
