"""
spark_sql_mllib.py  -  Tema 3.3.3 Uso de SparkSQL y SparkMLlib

SparkSQL: consultas tipo SQL sobre el dataset de combates.
SparkMLlib: entrena un clasificador del ganador con MLlib (para comparar
con el de scikit-learn).
"""

from pyspark.sql import SparkSession
from pyspark.ml.feature import VectorAssembler
from pyspark.ml.classification import LogisticRegression
from pyspark.ml.evaluation import MulticlassClassificationEvaluator


def crear_spark(nombre="SimuladorCombateSQL"):
    spark = (SparkSession.builder
             .appName(nombre)
             .master("local[*]")
             .config("spark.ui.showConsoleProgress", "false")
             .getOrCreate())
    spark.sparkContext.setLogLevel("ERROR")
    return spark


def consultas_sql(ruta_csv="salidas/combates.csv", spark=None):
    """
    3.3.3 SparkSQL: carga el CSV como DataFrame y corre consultas SQL.
    Devuelve un diccionario con los resultados.
    """
    propia = False
    if spark is None:
        spark = crear_spark()
        propia = True

    df = spark.read.csv(ruta_csv, header=True, inferSchema=True)
    df.createOrReplaceTempView("combates")

    # Consulta 1: promedio de turnos
    prom = spark.sql("SELECT AVG(turnos) AS promedio_turnos FROM combates").collect()[0][0]

    # Consulta 2: top 5 personajes A con mas victorias
    top = spark.sql("""
        SELECT nombre_a AS personaje, COUNT(*) AS victorias
        FROM combates
        WHERE gano_a = 1
        GROUP BY nombre_a
        ORDER BY victorias DESC
        LIMIT 5
    """).collect()

    print(f"[SparkSQL] Promedio de turnos: {prom:.2f}")
    print("[SparkSQL] Top 5 ganadores (como A):")
    for fila in top:
        print(f"   {fila['personaje']}: {fila['victorias']}")

    resultado = {"promedio_turnos": prom,
                 "top_ganadores": [(f["personaje"], f["victorias"]) for f in top]}

    if propia:
        spark.stop()
    return resultado


def clasificar_con_mllib(ruta_csv="salidas/combates.csv", spark=None):
    """
    3.3.3 SparkMLlib: entrena una regresion logistica para predecir el ganador
    y devuelve la precision (accuracy).
    """
    propia = False
    if spark is None:
        spark = crear_spark()
        propia = True

    df = spark.read.csv(ruta_csv, header=True, inferSchema=True)

    caracteristicas = ["hp_a", "ataque_a", "defensa_a", "velocidad_a",
                       "hp_b", "ataque_b", "defensa_b", "velocidad_b"]

    # Armar el vector de caracteristicas (formato que pide MLlib)
    ensamblador = VectorAssembler(inputCols=caracteristicas, outputCol="features")
    datos = ensamblador.transform(df).select("features", df["gano_a"].alias("label"))

    entrenamiento, prueba = datos.randomSplit([0.8, 0.2], seed=42)

    modelo = LogisticRegression(maxIter=50)
    modelo_entrenado = modelo.fit(entrenamiento)

    predicciones = modelo_entrenado.transform(prueba)
    evaluador = MulticlassClassificationEvaluator(
        labelCol="label", predictionCol="prediction", metricName="accuracy")
    precision = evaluador.evaluate(predicciones)

    print(f"[SparkMLlib] Precision del modelo (regresion logistica): {precision:.1%}")

    if propia:
        spark.stop()
    return precision
