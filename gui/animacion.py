"""
animacion.py
Animacion de combate para la interfaz.

Reproduce el combate turno por turno dentro de la GUI: muestra las barras
de vida bajando y el texto "Peleando...". La simulacion del combate corre
en un hilo aparte para que la ventana no se congele.
"""

import threading
import time


class AnimadorCombate:
    """
    Reproduce un combate ya calculado, turno por turno, llamando a una
    funcion 'actualizar' por cada turno y a 'al_terminar' al final.

    Asi separamos el calculo (instantaneo) de la animacion (con pausas),
    y todo corre sin congelar la ventana.
    """

    def __init__(self, resultado, actualizar, al_terminar, retraso=0.6):
        """
        resultado   : el dict que devuelve combate.combatir()
        actualizar  : funcion(turno, hp1, hp2) que refresca la pantalla
        al_terminar : funcion() que se llama cuando acaba la animacion
        retraso     : segundos entre turnos
        """
        self.resultado = resultado
        self.actualizar = actualizar
        self.al_terminar = al_terminar
        self.retraso = retraso
        self._detener = False

    def iniciar(self):
        """Lanza la animacion en un hilo aparte."""
        hilo = threading.Thread(target=self._reproducir, daemon=True)
        hilo.start()

    def detener(self):
        self._detener = True

    def _reproducir(self):
        historial = self.resultado["historial"]
        nombres = list(historial.keys())
        serie1 = historial[nombres[0]]
        serie2 = historial[nombres[1]]
        total = len(serie1)

        for turno in range(total):
            if self._detener:
                return
            hp1 = serie1[turno]
            hp2 = serie2[turno]
            # Llamar a la actualizacion de pantalla
            try:
                self.actualizar(turno, hp1, hp2)
            except Exception:
                pass
            time.sleep(self.retraso)

        try:
            self.al_terminar()
        except Exception:
            pass
