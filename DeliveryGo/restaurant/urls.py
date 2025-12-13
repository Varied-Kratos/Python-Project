from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('menu/', views.menu, name='menu'),
    path('menu/category/<int:category_id>/', views.category_menu, name='category_menu'),
    path('api/add_to_cart/', views.add_to_cart, name='add_to_cart'),
    path('api/cart_count/', views.get_cart_count, name='cart_count'),
]