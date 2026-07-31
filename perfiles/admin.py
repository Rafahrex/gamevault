from django.contrib import admin

from .models import Achievement, GameLibrary, UserAchievement, UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at')
    search_fields = ('user__username', 'user__email')


@admin.register(GameLibrary)
class GameLibraryAdmin(admin.ModelAdmin):
    list_display = ('user', 'game', 'acquired_at')
    list_filter = ('acquired_at',)
    search_fields = ('user__username', 'game__title')


@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    list_display = ('name', 'points')
    search_fields = ('name',)


@admin.register(UserAchievement)
class UserAchievementAdmin(admin.ModelAdmin):
    list_display = ('user', 'achievement', 'earned_at')
    search_fields = ('user__username', 'achievement__name')
