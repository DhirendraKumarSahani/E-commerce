#!/usr/bin/env bash

pip install -r requirements.txt
python manage.py collectstatic --noinput
python manage.py migrate

# 🔥 ADD THIS LINE
python create_superuser.py