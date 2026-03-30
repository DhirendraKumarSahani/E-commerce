#!/usr/bin/env bash

echo "🚀 Installing dependencies..."
pip install -r requirements.txt

echo "📦 Collecting static files..."
python manage.py collectstatic --noinput

echo "🧱 Running migrations..."
python manage.py migrate

echo "👤 Creating admin user (if not exists)..."

python manage.py shell << END
import os
from django.contrib.auth import get_user_model

User = get_user_model()

USERNAME = os.getenv("ADMIN_USERNAME")
PHONE = os.getenv("ADMIN_PHONE")
PASSWORD = os.getenv("ADMIN_PASSWORD")
EMAIL = os.getenv("ADMIN_EMAIL")

# ⚠️ Check ENV variables
if not all([USERNAME, PHONE, PASSWORD]):
    print("❌ Missing environment variables. Skipping admin creation.")
else:
    if not User.objects.filter(phone=PHONE).exists():

        print("🚀 Creating Admin User...")

        admin = User.objects.create_superuser(
            username=USERNAME,
            phone=PHONE,
            password=PASSWORD
        )

        if EMAIL:
            admin.email = EMAIL

        admin.is_staff = True
        admin.is_superuser = True
        admin.save()

        print("✅ Admin created successfully")

    else:
        print("⚡ Admin already exists")

END

echo "🎉 Build completed successfully!"