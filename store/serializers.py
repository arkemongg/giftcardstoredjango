from django.conf import settings
import django.db.models
from requests import Response
from rest_framework import serializers
from store.models import (Address, Cart, CartItem, Category, CategoryImage, Customer, Order,
    orderItems, Products, ProductsImage)
from django.db import transaction

from .signals import order_created
from django.utils import timezone
import http.client
import json
from django.http import JsonResponse, HttpResponse


class ProductsImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoryImage
        fields = ['id','image']
    def create(self, validated_data):
        product_id = self.context['product_pk']
        product_image = ProductsImage.objects.create(product_id = product_id,**validated_data)
        return product_image

class SimpleCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['title']
        
class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Products
        fields = ['id','title','description','price','inventory','category','image']
    category = SimpleCategorySerializer()
    image = ProductsImageSerializer(many=True,read_only = True)

class CategoryImageSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        category_id = self.context['category_pk']
        category_image = CategoryImage.objects.create(category_id = category_id,**validated_data)
        return category_image
    class Meta:
        model = CategoryImage
        fields = ['id','image']
    
class CategorySerializer(serializers.ModelSerializer):
   
    class Meta:
        model = Category
        fields = ['id','title','description','image']

    image = CategoryImageSerializer(many = True)


class SimpleProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Products
        fields = ['id','title','price','category','image']

    category = SimpleCategorySerializer()
    image = ProductsImageSerializer(many=True,read_only = True)
    def get_image_url(self, obj):
        if obj.image.exists():
            image_path = obj.image.first().image.url
            return self.context['request'].build_absolute_uri(image_path)
        else:
            return None

class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = orderItems
        fields = ['id','product','quantity','unit_price','total_price']
    product = SimpleProductSerializer()

    total_price = serializers.SerializerMethodField()

    def get_total_price(self,request):
        return request.unit_price * request.quantity

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['pk','created_at','customer','items','payment_status','payment_url','order_status','total_price']
    items = OrderItemSerializer(many = True)
    total_price = serializers.SerializerMethodField()

    def get_total_price(self,request):
        total = 0;
        for items in request.items.all():
            total+=items.unit_price * items.quantity
        return total;

class CreateOrderSerializer(serializers.Serializer):
    cart_id = serializers.UUIDField()
    def validate_cart_id(self,cart_id):
        if not Cart.objects.filter(id = cart_id).exists():
            raise serializers.ValidationError("Cart_Not_Found")
        elif CartItem.objects.filter(cart_id = cart_id).count() < 1:
            raise serializers.ValidationError("Cart Is Empty")
        return cart_id
    
    def save(self, **kwargs):
        with transaction.atomic():
            if self.context['user_id'] == None:
                raise serializers.ValidationError("Annonymous User")
            
            
            customer = Customer.objects.get(user_id = self.context['user_id'])
            order = Order.objects.create(customer= customer)
            cartItem = CartItem.objects.filter(cart_id = self.validated_data['cart_id'])
            print(order.id)
            order_items = []
            total = 0
            for item in cartItem :
                total+=item.quantity * item.product.price
                order_item = orderItems(
                    order = order,
                    product = item.product,
                    quantity = item.quantity,
                    unit_price = item.product.price
                )
                order_items.append(order_item)
            
            # reqest payment_url
            conn = http.client.HTTPSConnection("api.commerce.coinbase.com")
            payload = {
            "name": customer.first_name() +' ' + customer.last_name(),
            "description": customer.first_name() +' ' + customer.last_name()+"'s" + "order",
            "pricing_type": "fixed_price",
            "local_price": {
                'amount' : str(total), 
                "currency": "USD"
            },
            "metadata": {
                "order_id": order.id,
                "customer_name": customer.first_name() +' ' + customer.last_name()
            },
            "redirect_url": "",
            "cancel_url": ""
            }

            # Convert payload to JSON
            payload_json = json.dumps(payload)

            headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'X-CC-Version': '2018-03-22',
            'X-CC-Api-Key': settings.COINBASE_API_KEY
            }

            conn.request("POST", "/charges", payload_json, headers)
            res = conn.getresponse()
            data = res.read()
            decoded_data = data.decode("utf-8")

            # Parse the decoded data as a dictionary
            data_dict = json.loads(decoded_data)

            # Access the values in the dictionar

            # Print the values
            payment_url = data_dict['data']['hosted_url']

            #request payment url
            order.payment_url = payment_url
            order.save()
            orderItems.objects.bulk_create(order_items)
            Cart.objects.filter(pk = self.validated_data['cart_id']).delete()
            order_created.send_robust(self.__class__,order = order)
            return order

class CartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['id','product','quantity','total_price','added_time']
    product = SimpleProductSerializer()
    total_price = serializers.SerializerMethodField()
    def get_total_price(self,val):
        return val.quantity * val.product.price


class AddCartItemSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField()
    class Meta:
        model = CartItem
        fields = ['id','product_id','quantity','added_time']
    
    def validate_product_id(self,id):
        if Products.objects.filter(pk = id).exists():
            return id
        raise serializers.ValidationError('Product not found')
    
    def validate_quantity(self,quantity):
        if quantity<1 :
            raise serializers.ValidationError("Can't be smaller than 1")
        return quantity

    def save(self, **kwargs):
        cart_pk = self.context['cart_pk']
        product_id = self.validated_data['product_id']
        qantity = self.validated_data['quantity']
        created_at = timezone.now()
        try:
            cart_item = CartItem.objects.get(cart_id = cart_pk,product_id = product_id)
            if cart_item.quantity + qantity >5 or qantity > 5:
                error_message = "Exceeded quantity limit"
                raise serializers.ValidationError(error_message)

            cart_item.quantity+=qantity
            cart_item.added_time = created_at
            cart_item.save()
        except CartItem.DoesNotExist:
            cart_items = CartItem.objects.filter(cart_id = cart_pk)
            
            if cart_items.count() >=5 :
                raise serializers.ValidationError('Exceded cart limit')
            
            if qantity > 5:
                raise serializers.ValidationError("Exceded quantity limit")
            cart_item = CartItem.objects.create(cart_id = cart_pk,**self.validated_data)
        self.instance = cart_item
        return self.instance
    
class UpdateCartItemSerailizer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['quantity']
        
    
class CartSerailizer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only = True)
    class Meta:
        model = Cart
        fields = ['id','created_at','items','total_price']
    items = CartItemSerializer(many = True,read_only = True)
    total_price = serializers.SerializerMethodField()

    def get_total_price(self,val):
        try:
            return val.total_price
        except:
            return 0
    
class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ['id','street1','street2','city','country','zip']

class CustomAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ['id','street1','street2','city','country','zip']


class CustomerSerializer(serializers.ModelSerializer):
    address = AddressSerializer(many=True)
    class Meta:
        model = Customer
        fields = ['id','phone','birth_date','membership','address']

    
class CustomerSerializerPost(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['phone','birth_date']



# {
#     "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTY4NDk1MjY5NywiaWF0IjoxNjg0ODY2Mjk3LCJqdGkiOiI0YmViYjcxMjYwNzc0ZDAyOWYwMDAwMGQ3M2ZhZjgyNSIsInVzZXJfaWQiOjY3fQ.cFTy3TzR1QBRAOEJvZhTQB0x59FIQnpxVNBtVgRcK7o",
#     "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNjg0OTUyNjk3LCJpYXQiOjE2ODQ4NjYyOTcsImp0aSI6IjRkMmYxZTI2NGIyNjRjZDc4ZWZhMjdmOGI5ZTBkZDU3IiwidXNlcl9pZCI6Njd9.E21a6vdrnTVpw-dW0NDhaHzVXYCa20xeywg0ocerBns"
# }
#03fHQkhTn04zDL3KEWGabogGJEHRlSW9