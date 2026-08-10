"""Vistas de recomendaciones.

El módulo evidencia el paradigma funcional en recomendaciones/pipeline.py
(funciones puras compuestas con reduce) y el declarativo en el ORM. Estas
vistas solo orquestan: obtienen las preferencias y ejecutan el pipeline.
También permiten al usuario personalizar sus gustos desde el cliente
(formulario PreferenceForm).
"""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Case, IntegerField, Value, When
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from .forms import PreferenceForm
from .models import UserPreference
from .pipeline import available_games, build_pipeline
from .serializers import GameRecommendationSerializer


def _build_recommendations(user):
    """Orquestador: une el ORM (I/O) con el pipeline funcional puro.

    Obtiene las preferencias del usuario y ejecuta el pipeline compuesto.
    Devuelve (lista de (juego, puntaje), dict {juego_id: puntaje}).
    """
    pref, _created = UserPreference.objects.get_or_create(user=user)
    favorite_ids = list(pref.favorite_genres.values_list('id', flat=True))
    if not favorite_ids:
        return [], {}

    wishlist_ids = set(user.wishlist.values_list('game_id', flat=True))
    pipeline = build_pipeline(favorite_ids, pref.max_price, wishlist_ids)

    # La única salida "imperativa" es la entrada declarativa del pipeline.
    scored = pipeline(available_games())
    scores = {game.pk: score for game, score in scored}
    return scored, scores


class RecomendacionesView(generics.ListAPIView):
    """Endpoint REST: GET /recomendaciones/api/

    Devuelve el top-N de juegos recomendados para el usuario autenticado.
    El orden respeta el puntaje calculado por el pipeline funcional.
    """

    serializer_class = GameRecommendationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        scored, self._scores = _build_recommendations(self.request.user)
        pks = [game.pk for game, _score in scored]
        if not pks:
            return available_games().none()
        # Preserva el orden del pipeline sin volver a puntuar en la BD.
        preserved_order = Case(
            *[When(pk=pk, then=Value(index)) for index, pk in enumerate(pks)],
            default=Value(len(pks)),
            output_field=IntegerField(),
        )
        return available_games().filter(pk__in=pks).order_by(preserved_order)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['scores'] = getattr(self, '_scores', {})
        return context


def recomendaciones_page(request):
    """Página de recomendaciones: permite personalizar gustos y ver el top-N.

    UX (feedback): el panel de preferencias del cliente se construye aquí
    con el estado actual del usuario (géneros favoritos y precio máximo).
    """
    context = {'user_authenticated': request.user.is_authenticated}
    if request.user.is_authenticated:
        pref, _created = UserPreference.objects.get_or_create(user=request.user)
        context['form'] = PreferenceForm(instance=pref)
        scored, _scores = _build_recommendations(request.user)
        context['recomendaciones'] = scored
        context['total'] = len(scored)
    return render(request, 'recomendaciones/recomendaciones.html', context)


@login_required
@require_POST
def update_preferences(request):
    """Guarda los gustos del usuario (géneros favoritos y precio máximo).

    Patrón PRG (Post/Redirect/Get): tras guardar redirige a la página para
    que el formulario nunca se reenvíe al refrescar.
    """
    pref, _created = UserPreference.objects.get_or_create(user=request.user)
    form = PreferenceForm(request.POST, instance=pref)
    if form.is_valid():
        form.save()
        messages.success(request, 'Preferencias actualizadas.')
    else:
        messages.error(request, 'No se pudieron guardar las preferencias.')
    return redirect('recomendaciones:recomendaciones_page')
