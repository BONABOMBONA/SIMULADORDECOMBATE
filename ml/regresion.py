"""
regresion.py  -  Tema 3.1.2 Regresion (aprendizaje supervisado)

Entrena un modelo que predice CUANTOS TURNOS durara un combate a partir
de los stats de los dos peleadores.
"""

import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score
import joblib

CARACTERISTICAS = ["hp_a", "ataque_a", "defensa_a", "velocidad_a",
                   "hp_b", "ataque_b", "defensa_b", "velocidad_b"]


def entrenar(df, semilla=42):
    """
    Entrena el regresor para predecir 'turnos'.
    Devuelve: modelo, error_medio (MAE), r2, (X_test, y_test, predicciones)
    """
    X = df[CARACTERISTICAS]
    y = df["turnos"]
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=semilla)

    modelo = RandomForestRegressor(n_estimators=100, random_state=semilla)
    modelo.fit(X_train, y_train)

    predicciones = modelo.predict(X_test)
    mae = mean_absolute_error(y_test, predicciones)
    r2 = r2_score(y_test, predicciones)

    print(f"[Regresion] Error medio: {mae:.2f} turnos | R2: {r2:.2f}")
    return modelo, mae, r2, (X_test, y_test, predicciones)


def predecir_turnos(modelo, personaje_a, personaje_b):
    """Predice cuantos turnos duraria el combate entre A y B."""
    fila = pd.DataFrame([[personaje_a.hp_max, personaje_a.ataque, personaje_a.defensa, personaje_a.velocidad,
                          personaje_b.hp_max, personaje_b.ataque, personaje_b.defensa, personaje_b.velocidad]],
                        columns=CARACTERISTICAS)
    return round(modelo.predict(fila)[0])


def guardar_modelo(modelo, ruta="salidas/modelo_regresion.joblib"):
    joblib.dump(modelo, ruta)
    print(f"[OK] Modelo guardado en {ruta}")


def cargar_modelo(ruta="salidas/modelo_regresion.joblib"):
    return joblib.load(ruta)
