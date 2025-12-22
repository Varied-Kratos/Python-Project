from django.urls import path
from . import views
from django.contrib.auth.decorators import login_required

urlpatterns = [
    path('', views.home, name='home'),
    path('menu/', views.menu, name='menu'),
    path('category/<int:category_id>/', views.category_menu, name='category_menu'),

    path('cart/', login_required(views.cart_view), name='cart'),
    path('cart/add/', login_required(views.add_to_cart), name='add_to_cart'),
    path('cart/update/<int:item_id>/', login_required(views.update_cart_item), name='update_cart_item'),
    path('cart/remove/<int:item_id>/', login_required(views.remove_cart_item), name='remove_cart_item'),

    path('checkout/', login_required(views.checkout), name='checkout'),
    path('checkout/create_order/', login_required(views.create_order), name='create_order'),
    path('order-confirmation/<int:order_id>/', login_required(views.order_confirmation), name='order_confirmation'),

    path('api/cart_count/', views.get_cart_count, name='cart_count'),
    path('api/cart_data/', login_required(views.get_cart_data), name='cart_data'),
    path('api/add_to_cart/', login_required(views.add_to_cart), name='add_to_cart_api'),

    path('api/create_order/', login_required(views.create_order), name='api_create_order'),

    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
]
