"""
nosql_simulacion.py
Conexion con la base de datos NoSQL (MongoDB Atlas).
Guarda personajes y combates como documentos flexibles, los lee y los
transforma en DataFrames estructurados para el analisis posterior.
"""

import pandas as pd
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError, ConnectionFailure

import config


def conectar():
    try:
        cliente = MongoClient(config.MONGO_URI, serverSelectionTimeoutMS=5000)
        cliente.admin.command("ping")
        base = cliente[config.DB_NAME]
        print(f"[OK] Conectado a MongoDB Atlas, base '{config.DB_NAME}'")
        return cliente, base
    except (ServerSelectionTimeoutError, ConnectionFailure) as e:
        print("[ERROR] No se pudo conectar a MongoDB Atlas.")
        print("  Revisa: 1) tu cadena en config.py (usuario/contrasena),")
        print("          2) que tu IP este permitida en Network Access,")
        print("          3) tu conexion a internet.")
        print(f"  Detalle: {e}")
        raise


def guardar_personajes(personajes, reemplazar=True):
    if not personajes:
        print("No hay personajes que guardar.")
        return 0
    cliente, base = conectar()
    coleccion = base[config.COLECCION_PERSONAJES]
    guardados = 0
    for p in personajes:
        if reemplazar:
            coleccion.update_one(
                {"nombre": p["nombre"], "fuente": p.get("fuente", "")},
                {"$set": p}, upsert=True)
        else:
            coleccion.insert_one(p)
        guardados += 1
    print(f"[OK] {guardados} personajes guardados en Mongo")
    cliente.close()
    return guardados


def obtener_personajes():
    cliente, base = conectar()
    coleccion = base[config.COLECCION_PERSONAJES]
    personajes = list(coleccion.find({}, {"_id": 0}))
    cliente.close()
    print(f"[OK] {len(personajes)} personajes leidos de Mongo")
    return personajes


def personajes_a_dataframe():
    personajes = obtener_personajes()
    if not personajes:
        return pd.DataFrame()
    filas = []
    for p in personajes:
        filas.append({
            "nombre": p.get("nombre", ""), "fuente": p.get("fuente", ""),
            "hp": p.get("hp", 0), "ataque": p.get("ataque", 0),
            "defensa": p.get("defensa", 0), "velocidad": p.get("velocidad", 0),
        })
    return pd.DataFrame(filas)


def guardar_combates(registros):
    if not registros:
        print("No hay combates que guardar.")
        return 0
    cliente, base = conectar()
    coleccion = base[config.COLECCION_COMBATES]
    coleccion.insert_many(registros)
    print(f"[OK] {len(registros)} combates guardados en Mongo")
    cliente.close()
    return len(registros)


def combates_a_dataframe():
    cliente, base = conectar()
    coleccion = base[config.COLECCION_COMBATES]
    combates = list(coleccion.find({}, {"_id": 0}))
    cliente.close()
    print(f"[OK] {len(combates)} combates leidos de Mongo")
    return pd.DataFrame(combates)


def contar_personajes():
    cliente, base = conectar()
    n = base[config.COLECCION_PERSONAJES].count_documents({})
    cliente.close()
    return n


def limpiar_personajes():
    cliente, base = conectar()
    res = base[config.COLECCION_PERSONAJES].delete_many({})
    cliente.close()
    print(f"[OK] {res.deleted_count} personajes borrados")
    return res.deleted_count


def limpiar_combates():
    cliente, base = conectar()
    res = base[config.COLECCION_COMBATES].delete_many({})
    cliente.close()
    print(f"[OK] {res.deleted_count} combates borrados")
    return res.deleted_count
