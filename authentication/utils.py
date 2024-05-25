# authentication/utils.py

import random
import string
from django.contrib.auth import get_user_model
from authentication.validator import FormValidator

User = get_user_model()


def validate_signup_form(username, first_name, last_name, email):
    validator = FormValidator()
    validator.validate_username(username)
    validator.validate_name(first_name)
    validator.validate_name(last_name)
    validator.validate_email(email)


def create_user(username, first_name, last_name, email, password, send_test_account_settings, subscribe_to_newsletter,
                accept_terms_of_service):
    return User.objects.create_user(
        username=username,
        first_name=first_name,
        last_name=last_name,
        email=email,
        password=password,
        send_test_account_settings=send_test_account_settings,
        subscribe_to_newsletter=subscribe_to_newsletter,
        accept_terms_of_service=accept_terms_of_service
    )


def generate_random_pw(length: int = 16) -> str:
    """
    Generates a random password.

    Parameters
    ----------
    length: int
        The length of the returned password.
    Returns
    -------
    str
        The randomly generated password.
    """
    letters = string.ascii_letters + string.digits
    return ''.join(random.choice(letters) for _ in range(length))
