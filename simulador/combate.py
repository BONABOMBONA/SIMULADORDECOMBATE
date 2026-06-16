"""
combate.py
Logica del combate por turnos entre dos personajes.
"""

import random


def _orden_de_ataque(p1, p2):
    if p1.velocidad > p2.velocidad:
        return p1, p2
    if p2.velocidad > p1.velocidad:
        return p2, p1
    return random.choice([(p1, p2), (p2, p1)])


def combatir(p1, p2, registrar=False, max_turnos=200):
    p1.reiniciar()
    p2.reiniciar()
    historial = {p1.nombre: [p1.hp_actual], p2.nombre: [p2.hp_actual]}
    dano_total = {p1.nombre: 0, p2.nombre: 0}
    if registrar:
        print(f"\n==== COMBATE: {p1.nombre} vs {p2.nombre} ====")
    turno = 0
    while p1.esta_vivo() and p2.esta_vivo() and turno < max_turnos:
        turno += 1
        primero, segundo = _orden_de_ataque(p1, p2)
        dano = primero.calcular_dano_contra(segundo)
        segundo.recibir_dano(dano)
        dano_total[primero.nombre] += dano
        if registrar:
            print(f"Turno {turno}: {primero.nombre} hace {dano} de dano -> {segundo.nombre} queda en {segundo.hp_actual} HP")
        if segundo.esta_vivo():
            dano = segundo.calcular_dano_contra(primero)
            primero.recibir_dano(dano)
            dano_total[segundo.nombre] += dano
            if registrar:
                print(f"Turno {turno}: {segundo.nombre} hace {dano} de dano -> {primero.nombre} queda en {primero.hp_actual} HP")
        historial[p1.nombre].append(p1.hp_actual)
        historial[p2.nombre].append(p2.hp_actual)
    if p1.esta_vivo() and not p2.esta_vivo():
        ganador, perdedor = p1.nombre, p2.nombre
    elif p2.esta_vivo() and not p1.esta_vivo():
        ganador, perdedor = p2.nombre, p1.nombre
    else:
        if p1.hp_actual >= p2.hp_actual:
            ganador, perdedor = p1.nombre, p2.nombre
        else:
            ganador, perdedor = p2.nombre, p1.nombre
    if registrar:
        print(f"==== GANADOR: {ganador} (en {turno} turnos) ====\n")
    return {"ganador": ganador, "perdedor": perdedor, "turnos": turno,
            "dano_total": dano_total, "historial": historial}
