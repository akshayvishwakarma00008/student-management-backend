from django.core.mail import EmailMessage, get_connection
import os


class Util:
    @staticmethod
    def send_email(data):
        email = EmailMessage(
            subject=data["subject"],
            body=data["body"],
            from_email=os.environ.get("EMAIL_FROM"),
            to=[data["to_email"]],
            connection=get_connection(
                username=os.environ.get("EMAIL_USER"),
                password=os.environ.get("EMAIL_PASSWORD"),
            ),
        )
        email.send()
