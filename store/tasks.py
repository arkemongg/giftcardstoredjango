from celery import shared_task
from .models import Order
from django.utils import timezone
from datetime import datetime, timedelta

from templated_mail.mail import BaseEmailMessage

@shared_task 
def update_order_payment_status(order_id):
    order = Order.objects.get(id = order_id)

@shared_task
def update_order_status(order_id,charge_type):
    order = Order.objects.prefetch_related('customer').prefetch_related('customer__user').get(id = order_id)
    if 'charge:created' == charge_type:
        message = BaseEmailMessage(
        template_name='emails/order_created_email.html',
        context= {'order':order}
        )
        message.send([order.customer.user.email])
        
    elif 'charge:failed' == charge_type:
        message = BaseEmailMessage(
        template_name='emails/order_failed.html',
        context= {'order':order}
        )
        message.send([order.customer.user.email])
        
        order.payment_status = 'F'
        order.payment_url = '-'
        order.order_status = 'F'
        order.save()
    elif 'charge:confirmed' == charge_type :
        order.payment_status = 'C'
        order.payment_url = '-'
        order.save()
    else:
        print(order)
        print(charge_type)

@shared_task
def update_order_status_every_three_hours():
    current_time = timezone.now()
    two_hours_ago = current_time - timezone.timedelta(hours=2)
    order = Order.objects.exclude(payment_url = '-').filter(created_at__range=(two_hours_ago, current_time))
    print(order)

# celery -A giftcardstore worker -l info --pool=solo