import time

from web_server import celery


@celery.task
def send_confirmation_email(email: str):
    time.sleep(5)
    print(f"sending email to {email}")
