import base64
import os

from dotenv import load_dotenv

load_dotenv()

# General
PRODUCTION = True if os.getenv("PRODUCTION") == "True" else False
BACKEND_HOST = os.getenv("BACKEND_HOST")
FRONTEND_URL = os.getenv("FRONTEND_URL")

# Database
DB_URL = os.getenv("DB_URL")

# security
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 7200
AES_KEY = base64.b64decode(os.getenv("AES_KEY"))

# Email
DOMAIN_EMAIL = os.getenv("DOMAIN_EMAIL")
RESEND_API_KEY = os.getenv("RESEND_API_KEY")
CONFIRMATION_URL = f"{BACKEND_HOST}/confirmation-email"
ADMINSTRATOR_EMAIL = os.getenv("ADMINSTRATOR_EMAIL")
