"""
procesamiento_no_estructurado.py
Convierte TEXTO LIBRE en datos estructurados con los stats del combate.
Tercera via de ingesta. Cumple el requisito de no-estructurado -> tabular.
"""

import re
import csv
from datetime import datetime

SINONIMOS = {
    "hp":        ["hp", "vida", "salud", "puntos de vida", "resistencia", "poder"],
    "ataque":    ["ataque", "fuerza", "dano", "golpe"],
    "defensa":   ["defensa", "armadura", "proteccion", "blindaje"],
    "velocidad": ["velocidad", "rapidez", "agilidad", "veloz"],
}


def _buscar_stat(texto, palabras_clave):
    for palabra in palabras_clave:
        m = re.search(palabra + r"\D{0,12}(\d+)", texto, re.IGNORECASE)
        if m:
            return int(m.group(1))
        m = re.search(r"(\d+)\D{0,12}" + palabra, texto, re.IGNORECASE)
        if m:
            return int(m.group(1))
    return None


def _buscar_nombre(texto):
    for patron in [r"llamad[oa]\s+([A-ZA-Z][\w]+)",
                   r"se llama\s+([A-ZA-Z][\w]+)",
                   r"nombre\s*:?\s*([A-ZA-Z][\w]+)"]:
        m = re.search(patron, texto)
        if m:
            return m.group(1)
    m = re.search(r"\b([A-Z][\w]{2,})\b", texto)
    if m:
        return m.group(1)
    return "Personaje"


def extraer_stats(texto):
    stats = {}
    for stat, palabras in SINONIMOS.items():
        valor = _buscar_stat(texto, palabras)
        if valor is not None:
            stats[stat] = valor
    return stats


def procesar_texto(texto, nombre=None):
    stats = extraer_stats(texto)
    if nombre is None:
        nombre = _buscar_nombre(texto)
    return {"nombre": nombre, "tipo": "texto", "stats_crudos": stats,
            "fuente_url": "texto_libre",
            "fecha_extraccion": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "texto_original": texto.strip()}


def texto_a_personaje_dict(texto, nombre=None, valor_defecto=50):
    registro = procesar_texto(texto, nombre)
    s = registro["stats_crudos"]
    def limpiar(v):
        v = int(v)
        return max(1, min(255, v))
    return {"nombre": registro["nombre"], "fuente": "texto_libre",
            "hp": limpiar(s.get("hp", valor_defecto)),
            "ataque": limpiar(s.get("ataque", valor_defecto)),
            "defensa": limpiar(s.get("defensa", valor_defecto)),
            "velocidad": limpiar(s.get("velocidad", valor_defecto)),
            "extra": {"texto_original": registro["texto_original"]}}


def guardar_csv(registros, ruta="salidas/personajes_texto.csv"):
    if not registros:
        print("No hay registros que guardar.")
        return
    columnas = ["nombre", "tipo", "hp", "ataque", "defensa", "velocidad",
                "fuente_url", "fecha_extraccion"]
    with open(ruta, "w", newline="", encoding="utf-8") as f:
        escritor = csv.DictWriter(f, fieldnames=columnas, extrasaction="ignore")
        escritor.writeheader()
        for r in registros:
            fila = {"nombre": r["nombre"], "tipo": r["tipo"],
                    "fuente_url": r.get("fuente_url", ""),
                    "fecha_extraccion": r.get("fecha_extraccion", "")}
            fila.update(r["stats_crudos"])
            escritor.writerow(fila)
    print(f"Guardados {len(registros)} registros en {ruta}")
