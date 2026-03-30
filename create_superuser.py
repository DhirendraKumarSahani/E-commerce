import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

USERNAME = os.getenv('DJANGO_SUPERUSER_USERNAME')
EMAIL = os.getenv('DJANGO_SUPERUSER_EMAIL')
PASSWORD = os.getenv('DJANGO_SUPERUSER_PASSWORD')

if USERNAME and EMAIL and PASSWORD:
    if not User.objects.filter(username=USERNAME).exists():
        User.objects.create_superuser(
            username=USERNAME,
            email=EMAIL,
            password=PASSWORD
        )
        print("✅ Superuser created")
    else:
        print("⚡ Superuser already exists")
else:
    print("❌ Missing environment variables")