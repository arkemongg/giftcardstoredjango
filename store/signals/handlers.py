from django.dispatch import receiver
from django.db.models.signals import post_save,pre_delete
from store.models import Address, CategoryImage, Customer
from django.conf import settings
import os

@receiver(post_save,sender = settings.AUTH_USER_MODEL)
def create_customer_for_new_user(sender,**kwargs):
    if kwargs['created']:
        customer = Customer.objects.create(user = kwargs['instance'])
        customer.save()
        address = Address.objects.create(customer_id = customer.id)
        address.save()

@receiver(pre_delete, sender=CategoryImage)
def delete_image_file(sender, instance, **kwargs):
    print('Images')
    if instance.image:
        file_path = instance.image.path
        if os.path.exists(file_path):
            os.remove(file_path)      