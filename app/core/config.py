import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# MongoDB Configuration
MONGO_URI = os.getenv("MONGO_URI")

if not MONGO_URI:
    raise ValueError("MONGO_URI is not set in environment variables")

# Add tlsAllowInvalidCertificates to the connection string for development
if "tlsAllowInvalidCertificates" not in MONGO_URI:
    if "?" in MONGO_URI:
        MONGO_URI += "&tlsAllowInvalidCertificates=true"
    else:
        MONGO_URI += "?tlsAllowInvalidCertificates=true"

# Extract database name from the URI if needed
from urllib.parse import urlparse
parsed_uri = urlparse(MONGO_URI)
MONGO_DB_NAME = parsed_uri.path.strip('/') or 'chat_aug'

# JWT Configuration
JWT_SECRET = os.getenv("JWT_SECRET", "supersecretjwtkey")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")

# OpenAI Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")  # Keep your OpenAI API key in .env file
