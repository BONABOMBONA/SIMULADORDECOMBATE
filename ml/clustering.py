"""
clustering.py  -  Tema 3.2.1 Analisis de grupos (aprendizaje NO supervisado)

Agrupa a los personajes en categorias segun sus stats usando KMeans,
sin decirle al modelo las etiquetas. Descubre grupos naturales como
"tanques", "atacantes" o "equilibrados".
"""

import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

STATS = ["hp", "ataque", "defensa", "velocidad"]


def agrupar(df, n_grupos=3, semilla=42):
    """
    Aplica KMeans a los stats de los personajes.
    Devuelve: df_con_grupo, modelo, escalador
    """
    if len(df) < n_grupos:
        n_grupos = max(1, len(df))

    X = df[STATS]
    escalador = StandardScaler()
    X_escalado = escalador.fit_transform(X)

    modelo = KMeans(n_clusters=n_grupos, random_state=semilla, n_init=10)
    etiquetas = modelo.fit_predict(X_escalado)

    df_resultado = df.copy()
    df_resultado["grupo"] = etiquetas
    df_resultado["nombre_grupo"] = [_nombrar_grupo(modelo, e) for e in etiquetas]

    print(f"[Clustering] {len(df)} personajes agrupados en {n_grupos} grupos")
    return df_resultado, modelo, escalador


def _nombrar_grupo(modelo, etiqueta):
    """
    Pone un nombre interpretable al grupo segun que stat domina su centro.
    Los centros estan en escala estandarizada (STATS en el mismo orden).
    """
    centro = modelo.cluster_centers_[etiqueta]
    # indice del stat mas alto en el centro del grupo
    idx_dominante = centro.argmax()
    nombre_stat = STATS[idx_dominante]
    mapa = {"hp": "Resistente", "ataque": "Atacante",
            "defensa": "Defensivo", "velocidad": "Veloz"}
    return mapa.get(nombre_stat, "Equilibrado")


def resumen_grupos(df_con_grupo):
    """Devuelve el promedio de cada stat por grupo (para el informe)."""
    return df_con_grupo.groupby("nombre_grupo")[STATS].mean().round(1)
