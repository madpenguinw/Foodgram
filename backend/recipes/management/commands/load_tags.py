from django.core.management import BaseCommand

from recipes.models import Tag


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        data = [
            {'name': 'Суп', 'color': '#F9A62B', 'slug': 'soup'},
            {'name': 'Гарнир', 'color': '#8775D2', 'slug': 'garnish'},
            {'name': 'Салат', 'color': '#49B64E', 'slug': 'salad'},
            {'name': 'Рыба', 'color': '#4A61DD', 'slug': 'fish'},
            {'name': 'Мясо', 'color': '#E26C2D', 'slug': 'meat'}]
        Tag.objects.bulk_create(Tag(**tag) for tag in data)
        self.stdout.write(self.style.SUCCESS('Все тэги загружены'))
