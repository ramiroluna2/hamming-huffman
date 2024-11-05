# --- Laboratorio 1 - Arias, Juan / Guiñazu, Joaquin / Luna, Ramiro ---
# Cada procedimiento utiliza un archivo fuente, y guarda el archivo resultante.
# Cada procedimiento acepta únicamente archivos válidos.

import math
import random
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import os
import base64


ruta_desproteger_sin_errores_sin_corregir = None
ruta_desproteger_sin_errores_con_corregir = None
ruta_desproteger_con_errores_sin_corregir = None
ruta_desproteger_con_errores_con_corregir = None


stats_data = {
    "Archivo original": {
        "Peso en kb": "-",
        "Cantidad de errores simples": "-",
        "Cantidad de errores dobles": "-"
    },
    "Archivo protegido": {
        "Peso en kb": "-",
        "Cantidad de errores simples": "-",
        "Cantidad de errores dobles": "-"
    },
    "Archivo protegido con errores": {
        "Peso en kb": "-",
        "Cantidad de errores simples": "-",
        "Cantidad de errores dobles": "-"
    },
    "Desprotegido sin errores corregido": {
        "Peso en kb": "-",
        "Cantidad de errores simples": "-",
        "Cantidad de errores dobles": "-"
    },
    "Desprotegido sin errores sin corregir": {
        "Peso en kb": "-",
        "Cantidad de errores simples": "-",
        "Cantidad de errores dobles": "-"
    },
    "Desprotegido con errores corregido": {
        "Peso en kb": "-",
        "Cantidad de errores simples": "-",
        "Cantidad de errores dobles": "-"
    },
    "Desprotegido con errores sin corregir": {
        "Peso en kb": "-",
        "Cantidad de errores simples": "-",
        "Cantidad de errores dobles": "-"
    }
}


# --- Funciones para el manejo de archivos y Hamming ---



def proteger_archivo_txt(archivo, tamaño_bloque):
    """
    Codifica un archivo de texto utilizando el código Hamming.

    Args:
        archivo (str): El contenido del archivo de texto.
        tamaño_bloque (int): El tamaño del bloque a utilizar en el código Hamming.

    Returns:
        list: Una lista de cadenas binarias, donde cada cadena representa un bloque codificado.
    """

    # Convertir el archivo a una secuencia binaria
    secuencia_binaria = ''.join(format(ord(caracter), '08b') for caracter in archivo)
    

    # Dividir la secuencia binaria en bloques
    bloques_hamming = []
    while secuencia_binaria:
        bloque_aux = ['0'] * (tamaño_bloque + 1)  # Inicializar el bloque con ceros
        for i in range(1, tamaño_bloque + 1):
            # Asignar bits de datos a las posiciones adecuadas del bloque
            if (i & (i - 1)) != 0:  # Verificar si i es una potencia de 2
                if secuencia_binaria:
                    bloque_aux[i] = secuencia_binaria[0]
                    secuencia_binaria = secuencia_binaria[1:]
        bloques_hamming.append(''.join(bloque_aux[1:]))  # Eliminar el primer bit y convertir a cadena

    # Calcular los bits de paridad para cada bloque
    for bloque in bloques_hamming:
        bloque_enteros = [int(bit) for bit in bloque]  # Convertir a lista de enteros
        for i in range(len(bloque_enteros) - 1):
            if i & (i + 1) == 0:  # Verificar si i es una potencia de 2
                paridad = 0
                for j in range(i, len(bloque_enteros), 2 * (i + 1)):
                    for k in range(j, min(j + (i + 1), len(bloque_enteros))):
                        paridad ^= bloque_enteros[k]  # Calcular la paridad XOR
                bloque_enteros[i] = paridad  # Asignar la paridad al bit de paridad
        # Calcular el bit de paridad final
        paridad_final = 0
        for i in range(len(bloque_enteros)):
            paridad_final ^= bloque_enteros[i]
        bloque_enteros[tamaño_bloque - 1] = paridad_final
        bloques_hamming[bloques_hamming.index(bloque)] = ''.join(str(bit) for bit in bloque_enteros)  # Convertir a cadena
    return bloques_hamming


def desproteger_archivo_txt(bloques, tamaño_bloque, correccion):
    """
    Decodifica un archivo codificado con Hamming.

    Args:
        bloques (list): Una lista de cadenas binarias, donde cada cadena representa un bloque codificado.
        tamaño_bloque (int): El tamaño del bloque utilizado en el código Hamming.
        correccion (bool): Si True, corrige errores durante la decodificación.

    Returns:
        str: El archivo de texto decodificado.
    """

    errores_simples = 0
    errores_dobles = 0  # Inicializar el contador de errores dobles

    # Corregir errores si se especificó la corrección
    if correccion:
        for bloque_idx, bloque in enumerate(bloques):
            control_cod = []
            control_decod = []                 
            aux = 0
            bloqueaux = bloque
            for i in range(tamaño_bloque - 1):
                if i & (i + 1) == 0:
                    paridad = 0
                    control_cod.append(int(bloque[i]))  # Obtener el bit de paridad
                    for j in range(i, len(bloque), 2 * (i + 1)):
                        for k in range(j, min(j + (i + 1), len(bloque))):
                            paridad ^= int(bloque[k])  # Calcular la paridad XOR
                    paridad ^= int(bloque[i])  # Incluir el bit de paridad en el cálculo
                    control_decod.append(paridad)  # Almacenar la paridad calculada
                aux ^= int(bloque[i])

            # Determinar la posición del error
            error_binario = ""
            for j in range(len(control_cod)):
                if control_cod[j] != control_decod[j]:
                    error_binario =  "1" + error_binario   # Error encontrado
                else:
                    error_binario =  "0" + error_binario   # Error encontrado
            error_entero = int(error_binario, 2)  # Convertir a entero
            if error_entero != 0:
                if (aux == int(bloque[tamaño_bloque - 1])):
                    errores_dobles += 1  # Incrementar el contador de errores dobles
                else:
                    errores_simples += 1  # Incrementar el contador de errores simples
                    # Corregir el error en el bloque
                    bloque = bloque[:error_entero - 1] + str(int(bloque[error_entero - 1]) ^ 1) + bloque[error_entero:]
                    bloques[bloque_idx] = bloque

    # Combinar los bloques en una secuencia binaria
    binario = ""
    for bloque in bloques:
        for i in range(0, len(bloque)):
            if (i + 1 & i) != 0:  # Verificar si i no es una potencia de 2 (bit de datos)
                binario += bloque[i]

    # Convertir la secuencia binaria a texto
    texto = ""
    for i in range(0, len(binario), 8):
        byte = binario[i:i + 8]  # Obtener un byte de la secuencia
        if not all(bit == "0" for bit in byte):  # Si el byte es todo ceros, termina 
            caracter = chr(int(byte, 2))  # Convertir a caracter
            texto += caracter
    return texto, errores_simples, errores_dobles


def blocks_to_text(bloques):
    """
    Convierte una lista de bloques binarios a texto.

    Args:
        bloques (list): Una lista de cadenas binarias, donde cada cadena representa un bloque.

    Returns:
        str: El texto reconstruido a partir de los bloques.
    """
    binario = ""
    for bloque in bloques:
        for i in range(0, len(bloque)):
            binario += bloque[i]  # Concatenar los bloques en una secuencia binaria
    texto = ""
    for i in range(0, len(binario), 8):
        byte = binario[i:i + 8]  # Obtener un byte de la secuencia
        caracter = chr(int(byte, 2))  # Convertir a caracter
        texto += caracter
    return texto


def bits_to_blocks(cadena_bits, tamaño_bloque):
    """
    Divide una cadena de bits en bloques de tamaño específico.

    Args:
        cadena_bits (str): La cadena de bits a dividir.
        tamaño_bloque (int): El tamaño del bloque deseado.

    Returns:
        list: Una lista de bloques de bits.
    """
    bloques = []
    for i in range(0, len(cadena_bits), tamaño_bloque):
        bloque = cadena_bits[i:i + tamaño_bloque]
        bloques.append(bloque)
    return bloques


def char_to_binary(text):
    """
    Convierte una cadena de texto a una cadena de bits.

    Args:
        text (str): La cadena de texto a convertir.

    Returns:
        str: La cadena de bits resultante.
    """
    binary_text = ''
    for char in text:
        binary_char = bin(ord(char))[2:].zfill(8)  # Convertir a binario, eliminar '0b', rellenar con ceros a 8 dígitos
        binary_text += binary_char
    return binary_text


def introducir_errores(bloques, probabilidad_simple, probabilidad_doble):
    """
    Introduce errores aleatorios en los bloques codificados, considerando probabilidades simple y doble.
    Si se introduce un error simple, no se introduce un error doble en el mismo bloque.

    Args:
        bloques (list): Una lista de bloques codificados.
        probabilidad_simple (float): Probabilidad de introducir un error simple (0.0 - 1.0).
        probabilidad_doble (float): Probabilidad de introducir un error doble (0.0 - 1.0).

    Returns:
        list: La lista de bloques con errores introducidos.
    """
    bloques_con_error = []
    excep = '00101101'  # MANEJO DE ERROR DE CODIFICACIÓN UTF 
    count = 0
    for bloque in bloques:
        prob = random.random()

        if (prob < (probabilidad_simple - probabilidad_doble) and probabilidad_doble != 0):
            count = count + 1
            err1 = random.randint(0, int(len(bloque)) - 1)  # Posición del primer error
            err2 = random.randint(0, int(len(bloque)) - 1)  # Posición del segundo error
            # Asegurar que las posiciones son distintas
            while err1 == err2:
                err2 = random.randint(0, int(len(bloque)) - 1)
            for i in range(len(bloque)):
                if i == err1 or i == err2:
                    # Introducir un error en la posición i
                    bloque = bloque[:i] + str((int(bloque[i]) ^ 1)) + bloque[i + 1:]

        elif prob < probabilidad_simple:
            err = random.randint(0, int(len(bloque)) - 1)  # Posición aleatoria del error
            while (bloque == excep and err == 2):
                err = random.randint(0, int(len(bloque)) - 1)  # Posición aleatoria del error
            for i in range(len(bloque)):
                if i == err:
                    # Introducir un error en la posición i
                    bloque = bloque[:i] + str((int(bloque[i]) ^ 1)) + bloque[i + 1:]
        
        bloques_con_error.append(bloque)
        print(count)
    return bloques_con_error


def actualizar_stats_original(ruta_archivo):
    """Actualiza las estadísticas del archivo original."""
    if ruta_archivo:
        stats_data["Archivo original"]["Peso en kb"] = os.path.getsize(ruta_archivo) / 1024
    else:
        stats_data["Archivo original"]["Peso en kb"] = "-"

def actualizar_stats_protegido(peso):
    """Actualiza las estadísticas del archivo original."""
    stats_data["Archivo protegido"]["Peso en kb"] = peso


def actualizar_stats_err(peso):
    """Actualiza las estadísticas del archivo original."""
    stats_data["Archivo protegido con errores"]["Peso en kb"] = peso


def actualizar_stats_desproteger_sin_errores(ruta_archivo, correccion):
    """Actualiza las estadísticas del archivo desprotegido sin errores."""
    global ruta_desproteger_sin_errores_sin_corregir, ruta_desproteger_sin_errores_con_corregir
    key = "Desprotegido sin errores sin corregir" if not correccion else "Desprotegido sin errores corregido"
    if ruta_archivo:
        stats_data[key]["Peso en kb"] = os.path.getsize(ruta_archivo) / 1024
        # ... (Agregar lógica para contar errores simples y dobles, si es necesario)
    else:
        stats_data[key]["Peso en kb"] = "-"

def actualizar_stats_desproteger_con_errores(ruta_archivo, correccion):
    """Actualiza las estadísticas del archivo desprotegido con errores."""
    global ruta_desproteger_con_errores_sin_corregir, ruta_desproteger_con_errores_con_corregir
    key = "Desprotegido con errores sin corregir" if not correccion else "Desprotegido con errores corregido"
    if ruta_archivo:
        stats_data[key]["Peso en kb"] = os.path.getsize(ruta_archivo) / 1024
        # ... (Agregar lógica para contar errores simples y dobles, si es necesario)
    else:
        stats_data[key]["Peso en kb"] = "-"




# --- Funciones para la interfaz gráfica ---

def seleccionar_archivo():
    """
    Permite al usuario seleccionar un archivo de texto.
    """
    global archivo_texto
    global archivo
    global nombre_archivo_prot
    global nombre_archivo_error

    archivo = filedialog.askopenfilename(filetypes=[("Archivos de texto", "*.txt"), ("Archivos codificados", "*.HA1; *.HA2; *.HA3; *.HE1; *.HE2; *.HE3"), ("Archivos Huffman", "*.huf")])
    if archivo:
        try:
            with open(archivo, 'r', encoding='utf-8') as f:
                archivo_texto = f.read()
            actualizar_stats_original(archivo)
            # Deshabilitar botones según la extensión del archivo seleccionado
            _, extension = os.path.splitext(archivo)
            if extension.upper() in (".huf"):
                label_archivo.config(text=f"Archivo '{os.path.basename(archivo)}' cargado (Huffman)")
            elif extension.upper() in (".HA1", ".HA2", ".HA3"):
                boton_proteger.config(state=tk.DISABLED)
                nombre_archivo_prot = archivo
                label_archivo.config(text=f"Archivo '{os.path.basename(archivo)}' cargado (Protegido)")
            elif extension.upper() in (".HE1", ".HE2", ".HE3"):
                boton_proteger.config(state=tk.DISABLED)
                boton_introducir_errores.config(state=tk.DISABLED)
                nombre_archivo_error = archivo
                label_archivo.config(text=f"Archivo '{os.path.basename(archivo)}' cargado (Protegido con errores)")
                # Actualizar el dropdown de desproteger
                dropdown_desproteger.set("Archivo con errores")  # Selecciona la opción con errores
                dropdown_menu_desproteger["menu"].entryconfigure(0, state=tk.DISABLED) # Deshabilita la opción "Archivo sin errores"
            else:
                boton_proteger.config(state=tk.NORMAL)
                boton_introducir_errores.config(state=tk.NORMAL)
                label_archivo.config(text=f"Archivo '{os.path.basename(archivo)}' cargado")
                # Restablecer el dropdown de desproteger
                dropdown_desproteger.set("Archivo sin errores")
                dropdown_menu_desproteger["menu"].entryconfigure(0, state=tk.NORMAL)  # Habilita la opción "Archivo sin errores"
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar el archivo: {e}")

        boton_seleccionar.pack_forget()  # Ocultar el botón de seleccionar archivo
def proteger_archivo():
    """
    Maneja la acción de proteger un archivo de texto.
    """
    try: 
        if archivo_texto:
            tamaño_bloque = int(dropdown_tamaño_bloque.get())
            bloques_protegidos = proteger_archivo_txt(archivo_texto, tamaño_bloque)
            extension = ".HA1" if tamaño_bloque == 8 else ".HA2" if tamaño_bloque == 4096 else ".HA3"
            global nombre_archivo_prot
            nombre_archivo_prot = f"{os.path.basename(archivo)}-protected{extension}"
            if nombre_archivo_prot:
                cadena = ""
                with open(nombre_archivo_prot, 'w', encoding="utf-8") as f:
                    for bloque in bloques_protegidos:
                        cadena = cadena + bloque
                    byte_array = int(cadena, 2).to_bytes((len(cadena) + 7) // 8, byteorder='big')
                    base64_encoded = base64.b64encode(byte_array).decode('utf-8')
                    f.write(base64_encoded)
                peso = os.path.getsize(nombre_archivo_prot) / 1024
                actualizar_stats_protegido(peso)

                messagebox.showinfo("Proteger archivo", f"Archivo protegido guardado como '{nombre_archivo_prot}'")
        else:
            messagebox.showerror("Error", "Debe seleccionar un archivo primero.")
    except Exception:
        messagebox.showwarning("Error", "Debe seleccionar un archivo primero.")
def introducir_errores_interfaz():
    """
    Maneja la acción de introducir errores en un archivo codificado, con inputs para probabilidad.
    """
    global nombre_archivo_prot  # Acceder a la variable global
    global nombre_archivo_error  # Agregar la variable global
    try: 
        if nombre_archivo_prot:  # Verificar si se ha protegido un archivo
            try:
                # Obtener la extensión del archivo protegido (HA1, HA2, HA3)
                _, extension_entrada = os.path.splitext(nombre_archivo_prot)
                
                # Extraer el tamaño de bloque de la extensión
                if extension_entrada.endswith("1"):
                    tamaño_bloque = 8
                elif extension_entrada.endswith("2"):
                    tamaño_bloque = 4096
                elif extension_entrada.endswith("3"):
                    tamaño_bloque = 65536
                else:
                    messagebox.showerror("Error", "Extensión de archivo no válida.")
                    return

                # Obtener la probabilidad de error simple del input
                probabilidad_simple = float(entry_simple.get().replace(",", "."))  # Convertir a decimal
                # Obtener la probabilidad de error doble del input
                probabilidad_doble = float(entry_doble.get().replace(",", "."))  # Convertir a decimal

                # Validar que las probabilidades estén entre 0 y 1
                if not 0 <= probabilidad_simple <= 1 or not 0 <= probabilidad_doble <= 1:
                    messagebox.showerror("Error", "Las probabilidades de error deben estar entre 0 y 1.")
                    return

                # Validar que la probabilidad doble sea menor que la simple
                if probabilidad_doble >= probabilidad_simple:
                    messagebox.showerror("Error", "La probabilidad de error doble debe ser menor que la simple.")
                    return

                # Abrir el archivo .HAx
                with open(nombre_archivo_prot, 'r', encoding="utf-8") as archivo:
                    base64_encoded = archivo.read()

                byte_array = base64.b64decode(base64_encoded)
                bits = ''.join(format(byte, '08b') for byte in byte_array)

                # Convertir el texto en bloques
                bloques = bits_to_blocks(bits, tamaño_bloque)

                # Introducir errores en los bloques
                bloques_con_errores = introducir_errores(bloques, probabilidad_simple, probabilidad_doble)

                # Generar el nombre del archivo con errores (.HE1, .HE2, .HE3)
                extension = ".HE1" if tamaño_bloque == 8 else ".HE2" if tamaño_bloque == 4096 else ".HE3"
                nombre_archivo_base = os.path.splitext(os.path.basename(nombre_archivo_prot))[0]
                nombre_archivo = f"{nombre_archivo_base}-with-errors{extension}"
                cadena = ""
                # Guardar el archivo con errores
                with open(nombre_archivo, 'w', encoding="utf-8") as f:
                    for bloque in bloques_con_errores:
                        cadena = cadena + bloque
                    byte_array = int(cadena, 2).to_bytes((len(cadena) + 7) // 8, byteorder='big')
                    base64_encoded = base64.b64encode(byte_array).decode('utf-8')
                    f.write(base64_encoded)
                peso = os.path.getsize(nombre_archivo) / 1024
                actualizar_stats_err(peso)


                messagebox.showinfo("Éxito", f"Archivo con errores guardado como: {nombre_archivo}")
                nombre_archivo_error = nombre_archivo # Actualizar la variable global
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo cargar o guardar el archivo: {e}")
        else:
            messagebox.showwarning("Atención", "Debe proteger un archivo primero.")  
    except Exception as e:
        messagebox.showwarning("Error", "Debe proteger un archivo primero.")  


def desproteger_archivo(correccion):
    """
    Maneja la acción de desproteger un archivo codificado.
    """
    global nombre_archivo_prot
    global nombre_archivo_error
    global ruta_desproteger_sin_errores_sin_corregir
    global ruta_desproteger_sin_errores_con_corregir
    global ruta_desproteger_con_errores_sin_corregir
    global ruta_desproteger_con_errores_con_corregir
    
    try:
         # Obtener la opción seleccionada en el menú desplegable
        opcion_seleccionada = dropdown_desproteger.get()

        if opcion_seleccionada == "Archivo sin errores":
            archivo_seleccionado = nombre_archivo_prot
        elif opcion_seleccionada == "Archivo con errores":
            archivo_seleccionado = nombre_archivo_error
        else:
            raise ValueError("Opción de archivo no válida.")
        try: 
            if archivo_seleccionado:
                try:
                    _, extension_entrada = os.path.splitext(archivo_seleccionado)
                    
                    # Extraer el tamaño de bloque de la extensión
                    if extension_entrada.endswith("1"):
                        tamaño_bloque = 8
                    elif extension_entrada.endswith("2"):
                        tamaño_bloque = 4096
                    elif extension_entrada.endswith("3"):
                        tamaño_bloque = 65536
                    else:
                        messagebox.showerror("Error", "Extensión de archivo no válida.")
                        return

                    with open(archivo_seleccionado, 'r', encoding="utf-8") as archivo:
                        base64_encoded = archivo.read()

                    byte_array = base64.b64decode(base64_encoded)
                    bits = ''.join(format(byte, '08b') for byte in byte_array)

                    # Convertir el texto en bloques
                    bloques = bits_to_blocks(bits, tamaño_bloque)

                    # Desproteger los bloques
                    archivo_decodificado, errores_simples, errores_dobles = desproteger_archivo_txt(bloques, tamaño_bloque, correccion)

                    # Generar la extensión de salida (DE o DC)
                    extension_salida = ".DE" + extension_entrada[-1]
                    if correccion:
                        extension_salida = extension_salida.replace("DE", "DC") 
                    nombre_archivo_base = os.path.splitext(os.path.basename(archivo_seleccionado))[0]
                    nombre_archivo = f"{nombre_archivo_base}-unprotected{extension_salida}"
                    
                    # Guardar el archivo desprotegido y actualizar la ruta correspondiente
                    with open(nombre_archivo, 'w', encoding="utf-8") as archivo:
                        archivo.write(archivo_decodificado)
                    
                    # Actualizar la ruta según la opción y la corrección
                    if opcion_seleccionada == "Archivo sin errores":
                        if correccion:
                            ruta_desproteger_sin_errores_con_corregir = nombre_archivo
                            actualizar_stats_desproteger_sin_errores(ruta_desproteger_sin_errores_con_corregir, True)
                            stats_data["Desprotegido sin errores corregido"]["Cantidad de errores simples"] = errores_simples
                            stats_data["Desprotegido sin errores corregido"]["Cantidad de errores dobles"] = errores_dobles
                        else:
                            ruta_desproteger_sin_errores_sin_corregir = nombre_archivo
                            actualizar_stats_desproteger_sin_errores(ruta_desproteger_sin_errores_sin_corregir, False)
                            stats_data["Desprotegido sin errores sin corregir"]["Cantidad de errores simples"] = errores_simples
                            stats_data["Desprotegido sin errores sin corregir"]["Cantidad de errores dobles"] = errores_dobles
                    else:
                        if correccion:
                            ruta_desproteger_con_errores_con_corregir = nombre_archivo
                            actualizar_stats_desproteger_con_errores(ruta_desproteger_con_errores_con_corregir, True)
                            stats_data["Desprotegido con errores corregido"]["Cantidad de errores simples"] = errores_simples
                            stats_data["Desprotegido con errores corregido"]["Cantidad de errores dobles"] = errores_dobles
                        else:
                            ruta_desproteger_con_errores_sin_corregir = nombre_archivo
                            actualizar_stats_desproteger_con_errores(ruta_desproteger_con_errores_sin_corregir, False)
                            stats_data["Desprotegido con errores sin corregir"]["Cantidad de errores simples"] = errores_simples
                            stats_data["Desprotegido con errores sin corregir"]["Cantidad de errores dobles"] = errores_dobles
                    
                    messagebox.showinfo("Éxito", f"Archivo desprotegido guardado como: {nombre_archivo}")
                except Exception as e:
                    messagebox.showerror("Error", f"No se pudo cargar o guardar el archivo: {e}")
            else:
                messagebox.showwarning("Atención", f"No se ha generado un '{opcion_seleccionada}'.")
        except Exception as e:
            messagebox.showwarning("Atención", f"No se ha generado un '{opcion_seleccionada}'.")
    except ValueError as e:
        messagebox.showerror("Error", str(e))
    except Exception as e:
        messagebox.showwarning("Atención", "Debe proteger un archivo primero o introducir errores.")

def ver_archivos():
    """
    Abre una ventana para comparar el archivo original y sus desprotecciones.
    """
    global archivo  # Acceder a la variable global del archivo original
    try: 
        if archivo:
            ventana_ver = tk.Toplevel(root)
            ventana_ver.title("Comparar archivos")

            # Crear áreas de texto para cada archivo
            area_texto_original = scrolledtext.ScrolledText(ventana_ver, width=40, height=20)
            area_texto_original.pack(side=tk.LEFT)

            # Mostrar el contenido del archivo original
            try:
                with open(archivo, 'r', encoding='utf-8') as f:
                    contenido_original = f.read()
                area_texto_original.insert(tk.END, f"\n\nArchivo Original\n\n{contenido_original}") 
                area_texto_original.tag_add("titulo_original", "1.0", "1.0 lineend")
                area_texto_original.tag_config("titulo_original", foreground="blue", font=("Helvetica", 12, "bold"))
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo cargar el archivo original: {e}")

            # Mostrar archivos desprotegidos en áreas de texto separadas
            for ruta, nombre in zip(
                [
                    ruta_desproteger_sin_errores_sin_corregir,
                    ruta_desproteger_sin_errores_con_corregir,
                    ruta_desproteger_con_errores_sin_corregir,
                    ruta_desproteger_con_errores_con_corregir,
                ],
                [
                    "Desprotegido sin errores, sin corregir",
                    "Desprotegido sin errores, con corrección",
                    "Desprotegido con errores, sin corregir",
                    "Desprotegido con errores, con corrección",
                ],
            ):
                if ruta:  # Verificar si la ruta está definida
                    area_texto_desprotegido = scrolledtext.ScrolledText(ventana_ver, width=40, height=20)
                    area_texto_desprotegido.pack(side=tk.LEFT)
                    try:
                        with open(ruta, 'r', encoding='utf-8') as f:
                            contenido_desprotegido = f.read()
                        area_texto_desprotegido.insert(tk.END, f"\n\n{nombre}\n\n{contenido_desprotegido}")
                        area_texto_desprotegido.tag_add("titulo_desprotegido", "1.0", "1.0 lineend")
                        area_texto_desprotegido.tag_config("titulo_desprotegido", foreground="blue", font=("Helvetica", 12, "bold"))
                    except Exception as e:
                        messagebox.showerror("Error", f"No se pudo cargar el archivo desprotegido: {e}")

        else:
            messagebox.showwarning("Atención", "Debe seleccionar un archivo primero.")
    except Exception as e:
        messagebox.showwarning("Atención", "Debe seleccionar un archivo primero.")



def ver_estadisticas():
    """
    Muestra la tabla de estadísticas en una nueva ventana.
    """
    stats_window = tk.Toplevel(root)
    stats_window.title("Estadísticas")

    # Crea una etiqueta vacía en la celda superior izquierda
    tk.Label(stats_window, text="", width=30).grid(row=0, column=0, sticky="w")

    # Crea el encabezado de la tabla
    header_labels = ["Peso en kb", "Cantidad de errores simples", "Cantidad de errores dobles"]
    for i, label_text in enumerate(header_labels):
        label = tk.Label(stats_window, text=label_text, width=20, relief=tk.RIDGE)
        label.grid(row=0, column=i + 1, sticky="ew")  # Ajustar las columnas del encabezado

    # Crea las filas de la tabla
    for i, (key, values) in enumerate(stats_data.items()):
        label_key = tk.Label(stats_window, text=key, width=30, anchor=tk.W)
        label_key.grid(row=i + 1, column=0, sticky="w")

        # Crea las columnas de la fila
        for j, value in enumerate(values.values()):
            label_value = tk.Label(stats_window, text=value, width=20, relief=tk.RIDGE)
            label_value.grid(row=i + 1, column=j + 1, sticky="ew")


# --- Configuración de la interfaz gráfica ---

root = tk.Tk()
root.title("Protección y Desprotección de Archivos con Hamming")

# Ampliar la ventana
root.geometry("500x500")  

root.configure(bg="#5c5a5a")  # Color gris claro

frame = tk.Frame(root)
frame.pack(pady=20)
frame.configure(bg="#5c5a5a")  # Color gris claro


label_archivo = tk.Label(frame, text="")
label_archivo.pack(pady=10, anchor="w")  # Alinear a la izquierda
label_archivo.configure(bg="#5c5a5a")  # Color gris claro

boton_seleccionar = tk.Button(frame, text="Seleccionar archivo", command=seleccionar_archivo, bg="#555555", fg="white", activebackground="#777777", activeforeground="white")
boton_seleccionar.pack(pady=10)  # Alinear a la izquierda


# --- Marco para proteger archivo ---
marco_proteger = tk.Frame(frame, bg="#282828")
marco_proteger.pack(pady=10, anchor='w')

boton_proteger = tk.Button(marco_proteger, text="Proteger archivo", command=proteger_archivo, bg="#555555", fg="white", activebackground="#777777", activeforeground="white")
boton_proteger.pack(side=tk.LEFT, padx=5)

tamaño_bloque_label = tk.Label(marco_proteger, text="Tamaño del bloque:", bg="#282828", fg="white")
tamaño_bloque_label.pack(side=tk.LEFT, padx=5)

dropdown_tamaño_bloque = tk.StringVar()
dropdown_tamaño_bloque.set("8")  # Valor predeterminado
dropdown_menu = tk.OptionMenu(marco_proteger, dropdown_tamaño_bloque, "8", "4096", "65536")
dropdown_menu.config(bg="#333333", fg="white", highlightthickness=0)
dropdown_menu["menu"].config(bg="#333333", fg="white")
dropdown_menu.pack(side=tk.LEFT, padx=5)

# --- Botón Introducir errores ---
boton_introducir_errores = tk.Button(frame, text="Introducir errores", command=introducir_errores_interfaz, bg="#555555", fg="white", activebackground="#777777", activeforeground="white")
boton_introducir_errores.pack(pady=10, anchor="w")  # Alinear a la izquierda


label_simple = tk.Label(frame, text="Probabilidad de error simple (0 a 1):", bg="#555555", fg="white", activebackground="#777777", activeforeground="white")
label_simple.pack(anchor="w")
entry_simple = tk.Entry(frame)
entry_simple.insert(0, "0")
entry_simple.pack(anchor="w")

label_doble = tk.Label(frame, text="Probabilidad de error doble (0 a 1):", bg="#555555", fg="white", activebackground="#777777", activeforeground="white")
label_doble.pack(anchor="w")
entry_doble = tk.Entry(frame)
entry_doble.insert(0, "0")
entry_doble.pack(anchor="w")




# --- Marco para desproteger sin corregir ---
marco_desproteger_sin_corregir = tk.Frame(frame, bg="#282828")
marco_desproteger_sin_corregir.pack(pady=10)

boton_desproteger_sin_correccion = tk.Button(marco_desproteger_sin_corregir, text="Desproteger sin corregir", command=lambda: desproteger_archivo(False), bg="#555555", fg="white", activebackground="#777777", activeforeground="white")
boton_desproteger_sin_correccion.pack(side=tk.LEFT, padx=5)

dropdown_desproteger = tk.StringVar()
dropdown_desproteger.set("Archivo sin errores")
dropdown_menu_desproteger = tk.OptionMenu(marco_desproteger_sin_corregir, dropdown_desproteger, "Archivo sin errores", "Archivo con errores")
dropdown_menu_desproteger.config(bg="#333333", fg="white", highlightthickness=0)
dropdown_menu_desproteger["menu"].config(bg="#333333", fg="white")
dropdown_menu_desproteger.pack(side=tk.LEFT, padx=5)

boton_desproteger_con_correccion = tk.Button(marco_desproteger_sin_corregir, text="Desproteger corrigiendo", command=lambda: desproteger_archivo(True), bg="#555555", fg="white", activebackground="#777777", activeforeground="white")
boton_desproteger_con_correccion.pack(pady=10, anchor="w")  # Alinear a la izquierda

boton_ver_archivos = tk.Button(frame, text="Ver archivos", command=ver_archivos, bg="#555555", fg="white", activebackground="#777777", activeforeground="white")
boton_ver_archivos.pack(pady=10)  # Alinear a la izquierda}

# Botón para ver estadísticas
boton_ver_estadisticas = tk.Button(frame, text="Ver Estadísticas", command=ver_estadisticas, bg="#555555", fg="white", activebackground="#777777", activeforeground="white")
boton_ver_estadisticas.pack(pady=10)  # Alinear a la izquierda

# --- Botón "Volver"
boton_volver = tk.Button(frame, text="Volver", command=lambda: root.destroy(), bg="#555555", fg="white", activebackground="#777777", activeforeground="white")
boton_volver.pack(pady=10)  # Alinear a la izquierda


root.mainloop()