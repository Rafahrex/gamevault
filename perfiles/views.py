from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Avg
from django.http import HttpResponseNotAllowed
from django.shortcuts import get_object_or_404, redirect, render

from tienda.models import Game

from .forms import ReviewForm, UserProfileForm
from .models import GameLibrary, Review, UserProfile, Wishlist


def public_profile(request, username):
    profile_user = get_object_or_404(User, username=username)
    profile, _ = UserProfile.objects.get_or_create(user=profile_user)
    context = {
        "profile_user": profile_user,
        "profile": profile,
        "library": profile_user.game_library.select_related("game").all(),
        "achievements": profile_user.achievements.select_related("achievement").all(),
        "reviews": profile_user.reviews.select_related("game").all(),
    }
    return render(request, "perfiles/profile.html", context)


@login_required
def dashboard(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    return render(
        request,
        "perfiles/dashboard.html",
        {
            "profile": profile,
            "library_count": profile.library_size(),
            "wishlist_count": request.user.wishlist.count(),
            "achievement_count": request.user.achievements.count(),
            "achievement_points": profile.achievement_points(),
        },
    )


@login_required
def edit_profile(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    form = UserProfileForm(request.POST or None, instance=profile)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Perfil actualizado correctamente.")
        return redirect("perfiles:profile", username=request.user.username)
    return render(request, "perfiles/edit_profile.html", {"form": form})


@login_required
def library(request):
    games = request.user.game_library.select_related("game", "game__genre")
    return render(request, "perfiles/library.html", {"library": games})


@login_required
def wishlist(request):
    items = request.user.wishlist.select_related("game", "game__genre")
    return render(request, "perfiles/wishlist.html", {"wishlist": items})


@login_required
def toggle_wishlist(request, game_id):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])
    game = get_object_or_404(Game, pk=game_id)
    created = Wishlist.toggle(request.user, game)
    if created:
        messages.success(request, f"{game.title} se agregó a tu wishlist.")
    else:
        messages.info(request, f"{game.title} se eliminó de tu wishlist.")
    return redirect(request.POST.get("next") or "perfiles:wishlist")


def game_detail(request, game_id):
    game = get_object_or_404(Game.objects.select_related("genre"), pk=game_id)
    reviews = game.reviews.select_related("user").all()
    user_review = None
    in_wishlist = False
    if request.user.is_authenticated:
        user_review = reviews.filter(user=request.user).first()
        in_wishlist = Wishlist.objects.filter(user=request.user, game=game).exists()
    return render(
        request,
        "perfiles/game_detail.html",
        {
            "game": game,
            "reviews": reviews,
            "average_rating": reviews.aggregate(value=Avg("rating"))["value"],
            "user_review": user_review,
            "in_wishlist": in_wishlist,
        },
    )


@login_required
def review_game(request, game_id):
    game = get_object_or_404(Game, pk=game_id)
    review = Review.objects.filter(user=request.user, game=game).first()
    form = ReviewForm(request.POST or None, instance=review)
    if request.method == "POST" and form.is_valid():
        saved_review = form.save(commit=False)
        saved_review.user = request.user
        saved_review.game = game
        saved_review.save()
        messages.success(request, "Tu reseña fue guardada.")
        return redirect("perfiles:game_detail", game_id=game.id)
    return render(request, "perfiles/review_form.html", {"form": form, "game": game})


@login_required
def delete_review(request, game_id):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])
    review = get_object_or_404(Review, user=request.user, game_id=game_id)
    review.delete()
    messages.info(request, "Tu reseña fue eliminada.")
    return redirect("perfiles:game_detail", game_id=game_id)
