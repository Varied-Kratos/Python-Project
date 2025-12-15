from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Case, When, IntegerField
import json
from .models import Category, MenuItem, CartItem


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