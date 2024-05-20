# authentication/image_models.py

from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    send_test_account_settings = models.BooleanField(default=False)
    subscribe_to_newsletter = models.BooleanField(default=False)
    accept_terms_of_service = models.BooleanField(default=False)
