"""
biblioteca.py
URLs precargadas para la opcion "Biblioteca" de la interfaz.
Cada entrada se obtiene por web scraping en vivo (no son datos hardcodeados).
"""

BIBLIOTECA = [
    {
        "nombre": "Pokemon - Primera generacion (151)",
        "url": "https://pokemondb.net/pokedex/stats/gen1",
        "tipo": "pokemon",
        "descripcion": "Los 151 Pokemon de la primera generacion con sus stats base.",
    },
    {
        "nombre": "Paises del mundo",
        "url": "https://www.scrapethissite.com/pages/simple/",
        "tipo": "paises",
        "descripcion": "Paises con poblacion y area, mapeados a stats de combate.",
    },
    {
        "nombre": "Superheroes - Superhero Database",
        "url": "https://raw.githubusercontent.com/tashapiro/superhero-comics/main/data/superheroes.csv",
        "tipo": "superheroes",
        "descripcion": "Superheroes con sus powerstats (fuerza, velocidad, etc.).",
    },
]


def listar_fuentes():
    return [entrada["nombre"] for entrada in BIBLIOTECA]


def obtener_por_nombre(nombre):
    for entrada in BIBLIOTECA:
        if entrada["nombre"] == nombre:
            return entrada
    return None


def obtener_por_tipo(tipo):
    return [e for e in BIBLIOTECA if e["tipo"] == tipo]


def obtener_urls():
    return [entrada["url"] for entrada in BIBLIOTECA]
