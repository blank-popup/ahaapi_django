$env:DJANGO_SETTINGS_MODULE="ahaapi.config.settings.specific.production"

uv run python manage.py runserver
