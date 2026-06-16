"""
graficas.py
Modulo de visualizacion. Genera las graficas representativas del proyecto
y las guarda como PNG en salidas/graficas/.

Usa el backend 'Agg' de matplotlib para poder generar imagenes sin
necesidad de una ventana (funciona dentro de la GUI y en segundo plano).
"""

import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

CARPETA = os.path.join("salidas", "graficas")
os.makedirs(CARPETA, exist_ok=True)


def curva_de_vida(historial, ganador, ruta=None):
    """
    Dibuja la curva de vida (HP por turno) de cada peleador.
    'historial' es el diccionario {nombre: [hp_turno_0, hp_turno_1, ...]}
    que devuelve el combate. Es la grafica del combate uno a uno.
    """
    if ruta is None:
        ruta = os.path.join(CARPETA, "curva_vida.png")

    fig, ax = plt.subplots(figsize=(7, 4))
    estilos = ["-", "--"]
    for i, (nombre, hps) in enumerate(historial.items()):
        ax.plot(range(len(hps)), hps, estilos[i % 2], marker="o",
                linewidth=2, markersize=4, label=nombre)
    ax.set_xlabel("Turno")
    ax.set_ylabel("HP")
    ax.set_title(f"Curva de vida - Gano: {ganador}")
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.set_ylim(bottom=0)
    fig.tight_layout()
    fig.savefig(ruta, dpi=100)
    plt.close(fig)
    return ruta


def grafica_victorias(victorias, ruta=None):
    """
    Grafica de barras de victorias por personaje.
    'victorias' es una lista [(nombre, conteo), ...].
    """
    if ruta is None:
        ruta = os.path.join(CARPETA, "victorias.png")

    nombres = [v[0] for v in victorias]
    conteos = [v[1] for v in victorias]

    fig, ax = plt.subplots(figsize=(8, 4))
    ax.bar(nombres, conteos, color="#4C72B0")
    ax.set_xlabel("Personaje")
    ax.set_ylabel("Victorias")
    ax.set_title("Victorias por personaje (simulacion masiva)")
    plt.setp(ax.get_xticklabels(), rotation=30, ha="right")
    ax.grid(True, axis="y", alpha=0.3)
    fig.tight_layout()
    fig.savefig(ruta, dpi=100)
    plt.close(fig)
    return ruta


def grafica_clusters(df_con_grupo, ruta=None):
    """
    Dispersa los personajes por ataque vs defensa, coloreados por grupo.
    'df_con_grupo' es el DataFrame que devuelve clustering.agrupar().
    """
    if ruta is None:
        ruta = os.path.join(CARPETA, "clusters.png")

    fig, ax = plt.subplots(figsize=(7, 5))
    grupos = df_con_grupo["grupo"].unique()
    colores = plt.cm.tab10.colors
    for g in grupos:
        sub = df_con_grupo[df_con_grupo["grupo"] == g]
        etiqueta = sub["nombre_grupo"].iloc[0] if "nombre_grupo" in sub else f"Grupo {g}"
        ax.scatter(sub["ataque"], sub["defensa"],
                   color=colores[g % len(colores)], label=etiqueta, s=80)
        for _, fila in sub.iterrows():
            ax.annotate(fila["nombre"], (fila["ataque"], fila["defensa"]),
                        fontsize=7, xytext=(4, 4), textcoords="offset points")
    ax.set_xlabel("Ataque")
    ax.set_ylabel("Defensa")
    ax.set_title("Grupos de personajes (KMeans)")
    ax.legend()
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(ruta, dpi=100)
    plt.close(fig)
    return ruta


def matriz_confusion(matriz, ruta=None):
    """
    Dibuja la matriz de confusion del clasificador (que tan bien predice).
    """
    if ruta is None:
        ruta = os.path.join(CARPETA, "matriz_confusion.png")

    fig, ax = plt.subplots(figsize=(5, 4))
    im = ax.imshow(matriz, cmap="Blues")
    etiquetas = ["Gano B (0)", "Gano A (1)"]
    ax.set_xticks([0, 1]); ax.set_yticks([0, 1])
    ax.set_xticklabels(etiquetas); ax.set_yticklabels(etiquetas)
    ax.set_xlabel("Prediccion")
    ax.set_ylabel("Real")
    ax.set_title("Matriz de confusion (clasificacion)")
    # Escribir los numeros dentro de cada celda
    for i in range(matriz.shape[0]):
        for j in range(matriz.shape[1]):
            ax.text(j, i, str(matriz[i, j]), ha="center", va="center",
                    color="black", fontsize=12)
    fig.colorbar(im)
    fig.tight_layout()
    fig.savefig(ruta, dpi=100)
    plt.close(fig)
    return ruta
