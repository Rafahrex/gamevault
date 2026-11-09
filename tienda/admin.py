from django.contrib import admin
from .models import Game, Genre, Order, OrderItem

# Register your models here.

@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ('title', 'genre', 'price', 'stock', 'rating')
    list_filter = ('genre', 'release_date')
    search_fields = ('title', 'description')
    list_editable = ('price', 'stock')


admin.site.register(Genre)
admin.site.register(Order)
admin.site.register(OrderItem)
