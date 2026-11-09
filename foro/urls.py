from django.urls import path

from . import views

app_name = 'foro'

urlpatterns = [
    path('', views.thread_list, name='thread_list'),
    path('nuevo/', views.thread_create, name='thread_create'),
    path('notificaciones/', views.notifications, name='notifications'),
    path('hilo/<int:pk>/', views.thread_detail, name='thread_detail'),
    path('hilo/<int:pk>/eliminar/', views.delete_thread, name='delete_thread'),
    path(
        'comentario/<int:pk>/eliminar/',
        views.delete_comment,
        name='delete_comment',
    ),
    path(
        'comentario/<int:comment_id>/votar/',
        views.toggle_vote,
        name='toggle_vote',
    ),
]
