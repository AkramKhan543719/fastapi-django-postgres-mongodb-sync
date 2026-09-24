from pathlib import Path


# =========================================================
# BASE DIRECTORY
# =========================================================

BASE_DIR = Path(__file__).resolve().parent.parent


# =========================================================
# SECURITY
# =========================================================

SECRET_KEY = "django-development-secret-key-change-later"

DEBUG = True

ALLOWED_HOSTS = [
    "127.0.0.1",
    "localhost"
]


# =========================================================
# APPLICATIONS
# =========================================================

INSTALLED_APPS = [

    # Django
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Django REST Framework
    "rest_framework",

    # Project applications
    "authentication",
    "mongodb_api",
    "synchronization",
]


# =========================================================
# MIDDLEWARE
# =========================================================

MIDDLEWARE = [

    "django.middleware.security.SecurityMiddleware",

    "django.contrib.sessions.middleware.SessionMiddleware",

    "django.middleware.common.CommonMiddleware",

    "django.middleware.csrf.CsrfViewMiddleware",

    "django.contrib.auth.middleware.AuthenticationMiddleware",

    "django.contrib.messages.middleware.MessageMiddleware",

    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


# =========================================================
# URL CONFIGURATION
# =========================================================

ROOT_URLCONF = "config.urls"


# =========================================================
# TEMPLATES
# =========================================================

TEMPLATES = [

    {
        "BACKEND":
            "django.template.backends.django.DjangoTemplates",

        "DIRS": [],

        "APP_DIRS": True,

        "OPTIONS": {

            "context_processors": [

                "django.template.context_processors.request",

                "django.contrib.auth.context_processors.auth",

                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]


# =========================================================
# WSGI / ASGI
# =========================================================

WSGI_APPLICATION = "config.wsgi.application"

ASGI_APPLICATION = "config.asgi.application"


# =========================================================
# POSTGRESQL DATABASE
# =========================================================

DATABASES = {

    "default": {

        "ENGINE":
            "django.db.backends.postgresql",

        "NAME":
            "deepstream_db",

        "USER":
            "postgres",

        "PASSWORD":
            "postgres",

        "HOST":
            "localhost",

        "PORT":
            "5432",
    }
}


# =========================================================
# PASSWORD VALIDATION
# =========================================================

AUTH_PASSWORD_VALIDATORS = [

    {
        "NAME":
            "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },

    {
        "NAME":
            "django.contrib.auth.password_validation.MinimumLengthValidator"
    },

    {
        "NAME":
            "django.contrib.auth.password_validation.CommonPasswordValidator"
    },

    {
        "NAME":
            "django.contrib.auth.password_validation.NumericPasswordValidator"
    },
]


# =========================================================
# INTERNATIONALIZATION
# =========================================================

LANGUAGE_CODE = "en-us"

TIME_ZONE = "Asia/Kolkata"

USE_I18N = True

USE_TZ = True


# =========================================================
# STATIC FILES
# =========================================================

STATIC_URL = "static/"


# =========================================================
# DEFAULT PRIMARY KEY
# =========================================================

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# =========================================================
# DJANGO REST FRAMEWORK
# =========================================================

REST_FRAMEWORK = {

    "DEFAULT_AUTHENTICATION_CLASSES": (

        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),

    "DEFAULT_PERMISSION_CLASSES": (

        "rest_framework.permissions.IsAuthenticated",
    ),
}


# =========================================================
# JWT CONFIGURATION
# =========================================================

from datetime import timedelta


SIMPLE_JWT = {

    "ACCESS_TOKEN_LIFETIME":
        timedelta(minutes=30),

    "REFRESH_TOKEN_LIFETIME":
        timedelta(days=1),

    "ROTATE_REFRESH_TOKENS":
        False,

    "BLACKLIST_AFTER_ROTATION":
        False,

    "AUTH_HEADER_TYPES":
        ("Bearer",),
}


# =========================================================
# MONGODB CONFIGURATION
# =========================================================

MONGO_URI = "mongodb://127.0.0.1:27017"

MONGO_DATABASE = "deepstream_mongodb"