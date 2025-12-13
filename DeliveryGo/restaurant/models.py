from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    icon = models.CharField(max_length=50, default="🍕")
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order']
        verbose_name_plural = "Категории"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            from django.utils.text import slugify
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class MenuItem(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='items')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    weight = models.CharField(max_length=50, blank=True, null=True)
    calories = models.IntegerField(blank=True, null=True)
    is_spicy = models.BooleanField(default=False)
    is_vegetarian = models.BooleanField(default=False)
    is_bestseller = models.BooleanField(default=False)
    is_available = models.BooleanField(default=True)
    image_url = models.URLField(max_length=500, blank=True, null=True)

    class Meta:
        ordering = ['category', 'name']
        verbose_name_plural = "Блюда"

    def __str__(self):
        return f"{self.name} - {self.price}₽"


class CartItem(models.Model):
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)
    session_key = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"{self.menu_item.name} x{self.quantity}"
