import base64
import os

from dotenv import load_dotenv

load_dotenv()

# Database
DB_URL = os.getenv("DB_URL")

# security
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 7200
AES_KEY = base64.b64decode(os.getenv("AES_KEY"))
