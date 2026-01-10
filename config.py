"""
Application Configuration
Environment-based settings for different deployment stages
"""

import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    """
    Application settings with environment variable support
    """

    # App Info
    APP_NAME = "Event Invitation Platform"
    APP_VERSION = "1.0.0"
    DEBUG = os.getenv("DEBUG", "True") == "True"

    # Server
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", 3000))

    # Security
    SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production-asap")
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_HOURS = 24

    # Database (Phase 2)
    # For now: file-based (config.json)
    # Later: SQLite → PostgreSQL
    DATABASE_URL = os.getenv(
        "DATABASE_URL",
        "sqlite:///./events.db"  # Local SQLite for Phase 2
    )
    # For PostgreSQL (Phase 3): postgresql://user:password@localhost/dbname

    # File Storage
    # Phase 1: Local filesystem
    # Phase 4: GCP Cloud Storage
    UPLOAD_DIR = os.getenv("UPLOAD_DIR", "./uploads")
    MAX_UPLOAD_SIZE_MB = 10

    # Phase 4: Google Cloud Storage
    GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID", "")
    GCP_BUCKET_NAME = os.getenv("GCP_BUCKET_NAME", "")
    GCP_CREDENTIALS_PATH = os.getenv("GCP_CREDENTIALS_PATH", "")

    # OAuth (Phase 2: Google Login)
    GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")
    GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")
    GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:3000/auth/google/callback")

    # Email (Phase 3: RSVP notifications)
    SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
    SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
    SMTP_USER = os.getenv("SMTP_USER", "")
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
    FROM_EMAIL = os.getenv("FROM_EMAIL", "noreply@eventinvites.com")

    # Payment (Phase 3: Theme marketplace)
    STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "")
    STRIPE_PUBLISHABLE_KEY = os.getenv("STRIPE_PUBLISHABLE_KEY", "")
    RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY_ID", "")
    RAZORPAY_KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET", "")

    # Features (toggle for phased rollout)
    ENABLE_DATABASE = os.getenv("ENABLE_DATABASE", "False") == "True"
    ENABLE_GOOGLE_OAUTH = os.getenv("ENABLE_GOOGLE_OAUTH", "False") == "True"
    ENABLE_PAYMENTS = os.getenv("ENABLE_PAYMENTS", "False") == "True"
    ENABLE_EMAIL = os.getenv("ENABLE_EMAIL", "False") == "True"
    ENABLE_CLOUD_STORAGE = os.getenv("ENABLE_CLOUD_STORAGE", "False") == "True"

    # CORS (for frontend)
    CORS_ORIGINS = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8000",
    ]

    # Add production domains in Phase 4


settings = Settings()
