"""
personaje.py
Define la clase Personaje, la unidad basica del simulador de combate.
"""

import random


class Personaje:
    """Representa a un peleador dentro del simulador."""

    def __init__(self, nombre, hp, ataque, defensa, velocidad,
                 fuente="manual", extra=None):
        self.nombre = nombre
        self.fuente = fuente
        self.extra = extra or {}
        self.hp_max = int(hp)
        self.ataque = int(ataque)
        self.defensa = int(defensa)
        self.velocidad = int(velocidad)
        self.hp_actual = self.hp_max

    def esta_vivo(self):
        return self.hp_actual > 0

    def recibir_dano(self, cantidad):
        self.hp_actual -= cantidad
        if self.hp_actual < 0:
            self.hp_actual = 0
        return self.hp_actual

    def calcular_dano_contra(self, oponente):
        base = self.ataque - oponente.defensa
        if base < 1:
            base = 1
        azar = random.uniform(0.85, 1.15)
        dano = round(base * azar)
        if dano < 1:
            dano = 1
        return dano

    def reiniciar(self):
        self.hp_actual = self.hp_max

    def stats_dict(self):
        return {"hp": self.hp_max, "ataque": self.ataque,
                "defensa": self.defensa, "velocidad": self.velocidad}

    def to_dict(self):
        return {"nombre": self.nombre, "fuente": self.fuente,
                "hp": self.hp_max, "ataque": self.ataque,
                "defensa": self.defensa, "velocidad": self.velocidad,
                "extra": self.extra}

    @classmethod
    def from_dict(cls, datos):
        return cls(nombre=datos.get("nombre", "Desconocido"),
                   hp=datos.get("hp", 100), ataque=datos.get("ataque", 50),
                   defensa=datos.get("defensa", 50), velocidad=datos.get("velocidad", 50),
                   fuente=datos.get("fuente", "manual"), extra=datos.get("extra", {}))

    def __repr__(self):
        return (f"{self.nombre} (HP:{self.hp_max} ATK:{self.ataque} "
                f"DEF:{self.defensa} VEL:{self.velocidad})")
