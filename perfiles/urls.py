from django.urls import path

from .views import (
    GameReviewsView,
    MyGameLibraryView,
    PublicAchievementsView,
    PublicProfileView,
    ReviewDetailView,
    WishlistItemView,
    WishlistView,
)


app_name = 'perfiles'

urlpatterns = [
    path('perfiles/<str:username>/', PublicProfileView.as_view(), name='profile'),
    path(
        'perfiles/<str:username>/logros/',
        PublicAchievementsView.as_view(),
        name='achievements',
    ),
    path('biblioteca/', MyGameLibraryView.as_view(), name='library'),
    path('wishlist/', WishlistView.as_view(), name='wishlist'),
    path(
        'wishlist/<int:pk>/',
        WishlistItemView.as_view(),
        name='wishlist-item',
    ),
    path(
        'juegos/<int:game_id>/resenas/',
        GameReviewsView.as_view(),
        name='game-reviews',
    ),
    path('resenas/<int:pk>/', ReviewDetailView.as_view(), name='review-detail'),
]
