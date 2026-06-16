"""
ventana.py
Ventana principal de la aplicacion (CustomTkinter).

Une las pantallas (ingesta y combate) con un menu lateral. Maneja la
lista de personajes y el ML que trabaja OCULTO: cuando hay suficientes
personajes, corre la simulacion masiva por detras y entrena el modelo
de clasificacion para calcular las probabilidades que se muestran al
pelear. El usuario nunca ve "machine learning" en la pantalla.

La base de datos (Mongo) se usa si esta disponible; si falla la conexion,
la app sigue funcionando con los personajes en memoria para no romper la demo.
"""

import threading
import customtkinter as ctk

from simulador.personaje import Personaje
from simulador.generador import simular_muchos
from ml import clasificacion
import config

# Intentar usar Mongo, pero no romper si no se puede conectar
try:
    from datos import nosql_simulacion as db
    HAY_DB = True
except Exception:
    HAY_DB = False


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Simulador de Combate")
        self.geometry("900x600")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Estado
        self.personajes = []        # lista de dicts de personajes
        self.modelo_clf = None      # modelo de ML (oculto)

        self._construir()
        self._cargar_personajes_iniciales()

    # ----------------------------------------------------------
    #   Construccion de la interfaz
    # ----------------------------------------------------------
    def _construir(self):
        # Menu lateral
        self.lateral = ctk.CTkFrame(self, width=180, corner_radius=0)
        self.lateral.pack(side="left", fill="y")

        ctk.CTkLabel(self.lateral, text="Simulador\nde Combate",
                     font=ctk.CTkFont(size=18, weight="bold")).pack(pady=(24, 20))

        ctk.CTkButton(self.lateral, text="Personajes",
                      command=self._ver_ingesta).pack(fill="x", padx=12, pady=6)
        ctk.CTkButton(self.lateral, text="Combatir",
                      command=self._ver_combate).pack(fill="x", padx=12, pady=6)

        # Etiqueta de estado (cuantos personajes, estado del modelo)
        self.lbl_estado = ctk.CTkLabel(self.lateral, text="", text_color="gray",
                                       font=ctk.CTkFont(size=11), wraplength=150)
        self.lbl_estado.pack(side="bottom", pady=16)

        # Contenedor de pantallas
        self.contenedor = ctk.CTkFrame(self, fg_color="transparent")
        self.contenedor.pack(side="left", fill="both", expand=True)

        # Importar aqui para evitar import circular
        from gui.pantalla_ingesta import PantallaIngesta
        self.pantalla_ingesta = PantallaIngesta(self.contenedor, self)
        self.pantalla_combate = None   # se crea la primera vez que se entra

        self._ver_ingesta()

    def _ocultar_todo(self):
        self.pantalla_ingesta.pack_forget()
        if self.pantalla_combate is not None:
            self.pantalla_combate.pack_forget()

    def _ver_ingesta(self):
        self._ocultar_todo()
        self.pantalla_ingesta.pack(fill="both", expand=True)

    def _ver_combate(self):
        self._ocultar_todo()
        # Crear la pantalla de combate la primera vez que se entra
        if self.pantalla_combate is None:
            from gui.pantalla_combate import PantallaCombate
            self.pantalla_combate = PantallaCombate(self.contenedor, self)
        else:
            self.pantalla_combate.refrescar_personajes()
        self.pantalla_combate.pack(fill="both", expand=True)

    # ----------------------------------------------------------
    #   Manejo de personajes
    # ----------------------------------------------------------
    def _cargar_personajes_iniciales(self):
        """Al arrancar, intenta leer personajes de Mongo (si hay conexion)."""
        if HAY_DB:
            def _cargar():
                try:
                    guardados = db.obtener_personajes()
                    if guardados:
                        self.personajes = guardados
                        self.despues(self._actualizar_estado)
                        self._preparar_modelo()
                except Exception:
                    pass
            threading.Thread(target=_cargar, daemon=True).start()
        self._actualizar_estado()

    def agregar_personajes(self, nuevos):
        """Agrega personajes a la lista (y a Mongo si hay), y reentrena el ML."""
        # Evitar duplicados por nombre+fuente
        existentes = {(p["nombre"], p.get("fuente", "")) for p in self.personajes}
        for p in nuevos:
            clave = (p["nombre"], p.get("fuente", ""))
            if clave not in existentes:
                self.personajes.append(p)
                existentes.add(clave)

        # Guardar en Mongo en segundo plano (si hay conexion)
        if HAY_DB:
            threading.Thread(target=self._guardar_db, args=(nuevos,), daemon=True).start()

        self._actualizar_estado()
        # Reentrenar el modelo oculto con los nuevos personajes
        self._preparar_modelo()

    def _guardar_db(self, nuevos):
        try:
            db.guardar_personajes(nuevos)
        except Exception:
            pass

    def crear_personaje(self, nombre):
        """Crea un objeto Personaje a partir del nombre (busca en la lista)."""
        for p in self.personajes:
            if p["nombre"] == nombre:
                return Personaje.from_dict(p)
        return None

    def limpiar_todo(self):
        """Borra todos los personajes: de la base de datos y de la memoria."""
        # Borrar de Mongo (si hay conexion)
        if HAY_DB:
            try:
                db.limpiar_personajes()
                db.limpiar_combates()
            except Exception:
                pass
        # Vaciar la memoria y el modelo
        self.personajes = []
        self.modelo_clf = None
        self._actualizar_estado()

    # ----------------------------------------------------------
    #   ML OCULTO: simulacion masiva + entrenamiento
    # ----------------------------------------------------------
    def _preparar_modelo(self):
        """
        Corre la simulacion masiva y entrena el clasificador EN SEGUNDO PLANO.
        Esto alimenta las probabilidades. El usuario no lo ve.
        """
        if len(self.personajes) < 2:
            return

        def _entrenar():
            try:
                objetos = [Personaje.from_dict(p) for p in self.personajes]
                import pandas as pd
                registros = simular_muchos(objetos, n_combates=config.N_COMBATES_MASIVA,
                                           semilla=config.SEMILLA)
                df = pd.DataFrame(registros)
                modelo, _, _, _ = clasificacion.entrenar(df)
                self.modelo_clf = modelo
                self.despues(self._actualizar_estado)
            except Exception:
                pass
        threading.Thread(target=_entrenar, daemon=True).start()

    def calcular_probabilidades(self, pa, pb):
        """
        Devuelve (prob_a, prob_b) en porcentaje. Usa el modelo de ML si esta
        listo; si no, usa una estimacion simple basada en los stats.
        """
        if self.modelo_clf is not None:
            try:
                return clasificacion.probabilidades_combate(self.modelo_clf, pa, pb)
            except Exception:
                pass
        # Respaldo: estimacion por suma de stats (mientras el modelo entrena)
        fuerza_a = pa.hp_max + pa.ataque + pa.defensa + pa.velocidad
        fuerza_b = pb.hp_max + pb.ataque + pb.defensa + pb.velocidad
        total = fuerza_a + fuerza_b
        pa_pct = round(fuerza_a / total * 100) if total else 50
        return pa_pct, 100 - pa_pct

    # ----------------------------------------------------------
    #   Utilidades de interfaz
    # ----------------------------------------------------------
    def _actualizar_estado(self):
        n = len(self.personajes)
        estado_modelo = "modelo listo" if self.modelo_clf else "entrenando..."
        if n < 2:
            estado_modelo = "faltan personajes"
        texto = f"{n} personajes\n({estado_modelo})"
        if not HAY_DB:
            texto += "\n[sin conexion a BD]"
        try:
            self.lbl_estado.configure(text=texto)
        except Exception:
            pass

    def despues(self, funcion, ms=0):
        """Ejecuta una funcion en el hilo de la interfaz (thread-safe)."""
        try:
            self.after(ms, funcion)
        except Exception:
            pass


def iniciar():
    app = App()
    app.mainloop()
