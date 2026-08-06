from django.contrib import admin
from .models import Achievement, GameLibrary, Review, UserAchievement, UserProfile, Wishlist


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "created_at")
    search_fields = ("user__username", "bio")


@admin.register(GameLibrary)
class GameLibraryAdmin(admin.ModelAdmin):
    list_display = ("user", "game", "acquired_at")
    search_fields = ("user__username", "game__title")
    list_filter = ("acquired_at",)


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ("user", "game", "added_at")
    search_fields = ("user__username", "game__title")


@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    list_display = ("name", "points")
    search_fields = ("name",)


@admin.register(UserAchievement)
class UserAchievementAdmin(admin.ModelAdmin):
    list_display = ("user", "achievement", "earned_at")
    search_fields = ("user__username", "achievement__name")


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("user", "game", "rating", "updated_at")
    list_filter = ("rating",)
    search_fields = ("user__username", "game__title", "comment")
