#!/usr/bin/env python
import os
import sys

from backend.settings.development import DEV_SERVER

if __name__ == "__main__":
    # To config different env for development and production.
    try:
        if sys.argv[1] == 'prod':
            os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings.production")
            sys.argv.remove('prod')
        else:
            os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings.development")
    except IndexError:
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings.development")

    # Only use in dev env.
    if len(sys.argv) == 1:
        sys.argv.append('runserver')
        sys.argv.append(DEV_SERVER)

    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)
