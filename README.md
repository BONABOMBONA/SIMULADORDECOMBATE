# Simulador de Combate

Simulador de combate por turnos entre personajes de distintos universos
(Pokemon, paises, superheroes) que funciona como un pipeline completo de
ciencia de datos: ingesta por web scraping, base de datos NoSQL,
machine learning y procesamiento distribuido con Apache Spark.

## Que hace

El usuario agrega personajes (por web scraping, por una biblioteca de URLs
precargadas, o creandolos a mano), todos se normalizan a stats comunes y se
guardan en MongoDB. Luego pueden pelear uno a uno (con animacion y
probabilidades) o en una simulacion masiva que alimenta los modelos de ML.

## Instalacion

1. Instalar Python 3 y las dependencias:

   ```
   pip install -r requirements.txt --break-system-packages
   ```

   (Para Spark se necesita tener Java instalado: `sudo apt install default-jdk`)

2. Configurar la base de datos en `config.py`:
   - Poner tu cadena de conexion de MongoDB Atlas en `MONGO_URI`.
   - En Atlas, permitir tu IP en Network Access (o 0.0.0.0/0 para la demo).

## Uso

- **Interfaz grafica (el juego):**

  ```
  python3 main.py
  ```

- **Analisis completo + informe PDF (para ver ML y Spark):**

  ```
  python3 analisis_completo.py
  ```

  Genera `salidas/informe_final.pdf` con todos los resultados.

- **Ejecutar modulos por separado** (opcional, para demostrar cada tema):

  ```
  python3 -c "from spark import rdd_procesamiento as r; r.victorias_por_personaje()"
  ```

## Estructura

```
simulador_combate/
├── main.py                  # Lanza la interfaz grafica
├── analisis_completo.py     # Pipeline completo + informe (ML y Spark)
├── config.py                # Conexion a Mongo, rutas, parametros
├── requirements.txt
│
├── simulador/               # Motor de combate (POO)
│   ├── personaje.py         # Clase Personaje
│   ├── combate.py           # Combate por turnos
│   └── generador.py         # Simulacion masiva
│
├── ingesta/                 # Entrada de datos
│   ├── web_scraping.py      # Scraper (3 estructuras + generico)
│   ├── biblioteca.py        # URLs precargadas
│   ├── normalizador.py      # Mapeo + Min-Max a stats comunes
│   └── procesamiento_no_estructurado.py   # Texto -> tabular
│
├── datos/
│   └── nosql_simulacion.py  # MongoDB + aplanado a DataFrame
│
├── ml/                      # Machine Learning (scikit-learn)
│   ├── clasificacion.py     # 3.1.1 - predice ganador
│   ├── regresion.py         # 3.1.2 - predice turnos
│   └── clustering.py        # 3.2.1 - agrupa personajes
│
├── spark/                   # Apache Spark
│   ├── rdd_procesamiento.py # 3.3.1 y 3.3.2 - RDD y transformaciones
│   └── spark_sql_mllib.py   # 3.3.3 - SparkSQL y SparkMLlib
│
├── visualizacion/
│   └── graficas.py          # Graficas (curva de vida, victorias, etc.)
│
├── reporte/
│   └── generador_reporte.py # Informe PDF
│
├── gui/                     # Interfaz (CustomTkinter)
│   ├── ventana.py           # Ventana principal + ML oculto
│   ├── pantalla_ingesta.py  # 3 modos de ingesta
│   ├── pantalla_combate.py  # Probabilidades -> animacion -> resultados
│   └── animacion.py         # Animacion de pelea
│
└── salidas/                 # Archivos generados (CSV, graficas, informe)
```

## Temario cubierto (Unidad III)

- 3.1.1 Clasificacion -> `ml/clasificacion.py`
- 3.1.2 Regresion -> `ml/regresion.py`
- 3.2.1 Analisis de grupos -> `ml/clustering.py`
- 3.3.1 / 3.3.2 RDD y transformaciones -> `spark/rdd_procesamiento.py`
- 3.3.3 SparkSQL y SparkMLlib -> `spark/spark_sql_mllib.py`
