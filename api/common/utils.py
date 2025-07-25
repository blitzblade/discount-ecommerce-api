import re
from decimal import Decimal

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


def calculate_shipping(subtotal, address, shipping_method_name="Standard", weight=0):
    """
    Dynamically calculate shipping using ShippingZone and ShippingMethod models.
    Returns Decimal shipping cost, or None if delivery is not supported.
    """
    from api.orders.models import Country, ShippingMethod, ShippingZone

    country_code = getattr(address, "country", None)
    if not country_code:
        return Decimal("0")
    try:
        country = Country.objects.get(code=country_code)
        zone = ShippingZone.objects.get(country=country)
        method = ShippingMethod.objects.get(
            zone=zone, name__iexact=shipping_method_name, active=True
        )
    except (
        Country.DoesNotExist,
        ShippingZone.DoesNotExist,
        ShippingMethod.DoesNotExist,
    ):
        return None  # Delivery not supported
    # Free shipping if subtotal exceeds free_over
    if method.free_over and subtotal >= method.free_over:
        return Decimal("0")
    return method.base_rate + (method.per_kg_rate * Decimal(weight))


def calculate_tax(subtotal, address):
    """
    Dynamically calculate tax using TaxZone and TaxRate models.
    """
    from api.orders.models import Country, TaxRate, TaxZone

    country_code = getattr(address, "country", None)
    if not country_code:
        return Decimal("0.00")
    try:
        country = Country.objects.get(code=country_code)
        zone = TaxZone.objects.get(country=country, active=True)
        rate = (
            TaxRate.objects.filter(zone=zone, active=True)
            .order_by("-start_date")
            .first()
        )
    except (Country.DoesNotExist, TaxZone.DoesNotExist, TaxRate.DoesNotExist):
        return Decimal("0.00")
    if not rate:
        return Decimal("0.00")
    return (subtotal * rate.rate).quantize(Decimal("0.01"))


def check_delivery_availability(country_code):
    """
    Returns True if delivery is available to the given country code, else False.
    """
    from api.orders.models import Country, ShippingMethod, ShippingZone

    if not country_code:
        return False, "Country code is required."

    try:
        country = Country.objects.get(code=country_code.upper())
        zone = ShippingZone.objects.get(country=country)
        has_method = ShippingMethod.objects.filter(zone=zone, active=True).exists()
        if has_method:
            return True, f"Delivery is available to {country.name}."
        else:
            return False, f"No active shipping methods for {country.name}."
    except Country.DoesNotExist:
        return False, f"Country with code '{country_code}' not found."
    except ShippingZone.DoesNotExist:
        return False, f"No shipping zone configured for {country_code}."
