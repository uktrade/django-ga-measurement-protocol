DATABASES = {
    "default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"},
}

INSTALLED_APPS = [
    "django_ga_measurement_protocol.tests.testapp",
]

SECRET_KEY = "abcdefghijklmnopqrstuvwxyz"
