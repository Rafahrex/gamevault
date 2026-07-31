from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from tienda.models import Game, Genre

from .models import (
    Achievement,
    GameLibrary,
    Review,
    UserAchievement,
    UserProfile,
    Wishlist,
)


class ProfilesApiTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='ana',
            password='clave-segura-123',
            first_name='Ana',
        )
        self.other_user = User.objects.create_user(
            username='luis',
            password='clave-segura-456',
        )
        UserProfile.objects.create(
            user=self.user,
            avatar='https://example.com/ana.png',
            bio='Jugadora de RPG.',
        )
        UserProfile.objects.create(user=self.other_user)

        genre = Genre.objects.create(name='RPG')
        self.game = Game.objects.create(
            title='Aventura',
            description='Juego de aventura.',
            genre=genre,
            price='19.99',
            rating='8.50',
            stock=5,
            cover_image='https://example.com/aventura.png',
        )
        self.other_game = Game.objects.create(
            title='Carreras',
            description='Juego de carreras.',
            genre=genre,
            price='12.00',
            rating='7.00',
            stock=5,
        )
        GameLibrary.objects.create(user=self.user, game=self.game)
        GameLibrary.objects.create(user=self.other_user, game=self.other_game)

        achievement = Achievement.objects.create(
            name='Primer juego',
            description='Adquirió su primer juego.',
            points=10,
            icon='https://example.com/badge.png',
        )
        UserAchievement.objects.create(
            user=self.user,
            achievement=achievement,
        )

    def test_public_profile_contains_summary(self):
        response = self.client.get(
            reverse('perfiles:profile', kwargs={'username': 'ana'})
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'ana')
        self.assertEqual(response.data['games_count'], 1)
        self.assertEqual(response.data['achievements_count'], 1)
        self.assertEqual(response.data['achievement_points'], 10)

    def test_library_requires_authentication(self):
        response = self.client.get(reverse('perfiles:library'))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_library_only_returns_authenticated_users_games(self):
        self.client.force_authenticate(self.user)
        response = self.client.get(reverse('perfiles:library'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], 'Aventura')

    def test_achievements_are_public_and_include_badge_data(self):
        response = self.client.get(
            reverse('perfiles:achievements', kwargs={'username': 'ana'})
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Primer juego')
        self.assertEqual(response.data[0]['points'], 10)

    def test_unknown_profile_returns_404(self):
        response = self.client.get(
            reverse('perfiles:profile', kwargs={'username': 'desconocido'})
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_authenticated_user_can_add_and_remove_wishlist_item(self):
        self.client.force_authenticate(self.user)
        response = self.client.post(
            reverse('perfiles:wishlist'),
            {'game': self.other_game.id},
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        item = Wishlist.objects.get(user=self.user, game=self.other_game)

        response = self.client.delete(
            reverse('perfiles:wishlist-item', kwargs={'pk': item.pk})
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Wishlist.objects.filter(pk=item.pk).exists())

    def test_wishlist_does_not_expose_another_users_items(self):
        Wishlist.objects.create(user=self.other_user, game=self.game)
        self.client.force_authenticate(self.user)

        response = self.client.get(reverse('perfiles:wishlist'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])

    def test_authenticated_user_can_review_a_game(self):
        self.client.force_authenticate(self.user)
        response = self.client.post(
            reverse('perfiles:game-reviews', kwargs={'game_id': self.game.id}),
            {'game': self.game.id, 'rating': 9, 'comment': 'Excelente.'},
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            Review.objects.filter(user=self.user, game=self.game, rating=9).exists()
        )

    def test_review_rating_must_be_between_one_and_ten(self):
        self.client.force_authenticate(self.user)
        response = self.client.post(
            reverse('perfiles:game-reviews', kwargs={'game_id': self.game.id}),
            {'game': self.game.id, 'rating': 11, 'comment': 'Inválida.'},
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_cannot_edit_another_users_review(self):
        review = Review.objects.create(
            user=self.other_user,
            game=self.game,
            rating=7,
        )
        self.client.force_authenticate(self.user)

        response = self.client.patch(
            reverse('perfiles:review-detail', kwargs={'pk': review.pk}),
            {'rating': 10},
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
