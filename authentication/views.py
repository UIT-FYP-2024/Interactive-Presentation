# authentication/views.py

from django.contrib import messages
from django.contrib.auth import login, authenticate, logout, get_user_model
from django.core.mail import send_mail
from django.shortcuts import render, redirect
from authentication.exception import *
from authentication.validator import FormValidator


def sign_up(request):
    User = get_user_model()
    if request.user.is_authenticated:
        return render(request=request, template_name="dashboard/landing_home.html", context={})

    if request.method == 'POST':
        try:
            validator = FormValidator()

            username = request.POST.get('username', '')
            first_name = request.POST.get('first_name', '')
            last_name = request.POST.get('last_name', '')
            email = request.POST.get('email', '')
            password = request.POST.get('password', '')

            validator.validate_username(username)
            validator.validate_name(first_name)
            validator.validate_name(last_name)
            validator.validate_email(email)

            send_test_account_settings = request.POST.get('send_test_account_settings', '') == 'on'
            subscribe_to_newsletter = request.POST.get('subscribe_to_newsletter', '') == 'on'
            accept_terms_of_service = request.POST.get('accept_terms_of_service', '') == 'on'

            User.objects.create_user(
                username=username,
                first_name=first_name,
                last_name=last_name,
                email=email,
                password=password,
                send_test_account_settings=send_test_account_settings,
                subscribe_to_newsletter=subscribe_to_newsletter,
                accept_terms_of_service=accept_terms_of_service
            )
            # login(request, new_user)
            return redirect("sign_in")
        except (CredentialsError, ResetError, RegisterError, ForgotError, UpdateError) as e:
            messages.error(request, str(e))

    return render(request=request, template_name="authentication/login_registration_advanced.html", context={})


def sign_in(request):
    if request.method == 'POST':
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("index")
        else:
            messages.error(request, "Invalid credentials")

    return render(request=request, template_name="authentication/login_advanced.html", context={})


def sign_out(request):
    logout(request)
    return redirect("login_advanced")


def recover_password(request):
    if request.method == 'POST':
        email = request.POST.get("email")
        print(email)
        subject = 'Test Email'
        message = 'This is a test email sent using SMTP in Django.'
        from_email = 'wajahatashfaq2001@gmail.com'
        recipient_list = [email]
        send_mail(subject, message, from_email, recipient_list)

    return render(request, 'authentication/login_password_recover.html')


def reset_password(request):
    if request.method == 'POST':
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        if new_password == confirm_password:
            user = request.user
            user.set_password(new_password)
            user.save()
            messages.success(request, 'Password has been reset successfully. Please log in with your new password.')
            return redirect('sign_in')
        else:
            messages.error(request, 'Passwords do not match. Please try again.')

    return render(request, 'authentication/login_password_reset.html')
