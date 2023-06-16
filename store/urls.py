from django.urls import path , include

from rest_framework_nested import routers

from .views import (AddressViewSet, CartItemViewSet, CartViewSet, CategoryViewSet, CustomerViewSet,
    OrderViewSet, ProductsViewSet,coinbase_webhook , OrderItemsViewSet)
router = routers.DefaultRouter()
router.register('products',ProductsViewSet,basename='products-list')
router.register('categories',CategoryViewSet,basename='categories-list')
router.register('orders',OrderViewSet,basename='orders-list')
router.register('carts',CartViewSet,basename='cart')
router.register('customer',CustomerViewSet,basename='customer')

cart_router = routers.NestedDefaultRouter(router,'carts',lookup = 'cart')
cart_router.register('items',CartItemViewSet,basename='cart-items')

customer_address = routers.NestedDefaultRouter(router,'customer',lookup = 'customer')
customer_address.register('address',AddressViewSet,basename='customer-address')

order_router = routers.NestedDefaultRouter(router,'orders',lookup = 'order')
order_router.register('items',OrderItemsViewSet,basename='items')
urlpatterns = [
    path('', include(router.urls)),
    path('',include(cart_router.urls)),
    path('',include(customer_address.urls)),
    path('',include(order_router.urls)),
    path('coinbase-webhook/', coinbase_webhook, name='coinbase_webhook'),
]