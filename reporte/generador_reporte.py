"""
generador_reporte.py
Genera el informe final del pipeline en PDF.

El informe documenta todo el proceso: cuantos personajes se ingirieron,
los resultados de los modelos de ML, el procesamiento con Spark y las
graficas generadas. Es el entregable donde la maestra ve todo el analisis
(aunque en la pantalla del juego el ML quede invisible).

Usa matplotlib (PdfPages) para no depender de librerias extra.
"""

import os
from datetime import datetime

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages


def _pagina_texto(pdf, titulo, lineas):
    """Crea una pagina de PDF con texto."""
    fig = plt.figure(figsize=(8.5, 11))
    fig.text(0.5, 0.93, titulo, ha="center", fontsize=18, weight="bold")
    y = 0.86
    for linea in lineas:
        fig.text(0.1, y, linea, fontsize=11, va="top")
        y -= 0.035
    plt.axis("off")
    pdf.savefig(fig)
    plt.close(fig)


def _pagina_imagen(pdf, titulo, ruta_img):
    """Crea una pagina de PDF con una imagen (grafica)."""
    if not os.path.exists(ruta_img):
        return
    fig = plt.figure(figsize=(8.5, 11))
    fig.text(0.5, 0.95, titulo, ha="center", fontsize=15, weight="bold")
    img = plt.imread(ruta_img)
    ax = fig.add_axes([0.1, 0.25, 0.8, 0.6])
    ax.imshow(img)
    ax.axis("off")
    pdf.savefig(fig)
    plt.close(fig)


def generar_informe(datos, ruta="salidas/informe_final.pdf"):
    """
    Genera el informe en PDF.

    'datos' es un diccionario con la informacion a documentar:
      n_personajes, fuentes, n_combates, precision_clf, mae_reg, r2_reg,
      resumen_grupos (texto), victorias (lista), spark_sql (dict),
      precision_mllib, graficas (lista de rutas PNG)
    """
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M")

    with PdfPages(ruta) as pdf:
        # --- Portada ---
        _pagina_texto(pdf, "Simulador de Combate", [
            "Informe del pipeline de ciencia de datos",
            "",
            f"Fecha de generacion: {fecha}",
            "",
            "Este informe documenta el proceso completo: ingesta de datos por",
            "web scraping, normalizacion, base de datos NoSQL, simulacion de",
            "combates, modelos de machine learning y procesamiento distribuido",
            "con Apache Spark.",
        ])

        # --- Resumen de datos ---
        _pagina_texto(pdf, "1. Datos del pipeline", [
            f"Personajes en la base: {datos.get('n_personajes', 'N/D')}",
            f"Fuentes de datos: {datos.get('fuentes', 'N/D')}",
            f"Combates simulados: {datos.get('n_combates', 'N/D')}",
            "",
            "Los personajes provienen de distintas fuentes web y fueron",
            "normalizados a una escala comun (1-255) con Min-Max para que",
            "puedan enfrentarse de forma justa.",
        ])

        # --- Resultados ML ---
        _pagina_texto(pdf, "2. Machine Learning (scikit-learn)", [
            "3.1.1 Clasificacion (predecir el ganador):",
            f"    Precision del modelo: {datos.get('precision_clf', 'N/D')}",
            "",
            "3.1.2 Regresion (predecir turnos del combate):",
            f"    Error medio: {datos.get('mae_reg', 'N/D')} turnos",
            f"    R2: {datos.get('r2_reg', 'N/D')}",
            "",
            "3.2.1 Analisis de grupos (KMeans):",
        ] + [f"    {l}" for l in str(datos.get('resumen_grupos', '')).split("\n")])

        # --- Resultados Spark ---
        sql = datos.get("spark_sql", {})
        top = sql.get("top_ganadores", []) if isinstance(sql, dict) else []
        _pagina_texto(pdf, "3. Procesamiento distribuido (Apache Spark)", [
            "3.3.1 y 3.3.2 RDD y transformaciones:",
            "    Se cargaron los combates como RDD y se contaron las",
            "    victorias por personaje con map/filter/reduceByKey.",
            "",
            "3.3.3 SparkSQL y SparkMLlib:",
            f"    Promedio de turnos (SQL): {sql.get('promedio_turnos', 'N/D') if isinstance(sql, dict) else 'N/D'}",
            f"    Precision del modelo MLlib: {datos.get('precision_mllib', 'N/D')}",
            "",
            "    Top ganadores (SparkSQL):",
        ] + [f"      {n}: {v}" for n, v in top])

        # --- Graficas ---
        titulos = {
            "victorias.png": "Victorias por personaje",
            "clusters.png": "Grupos de personajes (KMeans)",
            "matriz_confusion.png": "Matriz de confusion (clasificacion)",
            "curva_vida.png": "Ejemplo de curva de vida de un combate",
        }
        for ruta_img in datos.get("graficas", []):
            nombre = os.path.basename(ruta_img)
            _pagina_imagen(pdf, titulos.get(nombre, nombre), ruta_img)

    print(f"[OK] Informe generado en {ruta}")
    return ruta
