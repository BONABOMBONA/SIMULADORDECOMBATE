"""
clasificacion.py  -  Tema 3.1.1 Clasificacion (aprendizaje supervisado)

Entrena un modelo que predice QUIEN GANA un combate a partir de los stats
de los dos peleadores. Esta prediccion es la que alimenta las probabilidades
que se muestran en la pantalla de combate (el ML "en el corazon").
"""

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, confusion_matrix
import joblib

# Las 8 columnas que describen un enfrentamiento (stats de A y de B)
CARACTERISTICAS = ["hp_a", "ataque_a", "defensa_a", "velocidad_a",
                   "hp_b", "ataque_b", "defensa_b", "velocidad_b"]


def entrenar(df, semilla=42):
    """
    Entrena el clasificador con el dataset de combates.
    Devuelve: modelo, precision, matriz_confusion, (X_test, y_test, predicciones)
    """
    X = df[CARACTERISTICAS]
    y = df["gano_a"]
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=semilla)

    modelo = RandomForestClassifier(n_estimators=100, random_state=semilla)
    modelo.fit(X_train, y_train)

    predicciones = modelo.predict(X_test)
    precision = accuracy_score(y_test, predicciones)
    matriz = confusion_matrix(y_test, predicciones)

    print(f"[Clasificacion] Precision del modelo: {precision:.1%}")
    return modelo, precision, matriz, (X_test, y_test, predicciones)


def predecir_probabilidad(modelo, personaje_a, personaje_b):
    """
    Devuelve la probabilidad (0 a 1) de que GANE el personaje A.
    Recibe dos objetos Personaje.
    """
    fila = pd.DataFrame([[personaje_a.hp_max, personaje_a.ataque, personaje_a.defensa, personaje_a.velocidad,
                          personaje_b.hp_max, personaje_b.ataque, personaje_b.defensa, personaje_b.velocidad]],
                        columns=CARACTERISTICAS)
    clases = list(modelo.classes_)
    idx_gana_a = clases.index(1)
    prob_a = modelo.predict_proba(fila)[0][idx_gana_a]
    return prob_a


def probabilidades_combate(modelo, personaje_a, personaje_b):
    """
    Devuelve las dos probabilidades en porcentaje (suman 100):
    (porcentaje_a, porcentaje_b). Listo para mostrar en pantalla.
    """
    prob_a = predecir_probabilidad(modelo, personaje_a, personaje_b)
    pa = round(prob_a * 100)
    pb = 100 - pa
    return pa, pb


def guardar_modelo(modelo, ruta="salidas/modelo_clasificacion.joblib"):
    joblib.dump(modelo, ruta)
    print(f"[OK] Modelo guardado en {ruta}")


def cargar_modelo(ruta="salidas/modelo_clasificacion.joblib"):
    return joblib.load(ruta)
