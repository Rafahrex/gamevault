def unread_notifications(request):
    """Context processor: expone a todas las plantillas el contador de
    notificaciones sin leer, para el icono de campana de la navegación.

    Para visitantes no autenticados devuelve 0: la campana se muestra igual
    y, al hacer clic, la vista de notificaciones redirige al login.
    """
    if request.user.is_authenticated:
        count = request.user.notifications.filter(is_read=False).count()
    else:
        count = 0
    return {'unread_notifications': count}
