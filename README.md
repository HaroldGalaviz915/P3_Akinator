# P3_Akinator
Practica numero 3 de Sistemas Expertos, de el juego adivina quien con personajes del anime Kimetsu no Yaiba
# 🧠 Akinator Kimetsu no Yaiba

Un programa tipo *Akinator* que adivina personajes del anime **Kimetsu no Yaiba** mediante preguntas de "sí" o "no".  
Si no logra adivinar el personaje, aprende uno nuevo y guarda su información e imagen para futuras partidas.

---

## 📌 Características

- Adivinación de personajes humanos o demonios del anime.
- Aprendizaje dinámico de nuevos personajes si no se encuentran coincidencias.
- Registro de atributos personalizados de los personajes.
- Integración con la cámara para tomar fotos de nuevos personajes.
- Interfaz gráfica interactiva y amigable con **Tkinter**.
- Guardado de datos en formato **JSON** (`personajes_kimetsu.json`).

---

## 🛠 Tecnologías

- **Python 3.x**
- **Tkinter** → Interfaz gráfica.
- **PIL (Pillow)** → Manejo de imágenes.
- **OpenCV (cv2)** → Captura de imágenes desde la cámara.
- **JSON** → Almacenamiento de personajes y atributos.

---

## 📁 Archivos del proyecto

- `akinator_kimetsu.py` → Código principal del juego.
- `personajes_kimetsu.json` → Base de datos de personajes (se genera automáticamente si no existe).
- `imagenes_personajes/` → Carpeta donde se guardan las fotos de los personajes.

---

## 🚀 Cómo usarlo

1. Clonar o descargar el proyecto.
2. Instalar las dependencias necesarias:

```bash
pip install pillow opencv-python
