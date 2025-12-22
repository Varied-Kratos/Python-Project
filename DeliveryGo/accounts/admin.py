from django.contrib import admin
from .models import UserProfile

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone', 'birth_date']
    list_filter = ['user__is_active']
    search_fields = ['user__username', 'phone', 'address']