"""
normalizador.py
Traduce los datos crudos del scraper a los 4 stats comunes del combate
y los escala a 1-255 con Min-Max. Hace que personajes de cualquier fuente
puedan pelear de forma justa entre si.
"""

RANGO_MIN = 1
RANGO_MAX = 255


def _mapear_registro(registro):
    tipo = registro["tipo"]
    s = registro["stats_crudos"]
    if tipo == "pokemon":
        return {"hp": s.get("hp", 0), "ataque": s.get("ataque", 0),
                "defensa": s.get("defensa", 0), "velocidad": s.get("velocidad", 0)}
    elif tipo == "superheroes":
        return {"hp": s.get("durability", 0), "ataque": s.get("strength", 0),
                "defensa": s.get("combat", 0), "velocidad": s.get("speed", 0)}
    elif tipo == "paises":
        poblacion = s.get("poblacion", 0)
        area = s.get("area", 1) or 1
        densidad = poblacion / area
        return {"hp": poblacion, "ataque": area,
                "defensa": densidad, "velocidad": 1.0 / area}
    elif tipo == "lol":
        return {"hp": s.get("hp", 0), "ataque": s.get("ataque", 0),
                "defensa": s.get("defensa", 0), "velocidad": s.get("velocidad", 0)}
    else:
        valores = list(s.values())
        while len(valores) < 4:
            valores.append(0)
        return {"hp": valores[0], "ataque": valores[1],
                "defensa": valores[2], "velocidad": valores[3]}


def _min_max(valores, nuevo_min=RANGO_MIN, nuevo_max=RANGO_MAX):
    vmin = min(valores)
    vmax = max(valores)
    if vmax == vmin:
        medio = (nuevo_min + nuevo_max) // 2
        return [medio for _ in valores]
    escalados = []
    for v in valores:
        e = (v - vmin) / (vmax - vmin) * (nuevo_max - nuevo_min) + nuevo_min
        escalados.append(int(round(e)))
    return escalados


def normalizar(registros):
    if not registros:
        return []
    mapeados = []
    for r in registros:
        mapeados.append({
            "nombre": r["nombre"],
            "fuente": r.get("fuente_url", r.get("tipo", "manual")),
            "comunes": _mapear_registro(r),
            "extra": r["stats_crudos"],
        })
    for stat in ["hp", "ataque", "defensa", "velocidad"]:
        valores = [m["comunes"][stat] for m in mapeados]
        escalados = _min_max(valores)
        for m, e in zip(mapeados, escalados):
            m["comunes"][stat] = e
    resultado = []
    for m in mapeados:
        resultado.append({
            "nombre": m["nombre"], "fuente": m["fuente"],
            "hp": m["comunes"]["hp"], "ataque": m["comunes"]["ataque"],
            "defensa": m["comunes"]["defensa"], "velocidad": m["comunes"]["velocidad"],
            "extra": m["extra"],
        })
    return resultado


def normalizar_manual(nombre, hp, ataque, defensa, velocidad):
    def recortar(v):
        v = int(v)
        if v < RANGO_MIN:
            return RANGO_MIN
        if v > RANGO_MAX:
            return RANGO_MAX
        return v
    return {"nombre": nombre, "fuente": "manual",
            "hp": recortar(hp), "ataque": recortar(ataque),
            "defensa": recortar(defensa), "velocidad": recortar(velocidad),
            "extra": {}}
