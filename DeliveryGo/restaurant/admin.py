from django.contrib import admin
from .models import Category, MenuItem, CartItem, Order, OrderItem

admin.site.register(Category)
admin.site.register(MenuItem)
admin.site.register(CartItem)
admin.site.register(Order)
admin.site.register(OrderItem)