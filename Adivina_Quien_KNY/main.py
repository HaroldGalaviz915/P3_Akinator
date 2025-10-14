import json

def cargar_personajes(archivo):
    with open(archivo, "r", encoding="utf-8") as f:
        return json.load(f)

def hacer_pregunta(caracteristica):
    respuesta = ""
    while respuesta not in ["si" or "SI" or "Si", "no" or "NO" or "No"]:
        respuesta = input(f"¿El personaje {caracteristica.replace('_', ' ')}? (si/no): ").lower()
    return respuesta

def filtrar_personajes(personajes, caracteristica, respuesta):
    return {
        nombre: datos for nombre, datos in personajes.items()
        if datos.get(caracteristica) == respuesta
    }

def main():
    print(" Bienvenido a 'Adivina Quién: Kimetsu no Yaiba' ")
    print("Responde las preguntas con 'sí' o 'no' para que el sistema adivine el personaje.")
    print("-" * 60)

    personajes = cargar_personajes("personajes.json")

    caracteristicas = set()
    for datos in personajes.values():
        caracteristicas.update(datos.keys())

    for c in caracteristicas:
        if len(personajes) <= 1:
            break
        respuesta = hacer_pregunta(c)
        personajes = filtrar_personajes(personajes, c, respuesta)

        if len(personajes) == 0:
            print(" No encontré ningún personaje con esas respuestas.")
            return

    if len(personajes) == 1:
        print(f" ¡Tu personaje es {list(personajes.keys())[0]}!")
    else:
        print(" No estoy seguro, pero podría ser uno de estos:")
        for nombre in personajes.keys():
            print("-", nombre)

if __name__ == "__main__":
    main()