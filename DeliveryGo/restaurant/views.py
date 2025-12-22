from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.db import transaction
from django.core.validators import ValidationError
from django.core.exceptions import ObjectDoesNotExist
import json
from .models import Category, MenuItem, CartItem, Order, OrderItem
from django.contrib.auth.decorators import login_required
from .models import CartItem, MenuItem, Order
from decimal import Decimal

def home(request):
    bestsellers = MenuItem.objects.filter(is_bestseller=True, is_available=True)[:6]
    categories = Category.objects.all()[:6]

    return render(request, 'restaurant/home.html', {
        'bestsellers': bestsellers,
        'categories': categories
    })


def menu(request):
    categories = Category.objects.prefetch_related('items').all()

    category_order = {
        'Супы': 1,
        'Горячие блюда': 2,
        'Закуски': 9,
        'Салаты': 4,
        'Паста': 5,
        'Пицца': 6,
        'Десерты': 7,
        'Напитки': 8,
        'Соусы': 10,
        'Бургеры' : 3,
    }

    categories = sorted(categories, key=lambda x: category_order.get(x.name, 99))

    return render(request, 'restaurant/menu.html', {
        'categories': categories
    })


def category_menu(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    items = MenuItem.objects.filter(category=category, is_available=True)

    return render(request, 'restaurant/category_menu.html', {
        'category': category,
        'items': items
    })


@csrf_exempt
def add_to_cart(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            item_id = data.get('item_id')
            quantity = int(data.get('quantity', 1))

            item = MenuItem.objects.get(id=item_id, is_available=True)

            session_key = request.session.session_key
            if not session_key:
                request.session.create()
                session_key = request.session.session_key

            cart_item = CartItem.objects.create(
                menu_item=item,
                quantity=quantity,
                session_key=session_key
            )

            return JsonResponse({
                'success': True,
                'message': f'{item.name} добавлен в корзину',
                'cart_item_id': cart_item.id
            })

        except MenuItem.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Товар не найден'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'Ошибка в добавлении'})


def get_cart_count(request):
    session_key = request.session.session_key
    if session_key:
        count = CartItem.objects.filter(session_key=session_key).count()
    else:
        count = 0

    return JsonResponse({'count': count})

@login_required(login_url='accounts:login')
def cart_view(request):
    session_key = request.session.session_key
    cart_items = CartItem.objects.filter(session_key=session_key)

    # Расчет суммы
    total_amount = 0
    for item in cart_items:
        total_amount += item.menu_item.price * item.quantity

    # Стоимость доставки (бесплатно от 2000₽)
    free_delivery_threshold = 2000
    delivery_fee = 0 if total_amount >= free_delivery_threshold else 200

    # Расчет сколько не хватает до бесплатной доставки
    needed_for_free = 0
    if total_amount < free_delivery_threshold:
        needed_for_free = free_delivery_threshold - total_amount

    context = {
        'cart_items': cart_items,
        'total_amount': total_amount,
        'delivery_fee': delivery_fee,
        'final_amount': total_amount + delivery_fee,
        'free_delivery_threshold': free_delivery_threshold,
        'needed_for_free': needed_for_free,  # Добавлено
    }
    return render(request, 'restaurant/cart.html', context)

@csrf_exempt
def update_cart_item(request, item_id):
    """Обновление количества товара в корзине"""
    if request.method == 'POST':
        try:
            # Для отладки
            print(f"Updating cart item: {item_id}")

            data = json.loads(request.body)
            action = data.get('action')  # 'increase', 'decrease', 'set'
            quantity = int(data.get('quantity', 1))

            session_key = request.session.session_key
            if not session_key:
                request.session.create()
                session_key = request.session.session_key

            print(f"Session key: {session_key}")
            print(f"Action: {action}")

            cart_item = CartItem.objects.get(id=item_id, session_key=session_key)

            if action == 'increase':
                cart_item.quantity += 1
            elif action == 'decrease':
                cart_item.quantity = max(1, cart_item.quantity - 1)
            elif action == 'set':
                cart_item.quantity = max(1, quantity)

            cart_item.save()

            # Пересчет сумм
            cart_items = CartItem.objects.filter(session_key=session_key)
            total_amount = sum(item.menu_item.price * item.quantity for item in cart_items)
            delivery_fee = 0 if total_amount >= 2000 else 200

            # Получаем общее количество товаров в корзине
            cart_count = cart_items.count()

            return JsonResponse({
                'success': True,
                'quantity': cart_item.quantity,
                'item_total': float(cart_item.menu_item.price * cart_item.quantity),
                'total_amount': float(total_amount),
                'delivery_fee': float(delivery_fee),
                'final_amount': float(total_amount + delivery_fee),
                'cart_count': cart_count,
            })

        except CartItem.DoesNotExist:
            print(f"Cart item not found: {item_id}")
            return JsonResponse({
                'success': False,
                'error': 'Товар не найден в корзине'
            })
        except Exception as e:
            print(f"Error updating cart item: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            })

    return JsonResponse({
        'success': False,
        'error': 'Метод не разрешен'
    })

@csrf_exempt
def remove_cart_item(request, item_id):
    if request.method == 'POST':
        try:
            session_key = request.session.session_key
            if not session_key:
                return JsonResponse({'success': False, 'error': 'Сессия не найдена'})

            cart_item = CartItem.objects.get(id=item_id, session_key=session_key)
            cart_item.delete()

            # Пересчет сумм
            cart_items = CartItem.objects.filter(session_key=session_key)
            total_amount = sum(item.menu_item.price * item.quantity for item in cart_items)
            delivery_fee = 0 if total_amount >= 2000 else 200

            return JsonResponse({
                'success': True,
                'total_amount': float(total_amount),
                'delivery_fee': float(delivery_fee),
                'final_amount': float(total_amount + delivery_fee),
                'cart_count': cart_items.count(),
            })

        except CartItem.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Товар не найден в корзине'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'Метод не разрешен'})

def checkout(request):
    session_key = request.session.session_key
    cart_items = CartItem.objects.filter(session_key=session_key)

    if not cart_items.exists():
        messages.warning(request, 'Ваша корзина пуста')
        return redirect('cart')

    total_amount = sum(item.menu_item.price * item.quantity for item in cart_items)
    delivery_fee = 0 if total_amount >= 2000 else 200

    # Если пользователь авторизован, заполняем форму его данными
    if request.user.is_authenticated:
        user = request.user
        initial_data = {
            'customer_name': f"{user.first_name} {user.last_name}".strip() or user.username,
            'email': user.email,
            'phone': user.userprofile.phone if hasattr(user, 'userprofile') and user.userprofile.phone else '',
            'delivery_address': user.userprofile.address if hasattr(user, 'userprofile') and user.userprofile.address else '',
        }
    else:
        initial_data = {
            'customer_name': request.session.get('customer_name', ''),
            'phone': request.session.get('phone', ''),
            'email': request.session.get('email', ''),
            'delivery_address': request.session.get('delivery_address', ''),
        }

    context = {
        'cart_items': cart_items,
        'total_amount': total_amount,
        'delivery_fee': delivery_fee,
        'final_amount': total_amount + delivery_fee,
        'initial_data': initial_data,
    }
    return render(request, 'restaurant/checkout.html', context)

@csrf_exempt
@transaction.atomic
def create_order(request):
    if request.method == 'POST':
        try:
            session_key = request.session.session_key
            if not session_key:
                return JsonResponse({'success': False, 'error': 'Сессия не найдена'})

            cart_items = CartItem.objects.filter(session_key=session_key)
            if not cart_items.exists():
                return JsonResponse({'success': False, 'error': 'Корзина пуста'})

            data = json.loads(request.body)

            required_fields = ['customer_name', 'phone', 'delivery_address']
            for field in required_fields:
                if not data.get(field):
                    return JsonResponse({
                        'success': False,
                        'error': f'Поле "{field}" обязательно для заполнения'
                    })

            total_amount = sum(item.menu_item.price * item.quantity for item in cart_items)
            delivery_fee = 0 if total_amount >= 2000 else 200

            # СОЗДАНИЕ ЗАКАЗА С ПОЛЬЗОВАТЕЛЕМ
            order = Order.objects.create(
                customer_name=data['customer_name'],
                phone=data['phone'],
                email=data.get('email', ''),
                delivery_address=data['delivery_address'],
                apartment=data.get('apartment', ''),
                entrance=data.get('entrance', ''),
                floor=data.get('floor', ''),
                intercom=data.get('intercom', ''),
                comment=data.get('comment', ''),
                payment_method=data.get('payment_method', 'cash'),
                total_amount=total_amount,
                delivery_fee=delivery_fee,
                session_key=session_key,
                # ВАЖНО: связываем заказ с пользователем, если он авторизован
                user=request.user if request.user.is_authenticated else None,
            )

            for cart_item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    menu_item=cart_item.menu_item,
                    quantity=cart_item.quantity,
                    price=cart_item.menu_item.price,
                )

            # Очищаем корзину
            cart_items.delete()

            # Очищаем данные из сессии
            for key in ['customer_name', 'phone', 'email', 'delivery_address']:
                if key in request.session:
                    del request.session[key]

            return JsonResponse({
                'success': True,
                'order_id': order.id,
                'order_number': order.order_number,
                'redirect_url': f'/order-confirmation/{order.id}/',
            })

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'Метод не разрешен'})

def order_confirmation(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    if order.session_key != request.session.session_key:
        messages.error(request, 'Доступ к этому заказу запрещен')
        return redirect('home')

    context = {
        'order': order,
        'order_items': order.items.all(),
    }
    return render(request, 'restaurant/order_confirmation.html', context)


def get_cart_data(request):
    session_key = request.session.session_key
    if not session_key:
        return JsonResponse({
            'count': 0,
            'total_amount': 0,
            'delivery_fee': 200,
            'final_amount': 200,
            'items': []
        })

    cart_items = CartItem.objects.filter(session_key=session_key)
    items_data = []
    total_amount = 0

    for item in cart_items:
        item_total = item.menu_item.price * item.quantity
        total_amount += item_total
        items_data.append({
            'id': item.id,
            'name': item.menu_item.name,
            'price': float(item.menu_item.price),
            'quantity': item.quantity,
            'total': float(item_total),
            'image_url': item.menu_item.image.url if item.menu_item.image else None,
        })

    delivery_fee = 0 if total_amount >= 2000 else 200

    return JsonResponse({
        'count': cart_items.count(),
        'total_amount': float(total_amount),
        'delivery_fee': float(delivery_fee),
        'final_amount': float(total_amount + delivery_fee),
        'items': items_data,
    })
def about(request):
    return render(request, 'restaurant/about.html')

def contact(request):
    return render(request, 'restaurant/contact.html')
