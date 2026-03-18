from .settings import *

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "test_db.sqlite3",
    }
}

REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"] = {
    "anon": "10000/minute",
    "user": "100000/minute",
    "burst": "1000/second",
    "sustained": "10000/minute",
    "login": "1000/minute",
    "register": "1000/minute",
    "reserve": "1000/minute",
}
