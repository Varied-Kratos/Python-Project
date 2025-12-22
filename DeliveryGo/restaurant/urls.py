from django.urls import path
from . import views

app_name = 'restaurant'

urlpatterns = [
    path('', views.home, name='home'),
    path('menu/', views.menu, name='menu'),
    path('menu/category/<int:category_id>/', views.category_menu, name='category_menu'),
    path('api/add_to_cart/', views.add_to_cart, name='add_to_cart'),
    path('api/cart_count/', views.get_cart_count, name='cart_count'),
    path('cart/', views.cart_view, name='cart'),
    path('cart/update/<int:item_id>/', views.update_cart_item, name='update_cart_item'),
    path('cart/remove/<int:item_id>/', views.remove_cart_item, name='remove_cart_item'),
    path('checkout/', views.checkout, name='checkout'),
    path('api/create_order/', views.create_order, name='create_order'),
    path('order-confirmation/<int:order_id>/', views.order_confirmation, name='order_confirmation'),
    path('api/cart_data/', views.get_cart_data, name='cart_data'),
]