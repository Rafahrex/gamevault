from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar = models.URLField(max_length=500, blank=True)
    bio = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Profile of {self.user.username}'

    def library_size(self):
        """Return the number of games acquired by the profile owner."""
        return self.user.game_library.count()

    def achievement_points(self):
        """Calculate the points earned through the user's achievements."""
        return sum(
            item.achievement.points
            for item in self.user.achievements.select_related('achievement')
        )


class GameLibrary(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='game_library')
    game = models.ForeignKey('tienda.Game', on_delete=models.CASCADE)
    acquired_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Game Libraries'
        unique_together = ('user', 'game')

    def __str__(self):
        return f'{self.user.username} - {self.game.title}'


class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wishlist')
    game = models.ForeignKey('tienda.Game', on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'game')

    def __str__(self):
        return f'{self.user.username} wants {self.game.title}'

    @classmethod
    def toggle(cls, user, game):
        """Add or remove a game and return True when it was added."""
        item, created = cls.objects.get_or_create(user=user, game=game)
        if not created:
            item.delete()
        return created


class Achievement(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    icon = models.URLField(max_length=500, blank=True)
    points = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name_plural = 'Achievements'

    def __str__(self):
        return self.name

    def award_to(self, user):
        """Award this achievement once and return the assignment created."""
        return UserAchievement.objects.get_or_create(user=user, achievement=self)


class UserAchievement(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='achievements')
    achievement = models.ForeignKey(Achievement, on_delete=models.CASCADE)
    earned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'achievement')

    def __str__(self):
        return f'{self.user.username} earned {self.achievement.name}'


class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    game = models.ForeignKey('tienda.Game', on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveSmallIntegerField()
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'game')

    def __str__(self):
        return f'{self.user.username} rated {self.game.title}: {self.rating}/10'
