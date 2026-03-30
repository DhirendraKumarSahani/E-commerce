import random

import requests
from django.conf import settings

def generate_otp():
    return random.randint(100000, 999999)

#------------------------------------------------------
# FAST2SMS SEND FUNCTION

def send_otp_fast2sms(phone, otp):
    url = "https://www.fast2sms.com/dev/bulkV2"

    payload = {
        "route": "otp",
        "variables_values": otp,
        "numbers": phone
    }

    headers = {
        "authorization": settings.FAST2SMS_API_KEY,
        "Content-Type": "application/json"
    }

    response = requests.post(url, json=payload, headers=headers)
    return response.json()
