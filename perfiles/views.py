from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework.permissions import (
    SAFE_METHODS,
    AllowAny,
    BasePermission,
    IsAuthenticated,
)

from .models import GameLibrary, Review, UserAchievement, UserProfile, Wishlist
from .serializers import (
    GameLibrarySerializer,
    PublicProfileSerializer,
    ReviewSerializer,
    UserAchievementSerializer,
    WishlistSerializer,
)


class PublicProfileView(generics.RetrieveAPIView):
    serializer_class = PublicProfileSerializer
    permission_classes = [AllowAny]
    lookup_field = 'username'

    def get_object(self):
        user = get_object_or_404(
            User.objects.prefetch_related(
                'game_library',
                'achievements__achievement',
            ),
            username=self.kwargs['username'],
            is_active=True,
        )
        UserProfile.objects.get_or_create(user=user)
        return user


class MyGameLibraryView(generics.ListAPIView):
    serializer_class = GameLibrarySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return (
            GameLibrary.objects.filter(user=self.request.user)
            .select_related('game', 'game__genre')
            .order_by('-acquired_at')
        )


class PublicAchievementsView(generics.ListAPIView):
    serializer_class = UserAchievementSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        user = get_object_or_404(
            User,
            username=self.kwargs['username'],
            is_active=True,
        )
        return (
            UserAchievement.objects.filter(user=user)
            .select_related('achievement')
            .order_by('-earned_at')
        )


class WishlistView(generics.ListCreateAPIView):
    serializer_class = WishlistSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return (
            Wishlist.objects.filter(user=self.request.user)
            .select_related('game')
            .order_by('-added_at')
        )

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class WishlistItemView(generics.DestroyAPIView):
    serializer_class = WishlistSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Wishlist.objects.filter(user=self.request.user)


class IsReviewOwnerOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, review):
        return request.method in SAFE_METHODS or review.user == request.user


class GameReviewsView(generics.ListCreateAPIView):
    serializer_class = ReviewSerializer

    def get_permissions(self):
        if self.request.method in SAFE_METHODS:
            return [AllowAny()]
        return [IsAuthenticated()]

    def get_queryset(self):
        return (
            Review.objects.filter(game_id=self.kwargs['game_id'])
            .select_related('user', 'game')
            .order_by('-created_at')
        )

    def perform_create(self, serializer):
        serializer.save(user=self.request.user, game_id=self.kwargs['game_id'])


class ReviewDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [IsReviewOwnerOrReadOnly]
    queryset = Review.objects.select_related('user', 'game')
