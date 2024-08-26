from django.core.management.base import BaseCommand
from crud.models import Restaurant

class Command(BaseCommand):
    help = 'Update the price_min field for all restaurants'

    def handle(self, *args, **kwargs):
        restaurants = Restaurant.objects.all()
        for restaurant in restaurants:
            price_min_str = restaurant.price_range.split('円')[0].replace('〜', '').replace(',', '').strip()
            if price_min_str.isdigit():
                restaurant.price_min = int(price_min_str)
                restaurant.save()
        self.stdout.write(self.style.SUCCESS('Successfully updated price_min for all restaurants'))
