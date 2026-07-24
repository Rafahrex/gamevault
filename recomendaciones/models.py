from django.db import models
from django.contrib.auth.models import User


class UserPreference(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='preferences')
    favorite_genres = models.ManyToManyField('tienda.Genre', blank=True)
    max_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Preferences of {self.user.username}'
