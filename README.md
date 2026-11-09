# GameVault

> [Versión en español](README.es.md)

A Steam-style video game web platform built with Django (MTV) and server-rendered
Django templates. Academic project for the **SC-250 Programming Paradigms** course
at Universidad Fidélitas: each module demonstrates a different programming paradigm
with working code.

**Stack:** Python, Django 6, Django REST Framework, PostgreSQL

## Modules and paradigms

| Module | Features | Paradigm |
|---|---|---|
| `tienda` (store) | Catalog, search by genre, cart, checkout, purchase history, authentication (login/register/logout) | Classic MVC/MTV |
| `perfiles` (profiles) | Dashboard, game library, wishlist, reviews, achievements, public profile | Object-oriented |
| `foro` (forum) | Threads per game, nested comments with pagination, votes, automatic notifications | **Event-driven** (Django Signals) |
| `recomendaciones` (recommendations) | Personalized recommendation pipeline + user-editable preferences | **Functional + declarative (ORM)** |

## Requirements

- Python 3.10+
- PostgreSQL 18+
- pip

## Setup (Windows / PowerShell)

```powershell
git clone https://github.com/Rafahrex/gamevault.git
cd gamevault

# 1. Virtual environment
python -m venv venv
venv\Scripts\activate

# 2. Dependencies
pip install -r requirements.txt

# 3. PostgreSQL database
psql -U postgres -c "CREATE DATABASE gamevault;"

# 4. Local configuration: copy .env.example to .env and fill in your values
#    (DJANGO_SECRET_KEY, DB_PASSWORD, ...). .env is never committed.
copy .env.example .env

# 5. Migrations
python manage.py migrate

# 6. Demo data (optional, recommended): 18 games across 9 genres
python manage.py seed_demo_data

# 7. Superuser (optional)
python manage.py createsuperuser

# 8. Development server
python manage.py runserver
```

> **Automatic setup:** you can also run `.\setup.ps1`. It creates `.env`, the
> virtual environment, installs dependencies, creates the database if needed and
> runs the migrations.

## Configuration

All secrets and machine-specific settings are read from environment variables
(loaded from `.env` with `python-dotenv`). See `.env.example`:

| Variable | Purpose |
|---|---|
| `DJANGO_DEBUG` | `True` for local development; defaults to `False` |
| `DJANGO_SECRET_KEY` | Required when `DJANGO_DEBUG` is off |
| `DJANGO_ALLOWED_HOSTS` | Comma-separated host list |
| `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT` | PostgreSQL connection |

## Main routes

| Route | Description |
|---|---|
| `/` | Store catalog |
| `/cart/`, `/checkout/`, `/historial/` | Cart, checkout and purchase history |
| `/login/`, `/register/`, `/logout/` | Authentication |
| `/perfiles/` | User dashboard |
| `/perfiles/biblioteca/`, `/perfiles/wishlist/` | Library and wishlist |
| `/perfiles/<username>/` | Public profile |
| `/foro/` | Thread list (filterable by game) |
| `/foro/hilo/<id>/` | Thread with nested comments and votes |
| `/foro/nuevo/`, `/foro/notificaciones/` | New thread and notifications |
| `/recomendaciones/` | Recommendations and preference editing |
| `/recomendaciones/preferencias/` | Saves favorite genres and max price (POST) |
| `/recomendaciones/api/` | REST endpoint (DRF) |

### REST endpoint

`GET /recomendaciones/api/` requires authentication. It returns the top-N
recommended games as JSON with their `affinity_score`, sorted by affinity.

## How each paradigm is implemented

- **Forum (event-driven):** `foro/signals.py` centralizes the `post_save`
  receiver (notify a thread's author when someone comments), `pre_delete`
  receivers (clean up notifications when content is deleted) and the custom
  `comment_voted` signal. Models emit events that other components handle
  without being coupled to them.
- **Recommendations (functional):** `recomendaciones/pipeline.py` is a pipeline
  of pure functions: `filter_by_preferences()` with `filter()`,
  `score_by_affinity()` with `map()`, `order_by_score()` with `sorted()` and
  `take_top_n()` with slicing, composed with `reduce()`. Queries use the ORM
  declaratively.

## Tests

```powershell
python manage.py test --settings=gamevault_config.test_settings
```

`test_settings` uses SQLite, so no PostgreSQL server is needed. The 29 tests
cover the forum signals, end-to-end views, the purity and ordering of the
recommendation pipeline, the REST endpoint and the preferences flow.

## Known limitations

- **Anonymous cart:** adding a game to the cart without logging in raises
  `IntegrityError: NOT NULL constraint failed: tienda_cart.user_id`
  (`tienda/views.py`). The flow assumes one cart per authenticated user, so log
  in before using the cart.

## Team

Academic team project. Initial architecture, data models, forum and
recommendations modules by [Rafael Brenes](https://github.com/Rafahrex);
store and profiles modules by the other team members.
