"""
config.py
Configuracion central del proyecto: conexion a la base de datos,
rutas de archivos y parametros generales.
"""

import os

# ==============================================================
#   CONEXION A MONGODB ATLAS
# ==============================================================
MONGO_URI = os.environ.get(
    "MONGO_URI",
    "mongodb+srv://BONABOMBONA:Dapasolo_26@cluster0.wcb2ll9.mongodb.net/?appName=Cluster0"
)

DB_NAME = "simulador_nosql"
COLECCION_PERSONAJES = "personajes"
COLECCION_COMBATES = "combates"

# ==============================================================
#   RUTAS DE ARCHIVOS DE SALIDA
# ==============================================================
CARPETA_SALIDAS = "salidas"
CARPETA_GRAFICAS = os.path.join(CARPETA_SALIDAS, "graficas")

RUTA_PERSONAJES_CSV = os.path.join(CARPETA_SALIDAS, "personajes_scrapeados.csv")
RUTA_COMBATES_CSV = os.path.join(CARPETA_SALIDAS, "combates.csv")
RUTA_INFORME = os.path.join(CARPETA_SALIDAS, "informe_final.pdf")

# ==============================================================
#   PARAMETROS DE SIMULACION Y ML
# ==============================================================
N_COMBATES_MASIVA = 3000
SEMILLA = 42
RANGO_STAT_MIN = 1
RANGO_STAT_MAX = 255

os.makedirs(CARPETA_GRAFICAS, exist_ok=True)
