from urllib.parse import quote

from django.core.management.base import BaseCommand
from django.db import transaction

from tienda.models import Game, Genre


STEAM_HEADERS = {
    'The Elder Scrolls V: Skyrim': 489830,
    'The Witcher 3: Wild Hunt': 292030,
    'God of War Ragnarok': 1593500,
    'Devil May Cry 5': 601150,
    'DOOM Eternal': 782330,
    'Overwatch 2': 2357570,
    'Hollow Knight': 367520,
    'Celeste': 504230,
    'Civilization VI': 289070,
    'Stellaris': 281990,
    'Stardew Valley': 413150,
    'The Sims 4': 1222670,
    'Portal 2': 620,
    'Baba Is You': 736260,
    'NBA 2K25': 2878980,
    'FIFA 25': 2669320,
    'Sekiro: Shadows Die Twice': 814380,
    'Dark Souls: Remastered': 570940,
    'Dark Souls II: Scholar of the First Sin': 335300,
    'Dark Souls III': 374320,
    'Elden Ring': 1245620,
    'Baldur\'s Gate 3': 1086940,
    'Cyberpunk 2077': 1091500,
    'Ghost of Tsushima': 2215430,
    'Red Dead Redemption 2': 1174180,
    'Rainbow Six Siege': 359550,
    'Titanfall 2': 1237970,
    'Ori and the Blind Forest': 261550,
    'Dead Cells': 588650,
    'Total War: Warhammer III': 1142710,
    'RimWorld': 294100,
    'Factorio': 427520,
    'Assetto Corsa Competizione': 805550,
    'Football Manager 2024': 2252570,
    'Outer Wilds': 753640,
}

WIKIPEDIA_COVERS = {
    'Forza Horizon 5': 'Forza_Horizon_5_cover_art.jpg',
}


def cover_url(title):
    """URL de portada real para un juego demo (Steam/Wikipedia)."""
    if title in STEAM_HEADERS:
        return (
            'https://cdn.cloudflare.steamstatic.com/steam/apps/'
            f'{STEAM_HEADERS[title]}/header.jpg'
        )
    if title in WIKIPEDIA_COVERS:
        return (
            'https://en.wikipedia.org/wiki/Special:FilePath/'
            + WIKIPEDIA_COVERS[title]
        )
    return 'https://placehold.co/460x215/16202d/66c0f4?text=' + quote(title)

DEMO_DATA = {
    'RPG': [
        ('The Elder Scrolls V: Skyrim', 39.99, 9.5, 12,
         'Aventura de rol en un enorme mundo abierto lleno de dragones.'),
        ('The Witcher 3: Wild Hunt', 29.99, 9.7, 10,
         'Rol con una narrativa profunda y decisiones que importan.'),
        ('Dark Souls: Remastered', 39.99, 9.3, 7,
         'Rol de acción implacable con un mundo interconectado.'),
        ('Dark Souls II: Scholar of the First Sin', 39.99, 8.8, 6,
         'La maldición de las almas continúa en una tierra olvidada.'),
        ('Dark Souls III', 59.99, 9.6, 9,
         'El fuego se apaga y la saga llega a su fin épico.'),
        ('Elden Ring', 59.99, 9.8, 12,
         'El mundo abierto de FromSoftware en su máxima expresión.'),
        ('Baldur\'s Gate 3', 59.99, 9.8, 10,
         'Rol táctico de Dungeons & Dragons con libertad total.'),
        ('Cyberpunk 2077', 49.99, 9.0, 11,
         'Rol futurista en la megaciudad de Night City.'),
    ],
    'Action': [
        ('God of War Ragnarok', 59.99, 9.6, 8,
         'Acción mitológica nórdica con combate visceral.'),
        ('Devil May Cry 5', 39.99, 9.0, 6,
         'Hack and slash frenético de alta velocidad.'),
        ('Sekiro: Shadows Die Twice', 59.99, 9.5, 8,
         'Ninja shinobi en el Japón feudal con combate de katanas.'),
        ('Ghost of Tsushima', 59.99, 9.5, 9,
         'Samurái en una isla devastada por la guerra.'),
        ('Red Dead Redemption 2', 59.99, 9.7, 8,
         'El salvaje oeste con una historia inolvidable.'),
    ],
    'Shooter': [
        ('DOOM Eternal', 39.99, 9.1, 9,
         'Shooter acelerado con demonios y combos implacables.'),
        ('Overwatch 2', 19.99, 8.2, 15,
         'Shooter por equipos con héroes variados.'),
        ('Rainbow Six Siege', 19.99, 8.6, 14,
         'Asalto táctico por equipos con destrucción ambiental.'),
        ('Titanfall 2', 29.99, 9.1, 13,
         'Acción frenética entre piloto y titán.'),
    ],
    'Platform': [
        ('Hollow Knight', 14.99, 9.4, 20,
         'Metroidvania atmosférico con combate preciso.'),
        ('Celeste', 19.99, 9.2, 18,
         'Plataformas duras con una historia conmovedora.'),
        ('Ori and the Blind Forest', 19.99, 9.0, 15,
         'Aventura de plataformas con un arte impresionante.'),
        ('Dead Cells', 24.99, 8.9, 17,
         'Roguelike de acción y plataformas sin descanso.'),
    ],
    'Strategy': [
        ('Civilization VI', 49.99, 9.3, 7,
         'Construye un imperio a través de los siglos.'),
        ('Stellaris', 44.99, 9.0, 5,
         'Estrategia espacial de gran escala.'),
        ('Total War: Warhammer III', 59.99, 9.2, 6,
         'Batallas masivas de fantasía con gestión de imperio.'),
    ],
    'Simulation': [
        ('Stardew Valley', 14.99, 9.5, 25,
         'Granja, amistades y aventura en un pueblo encantador.'),
        ('The Sims 4', 39.99, 8.0, 14,
         'Simula la vida de personajes a tu manera.'),
        ('RimWorld', 34.99, 9.3, 10,
         'Gestiona una colonia en un planeta hostil.'),
        ('Factorio', 34.99, 9.6, 12,
         'Automatización y fábricas infinitas.'),
    ],
    'Racing': [
        ('Forza Horizon 5', 59.99, 9.4, 9,
         'Carreras de mundo abierto con autos espectaculares.'),
        ('Assetto Corsa Competizione', 39.99, 8.9, 9,
         'Simulación de carreras GT con física realista.'),
    ],
    'Sports': [
        ('FIFA 25', 59.99, 8.5, 11,
         'Fútbol realista con modos en línea.'),
        ('NBA 2K25', 59.99, 8.3, 10,
         'Baloncesto con simulación completa.'),
        ('Football Manager 2024', 49.99, 8.7, 8,
         'Dirige tu club de fútbol hasta la gloria.'),
    ],
    'Puzzle': [
        ('Portal 2', 19.99, 9.6, 13,
         'Puzles con portales y humor brillante.'),
        ('Baba Is You', 14.99, 9.1, 12,
         'Rompe las reglas para resolver cada nivel.'),
        ('Outer Wilds', 24.99, 9.4, 11,
         'Un misterio espacial que se reinicia cada 22 minutos.'),
    ],
}


class Command(BaseCommand):
    help = 'Siembra juegos demo (y géneros) en la base de datos.'

    @transaction.atomic
    def handle(self, *args, **options):
        created = 0
        updated = 0
        for genre_name, games in DEMO_DATA.items():
            genre, _ = Genre.objects.get_or_create(name=genre_name)
            for title, price, rating, stock, description in games:
                cover = cover_url(title)
                _game, was_created = Game.objects.get_or_create(
                    title=title,
                    defaults={
                        'genre': genre,
                        'price': price,
                        'rating': rating,
                        'stock': stock,
                        'description': description,
                        'cover_image': cover,
                    },
                )
                if was_created:
                    created += 1
                elif _game.cover_image != cover:
                    _game.cover_image = cover
                    _game.save(update_fields=['cover_image'])
                    updated += 1
        self.stdout.write(
            self.style.SUCCESS(
                f'Listo. {created} juegos creados, {updated} portadas actualizadas.'
            )
        )
