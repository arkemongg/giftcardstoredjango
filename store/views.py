
from store.permissions import IsAdminUserOrReadOnly
from core.models import User
from store.tasks import update_order_status, update_order_status_django_bg
from store.pagination import DefaultLimitOffset, DefaultPagination
from .models import Address, Cart, CartItem, Category, Customer, Order, orderItems, Products
from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet,GenericViewSet
from rest_framework.mixins import RetrieveModelMixin,UpdateModelMixin,DestroyModelMixin,CreateModelMixin,ListModelMixin
from django.db.models import F,Sum,Value
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework import status
from rest_framework.permissions import IsAuthenticated,IsAdminUser
from store.serializers import (AddCartItemSerializer, AddressSerializer, CartItemSerializer,
    CartSerailizer, CategorySerializer, CreateOrderSerializer, CustomerSerializer,
    CustomerSerializerPost, OrderItemSerializer, OrderSerializer, ProductSerializer,
    UpdateCartItemSerailizer)
from django.http import HttpResponse
import json
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseBadRequest
import hmac
import hashlib

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
# Create your views here.

class ProductsViewSet(ModelViewSet):
    serializer_class = ProductSerializer
    pagination_class = DefaultLimitOffset
    filter_backends = [DjangoFilterBackend,SearchFilter]
    filterset_fields = ['category']
    search_fields = ['title']
    def get_queryset(self):
        if self.request.method == 'GET':
           # print(self.request.META.get('HTTP_USER_AGENT',''))
            return Products.objects.select_related('category').prefetch_related('image')
    permission_classes = [IsAdminUserOrReadOnly]

class CategoryViewSet(RetrieveModelMixin,ListModelMixin,GenericViewSet):
    permission_classes = [IsAdminUserOrReadOnly]
    serializer_class = CategorySerializer
    queryset = Category.objects.prefetch_related('image').all()
    def get_serializer_context(self):
        return super().get_serializer_context()


class OrderViewSet(ListModelMixin,CreateModelMixin,RetrieveModelMixin,GenericViewSet):
    permission_classes = [IsAuthenticated]
    def get_serializer_class(self):
        if self.request.method=="POST":
            return CreateOrderSerializer
        return OrderSerializer
    def get_queryset(self):
        try:
            customer = Customer.objects.only('id').get(user_id=self.request.user.id)
            customer_id = customer.id
            # orders = Order.objects.filter(customer_id = customer_id).order_by('-created_at')
            
            # for order in orders:
            #     print(order.customer.user.email)

            return Order.objects.prefetch_related('items').prefetch_related('items__product__image').prefetch_related('items__product__category').select_related('customer').filter(customer_id = customer_id).order_by('-created_at')
        except :
            pass
    def get_serializer_context(self):
        return {
            'user_id' : self.request.user.id
        }
    @action(detail=False, methods=['GET'],permission_classes=[IsAuthenticated])
    def last_order(self,request):
        try:
            customer_id = Customer.objects.only('id').get(user_id = self.request.user.id)
            serializer = OrderSerializer(Order.objects.prefetch_related('items').filter(customer_id = customer_id).latest('id'))
            return Response(serializer.data)
        except:
            raise serializers.ValidationError('No Order Found')

class OrderItemsViewSet(ListModelMixin,RetrieveModelMixin,GenericViewSet):
    permission_classes = [IsAdminUserOrReadOnly]
    def get_queryset(self,*args, **kwargs):
        if self.request.user.id == None:
            raise ValidationError({"detail": "BAD REQUEST"})
        
        order = Order.objects.get(id = Value(self.kwargs['order_pk']))
        customer = Customer.objects.only('id').get(user_id=self.request.user.id)
        customer_id = customer.id
        if order.customer.id != customer_id:
            raise ValidationError({"detail": "Invalid customer for this order"})
        return orderItems.objects.filter(order_id=self.kwargs['order_pk'])
    serializer_class = OrderItemSerializer

class CartViewSet(ListModelMixin,GenericViewSet,RetrieveModelMixin,CreateModelMixin,DestroyModelMixin):
    def get_serializer_class(self):
        return CartSerailizer
    
    def get_queryset(self):
        try:
            items = CartItem.objects.select_related('product').filter(cart_id = self.kwargs['pk'])
            total = 0
            for item in items :
                total += item.quantity * item.product.price
            cart = Cart.objects.prefetch_related('items').prefetch_related('items__product').prefetch_related('items__product__image').prefetch_related('items__product__category').annotate(total_price = Value(total))
            return cart.order_by('items__added_time')
        except:
            pass
    
class CartItemViewSet(ModelViewSet):
    http_method_names = ['get','post','patch','delete']
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return AddCartItemSerializer
        elif self.request.method == 'PATCH':
            return UpdateCartItemSerailizer
        return CartItemSerializer
    def get_queryset(self):
        return CartItem.objects.select_related("product").filter(cart_id = self.kwargs['cart_pk']).order_by('added_time')
    def get_serializer_context(self):
        return {
            'cart_pk' : self.kwargs['cart_pk']
        }
class CustomerViewSet(ListModelMixin,UpdateModelMixin,RetrieveModelMixin,GenericViewSet):
    http_method_names = ['get','put','option','head']
    permission_classes = [IsAuthenticated]
    def get_serializer_class(self):
        if self.request.method == 'PUT':
            return CustomerSerializerPost
        return CustomerSerializer

    def get_queryset(self):
            #security impliment
            # jwt_token = self.request.META.get('HTTP_AUTHORIZATION', '').split(' ')[1]
            # banned_jwt = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNjg3NDY3NTczLCJpYXQiOjE2ODczODExNzMsImp0aSI6IjRhYTcwZGZkNmI2YjQ0ZmVhODEwZGM4ZTg1MjE2OTRjIiwidXNlcl9pZCI6Njh9.nNHaX6vVGuvgl04Qcg1xC_Lfa9JYealFUDKEka9IM7U"
            # if jwt_token == banned_jwt:
            #     raise serializers.ValidationError({'error':'please login again'})
            return Customer.objects.filter(user_id = self.request.user.id)

    @action(detail=False, methods=['GET', 'PUT'],permission_classes = [IsAuthenticated])
    def me(self, request):
        if self.request.method == 'GET':
            customer = Customer.objects.get(user_id=self.request.user.id)
            serializer = CustomerSerializer(customer)
            return Response(serializer.data)
        elif self.request.method == 'PUT':
            customer = Customer.objects.get(user_id=self.request.user.id)
            serializer_update = CustomerSerializerPost(customer, data=self.request.data)
            serializer_update.is_valid(raise_exception=True)
            serializer_update.save()

            # Retrieve the complete data using both serializers and merge them
            serializer = CustomerSerializer(customer)
            serializer_post = CustomerSerializerPost(customer)
            merged_data = {**serializer.data, **serializer_post.data}

            return Response(merged_data)
        
class AddressViewSet(ModelViewSet):
    serializer_class = AddressSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get','put','patch','head', 'options']
    def get_queryset(self):
        customer_id = Customer.objects.only('id').get(user_id = self.request.user.id)
        return Address.objects.filter(customer_id = customer_id)
    @action(detail=False, methods=['GET', 'PUT'],permission_classes = [IsAuthenticated])
    def me(self, request, customer_pk=None):
        customer_id = Customer.objects.only('id').get(user_id = self.request.user.id)
        address =  Address.objects.get(customer_id = customer_id)
        if self.request.method == 'PUT':
            if self.request.data['country']=="":
                raise serializers.ValidationError("Country can't be NULL")
            serializer = AddressSerializer(address,data = self.request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
        serializer = AddressSerializer(address)
        return Response(serializer.data)

COINBASE_WEBHOOK_SECRET = settings.COINBASE_HOOK

@csrf_exempt
def coinbase_webhook(request):
    if request.method == 'POST':
        signature = request.headers.get('X-CC-Webhook-Signature', '')
        if not verify_coinbase_signature(signature, request.body):
            return HttpResponseBadRequest('Invalid signature')
        payload = json.loads(request.body)
        # print(payload)
        # print(payload['event']['type'])
        #update_order_status.delay(payload['event']['data']['metadata']['order_id'],payload['event']['type'])
        update_order_status_django_bg(payload['event']['data']['metadata']['order_id'],payload['event']['type'])
        return HttpResponse(status=200)
    else:
        return HttpResponseBadRequest('Invalid request method')

def verify_coinbase_signature(signature, payload):
    secret_bytes = bytes(COINBASE_WEBHOOK_SECRET, 'utf-8')
    expected_signature = hmac.new(secret_bytes, payload, hashlib.sha256).hexdigest()
    return hmac.compare_digest(signature, expected_signature)

# data = {
#     'attempt_number': 1,
#     'event': {
#         'api_version': '2018-03-22',
#         'created_at': '2023-05-30T21:12:02Z',
#         'data': {
#             'id': 'eb4304c7-fa58-435e-96d0-3ee33a8ec4ff',
#             'code': '4ML425A4',
#             'name': 'a',
#             'utxo': False,
#             'pricing': {
#                 'dai': {'amount': '9.999500024998750062', 'currency': 'DAI'},
#                 'usdc': {'amount': '10.000000', 'currency': 'USDC'},
#                 'local': {'amount': '10.00', 'currency': 'USD'},
#                 'pusdc': {'amount': '10.000000', 'currency': 'PUSDC'},
#                 'pweth': {'amount': '0.005242450216382133', 'currency': 'PWETH'},
#                 'tether': {'amount': '9.996151', 'currency': 'USDT'},
#                 'apecoin': {'amount': '3.130870381966186600', 'currency': 'APE'},
#                 'bitcoin': {'amount': '0.00035961', 'currency': 'BTC'},
#                 'polygon': {'amount': '11.046672000', 'currency': 'PMATIC'},
#                 'dogecoin': {'amount': '138.15016923', 'currency': 'DOGE'},
#                 'ethereum': {'amount': '0.005245000', 'currency': 'ETH'},
#                 'litecoin': {'amount': '0.10871338', 'currency': 'LTC'},
#                 'shibainu': {'amount': '1148765.077541640000000000', 'currency': 'SHIB'},
#                 'bitcoincash': {'amount': '0.08716496', 'currency': 'BCH'}
#             },
#             'checkout': {'id': '978efce3-3b95-489d-9c83-6f1cd7b70ed2'},
#             'fee_rate': 0.01,
#             'logo_url': '',
#             'metadata': {'name': '12'},
#             'payments': [],
#             'resource': 'charge',
#             'timeline': [{'time': '2023-05-30T21:12:02Z', 'status': 'NEW'}],
#             'addresses': {
#                 'dai': '0xcb266d923f6bf06c11e5580b6b31aaf4e48e3db6',
#                 'usdc': '0xcb266d923f6bf06c11e5580b6b31aaf4e48e3db6',
#                 'pusdc': '0xcb266d923f6bf06c11e5580b6b31aaf4e48e3db6',
#                 'pweth': '0xcb266d923f6bf06c11e5580b6b31aaf4e48e3db6',
#                 'tether': '0xcb266d923f6bf06c11e5580b6b31aaf4e48e3db6',
#                 'apecoin': '0xcb266d923f6bf06c11e5580b6b31aaf4e48e3db6',
#                 'bitcoin': '33GcLGi4W27obtvp2V6MfjphNfPJgpSPLd',
#                 'polygon': '0xcb266d923f6bf06c11e5580b6b31aaf4e48e3db6',
#                 'dogecoin': 'DU5eouoRioKHP779wV3fRFWndWwtcw7X7C',
#                 'ethereum': '0xcb266d923f6bf06c11e5580b6b31aaf4e48e3db6',
#                 'litecoin': 'MGtdKea8oSjdRa7Nd2FfxdcSGdhu72MZW6',
#                 'shibainu': '0xcb266d923f6bf06c11e5580b6b31aaf4e48e3db6',
#                 'bitcoincash': 'qqnaw9k0yyg7vms4c6nuv72ujk2jkxt5vg9tyw9mwc'
#             },
#             'pwcb_only': False,
#             'created_at': '2023-05-30T21:12:02Z',
#             'expires_at': '2023-05-30T22:12:02Z',
#             'hosted_url': 'https://commerce.coinbase.com/charges/4ML425A4',
#             'brand_color': '#122332',
#             'description': '5',
#             'fees_settled': True,
#             'pricing_type': 'fixed_price',
#             'support_email': 'ark.emon596@gmail.com',
#             'brand_logo_url': '',
#             'exchange_rates': {
#                 'APE-USD': '3.194',
#                 'BCH-USD': '114.725',
#                 'BTC-USD': '27808.09',
#                 'DAI-USD': '1.00005',
#                 'ETH-USD': '1906.755',
#                 'LTC-USD': '91.985',
#                 'DOGE-USD': '0.072385',
#                 'SHIB-USD': '0.000008705',
#                 'USDC-USD': '1.0',
#                 'USDT-USD': '1.000385',
#                 'PUSDC-USD': '1.0',
#                 'PWETH-USD': '1907.505',
#                 'PMATIC-USD': '0.90525'
#             },
#             'offchain_eligible': False,
#             'organization_name': '',
#             'payment_threshold': {
#                 'overpayment_absolute_threshold': {'amount': '5.00', 'currency': 'USD'},
#                 'overpayment_relative_threshold': '0.005',
#                 'underpayment_absolute_threshold': {'amount': '5.00', 'currency': 'USD'},
#                 'underpayment_relative_threshold': '0.005'
#             },
#             'local_exchange_rates': {
#                 'APE-USD': '3.194',
#                 'BCH-USD': '114.725',
#                 'BTC-USD': '27808.09',
#                 'DAI-USD': '1.00005',
#                 'ETH-USD': '1906.755',
#                 'LTC-USD': '91.985',
#                 'DOGE-USD': '0.072385',
#                 'SHIB-USD': '0.000008705',
#                 'USDC-USD': '1.0',
#                 'USDT-USD': '1.000385',
#                 'PUSDC-USD': '1.0',
#                 'PWETH-USD': '1907.505',
#                 'PMATIC-USD': '0.90525'
#             },
#             'coinbase_managed_merchant': False
#         },
#         'id': '845f8016-57ce-4b87-9299-3df6138eb2f6',
#         'resource': 'event',
#         'type': 'charge:created'
#     },
#     'id': '2cf56bd1-5742-4823-8445-d6be56e9653f',
#     'scheduled_for': '2023-05-30T21:12:02Z'
# }    
#user69  
# {
#     "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTY4NDQwODAxNywiaWF0IjoxNjg0MzIxNjE3LCJqdGkiOiJjMWJlNjYyMzY3NWY0ZTc0OTAwMjcyNGQxZDYyZDJmYSIsInVzZXJfaWQiOjUwfQ.eK8h8l8cPnX3RzU2D8KbRemhzkJexEeSLD57LngrdFc",
#     "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNjg0NDA4MDE3LCJpYXQiOjE2ODQzMjE2MTcsImp0aSI6ImRhNTJmNjljYTBjMzQ3NGI4ZjZhZTYyZDcyMjFjM2MzIiwidXNlcl9pZCI6NTB9.CPtpbllz7T6NJ9ag80AI_yBVyePUlBaqmRXu6HPP6YM"
# }
    