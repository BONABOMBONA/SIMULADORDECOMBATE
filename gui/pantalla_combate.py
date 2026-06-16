"""
pantalla_combate.py
Pantalla del combate uno a uno, dividida en PANTALLAS que se reemplazan:

  PANTALLA 1 (seleccion): elegir dos peleadores y pulsar "Pelear".
  PANTALLA 2 (probabilidades): muestra el % de cada uno (ML oculto).
  PANTALLA 3 (animacion): "Peleando..." con las barras de vida bajando.
  PANTALLA 4 (resultado): quien gano + la curva de vida en grande.

Cada pantalla ocupa toda la zona y reemplaza a la anterior.
"""

import os
import customtkinter as ctk
from tkinter import messagebox

from simulador.personaje import Personaje
from simulador.combate import combatir
from gui.animacion import AnimadorCombate
from visualizacion import graficas

try:
    from PIL import Image
    HAY_PIL = True
except ImportError:
    HAY_PIL = False


class SelectorPersonaje(ctk.CTkFrame):
    """Buscador + lista con scroll + tarjeta de stats del elegido."""
    def __init__(self, master, titulo, obtener_nombres, obtener_datos):
        super().__init__(master)
        self.obtener_nombres = obtener_nombres
        self.obtener_datos = obtener_datos   # funcion(nombre) -> dict del personaje
        self.seleccionado = None
        self._botones = []
        self._nombres_filtrados = []
        self._cuantos_visibles = 30

        ctk.CTkLabel(self, text=titulo,
                     font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(10, 4))
        self.buscador = ctk.CTkEntry(self, width=220, placeholder_text="Buscar...")
        self.buscador.pack(padx=10, pady=(0, 4))
        self.buscador.bind("<KeyRelease>", lambda e: self._filtrar())
        self.lbl_sel = ctk.CTkLabel(self, text="(ninguno)",
                                    text_color="#4C9AFF",
                                    font=ctk.CTkFont(size=15, weight="bold"))
        self.lbl_sel.pack(pady=(0, 4))

        # Tarjeta con los stats del personaje elegido
        self.tarjeta = ctk.CTkFrame(self)
        self.tarjeta.pack(padx=10, pady=(0, 6), fill="x")
        self.lbl_stats = ctk.CTkLabel(self.tarjeta, text="Elige un personaje",
                                      text_color="gray", justify="left",
                                      font=ctk.CTkFont(size=13))
        self.lbl_stats.pack(padx=10, pady=8)

        self.lista = ctk.CTkScrollableFrame(self, width=220, height=180)
        self.lista.pack(padx=10, pady=(0, 10))

    def refrescar(self):
        self._filtrar()

    def _filtrar(self):
        texto = self.buscador.get().strip().lower()
        nombres = self.obtener_nombres()
        if texto:
            nombres = [n for n in nombres if texto in n.lower()]

        # Reiniciar cuantos se muestran cada vez que cambia la busqueda
        self._nombres_filtrados = nombres
        self._cuantos_visibles = 30
        self._redibujar_lista()

    def _redibujar_lista(self):
        # Limpiar lo que haya
        for b in self._botones:
            b.destroy()
        self._botones = []

        nombres = self._nombres_filtrados
        total = len(nombres)
        mostrar = nombres[:self._cuantos_visibles]

        for nombre in mostrar:
            etiqueta = f"{nombre}  ({_universo_de(self.obtener_datos(nombre))})"
            b = ctk.CTkButton(self.lista, text=etiqueta, height=28,
                              fg_color="transparent", anchor="w",
                              command=lambda n=nombre: self._elegir(n))
            b.pack(fill="x", pady=1)
            self._botones.append(b)

        # Boton "ver mas" si quedan personajes por mostrar
        if total > self._cuantos_visibles:
            restantes = total - self._cuantos_visibles
            btn_mas = ctk.CTkButton(
                self.lista,
                text=f"Ver mas ({restantes} mas)",
                height=30, fg_color="#2D5F8A",
                command=self._ver_mas)
            btn_mas.pack(fill="x", pady=4)
            self._botones.append(btn_mas)

    def _ver_mas(self):
        # Mostrar 30 mas cada vez que se pulsa
        self._cuantos_visibles += 30
        self._redibujar_lista()

    def _elegir(self, nombre):
        self.seleccionado = nombre
        self.lbl_sel.configure(text=nombre)
        # Mostrar los stats del personaje elegido
        datos = self.obtener_datos(nombre)
        if datos:
            texto = (f"HP:  {datos.get('hp', '?')}\n"
                     f"Ataque:  {datos.get('ataque', '?')}\n"
                     f"Defensa:  {datos.get('defensa', '?')}\n"
                     f"Velocidad:  {datos.get('velocidad', '?')}\n"
                     f"Fuente:  {_fuente_corta(datos.get('fuente', ''))}")
            self.lbl_stats.configure(text=texto, text_color="white", justify="left")
        else:
            self.lbl_stats.configure(text="(sin datos)", text_color="gray")


def _fuente_corta(fuente):
    """Acorta la fuente para que quepa (ej. la URL larga -> dominio)."""
    if not fuente:
        return "manual"
    if "pokemondb" in fuente:
        return "Pokemon"
    if "scrapethissite" in fuente:
        return "Pais"
    if "superhero" in fuente:
        return "Superheroe"
    if fuente == "manual":
        return "Manual"
    if fuente == "texto_libre":
        return "Texto"
    return fuente[:20]


def _universo_de(datos):
    """
    Devuelve el universo del personaje para mostrar junto al nombre.
    Para Pokemon/Paises/Superheroes da el nombre; para un link manual
    da el dominio de la pagina; para creados a mano, 'manual'.
    """
    if not datos:
        return "?"
    fuente = datos.get("fuente", "")
    if "pokemondb" in fuente:
        return "Pokemon"
    if "scrapethissite" in fuente:
        return "Pais"
    if "superhero" in fuente or "tashapiro" in fuente:
        return "Superheroe"
    if "leagueoflegends" in fuente or "/lol" in fuente:
        return "LoL"
    if fuente == "manual":
        return "manual"
    if fuente == "texto_libre":
        return "texto"
    # Link manual: sacar el dominio de la URL
    if fuente.startswith("http"):
        try:
            dominio = fuente.split("//")[1].split("/")[0].replace("www.", "")
            return dominio
        except Exception:
            return "link"
    return fuente[:15] if fuente else "?"


class PantallaCombate(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, fg_color="transparent")
        self.app = app
        # Una sola "zona" que cambia de contenido en cada paso
        self.zona = ctk.CTkFrame(self, fg_color="transparent")
        self.zona.pack(fill="both", expand=True)
        self.mostrar_seleccion()

    # ==========================================================
    #   PANTALLA 1: SELECCION
    # ==========================================================
    def mostrar_seleccion(self):
        self._limpiar()
        ctk.CTkLabel(self.zona, text="Elige a los peleadores",
                     font=ctk.CTkFont(size=24, weight="bold")).pack(pady=(20, 16))

        fila = ctk.CTkFrame(self.zona, fg_color="transparent")
        fila.pack(pady=10)

        self.sel_a = SelectorPersonaje(fila, "Peleador 1", self._nombres, self._datos)
        self.sel_a.grid(row=0, column=0, padx=20)
        ctk.CTkLabel(fila, text="VS",
                     font=ctk.CTkFont(size=22, weight="bold")).grid(row=0, column=1, padx=16)
        self.sel_b = SelectorPersonaje(fila, "Peleador 2", self._nombres, self._datos)
        self.sel_b.grid(row=0, column=2, padx=20)

        self.sel_a.refrescar()
        self.sel_b.refrescar()

        ctk.CTkButton(self.zona, text="Pelear", command=self._pelear,
                      width=200, height=50,
                      font=ctk.CTkFont(size=18, weight="bold")).pack(pady=24)

    def refrescar_personajes(self):
        # Al volver a esta pestana, regresar a la pantalla de seleccion
        self.mostrar_seleccion()

    def _nombres(self):
        return [p["nombre"] for p in self.app.personajes]

    def _datos(self, nombre):
        """Devuelve el diccionario del personaje con ese nombre (para la tarjeta de stats)."""
        for p in self.app.personajes:
            if p["nombre"] == nombre:
                return p
        return None

    def _limpiar(self):
        for w in self.zona.winfo_children():
            w.destroy()

    def _pelear(self):
        if len(self.app.personajes) < 2:
            messagebox.showwarning("Faltan personajes",
                                   "Agrega al menos 2 personajes en la pestana de Personajes.")
            return
        nombre_a = self.sel_a.seleccionado
        nombre_b = self.sel_b.seleccionado
        if not nombre_a or not nombre_b:
            messagebox.showwarning("Elige peleadores",
                                   "Busca y selecciona un peleador en cada lado.")
            return
        if nombre_a == nombre_b:
            messagebox.showwarning("Mismo personaje", "Elige dos peleadores distintos.")
            return
        self.pa = self.app.crear_personaje(nombre_a)
        self.pb = self.app.crear_personaje(nombre_b)
        if self.pa is None or self.pb is None:
            messagebox.showerror("Error", "No se encontro alguno de los personajes.")
            return
        # Ir directo a la animacion (sin pantalla de probabilidades)
        self.mostrar_animacion()

    # ==========================================================
    #   PANTALLA 2: PROBABILIDADES
    # ==========================================================
    def mostrar_probabilidades(self):
        self._limpiar()
        prob_a, prob_b = self.app.calcular_probabilidades(self.pa, self.pb)

        ctk.CTkLabel(self.zona, text="Probabilidades de victoria",
                     font=ctk.CTkFont(size=22, weight="bold")).pack(pady=(60, 30))

        fila = ctk.CTkFrame(self.zona, fg_color="transparent")
        fila.pack(pady=10)
        ctk.CTkLabel(fila, text=f"{self.pa.nombre}\n{prob_a}%",
                     font=ctk.CTkFont(size=28, weight="bold")).grid(row=0, column=0, padx=50)
        ctk.CTkLabel(fila, text="vs",
                     font=ctk.CTkFont(size=18)).grid(row=0, column=1, padx=10)
        ctk.CTkLabel(fila, text=f"{self.pb.nombre}\n{prob_b}%",
                     font=ctk.CTkFont(size=28, weight="bold")).grid(row=0, column=2, padx=50)

        barra = ctk.CTkProgressBar(self.zona, width=460, height=16)
        barra.set(prob_a / 100)
        barra.pack(pady=36)

        ctk.CTkLabel(self.zona, text="Preparando el combate...",
                     text_color="gray").pack()

        self.app.despues(self.mostrar_animacion, 2800)

    # ==========================================================
    #   PANTALLA 3: ANIMACION
    # ==========================================================
    def mostrar_animacion(self):
        self._limpiar()
        self.resultado = combatir(self.pa, self.pb)

        ctk.CTkLabel(self.zona, text="Peleando...",
                     font=ctk.CTkFont(size=26, weight="bold")).pack(pady=(50, 30))

        cont = ctk.CTkFrame(self.zona, fg_color="transparent")
        cont.pack(pady=10)

        self.lbl_a = ctk.CTkLabel(cont, text=f"{self.pa.nombre}: {self.pa.hp_max} HP",
                                  font=ctk.CTkFont(size=15))
        self.lbl_a.pack(anchor="w")
        self.barra_a = ctk.CTkProgressBar(cont, width=460, height=22)
        self.barra_a.set(1.0)
        self.barra_a.pack(pady=(2, 20))

        self.lbl_b = ctk.CTkLabel(cont, text=f"{self.pb.nombre}: {self.pb.hp_max} HP",
                                  font=ctk.CTkFont(size=15))
        self.lbl_b.pack(anchor="w")
        self.barra_b = ctk.CTkProgressBar(cont, width=460, height=22)
        self.barra_b.set(1.0)
        self.barra_b.pack(pady=(2, 20))

        self.lbl_turno = ctk.CTkLabel(self.zona, text="Turno 0",
                                      font=ctk.CTkFont(size=16), text_color="gray")
        self.lbl_turno.pack(pady=20)

        animador = AnimadorCombate(
            self.resultado,
            actualizar=self._actualizar_turno,
            al_terminar=self.mostrar_resultado,
            retraso=0.7)
        animador.iniciar()

    def _actualizar_turno(self, turno, hp_a, hp_b):
        def _ui():
            self.lbl_a.configure(text=f"{self.pa.nombre}: {hp_a} HP")
            self.lbl_b.configure(text=f"{self.pb.nombre}: {hp_b} HP")
            self.barra_a.set(max(0, hp_a / self.pa.hp_max))
            self.barra_b.set(max(0, hp_b / self.pb.hp_max))
            self.lbl_turno.configure(text=f"Turno {turno}")
        self.app.despues(_ui)

    # ==========================================================
    #   PANTALLA 4: RESULTADO
    # ==========================================================
    def mostrar_resultado(self):
        def _ui():
            self._limpiar()
            ganador = self.resultado["ganador"]
            ctk.CTkLabel(self.zona, text=f"Gano: {ganador}",
                         font=ctk.CTkFont(size=26, weight="bold")).pack(pady=(16, 4))
            ctk.CTkLabel(self.zona,
                         text=f"Combate terminado en {self.resultado['turnos']} turnos",
                         text_color="gray").pack(pady=(0, 10))

            ruta = graficas.curva_de_vida(self.resultado["historial"], ganador)
            if HAY_PIL and os.path.exists(ruta):
                img = ctk.CTkImage(light_image=Image.open(ruta), size=(560, 270))
                ctk.CTkLabel(self.zona, image=img, text="").pack(pady=6)
            else:
                ctk.CTkLabel(self.zona, text=f"(Curva guardada en {ruta})",
                             text_color="gray").pack(pady=6)

            # --- Desglose turno por turno ---
            detalle = ctk.CTkScrollableFrame(self.zona, width=620, height=140)
            detalle.pack(padx=20, pady=6)

            hist = self.resultado["historial"]
            nombres = list(hist.keys())
            serie1 = hist[nombres[0]]
            serie2 = hist[nombres[1]]

            # Turno 0: info completa de los dos peleadores
            ctk.CTkLabel(detalle, text="Turno 0 (inicio)",
                         font=ctk.CTkFont(size=14, weight="bold"),
                         anchor="w").pack(fill="x", padx=8, pady=(4, 0))
            ctk.CTkLabel(
                detalle, anchor="w", justify="left",
                text=(f"   {self.pa.nombre} - HP:{self.pa.hp_max}  ATK:{self.pa.ataque}  "
                      f"DEF:{self.pa.defensa}  VEL:{self.pa.velocidad}")
            ).pack(fill="x", padx=8)
            ctk.CTkLabel(
                detalle, anchor="w", justify="left",
                text=(f"   {self.pb.nombre} - HP:{self.pb.hp_max}  ATK:{self.pb.ataque}  "
                      f"DEF:{self.pb.defensa}  VEL:{self.pb.velocidad}")
            ).pack(fill="x", padx=8, pady=(0, 4))

            # Turnos 1 en adelante: solo el HP de cada uno
            for turno in range(1, len(serie1)):
                ctk.CTkLabel(
                    detalle, anchor="w", justify="left",
                    text=(f"Turno {turno}:   {nombres[0]}: {serie1[turno]} HP   |   "
                          f"{nombres[1]}: {serie2[turno]} HP")
                ).pack(fill="x", padx=8, pady=1)

            ctk.CTkButton(self.zona, text="Otro combate",
                          command=self.mostrar_seleccion,
                          width=160, height=40).pack(pady=14)
        self.app.despues(_ui)
