import django.db.models
from django.utils.html import format_html
from django.contrib import admin

from store.models import Cart, CartItem, Category, CategoryImage, Order, orderItems, Products

# Register your models here.

@admin.register(Products)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['id','title','price','inventory']
    list_editable = ['price']
    list_per_page = 10

@admin.register(Category)
class CategoryAdmn(admin.ModelAdmin):
    list_display = ['id','title','description']

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['pk','total_price']
    def total_price(self,val):
        total = 0
        for items in val.items.all():
            total+=items.product.price * items.quantity
        return total
    

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ['pk','cart','product','total_price']

    def total_price(self,val):
        return val.product.price * val.quantity
    
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['pk','customer','payment_status','order_status','items__pk','payment','created_at']

    def items__pk(self,value):
        x = ""
        for items in value.items.all():
            x = x + items.product.title + '  |  '
        return x[:-1]
    
    def payment(self,value):
        value = value.payment_url
        if value == '-':
            return '-'
        
        html = format_html('<a href="{}" target="_blank">Pay Here</a>',value)
        return html
    
@admin.register(orderItems)
class OrderItemsAdmin(admin.ModelAdmin):
    list_display = ['pk','order_id','product']


@admin.register(CategoryImage)
class CategoryImageAdmin(admin.ModelAdmin):
    list_display = ['pk','category','image']
    