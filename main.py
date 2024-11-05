import os
import tkinter as tk
from tkinter import ttk, messagebox

def run_lab1():
    # Ocultar la ventana principal
    root.withdraw()

    # Ejecutar lab1.py en un nuevo proceso
    os.system("python lab1.py")

    # Mostrar la ventana principal nuevamente
    root.deiconify()

def run_lab2():
    # Ocultar la ventana principal
    root.withdraw()

    # Ejecutar lab2.py en un nuevo proceso
    os.system("python lab2.py")

    # Mostrar la ventana principal nuevamente
    root.deiconify()

def salir():
    root.destroy()

# Crear la ventana principal
root = tk.Tk()
root.title("Menú Principal")

# Establecer el tamaño de la ventana
root.geometry("400x300")

# Establecer el color de fondo de la ventana principal
root.configure(bg="#f0f0f0")

# Establecer un estilo personalizado para los botones
style = ttk.Style()
style.configure("TButton",
                font=("Helvetica", 12, "bold"),
                padding=10)
style.configure("TFrame", background="#f0f0f0")

# Crear el título
title_label = ttk.Label(root, text="Laboratorio 3: Arias - Guiñazu - Luna", font=("Helvetica", 16, "bold"))
title_label.pack(pady=20)

# Crear el marco para los botones
button_frame = ttk.Frame(root)
button_frame.pack(expand=True)

# Crear los botones
button1 = ttk.Button(button_frame, text="Compresión de archivos con Huffman", command=run_lab2)
button1.pack(pady=10, padx=20, fill='x')

button2 = ttk.Button(button_frame, text="Protección de archivos con Hamming", command=run_lab1)
button2.pack(pady=10, padx=20, fill='x')

button3 = ttk.Button(button_frame, text="Salir", command=salir)
button3.pack(pady=10, padx=20, fill='x')



# Iniciar el bucle de eventos
root.mainloop()