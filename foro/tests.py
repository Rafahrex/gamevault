from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from tienda.models import Game, Genre

from .models import Comment, Notification, Thread
from .signals import comment_voted


class SignalTests(TestCase):
    """Paradigma orientado a eventos: los receptores reaccionan a los eventos
    del ORM (post_save/pre_delete) y a la señal personalizada comment_voted."""

    def setUp(self):
        self.author = User.objects.create_user('author', password='x')
        self.other = User.objects.create_user('other', password='x')
        genre = Genre.objects.create(name='RPG')
        self.game = Game.objects.create(
            title='Juego', genre=genre, price=10, rating=8, stock=5
        )
        self.thread = Thread.objects.create(
            game=self.game, user=self.author, title='Título', content='Contenido'
        )

    def test_new_comment_notifies_thread_author(self):
        Comment.objects.create(thread=self.thread, user=self.other, content='Hola')
        notification = Notification.objects.get(user=self.author)
        self.assertIn('other', notification.message)
        self.assertFalse(notification.is_read)

    def test_author_comment_does_not_notify_itself(self):
        Comment.objects.create(thread=self.thread, user=self.author, content='Mío')
        self.assertFalse(Notification.objects.filter(user=self.author).exists())

    def test_comment_voted_signal_notifies_comment_author(self):
        comment = Comment.objects.create(
            thread=self.thread, user=self.other, content='Hola'
        )
        comment_voted.send(sender=Comment, comment=comment, user=self.author)
        self.assertTrue(
            Notification.objects.filter(user=self.other).exists()
        )

    def test_upvote_to_own_comment_is_ignored(self):
        comment = Comment.objects.create(
            thread=self.thread, user=self.author, content='Mío'
        )
        comment_voted.send(sender=Comment, comment=comment, user=self.author)
        self.assertFalse(
            Notification.objects.filter(user=self.author).exists()
        )

    def test_delete_comment_cleans_notifications(self):
        comment = Comment.objects.create(
            thread=self.thread, user=self.other, content='Hola'
        )
        comment_id = comment.pk
        self.assertTrue(
            Notification.objects.filter(comment_id=comment_id).exists()
        )
        comment.delete()
        self.assertFalse(
            Notification.objects.filter(comment_id=comment_id).exists()
        )


class ForoViewTests(TestCase):
    """Verifica las vistas del foro end-to-end (eventos + UI)."""

    def setUp(self):
        self.user = User.objects.create_user('user', password='x')
        self.other = User.objects.create_user('other', password='x')
        genre = Genre.objects.create(name='Acción')
        self.game = Game.objects.create(
            title='Juego', genre=genre, price=10, rating=8, stock=5
        )
        self.thread = Thread.objects.create(
            game=self.game, user=self.user, title='Título', content='Contenido'
        )
        self.client.force_login(self.user)

    def test_thread_list_renders(self):
        response = self.client.get(reverse('foro:thread_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.thread.title)

    def test_thread_detail_shows_comments(self):
        Comment.objects.create(
            thread=self.thread, user=self.other, content='Comentario'
        )
        response = self.client.get(
            reverse('foro:thread_detail', args=[self.thread.pk])
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Comentario')

    def test_create_comment_dispatches_event(self):
        self.client.post(
            reverse('foro:thread_detail', args=[self.thread.pk]),
            {'content': 'Nuevo'},
        )
        self.assertTrue(
            Comment.objects.filter(
                thread=self.thread, content='Nuevo'
            ).exists()
        )

    def test_vote_updates_score_and_emits_event(self):
        comment = Comment.objects.create(
            thread=self.thread, user=self.other, content='Comentario'
        )
        self.client.post(
            reverse('foro:toggle_vote', args=[comment.pk]),
            {'vote_type': 'upvote'},
        )
        self.assertEqual(comment.score, 1)
        self.assertTrue(
            Notification.objects.filter(user=self.other).exists()
        )

    def test_notifications_page_marks_as_read(self):
        Comment.objects.create(
            thread=self.thread, user=self.other, content='Comentario'
        )
        notification = Notification.objects.get(user=self.user)
        response = self.client.get(reverse('foro:notifications'))
        self.assertEqual(response.status_code, 200)
        notification.refresh_from_db()
        self.assertTrue(notification.is_read)
