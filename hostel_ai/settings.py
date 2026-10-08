"""
Django settings for the Hostel AI project.

Hostel AI is a role-based hostel complaint management system with
AI-assisted severity prediction, automatic internal department routing,
real-time-style alerts, and an analytics dashboard.
"""

from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent

# ---------------------------------------------------------------------------
# SECURITY
# ---------------------------------------------------------------------------
SECRET_KEY = os.environ.get(
    "DJANGO_SECRET_KEY",
    "django-insecure-hostel-ai-dev-key-change-this-before-deploying",
)

DEBUG = os.environ.get("DJANGO_DEBUG", "True") == "True"

ALLOWED_HOSTS = ["*"]  # tighten this for production

# ---------------------------------------------------------------------------
# APPLICATIONS
# ---------------------------------------------------------------------------
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "accounts",
    "complaints",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "hostel_ai.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "complaints.context_processors.notifications",
            ],
        },
    },
]

WSGI_APPLICATION = "hostel_ai.wsgi.application"
ASGI_APPLICATION = "hostel_ai.asgi.application"

# ---------------------------------------------------------------------------
# DATABASE  (SQLite by default so the project runs with zero setup)
# ---------------------------------------------------------------------------
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# ---------------------------------------------------------------------------
# AUTH
# ---------------------------------------------------------------------------
AUTH_USER_MODEL = "accounts.User"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LOGIN_URL = "accounts:login"
LOGIN_REDIRECT_URL = "accounts:redirect_after_login"
LOGOUT_REDIRECT_URL = "accounts:login"

# ---------------------------------------------------------------------------
# INTERNATIONALIZATION
# ---------------------------------------------------------------------------
LANGUAGE_CODE = "en-us"
TIME_ZONE = "Asia/Kolkata"
USE_I18N = True
USE_TZ = True

# ---------------------------------------------------------------------------
# STATIC / MEDIA
# ---------------------------------------------------------------------------
STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ---------------------------------------------------------------------------
# HOSTEL AI - custom application settings
# ---------------------------------------------------------------------------

# The handwritten spec named "Gemini 3.5" / "Gemini 3.1 Flash-lite" as the
# model to use. Those are not published Google model identifiers, so this
# project ships with a fast, fully offline scikit-learn text classifier
# ("local") that works out of the box with no API key and no internet
# connection required, trained on complaints/ml/train_severity_model.py.
#
# If you have access to a real Gemini API key and want the LLM to do the
# severity prediction + department routing instead, set:
#   SEVERITY_ENGINE = "gemini"
#   GEMINI_API_KEY  = "<your key>"   (or set the GEMINI_API_KEY env var)
#   GEMINI_MODEL    = "gemini-1.5-flash"   (use a real, current model name)
# and `pip install google-generativeai`. The code automatically falls back
# to the local model if the Gemini call fails or no key is configured.
SEVERITY_ENGINE = os.environ.get("SEVERITY_ENGINE", "local")  # "local" or "gemini"
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-1.5-flash")

# Departments used for hidden internal routing of complaints.
HOSTEL_DEPARTMENTS = [
    "Electrical",
    "Plumbing",
    "Food & Mess",
    "Cleanliness",
    "Security",
    "Internet & Wi-Fi",
    "Furniture",
    "General",
]
