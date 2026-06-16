"""
web_scraping.py
Extrae personajes de paginas web (ingesta de datos no estructurados).
Maneja pokemon, paises, superheroes y un parser generico de respaldo.
Conserva fuente_url y fecha_extraccion (trazabilidad).
"""

import csv
from datetime import datetime

import requests
from bs4 import BeautifulSoup

CABECERAS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/120.0 Safari/537.36"
}


def scrapear(url, tipo=None, timeout=20):
    try:
        respuesta = requests.get(url, headers=CABECERAS, timeout=timeout)
        respuesta.raise_for_status()
    except requests.RequestException as e:
        print(f"[ERROR] No se pudo acceder a {url}: {e}")
        return []

    # Superheroes viene de un CSV, no de HTML
    if tipo == "superheroes":
        registros = _parsear_superheroes_csv(respuesta.text)
    else:
        soup = BeautifulSoup(respuesta.text, "html.parser")
        if tipo == "pokemon":
            registros = _parsear_pokemon(soup)
        elif tipo == "paises":
            registros = _parsear_paises(soup)
        else:
            registros = _parsear_generico(soup)

    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    for r in registros:
        r["fuente_url"] = url
        r["fecha_extraccion"] = fecha

    print(f"[OK] {len(registros)} personajes extraidos de {url}")
    return registros


def _parsear_pokemon(soup):
    registros = []
    tabla = soup.find("table", id="pokedex") or soup.find("table")
    if not tabla:
        return registros
    cuerpo = tabla.find("tbody")
    filas = cuerpo.find_all("tr") if cuerpo else tabla.find_all("tr")[1:]
    for fila in filas:
        celdas = fila.find_all("td")
        if len(celdas) < 10:
            continue
        nombre_tag = fila.find("a", class_="ent-name")
        nombre = nombre_tag.get_text(strip=True) if nombre_tag else celdas[1].get_text(strip=True)
        try:
            hp = int(celdas[4].get_text(strip=True))
            ataque = int(celdas[5].get_text(strip=True))
            defensa = int(celdas[6].get_text(strip=True))
            velocidad = int(celdas[9].get_text(strip=True))
        except (ValueError, IndexError):
            continue
        registros.append({"nombre": nombre, "tipo": "pokemon",
                          "stats_crudos": {"hp": hp, "ataque": ataque,
                                           "defensa": defensa, "velocidad": velocidad}})
    return registros


def _parsear_paises(soup):
    registros = []
    paises = soup.find_all("div", class_="country")
    for pais in paises:
        nombre_tag = pais.find("h3")
        nombre = nombre_tag.get_text(strip=True) if nombre_tag else "Pais"
        pob_tag = pais.find("span", class_="country-population")
        area_tag = pais.find("span", class_="country-area")
        try:
            poblacion = float(pob_tag.get_text(strip=True))
            area = float(area_tag.get_text(strip=True))
        except (ValueError, AttributeError):
            continue
        registros.append({"nombre": nombre, "tipo": "paises",
                          "stats_crudos": {"poblacion": poblacion, "area": area}})
    return registros


def _parsear_superheroes_csv(texto_csv):
    """
    Lee superheroes desde un CSV (columnas: name, intelligence, strength,
    speed, durability, power, combat). Salta los que tengan datos faltantes.
    """
    import csv as _csv
    import io as _io
    registros = []
    lector = _csv.DictReader(_io.StringIO(texto_csv))
    columnas = ["intelligence", "strength", "speed", "durability", "power", "combat"]
    vistos = set()
    for fila in lector:
        nombre = (fila.get("name") or "").strip()
        if not nombre or nombre in vistos:
            continue
        stats = {}
        valido = True
        for col in columnas:
            valor = (fila.get(col) or "").strip()
            try:
                stats[col] = int(float(valor))
            except (ValueError, TypeError):
                valido = False
                break
        if valido and stats:
            vistos.add(nombre)
            registros.append({"nombre": nombre, "tipo": "superheroes",
                              "stats_crudos": stats})
    return registros


def _parsear_generico(soup):
    registros = []
    tabla = soup.find("table")
    if not tabla:
        return registros
    filas = tabla.find_all("tr")
    if len(filas) < 2:
        return registros
    encabezados = [c.get_text(strip=True).lower() for c in filas[0].find_all(["th", "td"])]
    for fila in filas[1:]:
        celdas = fila.find_all("td")
        if not celdas:
            continue
        nombre = celdas[0].get_text(strip=True)
        if not nombre:
            continue
        stats = {}
        for i, celda in enumerate(celdas[1:], start=1):
            texto = celda.get_text(strip=True).replace(",", "")
            try:
                valor = float(texto)
            except ValueError:
                continue
            clave = encabezados[i] if i < len(encabezados) else f"col{i}"
            stats[clave] = valor
        if stats:
            registros.append({"nombre": nombre, "tipo": "generico",
                              "stats_crudos": stats})
    return registros


def guardar_csv(registros, ruta="salidas/personajes_scrapeados.csv"):
    if not registros:
        print("No hay personajes que guardar.")
        return
    todas_stats = set()
    for r in registros:
        todas_stats.update(r["stats_crudos"].keys())
    todas_stats = sorted(todas_stats)
    columnas = ["nombre", "tipo"] + todas_stats + ["fuente_url", "fecha_extraccion"]
    with open(ruta, "w", newline="", encoding="utf-8") as f:
        escritor = csv.DictWriter(f, fieldnames=columnas)
        escritor.writeheader()
        for r in registros:
            fila = {"nombre": r["nombre"], "tipo": r["tipo"],
                    "fuente_url": r.get("fuente_url", ""),
                    "fecha_extraccion": r.get("fecha_extraccion", "")}
            fila.update(r["stats_crudos"])
            escritor.writerow(fila)
    print(f"Guardados {len(registros)} personajes en {ruta}")
