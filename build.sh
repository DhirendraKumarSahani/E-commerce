#!/usr/bin/env bash

pip install -r requirements.txt
python manage.py collectstatic --noinput
python manage.py migrate


# 🔥 ONE-TIME ADMIN RESET LOGIC

python manage.py shell << END
from django.contrib.auth import get_user_model
User = get_user_model()

# ✅ Check if admin already exists
if not User.objects.filter(phone="8882414182").exists():

    print("🚀 Creating Admin User...")

    admin = User.objects.create_superuser(
        username="dhirendra",        # required (manager ke liye)
        phone="8882414182",      # required (tumhare model ke liye)
        password="####ROY@@@@."
    )

    admin.email = "dhirendraroy8882414182@gmail.com"
    admin.is_staff = True
    admin.is_superuser = True
    admin.save()

    print("✅ Admin created successfully")

else:
    print("⚡ Admin already exists")

END