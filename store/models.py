from uuid import uuid4
from django.conf import settings
from django.db import models
from django.core.validators import MinValueValidator
from django_countries.fields import CountryField

class Promotion(models.Model):
    code = models.CharField(max_length=10)
    discount = models.DecimalField(decimal_places=2,max_digits=2)
    description = models.TextField()

class Category(models.Model):
    title = models.CharField(max_length=265)
    description = models.TextField()

    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"
class CategoryImage(models.Model):
    category = models.ForeignKey(Category,on_delete=models.CASCADE,related_name='image')
    image = models.ImageField(upload_to='store/image')


class Products(models.Model):
    title = models.CharField(max_length=265)
    description = models.TextField()
    price = models.DecimalField(max_digits=6,decimal_places=2)
    inventory = models.PositiveSmallIntegerField(validators=[MinValueValidator(1)])
    last_update = models.DateTimeField(auto_now_add=True)

    category = models.ForeignKey(Category,on_delete= models.PROTECT)
    promotion = models.ManyToManyField(Promotion,blank= True)
    def __str__(self):
        return self.title
    class Meta:
        verbose_name = "Product"
        verbose_name_plural = "Products"

class ProductsImage(models.Model):
    product = models.ForeignKey(Products,on_delete=models.CASCADE,related_name='image')
    image = models.ImageField(upload_to='store/image')


class Customer(models.Model):
    MEMBERSHIP_BRONZE = 'B'
    MEMBERSHIP_SILVER = 'S'
    MEMBERSHIP_GOLD = 'G'

    MEMEBERSHIP_CHOICES = [
        (MEMBERSHIP_BRONZE,'BRONZE'),
        (MEMBERSHIP_SILVER,'SILVER'),
        (MEMBERSHIP_GOLD,'GOLD'),
    ]

    phone = models.CharField(max_length=20)
    birth_date = models.DateField(blank=True,null=True)
    membership = models.CharField(max_length=1,choices=MEMEBERSHIP_CHOICES,default=MEMBERSHIP_BRONZE)
    user = models.OneToOneField(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)

    def first_name(self):
        return self.user.first_name

    def last_name(self):
        return self.user.last_name
    def __str__(self) -> str:
        return f'{self.user.first_name} {self.user.last_name}'

class Address(models.Model):
    customer = models.ForeignKey(Customer,on_delete=models.CASCADE,blank=True,null=True,related_name="address")
    street1 = models.CharField(max_length=265,blank=True,null=True)
    street2 = models.CharField(max_length=265,blank=True,null=True)
    city = models.CharField(max_length=265,blank=True,null=True)
    country = CountryField(blank=True,null=True,default='US')
    zip = models.CharField(max_length=265,null=True)


class Order(models.Model):
    PAYMENT_STATUS_PENDING = 'P'
    PAYMENT_STATUS_COMPLETE = 'C'
    PAYMENT_STATUS_FAILED = 'F'

    PAYMENT_STATUS_CHOICES = [
        (PAYMENT_STATUS_PENDING,'PAYMENT_STATUS_PENDING'),
        (PAYMENT_STATUS_COMPLETE,'PAYMENT_STATUS_COMPLETE'),
        (PAYMENT_STATUS_FAILED,'PAYMENT_STATUS_FAILED'),
    ]
    ORDER_STATUS_PENDING = 'P'
    ORDER_STATUS_COMPLETE = 'C'
    ORDER_STATUS_FAILED = 'F'

    ORDER_STATUS_CHOICES = [
        (ORDER_STATUS_PENDING,'ORDER_STATUS_PENDING'),
        (ORDER_STATUS_COMPLETE,'ORDER_STATUS_COMPLETE'),
        (ORDER_STATUS_FAILED,'ORDER_STATUS_FAILED'),
    ]
    
    order_status = models.CharField(max_length=1,choices=ORDER_STATUS_CHOICES,default=ORDER_STATUS_PENDING)
    payment_url = models.CharField(max_length=265,default='-')
    payment_status = models.CharField(max_length=1,choices=PAYMENT_STATUS_CHOICES,default=PAYMENT_STATUS_PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    customer = models.ForeignKey(Customer,models.PROTECT)

class orderItems(models.Model):
    order = models.ForeignKey(Order,on_delete=models.PROTECT,related_name='items')
    product = models.ForeignKey(Products,on_delete=models.PROTECT)
    quantity = models.PositiveSmallIntegerField(validators=[MinValueValidator(1)])
    unit_price = models.DecimalField(max_digits=6,decimal_places=2)
    def __str__(self):
        return self.product.title

class Cart(models.Model):
    id = models.UUIDField(primary_key=True,default=uuid4)
    created_at = models.DateTimeField(auto_now_add=True)

class CartItem(models.Model):
    cart = models.ForeignKey(Cart,on_delete=models.CASCADE,related_name='items')
    product = models.ForeignKey(Products,on_delete=models.CASCADE)
    quantity = models.IntegerField(validators=[MinValueValidator(1)])
    added_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.product
    class Meta:
        unique_together = [['cart','product']]
