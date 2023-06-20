import django.db.models
from django.utils.html import format_html
from django.contrib import admin

from store.models import (Cart, CartItem, Category, CategoryImage, Order, orderItems, Products,
    ProductsImage)

# Register your models here.

class ProductImageAdmin(admin.StackedInline):
    model = ProductsImage
    list_display = ['pk', 'image']
    extra = 1
    readonly_fields = ['formatted_image']
    def formatted_image(self, instance):
        if instance.image:
            return format_html('<img src="{}" width="200" />', instance.image.url)
        else:
            return '(No image)'

@admin.register(Products)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'price','display_image', 'inventory']
    list_editable = ['price']
    list_per_page = 10
    inlines = [ProductImageAdmin]

    def display_image(self, obj):
        if obj.image.exists():
            image_url = obj.image.first().image.url  # Assuming you have an ImageField in ProductsImage model
            return format_html('<img src="{}" width="100" height="100" />', image_url)
        else:
            return 'No image'

@admin.register(ProductsImage)
class ProductsImageAdmin(admin.ModelAdmin):
    list_display = ['pk', 'image','formatted_image']
    readonly_fields = ['formatted_image']
    def formatted_image(self, instance):
        if instance.image:
            return format_html('<img src="{}" width="200" />', instance.image.url)
        else:
            return '(No image)'


    
class CategoryInline(admin.StackedInline):
    model = CategoryImage
    list_display = ['pk', 'image']
    extra = 1
    readonly_fields = ['formatted_image']
    def formatted_image(self, instance):
        if instance.image:
            return format_html('<img src="{}" width="200" />', instance.image.url)
        else:
            return '(No image)'
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['id','title','description','display_image']
    inlines = [CategoryInline]

    def display_image(self, obj):
        if obj.image.exists():
            image_url = obj.image.first().image.url  # Assuming you have an ImageField in ProductsImage model
            return format_html('<img src="{}" width="100" height="100" />', image_url)
        else:
            return 'No image'

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

