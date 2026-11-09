from decimal import Decimal

from types import SimpleNamespace

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from tienda.models import Game, Genre

from .models import UserPreference
from .pipeline import (
    available_games,
    build_pipeline,
    order_by_score,
    score_game,
    take_top_n,
)


class PipelineUnitTests(TestCase):
    """Verifica el paradigma funcional: pureza y composición."""

    def test_score_game_is_pure(self):
        """Mismo input => mismo output (pureza)."""
        game = SimpleNamespace(pk=1, genre_id=7, rating=8, price=10)
        first = score_game(game, [7], None, set())
        second = score_game(game, [7], None, set())
        self.assertEqual(first, second)

    def test_order_and_top_n(self):
        """sorted() ordena y slicing selecciona top-N sin mutar la entrada."""
        scored = [
            (SimpleNamespace(pk=1), 0.5),
            (SimpleNamespace(pk=2), 0.9),
            (SimpleNamespace(pk=3), 0.7),
        ]
        original = list(scored)
        ordered = order_by_score(scored)
        self.assertEqual([pair[0].pk for pair in ordered], [2, 3, 1])
        self.assertEqual(scored, original, 'la entrada no debe mutarse')
        self.assertEqual(len(take_top_n(ordered, 2)), 2)

    def test_pipeline_filters_only_available_games(self):
        """El pipeline combina ORM declarativo (stock, género) y map/sorted."""
        genre = Genre.objects.create(name='RPG')
        game_in_stock = Game.objects.create(
            title='Disponible', genre=genre, price=10, rating=9, stock=5
        )
        Game.objects.create(title='Agotado', genre=genre, price=10, rating=9, stock=0)
        pipeline = build_pipeline([genre.id], None, set(), 5)
        result = pipeline(available_games())
        result_ids = [game.pk for game, _score in result]
        self.assertIn(game_in_stock.pk, result_ids)
        self.assertEqual(len(result), 1, 'debe excluir juegos sin stock')

    def test_pipeline_order_matches_score(self):
        """El top-N debe venir ordenado por puntaje descendente."""
        genre = Genre.objects.create(name='Acción')
        low = Game.objects.create(
            title='Bajo', genre=genre, price=10, rating=5, stock=5
        )
        high = Game.objects.create(
            title='Alto', genre=genre, price=10, rating=9, stock=5
        )
        pipeline = build_pipeline([genre.id], None, set(), 5)
        result = pipeline(available_games())
        ordered_pks = [game.pk for game, _score in result]
        self.assertEqual(ordered_pks, [high.pk, low.pk])


class RecomendacionesApiTests(TestCase):
    """Verifica el endpoint REST y la página de recomendaciones."""

    def test_api_returns_only_favorite_genres(self):
        genre = Genre.objects.create(name='Carreras')
        other_genre = Genre.objects.create(name='Puzzle')
        Game.objects.create(
            title='Juego Favorito', genre=genre, price=5, rating=7, stock=3
        )
        Game.objects.create(
            title='Otro Género', genre=other_genre, price=5, rating=9, stock=3
        )
        user = User.objects.create_user('api', password='x')
        pref = UserPreference.objects.create(user=user)
        pref.favorite_genres.add(genre)

        self.client.force_login(user)
        response = self.client.get(reverse('recomendaciones:recomendaciones_api'))
        self.assertEqual(response.status_code, 200)
        titles = [item['title'] for item in response.data]
        self.assertIn('Juego Favorito', titles)
        self.assertNotIn('Otro Género', titles)

    def test_api_requires_authentication(self):
        response = self.client.get(reverse('recomendaciones:recomendaciones_api'))
        self.assertEqual(response.status_code, 403)

    def test_recomendaciones_page_renders(self):
        user = User.objects.create_user('page', password='x')
        self.client.force_login(user)
        response = self.client.get(reverse('recomendaciones:recomendaciones_page'))
        self.assertEqual(response.status_code, 200)


class PreferenciasTests(TestCase):
    """UX (feedback): el usuario personaliza sus gustos desde el cliente."""

    def test_pagina_muestra_formulario_a_usuario_autenticado(self):
        user = User.objects.create_user('pref', password='x')
        self.client.force_login(user)
        response = self.client.get(reverse('recomendaciones:recomendaciones_page'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Tus preferencias')
        self.assertContains(response, 'Guardar preferencias')

    def test_pagina_no_muestra_formulario_a_anonimo(self):
        response = self.client.get(reverse('recomendaciones:recomendaciones_page'))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'Guardar preferencias')

    def test_update_preferences_guarda_gustos(self):
        genre = Genre.objects.create(name='RPG')
        user = User.objects.create_user('pref2', password='x')
        self.client.force_login(user)
        response = self.client.post(
            reverse('recomendaciones:update_preferences'),
            {'favorite_genres': [genre.id], 'max_price': '59.99'},
        )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response, reverse('recomendaciones:recomendaciones_page')
        )
        pref = UserPreference.objects.get(user=user)
        self.assertEqual(list(pref.favorite_genres.all()), [genre])
        self.assertEqual(pref.max_price, Decimal('59.99'))

    def test_update_preferences_requiere_login(self):
        response = self.client.post(
            reverse('recomendaciones:update_preferences'), {}
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('login'), response.url)
