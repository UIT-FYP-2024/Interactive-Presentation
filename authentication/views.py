import logging
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.core.mail import send_mail
from django.shortcuts import render, redirect

from .exception import *
from .utils import *

logger = logging.getLogger(__name__)

User = get_user_model()


def sign_up(request):
    """
    Handle user sign-up process.

    Args:
        request: The HTTP request object.

    Returns:
        HttpResponse: The rendered sign-up page or redirect to sign-in page.
    """
    if request.user.is_authenticated:
        return render(request=request, template_name="dashboard/landing_home.html", context={})

    if request.method == 'POST':
        try:
            username = request.POST.get('username', '')
            first_name = request.POST.get('first_name', '')
            last_name = request.POST.get('last_name', '')
            email = request.POST.get('email', '')
            password = request.POST.get('password', '')

            validate_signup_form(username, first_name, last_name, email)

            send_test_account_settings = request.POST.get('send_test_account_settings', '') == 'on'
            subscribe_to_newsletter = request.POST.get('subscribe_to_newsletter', '') == 'on'
            accept_terms_of_service = request.POST.get('accept_terms_of_service', '') == 'on'

            create_user(username, first_name, last_name, email, password, send_test_account_settings,
                        subscribe_to_newsletter, accept_terms_of_service)

            return redirect("sign_in")
        except (CredentialsError, ResetError, RegisterError, ForgotError, UpdateError) as e:
            logger.error(f"Error during sign-up: {e}", exc_info=True)
            messages.error(request, str(e))

    return render(request=request, template_name="authentication/login_registration_advanced.html", context={})


def sign_in(request):
    """
    Handle user sign-in process.

    Args:
        request: The HTTP request object.

    Returns:
        HttpResponse: The rendered sign-in page or redirect to the index page.
    """
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
    """
    Handle user sign-out process.

    Args:
        request: The HTTP request object.

    Returns:
        HttpResponse: Redirect to the login page.
    """
    logout(request)
    return render(request, 'authentication/login_advanced.html')


def recover_password(request):
    """
    Handle password recovery process.

    Args:
        request: The HTTP request object.

    Returns:
        HttpResponse: The rendered password recovery page.
    """
    if request.method == 'POST':
        email = request.POST.get("email")
        subject = 'Password Recovery'
        message = 'This is a test email for password recovery.'
        from_email = 'wajahatashfaq2001@gmail.com'
        recipient_list = [email]
        try:
            send_mail(subject, message, from_email, recipient_list)
            messages.success(request, 'Password recovery email sent successfully.')
        except Exception as e:
            logger.error(f"Error sending password recovery email: {e}", exc_info=True)
            messages.error(request, 'Failed to send password recovery email.')

    return render(request, 'authentication/login_password_recover.html')


def reset_password(request):
    """
    Handle password reset process.

    Args:
        request: The HTTP request object.

    Returns:
        HttpResponse: The rendered password reset page or redirect to the sign-in page.
    """
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
