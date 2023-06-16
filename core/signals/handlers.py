from store.signals import order_created
from django.dispatch import receiver
import http.client
import json
import time

@receiver(order_created)
def if_order_is_created_do(sender,**kwargs):
    
    return 0