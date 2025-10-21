import json
import tkinter as tk
from tkinter import messagebox, simpledialog
from PIL import Image, ImageTk
import cv2
import os
import threading

# ==============================
# Funciones de manejo de datos
# ==============================

DATA_FILE = "personajes_kimetsu.json"
IMAGES_DIR = "imagenes_personajes"
os.makedirs(IMAGES_DIR, exist_ok=True)

def cargar_datos(archivo):
    try:
        with open(archivo, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"humanos": {}, "demonios": {}}

def filtrar_personajes(candidatos, respuestas):
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
    utiles = []
    for a in set().union(*[c.keys() for c in candidatos.values()]):
        if a in respuestas:
            continue
        valores = set([c[a] for c in candidatos.values() if a in c])
        if len(valores) > 1:
            utiles.append(a)
    return utiles

def get_all_attributes(candidatos):
    atributos = set()
    for personaje in candidatos.values():
        atributos.update(personaje.keys())
    return atributos

# ==============================
# Función para captura de cámara en hilo
# ==============================
def tomar_foto(nombre):
    def _captura():
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            messagebox.showerror("Error", "No se pudo abrir la cámara.")
            return
        messagebox.showinfo("Cámara", "Presiona 's' para capturar la foto o 'q' para salir.")
        while True:
            ret, frame = cap.read()
            if not ret:
                continue
            cv2.imshow("Presiona 's' para capturar", frame)
            key = cv2.waitKey(1)
            if key & 0xFF == ord('s'):
                ruta = os.path.join(IMAGES_DIR, f"{nombre}.jpg")
                cv2.imwrite(ruta, frame)
                break
            elif key & 0xFF == ord('q'):
                break
        cap.release()
        cv2.destroyAllWindows()
    threading.Thread(target=_captura, daemon=True).start()

# ==============================
# Interfaz principal
# ==============================
class AkinatorDinamico:
    def __init__(self, root):
        self.root = root
        self.root.title("Akinator Kimetsu no Yaiba 🎯")
        self.root.geometry("600x550")
        self.root.config(bg="#1c1c1c")

        self.data = cargar_datos(DATA_FILE)
        self.respuestas = {}
        self.candidatos = {}
        self.atributos_pendientes = []
        self.grupo = None
        self.candidato_final = None

        # UI
        self.titulo = tk.Label(root, text="Akinator Kimetsu no Yaiba 🔥",
                               font=("Arial", 18, "bold"), fg="white", bg="#1c1c1c")
        self.titulo.pack(pady=10)

        self.pregunta = tk.Label(root, text="", font=("Arial", 14),
                                 fg="white", bg="#1c1c1c", wraplength=580)
        self.pregunta.pack(pady=10)

        self.boton_si = tk.Button(root, text="Sí", command=lambda: self.responder("si"),
                                  width=10, bg="#2ecc71", fg="white", font=("Arial", 12, "bold"))
        self.boton_no = tk.Button(root, text="No", command=lambda: self.responder("no"),
                                  width=10, bg="#e74c3c", fg="white", font=("Arial", 12, "bold"))

        self.boton_si.pack(side="left", padx=60, pady=10)
        self.boton_no.pack(side="right", padx=60, pady=10)

        self.reiniciar_btn = tk.Button(root, text="🔄 Reiniciar", command=self.reiniciar,
                                       bg="#3498db", fg="white", font=("Arial", 11))
        self.reiniciar_btn.pack(side="bottom", pady=15)

        self.imagen_label = tk.Label(root, bg="#1c1c1c")
        self.imagen_label.pack(pady=10)

        self.iniciar()

    # ==============================
    # Inicio del juego
    # ==============================
    def iniciar(self):
        self.respuestas.clear()
        self.candidatos.clear()
        self.atributos_pendientes.clear()
        self.grupo = None
        self.candidato_final = None
        self.boton_si.config(state="normal")
        self.boton_no.config(state="normal")
        self.pregunta.config(text="¿Es un demonio?")
        self.imagen_label.config(image="")

    # ==============================
    # Manejar respuesta
    # ==============================
    def responder(self, r):
        # Si estamos en la etapa de confirmar candidato final
        if self.candidato_final:
            if r == "si":
                self.pregunta.config(text=f"🥳 ¡Lo adiviné! Es {self.candidato_final}!")
                self.mostrar_imagen(self.candidato_final)
            else:
                messagebox.showinfo("Aprender personaje", "¡Vamos a aprender sobre tu personaje!")
                self.aprender_personaje()
            self.candidato_final = None
            return

        if self.grupo is None:
            self.grupo = "demonios" if r == "si" else "humanos"
            if self.grupo not in self.data:
                messagebox.showerror("Error", f"No se encontró el grupo '{self.grupo}' en el JSON.")
                self.iniciar()
                return
            self.candidatos = self.data[self.grupo].copy()
            self.atributos_pendientes = atributos_utiles(self.candidatos, self.respuestas)
            self.siguiente_pregunta()
            return

        if not self.atributos_pendientes:
            return

        # Guardar respuesta del atributo actual
        atributo = self.atributos_pendientes.pop(0)
        self.respuestas[atributo] = r

        # Filtrar candidatos
        self.candidatos = filtrar_personajes(self.candidatos, self.respuestas)

        # Si queda un solo candidato
        if len(self.candidatos) == 1:
            self.candidato_final = list(self.candidatos.keys())[0]
            self.pregunta.config(text=f"🎯 ¿Tu personaje es {self.candidato_final}?")
            return

        # Si no hay candidatos
        if len(self.candidatos) == 0:
            messagebox.showinfo("No encontrado", "No encontré ningún personaje con esas respuestas.")
            self.aprender_personaje()
            return

        # Actualizar atributos pendientes
        self.atributos_pendientes = atributos_utiles(self.candidatos, self.respuestas)
        self.siguiente_pregunta()

    # ==============================
    # Siguiente pregunta
    # ==============================
    def siguiente_pregunta(self):
        while self.atributos_pendientes:
            atributo = self.atributos_pendientes[0]

            # Saltar atributos irrelevantes según el grupo
            if self.grupo == "humanos" and "luna" in atributo:
                self.atributos_pendientes.pop(0)
                continue
            if self.grupo == "demonios" and ("pilar" in atributo or "respira" in atributo):
                self.atributos_pendientes.pop(0)
                continue

            self.pregunta.config(text=f"¿{atributo.replace('_', ' ')}?")
            break

        # Si no quedan atributos y hay varios candidatos
        if not self.atributos_pendientes and len(self.candidatos) > 1:
            posibles = "\n".join(self.candidatos.keys())
            messagebox.showinfo("Posibles personajes", f"No estoy seguro, pero podría ser:\n\n{posibles}")
            self.iniciar()

    # ==============================
    # Mostrar imagen
    # ==============================
    def mostrar_imagen(self, nombre):
        path = os.path.join(IMAGES_DIR, f"{nombre}.jpg")
        if os.path.exists(path):
            img = Image.open(path)
            img = img.resize((200, 250))
            self.tkimg = ImageTk.PhotoImage(img)
            self.imagen_label.config(image=self.tkimg)
        else:
            self.imagen_label.config(image="")

    # ==============================
    # Aprender personaje nuevo
    # ==============================
    def aprender_personaje(self):
        nombre = simpledialog.askstring("Aprender personaje", "¿Cuál era el personaje que pensabas?")
        if not nombre:
            self.iniciar()
            return

        if nombre in self.data[self.grupo]:
            messagebox.showinfo("Ya existe", f"El personaje '{nombre}' ya está en la base de datos.")
            self.iniciar()
            return

        atributos_nuevos = {}
        todos_atributos = get_all_attributes(self.data[self.grupo])
        for atributo in todos_atributos:
            r = messagebox.askquestion("Atributo", f"¿{atributo.replace('_',' ')}?")
            atributos_nuevos[atributo] = "si" if r == "yes" else "no"

        self.data[self.grupo][nombre] = atributos_nuevos

        # Tomar foto en hilo
        if messagebox.askyesno("Imagen", f"¿Deseas tomar una foto para {nombre}?"):
            tomar_foto(nombre)

        # Guardar JSON
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)

        messagebox.showinfo("Aprendido", f"✅ He aprendido sobre '{nombre}' 🎉")
        self.iniciar()

    # ==============================
    # Reiniciar juego
    # ==============================
    def reiniciar(self):
        self.iniciar()


# ==============================
# Ejecutar aplicación
# ==============================
if __name__ == "__main__":
    root = tk.Tk()
    app = AkinatorDinamico(root)
    root.mainloop()
