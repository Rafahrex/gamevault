# GameVault

Plataforma web de videojuegos con tienda, biblioteca personal, foro comunitario y recomendaciones personalizadas.

## Requisitos

- Python 3.10+
- PostgreSQL 18+
- pip

## Instalación

1. Clonar el repositorio:

```bash
git clone <repo-url>
cd gamevault
```

2. Crear y activar el entorno virtual:

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

3. Instalar dependencias:

```bash
pip install -r requirements.txt
```

4. Crear la base de datos en PostgreSQL:

```bash
psql -U postgres -c "CREATE DATABASE gamevault;"
```

5. Ejecutar migraciones:

```bash
python manage.py migrate
```

6. Crear superusuario (opcional):

```bash
python manage.py createsuperuser
```

7. Iniciar el servidor:

```bash
python manage.py runserver
```