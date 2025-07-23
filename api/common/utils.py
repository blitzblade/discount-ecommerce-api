import re

import environ
import pyotp
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.mail import send_mail

env = environ.Env()
BASE_OTP_SECRET = env("BASE_OTP_SECRET", default="BASE32SECRET3232")


def validate_phonenumber(value):
    # Example: Accepts only numbers, 10-15 digits, can be customized
    if not re.fullmatch(r"\+?\d{10,15}", value):
        raise ValidationError(
            "Enter a valid phone number (10-15 digits, optional leading +)."
        )


# OTP secret can be user-specific or global for demo; in production, store per user securely
# Generate a time-based OTP
def generate_otp(secret, interval=300):
    totp = pyotp.TOTP(secret, interval=interval)
    return totp.now()


# Verify a time-based OTP
def verify_otp(otp, secret, interval=300):
    totp = pyotp.TOTP(secret, interval=interval)
    return totp.verify(otp)


def send_email(subject, message, recipient_list, from_email=None, fail_silently=True):
    if from_email is None:
        from_email = settings.DEFAULT_FROM_EMAIL
    send_mail(subject, message, from_email, recipient_list, fail_silently=fail_silently)
