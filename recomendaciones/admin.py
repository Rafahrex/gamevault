from django.contrib import admin

from .models import UserPreference


@admin.register(UserPreference)
class UserPreferenceAdmin(admin.ModelAdmin):
    list_display = ('user', 'max_price', 'updated_at')
    filter_horizontal = ('favorite_genres',)
