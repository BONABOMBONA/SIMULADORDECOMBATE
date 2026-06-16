"""
rdd_procesamiento.py  -  Temas 3.3.1 y 3.3.2

3.3.1 Datos distribuidos resilientes (RDD): se cargan los combates como RDD.
3.3.2 Transformaciones de RDD: map, filter, reduceByKey sobre los combates.

Procesa el dataset de combates de forma distribuida con Apache Spark.
"""

from pyspark.sql import SparkSession


def crear_spark(nombre="SimuladorCombate"):
    """Crea (o reutiliza) una sesion local de Spark."""
    spark = (SparkSession.builder
             .appName(nombre)
             .master("local[*]")
             .config("spark.ui.showConsoleProgress", "false")
             .getOrCreate())
    spark.sparkContext.setLogLevel("ERROR")
    return spark


def victorias_por_personaje(ruta_csv="salidas/combates.csv", spark=None):
    """
    3.3.1 + 3.3.2: carga los combates como RDD y cuenta las victorias de
    cada personaje usando transformaciones (map, reduceByKey).
    Devuelve una lista [(personaje, victorias), ...] ordenada de mayor a menor.
    """
    propia = False
    if spark is None:
        spark = crear_spark()
        propia = True

    sc = spark.sparkContext

    # --- 3.3.1: crear el RDD a partir del CSV ---
    lineas = sc.textFile(ruta_csv)
    encabezado = lineas.first()
    datos = lineas.filter(lambda l: l != encabezado)   # 3.3.2: filter

    # Columnas: nombre_a(0) ... nombre_b(5) ... gano_a(10)
    def ganador_de_linea(linea):
        campos = linea.split(",")
        nombre_a = campos[0]
        nombre_b = campos[5]
        gano_a = campos[10]
        return nombre_a if gano_a == "1" else nombre_b

    # --- 3.3.2: map -> (ganador, 1) ; reduceByKey -> suma ---
    pares = datos.map(lambda l: (ganador_de_linea(l), 1))
    conteo = pares.reduceByKey(lambda x, y: x + y)

    resultado = conteo.collect()
    resultado.sort(key=lambda x: x[1], reverse=True)

    print("[Spark RDD] Victorias por personaje:")
    for nombre, victorias in resultado:
        print(f"   {nombre}: {victorias}")

    if propia:
        spark.stop()
    return resultado


def combates_largos(ruta_csv="salidas/combates.csv", min_turnos=5, spark=None):
    """
    3.3.2 (filter): cuenta cuantos combates duraron mas de 'min_turnos' turnos.
    """
    propia = False
    if spark is None:
        spark = crear_spark()
        propia = True

    sc = spark.sparkContext
    lineas = sc.textFile(ruta_csv)
    encabezado = lineas.first()
    datos = lineas.filter(lambda l: l != encabezado)

    # turnos es la columna 11
    largos = datos.filter(lambda l: int(l.split(",")[11]) > min_turnos)
    n = largos.count()
    print(f"[Spark RDD] Combates de mas de {min_turnos} turnos: {n}")

    if propia:
        spark.stop()
    return n
