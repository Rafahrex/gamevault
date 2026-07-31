# Evidencia del paradigma orientado a objetos

## Objetivo

GameVault utiliza programación orientada a objetos mediante los modelos, los
serializadores y las vistas basadas en clases de Django y Django REST Framework.

## Clases y responsabilidades

- `UserProfile`: encapsula la información pública adicional de un usuario.
- `GameLibrary`: representa la adquisición de un juego por un usuario.
- `Achievement` y `UserAchievement`: modelan badges y su asignación.
- `Wishlist`: representa la relación entre un usuario y un juego deseado.
- `Review`: encapsula una calificación y un comentario sobre un juego.
- `GameAdmin`: configura la gestión administrativa de juegos.

Cada clase tiene una responsabilidad concreta y conserva sus datos mediante el
ORM de Django.

## Abstracción

Los modelos convierten conceptos del dominio (perfil, juego, biblioteca, logro,
wishlist y reseña) en clases. El resto de la aplicación trabaja con estos
objetos sin manipular directamente las tablas de PostgreSQL.

Ejemplo:

```python
class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    game = models.ForeignKey('tienda.Game', on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField()
    comment = models.TextField(blank=True)
```

## Encapsulamiento

Las reglas de cada recurso están contenidas en su clase o serializer:

- `ReviewSerializer` valida calificaciones entre 1 y 10.
- `WishlistSerializer` evita agregar dos veces el mismo juego.
- `PublicProfileSerializer` decide cuáles datos personales son públicos.
- Las vistas filtran biblioteca y wishlist por `request.user`.

## Herencia

Las clases reutilizan comportamiento de Django:

```python
class Game(models.Model):
    ...

class WishlistView(generics.ListCreateAPIView):
    ...

class GameAdmin(admin.ModelAdmin):
    ...
```

`models.Model`, `ListCreateAPIView` y `ModelAdmin` son clases base. GameVault
hereda sus operaciones y agrega comportamiento específico.

## Polimorfismo

Las vistas sobrescriben métodos heredados como `get_queryset`,
`get_permissions` y `perform_create`. Django REST Framework llama a los mismos
métodos en distintas vistas, pero cada clase responde según su recurso.

## Relaciones entre objetos

- Un `User` tiene un `UserProfile`.
- Un `User` puede tener muchos elementos en `GameLibrary`.
- Un `User` puede tener muchos `Achievement` mediante `UserAchievement`.
- Un `User` puede guardar muchos juegos mediante `Wishlist`.
- Un `User` puede crear una `Review` por juego.

Estas asociaciones se implementan con `OneToOneField` y `ForeignKey`.

## Evidencia verificable

Las pruebas en `perfiles/tests.py` verifican:

- privacidad de la biblioteca y la wishlist;
- consulta pública del perfil y los logros;
- creación y eliminación de wishlist;
- creación y validación de reseñas;
- protección contra la edición de reseñas ajenas.

Para ejecutarlas:

```powershell
python manage.py test perfiles --settings=gamevault_config.test_settings
```
