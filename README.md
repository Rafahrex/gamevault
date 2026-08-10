# GameVault

Plataforma web de videojuegos tipo Steam construida con Django (MTV) y plantillas
Django del lado del servidor. Proyecto académico del curso **SC-250 Paradigmas de
Programación**: cada módulo evidencia un paradigma distinto con código real.

## Módulos y paradigmas

| Módulo | Funcionalidad | Paradigma evidenciado |
|---|---|---|
| `tienda` | Catálogo, búsqueda por género, carrito, checkout, historial de transacciones, autenticación (login/register/logout) | MVC/MTV clásico |
| `perfiles` | Dashboard, biblioteca, wishlist, reseñas, logros, perfil público | Orientado a objetos |
| `foro` | Hilos por juego, comentarios anidados con paginación, votos, notificaciones automáticas | **Orientado a eventos** (Django Signals) |
| `recomendaciones` | Pipeline de recomendaciones personalizadas + edición de preferencias desde el cliente | **Funcional + declarativo (ORM)** |

## Requisitos

- Python 3.10+ (desarrollado con Python 3.14)
- PostgreSQL 18+
- pip

## Instalación (Windows / PowerShell)

```powershell
git clone <repo-url>
cd gamevault

# 1. Entorno virtual
python -m venv venv
venv\Scripts\activate

# 2. Dependencias
pip install -r requirements.txt

# 3. Base de datos en PostgreSQL (el proyecto usa la BD "gamevault")
psql -U postgres -c "CREATE DATABASE gamevault;"

# 4. Credenciales: ajusta gamevault_config/settings.py -> DATABASES
#    (actualmente: NAME=gamevault, USER=postgres, PASSWORD=rafa20111,
#     HOST=localhost, PORT=5432)

# 5. Migraciones (incluye las de foro y recomendaciones)
python manage.py migrate

# 6. Datos demo (opcional pero recomendado): 18 juegos en 9 géneros
python manage.py seed_demo_data

# 7. Superusuario (opcional)
python manage.py createsuperuser

# 8. Servidor de desarrollo
python manage.py runserver
```

> **Setup automático:** también puedes ejecutar `.\setup.ps1`, que crea el venv,
> instala las dependencias, crea la base de datos si no existe y corre las
> migraciones.

## Rutas principales

| Ruta | Descripción |
|---|---|
| `/` | Catálogo de la tienda |
| `/cart/`, `/checkout/`, `/historial/` | Carrito, compra y historial |
| `/login/`, `/register/`, `/logout/` | Autenticación |
| `/perfiles/` | Dashboard del usuario |
| `/perfiles/biblioteca/`, `/perfiles/wishlist/` | Biblioteca y wishlist |
| `/perfiles/<username>/` | Perfil público |
| `/foro/` | Lista de hilos (filtrables por juego) |
| `/foro/hilo/<id>/` | Hilo con comentarios anidados y votos |
| `/foro/nuevo/`, `/foro/notificaciones/` | Crear hilo y notificaciones |
| `/recomendaciones/` | Recomendaciones y edición de preferencias del usuario |
| `/recomendaciones/preferencias/` | Guarda géneros favoritos y precio máximo (POST) |
| `/recomendaciones/api/` | Endpoint REST (DRF) |

### Endpoint REST

`GET /recomendaciones/api/` — requiere autenticación. Devuelve el top-N de
juegos recomendados en JSON con su `affinity_score`, ordenados por afinidad.

## Experiencia de usuario (preferencias)

En `/recomendaciones/` cada usuario autenticado puede **personalizar sus gustos**
desde el cliente: marcar sus géneros favoritos y definir un precio máximo. El
formulario (`recomendaciones/forms.py`) guarda esos datos y el pipeline funcional
recalcula las recomendaciones al instante.

## Cómo se evidencian los paradigmas

- **Foro (eventos):** `foro/signals.py` centraliza `post_save` (notificar al
  autor del hilo al crear un comentario), `pre_delete` (limpiar notificaciones
  al eliminar contenido) y la señal personalizada `comment_voted`. Los modelos
  emiten eventos que otros componentes escuchan sin acoplarse. Cada receptor
  tiene un comentario explicando qué evento dispara y por qué es EDA.
- **Recomendaciones (funcional):** `recomendaciones/pipeline.py` es un pipeline
  de funciones puras — `filter_by_preferences()` con `filter()`,
  `score_by_affinity()` con `map()`, `order_by_score()` con `sorted()`,
  `take_top_n()` con slicing — compuesto con `reduce()`. Las consultas usan el
  ORM de forma declarativa (`queryset.filter(...)` expresa QUÉ se necesita).

## Tests

```powershell
python manage.py test
```

Los tests crean una base temporal y verifican señales del foro, vistas
end-to-end, pureza/orden del pipeline, el endpoint REST y el flujo de
preferencias desde el cliente (29 tests).

## Limitaciones conocidas

- **Carrito de visitantes anónimos:** agregar un juego al carrito sin iniciar
  sesión lanza `IntegrityError: NOT NULL constraint failed: tienda_cart.user_id`
  (`tienda/views.py`). El flujo asume un carrito por usuario autenticado; por
  ahora se debe iniciar sesión antes de usar el carrito.
