from django.urls import path

from . import views

app_name = "perfiles"

urlpatterns = [
    path("dashboard/", views.dashboard, name="dashboard"),
    path("editar/", views.edit_profile, name="edit_profile"),
    path("biblioteca/", views.library, name="library"),
    path("wishlist/", views.wishlist, name="wishlist"),
    path("wishlist/<int:game_id>/toggle/", views.toggle_wishlist, name="toggle_wishlist"),
    path("juegos/<int:game_id>/", views.game_detail, name="game_detail"),
    path("juegos/<int:game_id>/resena/", views.review_game, name="review_game"),
    path("juegos/<int:game_id>/resena/eliminar/", views.delete_review, name="delete_review"),
    path("<str:username>/", views.public_profile, name="profile"),
]
