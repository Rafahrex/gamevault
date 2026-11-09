"""Vistas del foro.

La app foro se apoya en el paradigma orientado a eventos: la creación de un
comentario o un voto aquí abajo termina en cuanto el ORM publica el evento
post_save (o la señal personalizada comment_voted); las notificaciones se
generan por separado en foro/signals.py, sin que estas vistas llamen nunca a
Notification.objects.create().
"""

from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from tienda.models import Game

from .models import Comment, Thread, Vote
from .signals import comment_voted


def _unread_notifications(request):
    """Contador de notificaciones no leídas para el menú del foro."""
    if request.user.is_authenticated:
        return request.user.notifications.filter(is_read=False).count()
    return 0


def thread_list(request):
    """Hilos de discusión, opcionalmente filtrados por juego."""
    games = Game.objects.order_by('title')
    game_id = request.GET.get('game')
    threads = Thread.objects.select_related('game', 'user').annotate(
        comment_count=Count('comments')
    ).order_by('-created_at')
    if game_id:
        threads = threads.filter(game_id=game_id)

    paginator = Paginator(threads, 10)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, 'foro/thread_list.html', {
        'page_obj': page_obj,
        'games': games,
        'current_game': int(game_id) if game_id else None,
        'unread': _unread_notifications(request),
    })


def thread_detail(request, pk):
    """Detalle de un hilo: crea comentarios (respuestas anidadas) y lista los
    comentarios raíz con paginación."""
    thread = get_object_or_404(
        Thread.objects.select_related('game', 'user'), pk=pk
    )

    if request.method == 'POST':
        if not request.user.is_authenticated:
            messages.warning(request, 'Debes iniciar sesión para comentar.')
            return redirect('login')
        content = request.POST.get('content', '').strip()
        parent_id = request.POST.get('parent_id')
        parent = None
        if parent_id:
            parent = get_object_or_404(Comment, pk=parent_id, thread=thread)
        if content:
            Comment.objects.create(
                thread=thread, user=request.user, content=content, parent=parent
            )
            messages.success(request, 'Comentario publicado.')
        else:
            messages.error(request, 'El comentario no puede estar vacío.')
        return redirect('foro:thread_detail', pk=thread.pk)

    root_comments = thread.comments.filter(parent__isnull=True)
    paginator = Paginator(root_comments, 10)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, 'foro/thread_detail.html', {
        'thread': thread,
        'page_obj': page_obj,
        'unread': _unread_notifications(request),
    })


def thread_create(request):
    """Crea un hilo de discusión asociado a un juego."""
    if request.method == 'POST':
        if not request.user.is_authenticated:
            messages.warning(request, 'Debes iniciar sesión para crear un hilo.')
            return redirect('foro:thread_list')
        game = None
        game_id = request.POST.get('game')
        title = request.POST.get('title', '').strip()
        content = request.POST.get('content', '').strip()
        if game_id:
            game = get_object_or_404(Game, pk=game_id)
        if game and title and content:
            Thread.objects.create(
                game=game, user=request.user, title=title, content=content
            )
            messages.success(request, 'Hilo creado.')
            return redirect('foro:thread_list')
        messages.error(request, 'Completa todos los campos.')

    games = Game.objects.order_by('title')
    return render(request, 'foro/thread_form.html', {'games': games})


@require_POST
def toggle_vote(request, comment_id):
    """Registra o actualiza un voto (upvote/downvote) sobre un comentario.

    Al guardar un upvote se envía la señal personalizada comment_voted: es el
    EVENTO que notifica al autor del comentario. La vista solo publica el
    evento; no conoce a Notification.
    """
    comment = get_object_or_404(Comment, pk=comment_id)
    if not request.user.is_authenticated:
        messages.warning(request, 'Debes iniciar sesión para votar.')
        return redirect('foro:thread_detail', pk=comment.thread_id)
    if comment.user == request.user:
        messages.error(request, 'No puedes votar tu propio comentario.')
        return redirect('foro:thread_detail', pk=comment.thread_id)

    vote_type = request.POST.get('vote_type')
    if vote_type not in ('upvote', 'downvote'):
        messages.error(request, 'Voto inválido.')
        return redirect('foro:thread_detail', pk=comment.thread_id)

    vote, created = Vote.objects.get_or_create(
        user=request.user, comment=comment, defaults={'vote_type': vote_type}
    )
    if created:
        messages.success(request, 'Voto registrado.')
        if vote_type == 'upvote':
            comment_voted.send(
                sender=Comment, comment=comment, user=request.user
            )
    elif vote.vote_type == vote_type:
        vote.delete()
        messages.info(request, 'Voto retirado.')
    else:
        vote.vote_type = vote_type
        vote.save(update_fields=['vote_type'])
        messages.success(request, 'Voto actualizado.')
        if vote_type == 'upvote':
            comment_voted.send(
                sender=Comment, comment=comment, user=request.user
            )
    return redirect('foro:thread_detail', pk=comment.thread_id)


@require_POST
def delete_comment(request, pk):
    """Elimina un comentario (su autor, el creador del hilo o staff)."""
    comment = get_object_or_404(Comment, pk=pk)
    thread = comment.thread
    if not request.user.is_authenticated:
        messages.warning(request, 'Debes iniciar sesión.')
    elif (
        request.user != comment.user
        and request.user != thread.user
        and not request.user.is_staff
    ):
        messages.error(request, 'No tienes permiso para eliminar este comentario.')
    else:
        comment.delete()
        messages.success(request, 'Comentario eliminado.')
    return redirect('foro:thread_detail', pk=thread.pk)


@require_POST
def delete_thread(request, pk):
    """Elimina un hilo (solo su autor o staff)."""
    thread = get_object_or_404(Thread, pk=pk)
    if not request.user.is_authenticated:
        messages.warning(request, 'Debes iniciar sesión.')
    elif request.user != thread.user and not request.user.is_staff:
        messages.error(request, 'No tienes permiso para eliminar este hilo.')
    else:
        thread.delete()
        messages.success(request, 'Hilo eliminado.')
    return redirect('foro:thread_list')


def notifications(request):
    """Lista las notificaciones del usuario y las marca como leídas."""
    if not request.user.is_authenticated:
        return redirect('login')
    user_notifications = request.user.notifications.select_related(
        'comment__thread'
    )
    user_notifications.filter(is_read=False).update(is_read=True)
    return render(request, 'foro/notifications.html', {
        'notifications': user_notifications,
        'unread': 0,
    })
