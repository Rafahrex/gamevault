"""Pipeline de recomendaciones: paradigma funcional + declarativo.

=================== PARADIGMA FUNCIONAL ===================

Cada etapa es una FUNCIÓN PURA: mismo input => mismo output, sin efectos
secundarios y sin mutar variables externas. El flujo completo se compone
con ``reduce()``: el pipeline es una sola función que encadena etapas.

  available_games()
    -> filter_by_preferences()   (declarativo, filter())
    -> score_by_affinity()       (map())
    -> order_by_score()          (sorted())
    -> take_top_n()              (slicing)

=================== PARADIGMA DECLARATIVO ===================

La única salida al almacén es el ORM de Django: los queryset expresan QUÉ se
necesita (``filter(stock__gt=0)``, ``filter(genre_id__in=...)``), no un bucle
manual que arma el resultado.
"""

from functools import partial, reduce

from tienda.models import Game

TOP_N_DEFAULT = 10


def available_games():
    """DECLARATIVO: queryset que expresa QUÉ juegos hay disponibles.

    No hay ningún bucle: la condición ``stock__gt=0`` describe el resultado
    y PostgreSQL decide cómo filtrar.
    """
    return Game.objects.filter(stock__gt=0).select_related('genre')


def filter_by_preferences(games, favorite_genre_ids, max_price):
    """PUREZA + DECLARATIVO.

    ``filter()`` construye una NUEVA consulta sin modificar la entrada y sin
    efectos secundarios; es una transformación de datos, no un bucle con
    condicionales imperativos.
    """
    qs = games.filter(genre_id__in=favorite_genre_ids)
    if max_price is not None:
        qs = qs.filter(price__lte=max_price)
    return qs


def score_game(game, favorite_genre_ids, max_price, wishlist_ids):
    """PUREZA: afinidad de UN juego calculada sin estado externo.

    Ponderaciones: 40% afinidad de género, 30% popularidad (rating),
    20% deseo (está en la wishlist del usuario), 10% ajuste de precio.
    """
    genre_affinity = 1.0 if game.genre_id in favorite_genre_ids else 0.0
    popularity = float(game.rating or 0.0) / 10.0
    desired = 1.0 if game.pk in wishlist_ids else 0.0
    price_fit = 1.0 if max_price is None or game.price <= max_price else 0.5
    return (
        game,
        0.4 * genre_affinity + 0.3 * popularity + 0.2 * desired + 0.1 * price_fit,
    )


def score_by_affinity(games, favorite_genre_ids, max_price, wishlist_ids):
    """COMPOSICIÓN + INMUTABILIDAD.

    ``map()`` aplica score_game a cada juego y devuelve una lista NUEVA; la
    entrada no se modifica.
    """
    return list(
        map(
            partial(
                score_game,
                favorite_genre_ids=favorite_genre_ids,
                max_price=max_price,
                wishlist_ids=wishlist_ids,
            ),
            games,
        )
    )


def order_by_score(scored):
    """PUREZA: ``sorted()`` devuelve una lista nueva ordenada de mayor a menor
    afinidad, sin reordenar la lista original."""
    return sorted(scored, key=lambda pair: pair[1], reverse=True)


def take_top_n(scored, n=TOP_N_DEFAULT):
    """PUREZA: selección por slicing de las n primeras posiciones."""
    return scored[:n]


def build_pipeline(favorite_genre_ids, max_price, wishlist_ids, n=TOP_N_DEFAULT):
    """COMPOSICIÓN: ``reduce()`` encadena las etapas puras en un solo flujo.

    Devuelve una función ``run(games)`` que, al invocarse, pasa la entrada
    por cada etapa en orden: filtrar -> puntuar -> ordenar -> top-N.
    """
    stages = [
        partial(
            filter_by_preferences,
            favorite_genre_ids=favorite_genre_ids,
            max_price=max_price,
        ),
        partial(
            score_by_affinity,
            favorite_genre_ids=favorite_genre_ids,
            max_price=max_price,
            wishlist_ids=wishlist_ids,
        ),
        order_by_score,
        partial(take_top_n, n=n),
    ]

    def run(games):
        return reduce(lambda acc, stage: stage(acc), stages, games)

    return run
