from django.core.management.base import BaseCommand

from api.orders.models import Country

COUNTRIES = [
    {"code": "US", "name": "United States"},
    {"code": "CA", "name": "Canada"},
    {"code": "GB", "name": "United Kingdom"},
    {"code": "NG", "name": "Nigeria"},
    {"code": "ZA", "name": "South Africa"},
    {"code": "KE", "name": "Kenya"},
    {"code": "GH", "name": "Ghana"},
]


class Command(BaseCommand):
    help = "Add selected countries to the Country model."

    def handle(self, *args, **options):
        for country in COUNTRIES:
            obj, created = Country.objects.get_or_create(
                code=country["code"], defaults={"name": country["name"]}
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"Added {obj.name} ({obj.code})"))
            else:
                self.stdout.write(f"{obj.name} ({obj.code}) already exists.")
