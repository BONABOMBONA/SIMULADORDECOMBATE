"""
pantalla_ingesta.py
Pantalla de ingesta de personajes con tres modos desplegables:
  - Link manual: el usuario pega una URL y se scrapea.
  - Biblioteca: URLs precargadas que se scrapean en vivo.
  - Crear a mano: formulario con los 4 stats.

Cada modo, al elegirse, despliega abajo solo su contenido.
"""

import threading
import customtkinter as ctk
from tkinter import messagebox

from ingesta import web_scraping, normalizador, biblioteca
from simulador.personaje import Personaje


class PantallaIngesta(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, fg_color="transparent")
        self.app = app
        self._construir()

    def _construir(self):
        titulo = ctk.CTkLabel(self, text="Ingesta de personajes",
                              font=ctk.CTkFont(size=22, weight="bold"))
        titulo.pack(anchor="w", padx=20, pady=(20, 4))

        sub = ctk.CTkLabel(self, text="Elige como agregar personajes:",
                           text_color="gray")
        sub.pack(anchor="w", padx=20, pady=(0, 12))

        # --- Botones de los tres modos ---
        barra = ctk.CTkFrame(self, fg_color="transparent")
        barra.pack(anchor="w", padx=20)

        self.btn_link = ctk.CTkButton(barra, text="Link manual",
                                      command=lambda: self._mostrar("link"))
        self.btn_link.grid(row=0, column=0, padx=4)
        self.btn_bib = ctk.CTkButton(barra, text="Biblioteca",
                                     command=lambda: self._mostrar("biblioteca"))
        self.btn_bib.grid(row=0, column=1, padx=4)
        self.btn_mano = ctk.CTkButton(barra, text="Crear a mano",
                                      command=lambda: self._mostrar("mano"))
        self.btn_mano.grid(row=0, column=2, padx=4)

        # Boton para limpiar la base (en rojo, separado a la derecha)
        self.btn_limpiar = ctk.CTkButton(barra, text="Limpiar base",
                                         fg_color="#B22222", hover_color="#8B0000",
                                         command=self._limpiar_base)
        self.btn_limpiar.grid(row=0, column=3, padx=(30, 4))

        # --- Panel que cambia segun el modo ---
        self.panel = ctk.CTkFrame(self)
        self.panel.pack(fill="both", expand=True, padx=20, pady=16)

        self._mostrar("link")

    def _limpiar_base(self):
        """Borra TODOS los personajes (de la base y de la memoria del programa)."""
        confirmar = messagebox.askyesno(
            "Limpiar base",
            "Esto borrara TODOS los personajes cargados.\n\n"
            "Sirve para empezar de cero (por ejemplo, quitar los Pokemon "
            "y dejar solo superheroes).\n\n¿Seguro que quieres continuar?")
        if not confirmar:
            return
        self.app.limpiar_todo()
        messagebox.showinfo("Listo", "Base limpiada. Ya puedes cargar otras fuentes.")

    def _limpiar_panel(self):
        for w in self.panel.winfo_children():
            w.destroy()

    def _mostrar(self, modo):
        self._limpiar_panel()
        if modo == "link":
            self._panel_link()
        elif modo == "biblioteca":
            self._panel_biblioteca()
        elif modo == "mano":
            self._panel_mano()

    # ---------- MODO 1: link manual ----------
    def _panel_link(self):
        ctk.CTkLabel(self.panel, text="Pega la URL a scrapear:",
                     font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=16, pady=(16, 4))
        self.entrada_url = ctk.CTkEntry(self.panel, width=400,
                                        placeholder_text="https://...")
        self.entrada_url.pack(anchor="w", padx=16, pady=4)
        ctk.CTkButton(self.panel, text="Scrapear y guardar",
                      command=self._scrapear_manual).pack(anchor="w", padx=16, pady=12)
        self.estado_link = ctk.CTkLabel(self.panel, text="", text_color="gray")
        self.estado_link.pack(anchor="w", padx=16)

    def _scrapear_manual(self):
        url = self.entrada_url.get().strip()
        if not url:
            messagebox.showwarning("Falta URL", "Escribe una URL primero.")
            return
        self.estado_link.configure(text="Scrapeando...")
        threading.Thread(target=self._hacer_scraping, args=(url, None), daemon=True).start()

    # ---------- MODO 2: biblioteca ----------
    def _panel_biblioteca(self):
        ctk.CTkLabel(self.panel, text="Fuentes precargadas (se scrapean en vivo):",
                     font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=16, pady=(16, 8))
        for entrada in biblioteca.BIBLIOTECA:
            fila = ctk.CTkFrame(self.panel)
            fila.pack(fill="x", padx=16, pady=4)
            ctk.CTkLabel(fila, text=entrada["nombre"],
                         font=ctk.CTkFont(weight="bold")).pack(side="left", padx=10, pady=8)
            ctk.CTkButton(fila, text="Cargar", width=80,
                          command=lambda e=entrada: self._cargar_biblioteca(e)).pack(side="right", padx=10)
        self.estado_bib = ctk.CTkLabel(self.panel, text="", text_color="gray")
        self.estado_bib.pack(anchor="w", padx=16, pady=8)

    def _cargar_biblioteca(self, entrada):
        self.estado_bib.configure(text=f"Scrapeando {entrada['nombre']}...")
        threading.Thread(target=self._hacer_scraping,
                         args=(entrada["url"], entrada["tipo"]), daemon=True).start()

    # ---------- MODO 3: crear a mano ----------
    def _panel_mano(self):
        ctk.CTkLabel(self.panel, text="Nuevo personaje:",
                     font=ctk.CTkFont(size=14, weight="bold")).grid(row=0, column=0, columnspan=2, sticky="w", padx=16, pady=(16, 8))
        self.campos = {}
        etiquetas = [("nombre", "Nombre"), ("hp", "HP (vida)"),
                     ("ataque", "Ataque"), ("defensa", "Defensa"),
                     ("velocidad", "Velocidad")]
        for i, (clave, texto) in enumerate(etiquetas, start=1):
            ctk.CTkLabel(self.panel, text=texto).grid(row=i, column=0, sticky="w", padx=16, pady=4)
            entrada = ctk.CTkEntry(self.panel, width=200)
            if clave != "nombre":
                entrada.insert(0, "50")
            entrada.grid(row=i, column=1, sticky="w", padx=16, pady=4)
            self.campos[clave] = entrada
        ctk.CTkButton(self.panel, text="Guardar personaje",
                      command=self._guardar_manual).grid(row=6, column=0, columnspan=2, padx=16, pady=16)
        self.estado_mano = ctk.CTkLabel(self.panel, text="", text_color="gray")
        self.estado_mano.grid(row=7, column=0, columnspan=2, sticky="w", padx=16)

    def _guardar_manual(self):
        nombre = self.campos["nombre"].get().strip()
        if not nombre:
            messagebox.showwarning("Falta nombre", "Escribe un nombre.")
            return
        try:
            datos = normalizador.normalizar_manual(
                nombre,
                self.campos["hp"].get(), self.campos["ataque"].get(),
                self.campos["defensa"].get(), self.campos["velocidad"].get())
        except ValueError:
            messagebox.showerror("Error", "Los stats deben ser numeros.")
            return
        self.app.agregar_personajes([datos])
        self.estado_mano.configure(text=f"'{nombre}' guardado.")

    # ---------- comun ----------
    def _hacer_scraping(self, url, tipo):
        crudos = web_scraping.scrapear(url, tipo=tipo)
        if not crudos:
            self.app.despues(lambda: messagebox.showwarning(
                "Sin datos", "No se pudieron extraer personajes de esa pagina."))
            return
        normalizados = normalizador.normalizar(crudos)
        self.app.agregar_personajes(normalizados)
        msg = f"{len(normalizados)} personajes agregados."
        self.app.despues(lambda: self._avisar(msg))

    def _avisar(self, msg):
        for attr in ["estado_link", "estado_bib"]:
            if hasattr(self, attr):
                try:
                    getattr(self, attr).configure(text=msg)
                except Exception:
                    pass
