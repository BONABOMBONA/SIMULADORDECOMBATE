"""
analisis_completo.py
Corre TODO el pipeline de analisis y genera el informe final en PDF.

Este script es util para DEMOSTRAR el machine learning y Spark (que en la
GUI quedan ocultos). Lee los personajes de Mongo, corre la simulacion
masiva, entrena los modelos, procesa con Spark, genera las graficas y
arma el informe.

Uso:
    python3 analisis_completo.py
"""

import pandas as pd

import config
from simulador.personaje import Personaje
from simulador.generador import simular_muchos, guardar_csv
from ml import clasificacion, regresion, clustering
from visualizacion import graficas
from reporte import generador_reporte


def obtener_personajes():
    """Lee personajes de Mongo; si no hay conexion, usa unos de ejemplo."""
    try:
        from datos import nosql_simulacion as db
        personajes = db.obtener_personajes()
        if personajes:
            print(f"[OK] {len(personajes)} personajes leidos de Mongo")
            return [Personaje.from_dict(p) for p in personajes]
    except Exception as e:
        print(f"[AVISO] No se pudo leer de Mongo: {e}")

    print("[AVISO] Usando personajes de ejemplo.")
    return [
        Personaje("Pikachu", 80, 130, 60, 200, "pokemon"),
        Personaje("Charizard", 130, 180, 130, 167, "pokemon"),
        Personaje("Mexico", 200, 150, 40, 30, "paises"),
        Personaje("China", 255, 255, 170, 10, "paises"),
        Personaje("Batman", 100, 110, 130, 90, "superheroes"),
        Personaje("Hulk", 220, 230, 180, 80, "superheroes"),
    ]


def main():
    print("=" * 55)
    print("  ANALISIS COMPLETO DEL SIMULADOR DE COMBATE")
    print("=" * 55)

    # 1. Personajes
    personajes = obtener_personajes()
    fuentes = ", ".join(sorted(set(p.fuente for p in personajes)))

    # 2. Simulacion masiva
    print("\n[1] Simulacion masiva de combates...")
    registros = simular_muchos(personajes, n_combates=config.N_COMBATES_MASIVA,
                               semilla=config.SEMILLA)
    df = pd.DataFrame(registros)
    guardar_csv(registros, config.RUTA_COMBATES_CSV)

    # 3. Machine Learning
    print("\n[2] Machine Learning (scikit-learn)...")
    modelo_clf, precision, matriz, _ = clasificacion.entrenar(df)
    modelo_reg, mae, r2, _ = regresion.entrenar(df)
    df_pers = pd.DataFrame([p.to_dict() for p in personajes])
    df_grupos, _, _ = clustering.agrupar(df_pers, n_grupos=3)
    resumen = clustering.resumen_grupos(df_grupos)

    # 4. Spark
    print("\n[3] Procesamiento distribuido (Apache Spark)...")
    spark_sql = {}
    precision_mllib = "N/D"
    try:
        from spark import rdd_procesamiento, spark_sql_mllib
        spark = spark_sql_mllib.crear_spark()
        victorias_spark = rdd_procesamiento.victorias_por_personaje(
            config.RUTA_COMBATES_CSV, spark=spark)
        spark_sql = spark_sql_mllib.consultas_sql(config.RUTA_COMBATES_CSV, spark=spark)
        precision_mllib = f"{spark_sql_mllib.clasificar_con_mllib(config.RUTA_COMBATES_CSV, spark=spark):.1%}"
        spark.stop()
    except Exception as e:
        print(f"[AVISO] Spark no disponible: {e}")
        from collections import Counter
        c = Counter()
        for _, row in df.iterrows():
            c[row["nombre_a"] if row["gano_a"] == 1 else row["nombre_b"]] += 1
        victorias_spark = sorted(c.items(), key=lambda x: -x[1])

    # 5. Graficas
    print("\n[4] Generando graficas...")
    g1 = graficas.grafica_victorias(victorias_spark)
    g2 = graficas.grafica_clusters(df_grupos)
    g3 = graficas.matriz_confusion(matriz)

    # 6. Informe
    print("\n[5] Generando informe PDF...")
    datos = {
        "n_personajes": len(personajes), "fuentes": fuentes,
        "n_combates": len(df), "precision_clf": f"{precision:.1%}",
        "mae_reg": f"{mae:.2f}", "r2_reg": f"{r2:.2f}",
        "resumen_grupos": resumen.to_string(),
        "spark_sql": spark_sql, "precision_mllib": precision_mllib,
        "graficas": [g1, g2, g3],
    }
    generador_reporte.generar_informe(datos, config.RUTA_INFORME)

    print("\n" + "=" * 55)
    print(f"  LISTO. Informe en: {config.RUTA_INFORME}")
    print("=" * 55)


if __name__ == "__main__":
    main()
