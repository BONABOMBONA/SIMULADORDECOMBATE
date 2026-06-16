"""
generador.py
Simulacion masiva de combates. Genera el dataset que alimenta al ML y a Spark.
"""

import random
import csv
from simulador.combate import combatir


def simular_muchos(personajes, n_combates=2000, semilla=None):
    if len(personajes) < 2:
        raise ValueError("Se necesitan al menos 2 personajes para simular.")
    if semilla is not None:
        random.seed(semilla)
    registros = []
    for _ in range(n_combates):
        a, b = random.sample(personajes, 2)
        resultado = combatir(a, b)
        gano_a = 1 if resultado["ganador"] == a.nombre else 0
        registros.append({
            "nombre_a": a.nombre, "hp_a": a.hp_max, "ataque_a": a.ataque,
            "defensa_a": a.defensa, "velocidad_a": a.velocidad,
            "nombre_b": b.nombre, "hp_b": b.hp_max, "ataque_b": b.ataque,
            "defensa_b": b.defensa, "velocidad_b": b.velocidad,
            "gano_a": gano_a, "turnos": resultado["turnos"],
            "dano_a": resultado["dano_total"][a.nombre],
            "dano_b": resultado["dano_total"][b.nombre],
        })
    return registros


def guardar_csv(registros, ruta="salidas/combates.csv"):
    if not registros:
        print("No hay registros que guardar.")
        return
    columnas = list(registros[0].keys())
    with open(ruta, "w", newline="", encoding="utf-8") as f:
        escritor = csv.DictWriter(f, fieldnames=columnas)
        escritor.writeheader()
        escritor.writerows(registros)
    print(f"Guardados {len(registros)} combates en {ruta}")
