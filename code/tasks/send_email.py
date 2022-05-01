from web_server import celery


@celery.task
def send_confirmation_email(email: str):
    print(f"sending email to {email}")
