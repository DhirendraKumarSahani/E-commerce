import random
from django.conf import settings
from django.utils import timezone
from .models import PasswordResetOTP
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib import messages
from .utils import generate_otp, send_otp_fast2sms
from django.contrib.auth.hashers import make_password



User = get_user_model()


#-------------------------------------------------
# STEP 1: User Login View
def user_login(request):
    if request.method == 'POST':
        phone = request.POST.get('phone')
        password = request.POST.get('password')

        user = authenticate(request, phone=phone, password=password)

        if user is not None:
            login(request, user, backend='users.backends.PhoneBackend')
            return redirect('home')

        return render(request, 'users/login.html', {
            'error': 'Invalid mobile number or password'
        })

    return render(request, 'users/login.html')


#-------------------------------------------------

#-------------------------------------------------
# STEP 2: User Registration View
def user_register(request):
    if request.method == 'POST':
        phone = request.POST.get('phone')
        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email')  # optional

        if not all([phone, username, password]):
            return render(request, 'users/register.html', {
                'error': 'All fields are required'
            })

        if User.objects.filter(phone=phone).exists():
            return render(request, 'users/register.html', {
                'error': 'Mobile number already registered'
            })

        # 1️⃣ Create user
        user = User.objects.create_user(
            phone=phone,
            username=username,
            password=password
        )

        if email:
            user.email = email
            user.save()

        # 2️⃣ Authenticate user (IMPORTANT)
        auth_user = authenticate(
            request,
            phone=phone,
            password=password
        )

        # 3️⃣ Auto login
        if auth_user:
            login(request, auth_user)
            return redirect('home')

        return redirect('login')

    return render(request, 'users/register.html')


#-------------------------------------------------


#-------------------------------------------------
# STEP 3: User Logout View
def user_logout(request):
    logout(request)
    return redirect('/')
#-------------------------------------------------

    # #-------------------------------------------------
    # # Login Form (Phone + Password)

    # def login_view(request):
    #     if request.method == 'POST':
    #         phone = request.POST['phone']
    #         password = request.POST['password']

    #         user = authenticate(request, phone=phone, password=password)
    #         if user:
    #             login(request, user)
    #             return redirect(request.GET.get('next', '/'))

#----------------------------------------------
# Forgot Password View (Generate OTP)

from django.shortcuts import render, redirect
from django.contrib import messages
from .utils import generate_otp, send_otp_fast2sms
from django.contrib.auth import get_user_model

User = get_user_model()

def forgot_password(request):
    if request.method == 'POST':
        phone = request.POST.get('phone')

        if not User.objects.filter(phone=phone).exists():
            messages.error(request, "Mobile number not registered")
            return redirect('forgot_password')

        otp = generate_otp()

        # Store in session
        request.session['reset_phone'] = phone
        request.session['reset_otp'] = str(otp)

        send_otp_fast2sms(phone, otp)

        return redirect('verify_otp')

    return render(request, 'users/forgot_password.html')


#----------------------------------------------------------
# OTP Verification

def verify_otp(request):
    if request.method == 'POST':
        user_otp = request.POST.get('otp')
        session_otp = request.session.get('reset_otp')

        if user_otp == session_otp:
            return redirect('reset_password')
        else:
            messages.error(request, "Invalid OTP")

    return render(request, 'users/verify_otp.html')


#---------------------------------------------------------
# Reset Password

def reset_password(request):
    if request.method == 'POST':
        password = request.POST.get('password')
        phone = request.session.get('reset_phone')

        user = User.objects.get(phone=phone)
        user.password = make_password(password)
        user.save()

        # Clear session
        request.session.flush()

        messages.success(request, "Password reset successful")
        return redirect('login')

    return render(request, 'users/reset_password.html')



import requests

def send_otp_fast2sms(mobile, otp):
    url = "https://www.fast2sms.com/dev/bulkV2"

    payload = {
        "route": "otp",
        "variables_values": otp,
        "numbers": mobile,
    }

    headers = {
        "authorization": settings.FAST2SMS_API_KEY,
        "Content-Type": "application/json"
    }

    response = requests.post(url, json=payload, headers=headers)

    # 🔥 DEBUG LINE (YAHI PAR)
    print("FAST2SMS RESPONSE:", response.json())

    return response.json()
