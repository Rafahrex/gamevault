from django.db import models
from django.contrib.auth.models import User


class Thread(models.Model):
    game = models.ForeignKey('tienda.Game', on_delete=models.CASCADE, related_name='threads')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='threads')
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class Comment(models.Model):
    thread = models.ForeignKey(Thread, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f'Comment by {self.user.username} on {self.thread.title}'

    @property
    def score(self):
        """Puntaje del comentario: upvotes menos downvotes."""
        return self.votes.filter(vote_type='upvote').count() - self.votes.filter(vote_type='downvote').count()


class Vote(models.Model):
    VOTE_CHOICES = [
        ('upvote', 'Upvote'),
        ('downvote', 'Downvote'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='votes')
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='votes')
    vote_type = models.CharField(max_length=10, choices=VOTE_CHOICES)

    class Meta:
        unique_together = ('user', 'comment')

    def __str__(self):
        return f'{self.user.username} {self.vote_type} on comment #{self.comment.id}'


class Notification(models.Model):
    """Modelo nuevo (migración 0002). Las notificaciones NO se crean en las
    vistas: las genera el paradigma orientado a eventos (foro/signals.py)."""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, null=True, blank=True, related_name='notifications')
    message = models.CharField(max_length=255)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Notification for {self.user.username}: {self.message}'
