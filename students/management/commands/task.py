from django.core.management.base import BaseCommand
import kronos

@kronos.register('* * * * *')
class Command(BaseCommand):
    def handle(self, *args, **options):
        print("hello world")