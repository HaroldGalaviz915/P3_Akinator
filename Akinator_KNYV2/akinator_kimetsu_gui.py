import json
import os
import tkinter as tk
from tkinter import simpledialog
from PIL import Image, ImageTk
import cv2

# =======================================================
# 🧠 AKINATOR KIMETSU NO YAIBA
# -------------------------------------------------------
# Programa tipo "Akinator" que adivina personajes del
# anime Kimetsu no Yaiba mediante preguntas de "sí" o "no".
# Si no logra adivinar el personaje, aprende uno nuevo y
# guarda su información e imagen para futuras partidas.
# =======================================================


# ==============================
# Funciones de manejo de datos
# ==============================
def cargar_datos(archivo):
    """
    Carga el archivo JSON que contiene los personajes.
    Si no existe, crea una estructura vacía con 'humanos' y 'demonios'.
    """
    try:
        with open(archivo, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"humanos": {}, "demonios": {}}


def filtrar_personajes(candidatos, respuestas):
    """
    Filtra los personajes que coinciden con las respuestas dadas.
    Solo se mantienen aquellos cuyos atributos coinciden con las respuestas.
    """
    resultado = {}
    for nombre, atributos in candidatos.items():
        coincide = True
        for a, v in respuestas.items():
            if a in atributos and atributos[a] != v:
                coincide = False
                break
        if coincide:
            resultado[nombre] = atributos
    return resultado


def atributos_utiles(candidatos, respuestas):
    """
    Determina qué atributos todavía no se han preguntado
    y que pueden servir para distinguir a los personajes restantes.
    """
    utiles = []
    for a in set().union(*[c.keys() for c in candidatos.values()]):
        if a in respuestas:
            continue
        valores = set([c[a] for c in candidatos.values() if a in c])
        if len(valores) > 1:
            utiles.append(a)
    return utiles


def get_all_attributes(candidatos):
    """
    Devuelve todos los atributos posibles dentro del grupo de personajes.
    """
    atributos = set()
    for personaje in candidatos.values():
        atributos.update(personaje.keys())
    return atributos


# ==============================
# Interfaz principal con Tkinter
# ==============================
class AkinatorDinamico:
    """
    Clase principal que maneja la lógica del juego y la interfaz gráfica.
    """

    def __init__(self, root):
        # Configuración de la ventana principal
        self.root = root
        self.root.title("Akinator Kimetsu no Yaiba 🎯")
        self.root.geometry("600x500")
        self.root.config(bg="#1c1c1c")

        # Cargar los datos desde el archivo JSON
        self.data = cargar_datos("personajes_kimetsu.json")

        # Variables de estado del juego
        self.respuestas = {}
        self.candidatos = {}
        self.atributos_pendientes = []
        self.grupo = None
        self.personaje_actual = None

        # ======================
        # Elementos de la Interfaz
        # ======================
        self.titulo = tk.Label(root, text="Akinator Kimetsu no Yaiba 🔥",
                               font=("Arial", 18, "bold"), fg="white", bg="#1c1c1c")
        self.titulo.pack(pady=10)

        self.pregunta = tk.Label(root, text="", font=("Arial", 14),
                                 fg="white", bg="#1c1c1c", wraplength=580)
        self.pregunta.pack(pady=10)

        # Etiqueta para mostrar imágenes
        self.imagen_label = tk.Label(root, bg="#1c1c1c")
        self.imagen_label.pack(pady=10)

        # Botones de respuesta
        self.boton_si = tk.Button(root, text="Sí", command=lambda: self.responder("si"),
                                  width=10, bg="#2ecc71", fg="white", font=("Arial", 12, "bold"))
        self.boton_no = tk.Button(root, text="No", command=lambda: self.responder("no"),
                                  width=10, bg="#e74c3c", fg="white", font=("Arial", 12, "bold"))
        self.boton_si.pack(side="left", padx=50, pady=10)
        self.boton_no.pack(side="right", padx=50, pady=10)

        # Botón de reinicio
        self.reiniciar_btn = tk.Button(root, text="🔄 Reiniciar", command=self.reiniciar,
                                       bg="#3498db", fg="white", font=("Arial", 11))
        self.reiniciar_btn.pack(side="bottom", pady=10)

        # Iniciar el juego
        self.iniciar()

    # ==============================
    # Inicio del juego
    # ==============================
    def iniciar(self):
        """
        Reinicia todas las variables y comienza preguntando si el personaje es un demonio.
        """
        self.respuestas.clear()
        self.candidatos.clear()
        self.atributos_pendientes.clear()
        self.grupo = None
        self.personaje_actual = None
        self.boton_si.config(state="normal")
        self.boton_no.config(state="normal")
        self.pregunta.config(text="¿Es un demonio?")
        self.imagen_label.config(image="")

    # ==============================
    # Manejo de respuestas
    # ==============================
    def responder(self, r):
        """
        Procesa la respuesta del usuario ("si" o "no") y actualiza el estado del juego.
        """
        # Primera pregunta: define si es humano o demonio
        if self.grupo is None:
            self.grupo = "demonios" if r == "si" else "humanos"
            self.candidatos = self.data.get(self.grupo, {}).copy()
            self.atributos_pendientes = atributos_utiles(self.candidatos, self.respuestas)
            self.siguiente_pregunta()
            return

        # Si ya se definió el grupo, procesar las respuestas siguientes
        if not self.atributos_pendientes:
            return

        atributo = self.atributos_pendientes.pop(0)
        self.respuestas[atributo] = r
        self.candidatos = filtrar_personajes(self.candidatos, self.respuestas)

        # Caso 1: Queda un solo personaje
        if len(self.candidatos) == 1:
            self.personaje_actual = list(self.candidatos.keys())[0]
            self.pregunta.config(text=f"🎯 Tu personaje es {self.personaje_actual}!")
            self.mostrar_imagen(self.personaje_actual)
            self.boton_si.config(state="disabled")
            self.boton_no.config(state="disabled")
            return

        # Caso 2: No hay coincidencias → aprender personaje nuevo
        if len(self.candidatos) == 0:
            self.aprender_personaje()
            return

        # Caso 3: Aún quedan varios → seguir preguntando
        self.atributos_pendientes = atributos_utiles(self.candidatos, self.respuestas)
        self.siguiente_pregunta()

    # ==============================
    # Hacer la siguiente pregunta
    # ==============================
    def siguiente_pregunta(self):
        """
        Escoge el siguiente atributo a preguntar, evitando atributos que no aplican al grupo.
        """
        while self.atributos_pendientes:
            atributo = self.atributos_pendientes[0]
            # Evita atributos irrelevantes
            if self.grupo == "humanos" and "luna" in atributo:
                self.atributos_pendientes.pop(0)
                continue
            if self.grupo == "demonios" and ("pilar" in atributo or "respira" in atributo):
                self.atributos_pendientes.pop(0)
                continue
            # Mostrar la pregunta
            self.pregunta.config(text=f"¿{atributo.replace('_',' ')}?")
            break

        # Si no hay más preguntas posibles, muestra posibles coincidencias
        if not self.atributos_pendientes and len(self.candidatos) > 1:
            posibles = "\n".join(self.candidatos.keys())
            self.pregunta.config(text=f"No estoy seguro, pero podría ser:\n{posibles}")
            self.boton_si.config(state="disabled")
            self.boton_no.config(state="disabled")

    # ==============================
    # Mostrar imagen del personaje
    # ==============================
    def mostrar_imagen(self, nombre):
        """
        Muestra la imagen del personaje adivinado si existe en la carpeta.
        """
        carpeta = "imagenes_personajes"
        os.makedirs(carpeta, exist_ok=True)
        ruta = os.path.join(carpeta, f"{nombre}.jpg")
        if os.path.exists(ruta):
            img = Image.open(ruta).resize((250, 250))
            self.img_tk = ImageTk.PhotoImage(img)
            self.imagen_label.config(image=self.img_tk)
        else:
            self.imagen_label.config(image="")

    # ==============================
    # Aprender personaje nuevo
    # ==============================
    def aprender_personaje(self):
        """
        Si el programa no logra adivinar, pide los datos de un nuevo personaje y lo guarda.
        """
        nombre = simpledialog.askstring("Aprender personaje", "¿Cuál era el personaje que pensabas?")
        if not nombre:
            self.iniciar()
            return

        # Verificar si ya existe
        if nombre in self.data[self.grupo]:
            self.pregunta.config(text=f"El personaje '{nombre}' ya existe en la base de datos.")
            return

        atributos_nuevos = {}
        todos_atributos = get_all_attributes(self.data[self.grupo])

        # Preguntar por los atributos conocidos
        for atributo in todos_atributos:
            r = simpledialog.askstring("Atributo", f"¿{atributo.replace('_',' ')}? (si/no)")
            if not r: 
                r = "no"
            atributos_nuevos[atributo] = "si" if r.lower() == "si" else "no"

        # Permitir agregar nuevos atributos personalizados
        while True:
            extra = simpledialog.askstring("Atributo extra", "Agregar nuevo atributo personalizado (Enter para omitir)")
            if not extra:
                break
            r = simpledialog.askstring("Atributo", f"¿{extra.replace('_',' ')}? (si/no)")
            if not r: 
                r = "no"
            atributos_nuevos[extra] = "si" if r.lower() == "si" else "no"

        # Guardar el nuevo personaje
        self.data[self.grupo][nombre] = atributos_nuevos

        # Tomar una foto con la cámara
        self.tomar_foto(nombre)

        # Guardar cambios en el archivo JSON
        with open("personajes_kimetsu.json", "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)

        # Confirmar aprendizaje
        self.pregunta.config(text=f"✅ He aprendido sobre '{nombre}' 🎉")
        self.iniciar()

    # ==============================
    # Tomar foto con cámara
    # ==============================
    def tomar_foto(self, nombre):
        """
        Usa la cámara para tomar una foto del personaje nuevo.
        Guarda la imagen en la carpeta 'imagenes_personajes'.
        """
        carpeta = "imagenes_personajes"
        os.makedirs(carpeta, exist_ok=True)
        ruta = os.path.join(carpeta, f"{nombre}.jpg")
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            return
        ret, frame = cap.read()
        if ret:
            cv2.imshow(f"Toma la foto de {nombre}. Pulsa 's' para guardar", frame)
            key = cv2.waitKey(0)
            if key & 0xFF == ord('s'):
                cv2.imwrite(ruta, frame)
        cap.release()
        cv2.destroyAllWindows()

    # ==============================
    # Reiniciar el juego
    # ==============================
    def reiniciar(self):
        """
        Reinicia el juego completamente para comenzar una nueva partida.
        """
        self.iniciar()


# ==============================
# Ejecutar la aplicación
# ==============================
if __name__ == "__main__":
    """
    Punto de entrada del programa. 
    Crea la ventana principal de Tkinter y ejecuta el Akinator.
    """
    root = tk.Tk()
    app = AkinatorDinamico(root)
    root.mainloop()
