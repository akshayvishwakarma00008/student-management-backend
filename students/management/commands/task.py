from django.core.management.base import BaseCommand
import kronos
from account.utils import Util


@kronos.register("* * * * *")
class Command(BaseCommand):
    def handle(self, *args, **options):
        data = {
            "subject": "Testing Cron",
            "body": "mail getting sent",
            "to_email": "akshayvishwakarma00008@gmail.com",
        }
        Util.send_email(data)
