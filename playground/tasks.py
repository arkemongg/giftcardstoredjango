from time import sleep
from celery import shared_task

@shared_task
def notify_customer(message):
    print('Senfing 10k emails....')

    print(message)

    sleep(10)

    print('Emails were sent successfully')

