#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'FADEX9.settings')
    
    try:
        from django.core.management import execute_from_command_line

        # ✅ Create default superuser (only on first deploy)
        create_default_superuser()

    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    
    execute_from_command_line(sys.argv)


def create_default_superuser():
    from django.contrib.auth import get_user_model
    import django
    django.setup() 

    User = get_user_model()
    if not User.objects.filter(email='admin@fadex9.shop').exists():
        User.objects.create_superuser(
            email='admin@fadex9.shop',
            password='admin',
            first_name='Admin',
            last_name='User',
            phone_number='1234567890', 
        )
        print("✅ Superuser created.")
    else:
        print("⚠️ Superuser already exists.")


if __name__ == '__main__':
    main()