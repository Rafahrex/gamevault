"""Paradigma ORIENTADO A EVENTOS del foro.

Aquí viven los receptores (listeners). Las vistas y modelos SOLO publican
eventos; nadie llama a Notification.objects.create() fuera de este archivo.
"""

from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver, Signal

from .models import Comment, Notification, Thread

# Señal personalizada: se envía cuando un usuario vota un comentario.
comment_voted = Signal()


@receiver(post_save, sender=Comment)
def notify_thread_author_on_new_comment(sender, instance, created, **kwargs):
    """EVENTO post_save: al crear un comentario se notifica al autor del hilo.

    No se ignora en modo bulk: la acción crea la notificación como reacción
    al evento publicado por el ORM al guardar el comentario.
    """
    if created and instance.user_id != instance.thread.user_id:
        Notification.objects.create(
            user=instance.thread.user,
            comment=instance,
            message=f'{instance.user.username} comentó en tu hilo '
                    f'"{instance.thread.title}".',
        )


@receiver(pre_delete, sender=Comment)
def clean_up_comment_notifications(sender, instance, **kwargs):
    """EVENTO pre_delete: al borrar un comentario se eliminan sus
    notificaciones para no dejar referencias huérfanas."""
    Notification.objects.filter(comment=instance).delete()


@receiver(pre_delete, sender=Thread)
def clean_up_thread_notifications(sender, instance, **kwargs):
    """EVENTO pre_delete: al borrar un hilo se limpian las notificaciones
    de todos sus comentarios."""
    Notification.objects.filter(comment__thread=instance).delete()


@receiver(comment_voted)
def notify_comment_author_on_upvote(sender, comment, user, **kwargs):
    """EVENTO personalizado comment_voted: un upvote a un comentario
    notifica a su autor. La vista publica el evento; este receptor reacciona.
    """
    if comment.user_id != user.id:
        Notification.objects.create(
            user=comment.user,
            comment=comment,
            message=f'{user.username} dio un voto positivo a tu comentario.',
        )
