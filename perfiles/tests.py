from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from tienda.models import Game, Genre

from .models import Achievement, GameLibrary, Review, UserProfile, Wishlist


class ProfileFeaturesTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="player", password="safe-pass-123")
        self.genre = Genre.objects.create(name="RPG")
        self.game = Game.objects.create(
            title="Test Quest",
            description="A test game",
            genre=self.genre,
            price="19.99",
            stock=5,
        )

    def test_public_profile_is_visible_and_profile_is_created(self):
        response = self.client.get(reverse("perfiles:profile", args=[self.user.username]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.user.username)
        self.assertTrue(UserProfile.objects.filter(user=self.user).exists())

    def test_private_sections_require_login(self):
        response = self.client.get(reverse("perfiles:library"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response.url)

    def test_library_lists_acquired_games(self):
        GameLibrary.objects.create(user=self.user, game=self.game)
        self.client.force_login(self.user)
        response = self.client.get(reverse("perfiles:library"))
        self.assertContains(response, self.game.title)

    def test_wishlist_toggle_adds_and_removes_game(self):
        self.client.force_login(self.user)
        url = reverse("perfiles:toggle_wishlist", args=[self.game.id])
        self.client.post(url)
        self.assertTrue(Wishlist.objects.filter(user=self.user, game=self.game).exists())
        self.client.post(url)
        self.assertFalse(Wishlist.objects.filter(user=self.user, game=self.game).exists())

    def test_wishlist_toggle_rejects_get(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("perfiles:toggle_wishlist", args=[self.game.id]))
        self.assertEqual(response.status_code, 405)

    def test_profile_domain_methods_calculate_library_and_points(self):
        profile = UserProfile.objects.create(user=self.user)
        GameLibrary.objects.create(user=self.user, game=self.game)
        achievement = Achievement.objects.create(name="Primer paso", points=25)
        assignment, created = achievement.award_to(self.user)
        duplicate, created_again = achievement.award_to(self.user)
        self.assertTrue(created)
        self.assertFalse(created_again)
        self.assertEqual(assignment, duplicate)
        self.assertEqual(profile.library_size(), 1)
        self.assertEqual(profile.achievement_points(), 25)

    def test_review_is_created_and_updated_without_duplicates(self):
        self.client.force_login(self.user)
        url = reverse("perfiles:review_game", args=[self.game.id])
        self.client.post(url, {"rating": 8, "comment": "Muy bueno"})
        self.client.post(url, {"rating": 9, "comment": "Excelente"})
        self.assertEqual(Review.objects.filter(user=self.user, game=self.game).count(), 1)
        self.assertEqual(Review.objects.get(user=self.user, game=self.game).rating, 9)

    def test_review_rating_must_be_between_one_and_ten(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("perfiles:review_game", args=[self.game.id]),
            {"rating": 11, "comment": "Inválida"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Review.objects.exists())
        self.assertContains(response, "entre 1 y 10")
