from django.contrib import admin
from .models import Game, Genre

# Register your models here.

admin.site.register(Game)
if 'Genre' in globals():
    admin.site.register(Genre)