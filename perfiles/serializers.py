from django.contrib.auth.models import User
from rest_framework import serializers

from tienda.models import Game

from .models import GameLibrary, Review, UserAchievement, Wishlist


class PublicProfileSerializer(serializers.ModelSerializer):
    avatar = serializers.CharField(source='profile.avatar', read_only=True, default='')
    bio = serializers.CharField(source='profile.bio', read_only=True, default='')
    member_since = serializers.DateTimeField(
        source='profile.created_at', read_only=True, default=None
    )
    games_count = serializers.IntegerField(source='game_library.count', read_only=True)
    achievements_count = serializers.IntegerField(
        source='achievements.count', read_only=True
    )
    achievement_points = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'username',
            'first_name',
            'last_name',
            'avatar',
            'bio',
            'member_since',
            'games_count',
            'achievements_count',
            'achievement_points',
        )

    def get_achievement_points(self, user):
        return sum(
            item.achievement.points
            for item in user.achievements.select_related('achievement')
        )


class GameLibrarySerializer(serializers.ModelSerializer):
    game_id = serializers.IntegerField(source='game.id', read_only=True)
    title = serializers.CharField(source='game.title', read_only=True)
    description = serializers.CharField(source='game.description', read_only=True)
    genre = serializers.CharField(source='game.genre.name', read_only=True)
    price = serializers.DecimalField(
        source='game.price', max_digits=10, decimal_places=2, read_only=True
    )
    rating = serializers.DecimalField(
        source='game.rating', max_digits=3, decimal_places=2, read_only=True
    )
    cover_image = serializers.URLField(source='game.cover_image', read_only=True)

    class Meta:
        model = GameLibrary
        fields = (
            'id',
            'game_id',
            'title',
            'description',
            'genre',
            'price',
            'rating',
            'cover_image',
            'acquired_at',
        )


class UserAchievementSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='achievement.name', read_only=True)
    description = serializers.CharField(
        source='achievement.description', read_only=True
    )
    icon = serializers.URLField(source='achievement.icon', read_only=True)
    points = serializers.IntegerField(source='achievement.points', read_only=True)

    class Meta:
        model = UserAchievement
        fields = ('id', 'name', 'description', 'icon', 'points', 'earned_at')


class WishlistSerializer(serializers.ModelSerializer):
    game = serializers.PrimaryKeyRelatedField(queryset=Game.objects.all())
    title = serializers.CharField(source='game.title', read_only=True)
    cover_image = serializers.URLField(source='game.cover_image', read_only=True)
    price = serializers.DecimalField(
        source='game.price', max_digits=10, decimal_places=2, read_only=True
    )

    class Meta:
        model = Wishlist
        fields = ('id', 'game', 'title', 'cover_image', 'price', 'added_at')
        validators = []

    def validate_game(self, game):
        request = self.context['request']
        if Wishlist.objects.filter(user=request.user, game=game).exists():
            raise serializers.ValidationError('El juego ya está en tu wishlist.')
        return game


class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source='user.username', read_only=True)
    game = serializers.PrimaryKeyRelatedField(read_only=True)
    game_title = serializers.CharField(source='game.title', read_only=True)

    class Meta:
        model = Review
        fields = (
            'id',
            'user',
            'game',
            'game_title',
            'rating',
            'comment',
            'created_at',
            'updated_at',
        )
        validators = []

    def validate_rating(self, value):
        if not 1 <= value <= 10:
            raise serializers.ValidationError('La calificación debe estar entre 1 y 10.')
        return value

    def validate(self, attrs):
        request = self.context['request']
        game_id = (
            self.instance.game_id
            if self.instance
            else self.context['view'].kwargs.get('game_id')
        )
        duplicate = Review.objects.filter(user=request.user, game_id=game_id)
        if self.instance:
            duplicate = duplicate.exclude(pk=self.instance.pk)
        if duplicate.exists():
            raise serializers.ValidationError(
                'Ya publicaste una reseña para este juego.'
            )
        return attrs
