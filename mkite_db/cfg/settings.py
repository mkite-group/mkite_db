import os
import environ
from pathlib import Path

MKITE_ENV_KEY = "MKITE_ENV"
if not MKITE_ENV_KEY in os.environ:
    raise ValueError(
        f"{MKITE_ENV_KEY} is not defined in the environment. \
        Without this variable, it is unclear what database \
        or settings to use. Please create a .env file and \
        point the {MKITE_ENV_KEY} file to it."
    )
MKITE_ENV = os.environ[MKITE_ENV_KEY]
if not os.path.exists(MKITE_ENV):
    raise FileNotFoundError(f"Could not find environment file {MKITE_ENV}.")

# Reads the access to the database via environmental variables
env = environ.Env(DEBUG=(bool, False))
env.read_env(MKITE_ENV)

BASE_DIR = Path(__file__).resolve().parent.parent
DEBUG = env("DEBUG")
SECRET_KEY = env("SECRET_KEY")
ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS", default=["*"])

# Sets up the database connection
DATABASES = {"default": env.db()}

# Application definition
DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

THIRD_PARTY_APPS = ["django_extensions", "rest_framework", "taggit"]

LOCAL_APPS = [
    "mkite_db.orm.base",
    "mkite_db.orm.jobs",
    "mkite_db.orm.calcs",
    "mkite_db.orm.mols",
    "mkite_db.orm.structs",
    "mkite_db.workflow",
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "cfg.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ]
        },
    }
]

WSGI_APPLICATION = "cfg.wsgi.application"


# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


# Internationalization
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
STATIC_URL = "static/"

# Default primary key field type
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
