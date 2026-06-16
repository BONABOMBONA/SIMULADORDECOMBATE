"""
limpiar.py
Borra todos los personajes y combates de la base de datos, para empezar
de cero. Util cuando quedaron personajes de pruebas anteriores.

Uso:
    python3 limpiar.py
"""

from datos import nosql_simulacion as db


def main():
    print("Esto borrara TODOS los personajes y combates de la base.")
    respuesta = input("Escribe 'si' para continuar: ").strip().lower()
    if respuesta != "si":
        print("Cancelado.")
        return

    try:
        n1 = db.limpiar_personajes()
        n2 = db.limpiar_combates()
        print(f"Listo. Se borraron {n1} personajes y {n2} combates.")
        print("Ahora abre el programa y vuelve a cargar las fuentes que quieras.")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
