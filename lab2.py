import os
import heapq
import json
from collections import Counter
from bitarray import bitarray
import base64
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk

# Clase Nodo para el árbol de Huffman
class Node:
    def __init__(self, freq, symbol, left=None, right=None):
        # Inicializa un nodo del árbol de Huffman con su frecuencia, símbolo y referencias a los nodos hijos
        self.freq = freq
        self.symbol = symbol
        self.left = left
        self.right = right
        self.huff = ''  # Aquí se almacenará el código Huffman

    def __lt__(self, nxt):
        # Método especial para comparar nodos basados en su frecuencia
        return self.freq < nxt.freq

# Función para calcular las frecuencias y generar el árbol de Huffman
def build_huffman_tree(text):
    # Calcula las frecuencias de cada caracter en el texto
    frequency = Counter(text)

    #lista = ['a', 'b', 'c', 'a', 'b', 'a', 'd']
    #Counter({'a': 3, 'b': 2, 'c': 1, 'd': 1})


    # Crea un heap de prioridad a partir de las frecuencias
    heap = [[weight, Node(weight, char)] for char, weight in frequency.items()]
    heapq.heapify(heap)
    
    while len(heap) > 1:
        # Combina los dos nodos de menor frecuencia para formar un nuevo nodo
        lo = heapq.heappop(heap)
        hi = heapq.heappop(heap)
        node = Node(lo[0] + hi[0], None, lo[1], hi[1])
        heapq.heappush(heap, [node.freq, node])
    
    # Retorna el nodo raíz del árbol de Huffman y las frecuencias de cada caracter
    return heap[0][1], frequency

# Función para generar los códigos Huffman
def generate_huffman_codes(node, code=""):
    # Recorre el árbol de Huffman y genera los códigos para cada caracter
    if node is None:
        return {}
    if node.symbol is not None:
        return {node.symbol: code} if code else {node.symbol: "0"}  # Agrega código vacío si no hay código
    codes = {}
    codes.update(generate_huffman_codes(node.left, code + "0"))
    codes.update(generate_huffman_codes(node.right, code + "1"))
    return codes

# Función para comprimir el archivo
def compress_file(file_path):
    # Lee el contenido del archivo
    with open(file_path, 'r') as file:
        text = file.read()
        original_length = len(text)  # Guarda la longitud original    
    if original_length == 0:
        messagebox.showerror("Error", "El archivo está vacío. No se puede comprimir.")
        return None, None, 0  # Retorna None para indicar error
    # Construye el árbol de Huffman y los códigos Huffman
    huffman_tree, frequency = build_huffman_tree(text)
    huffman_codes = generate_huffman_codes(huffman_tree)
    
    # Codifica el texto usando los códigos Huffman
    encoded_text = ''.join(huffman_codes[char] for char in text)
    bit_array = bitarray(encoded_text)
    
    # Escribe el texto comprimido en un archivo
    compressed_file_path = file_path + '.huf'
    with open(compressed_file_path, 'w') as compressed_file:
        # Convierte los bytes a Base64 y escribe como texto
        compressed_file.write(base64.b64encode(bit_array.tobytes()).decode('ascii'))
    
    # Guarda la tabla de frecuencias en un archivo JSON
    frequency_table_path = file_path + '_freq.json'
    with open(frequency_table_path, 'w') as freq_file:
        # Agrega la longitud original al JSON
        frequency['original_length'] = original_length
        json.dump(frequency, freq_file)
    
    # Retorna la ruta del archivo comprimido, la tabla de frecuencias y el tamaño del texto comprimido
    return compressed_file_path, frequency_table_path, len(bit_array)
# Función para descomprimir el archivo
def decompress_file(compressed_file_path, frequency_table_path):
    # Lee el archivo comprimido y la tabla de frecuencias
    with open(compressed_file_path, 'r') as file:
        # Lee el archivo Base64 y lo convierte a bytes
        bit_array = bitarray()
        bit_array.frombytes(base64.b64decode(file.read()))
    
    with open(frequency_table_path, 'r') as freq_file:
        frequency = json.load(freq_file)
        original_length = frequency['original_length']  # Obtiene la longitud original del JSON
        del frequency['original_length']
    
    # Reconstruye el árbol de Huffman y los códigos Huffman a partir de la tabla de frecuencias
    huffman_tree = build_huffman_tree_from_freq(frequency)
    huffman_codes = generate_huffman_codes(huffman_tree)
    
    # Decodifica el texto comprimido usando los códigos Huffman
    inverse_huffman_codes = {v: k for k, v in huffman_codes.items()}
    current_code = ""
    decoded_text = []
    i = 0
    decoded_length = 0  # Contador de caracteres decodificados
    
    while decoded_length < original_length:  # Controla la decodificación con la longitud original
        # Concatena los bits hasta encontrar un código válido
        current_code += '1' if bit_array[i] else '0'
        if current_code in inverse_huffman_codes:
            character = inverse_huffman_codes[current_code]
            decoded_text.append(character)
            current_code = ""
            decoded_length += 1  # Incrementa el contador de caracteres decodificados
        i += 1

    print(current_code)
    
    # Escribe el texto descomprimido en un archivo
    decompressed_file_path = compressed_file_path + ".dhu"
    
    with open(decompressed_file_path, 'w') as decompressed_file:
        decompressed_file.write(''.join(decoded_text))
    
    # Retorna la ruta del archivo descomprimido
    return decompressed_file_path

# Función para construir el árbol de Huffman a partir de la tabla de frecuencias
def build_huffman_tree_from_freq(frequency):
    heap = [[weight, Node(weight, char)] for char, weight in frequency.items()]
    heapq.heapify(heap)
    
    while len(heap) > 1:
        lo = heapq.heappop(heap)
        hi = heapq.heappop(heap)
        node = Node(lo[0] + hi[0], None, lo[1], hi[1])
        heapq.heappush(heap, [node.freq, node])
    
    return heap[0][1]

# Función para ver estadísticas
def view_statistics(original_file, compressed_file, decompressed_file):
    # Verifica si cada archivo existe y obtiene su tamaño o establece a '-'
    original_size = os.path.getsize(original_file) if original_file and os.path.exists(original_file) else '-'
    compressed_size = os.path.getsize(compressed_file) if compressed_file and os.path.exists(compressed_file) else '-'
    decompressed_size = os.path.getsize(decompressed_file) if decompressed_file and os.path.exists(decompressed_file) else '-'

    # Construye el mensaje de estadísticas solo con los archivos presentes
    stats = []
    if original_size != '-':
        stats.append(f"Tamaño del archivo original: {original_size} bytes")
    if compressed_size != '-':
        stats.append(f"Tamaño del archivo comprimido: {compressed_size} bytes")
    if decompressed_size != '-':
        stats.append(f"Tamaño del archivo descomprimido: {decompressed_size} bytes")
    
    return "\n".join(stats)

# Clase principal para la GUI
class HuffmanApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Compresión de Archivos con Huffman")
        self.root.geometry("500x400")
        
        self.file_path = None
        self.compressed_file_path = None
        self.decompressed_file_path = None
        self.frequency_table_path = None
        self.original_text_length = 0

        self.create_widgets()

    def create_widgets(self):
        style = ttk.Style()
        style.configure("TButton", font=("Helvetica", 12), padding=10)
        style.configure("TLabel", font=("Helvetica", 14))
        
        self.label = ttk.Label(self.root, text="Compresión de Archivos con Huffman")
        self.label.pack(pady=20)

        self.load_button = ttk.Button(self.root, text="Cargar Archivo Texto", command=self.load_file)
        self.load_button.pack(pady=5)

        self.compress_button = ttk.Button(self.root, text="Compactar Archivo", command=self.compress_file)
        self.compress_button.pack(pady=5)

        self.decompress_button = ttk.Button(self.root, text="Descompactar Archivo", command=self.load_files_for_decompression)
        self.decompress_button.pack(pady=5)

        self.view_button = ttk.Button(self.root, text="Ver Archivos en Pantalla", command=self.view_files)
        self.view_button.pack(pady=5)

        self.stats_button = ttk.Button(self.root, text="Ver Estadística", command=self.view_statistics)
        self.stats_button.pack(pady=5)

        self.quit_button = ttk.Button(self.root, text="Salir", command=self.root.quit)
        self.quit_button.pack(pady=5)

    def load_file(self):
        self.file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if self.file_path:
            with open(self.file_path, 'r') as file:
                self.original_text_length = len(file.read())
            messagebox.showinfo("Archivo Cargado", f"Archivo cargado: {self.file_path}")

    def compress_file(self):
        if not self.file_path:
            messagebox.showerror("Error", "Por favor, cargue un archivo primero.")
            return
        
        self.compressed_file_path, self.frequency_table_path, _ = compress_file(self.file_path)
        messagebox.showinfo("Archivo Comprimido", f"Archivo comprimido generado: {self.compressed_file_path}\nTabla de frecuencia guardada: {self.frequency_table_path}")

    def load_files_for_decompression(self):
        self.compressed_file_path = filedialog.askopenfilename(filetypes=[("Huffman Compressed files", "*.huf"), ('Hamming Unprotected Files', '*.DC1 *.DC2 *.DC3 *.DE1 *.DE2 *.DE3')])
        self.frequency_table_path = filedialog.askopenfilename(filetypes=[("Frequency Table files", "*.json")])
        
        if self.compressed_file_path and self.frequency_table_path:
            self.decompress_file()

    def decompress_file(self):
        if not self.compressed_file_path or not self.frequency_table_path:
            messagebox.showerror("Error", "Por favor, cargue un archivo comprimido y su tabla de frecuencia primero.")
            return
        
        self.decompressed_file_path = decompress_file(self.compressed_file_path, self.frequency_table_path)
        messagebox.showinfo("Archivo Descomprimido", f"Archivo descomprimido generado: {self.decompressed_file_path}")

    def view_files(self):
        if not self.file_path and not self.compressed_file_path and not self.decompressed_file_path:
            messagebox.showerror("Error", "No hay ningún archivo cargado para ver.")
            return

        view_window = tk.Toplevel(self.root)
        view_window.title("Archivos Original, Comprimido y Descomprimido")
        view_window.geometry("600x600")

        if self.file_path and os.path.exists(self.file_path):
            original_label = ttk.Label(view_window, text="Archivo Original:")
            original_label.pack(pady=5)
            original_text = scrolledtext.ScrolledText(view_window, width=80, height=10)
            original_text.pack(pady=5)
            with open(self.file_path, 'r') as original_file:
                original_text.insert(tk.END, original_file.read())

        if self.compressed_file_path and os.path.exists(self.compressed_file_path):
            compressed_label = ttk.Label(view_window, text="Archivo Comprimido:")
            compressed_label.pack(pady=5)
            compressed_text = scrolledtext.ScrolledText(view_window, width=80, height=10)
            compressed_text.pack(pady=5)
            with open(self.compressed_file_path, 'r') as compressed_file:
                compressed_text.insert(tk.END, compressed_file.read())

        if self.decompressed_file_path and os.path.exists(self.decompressed_file_path):
            decompressed_label = ttk.Label(view_window, text="Archivo Descomprimido:")
            decompressed_label.pack(pady=5)
            decompressed_text = scrolledtext.ScrolledText(view_window, width=80, height=10)
            decompressed_text.pack(pady=5)
            with open(self.decompressed_file_path, 'r') as decompressed_file:
                decompressed_text.insert(tk.END, decompressed_file.read())


    def view_statistics(self):
        if not self.file_path and not self.compressed_file_path and not self.decompressed_file_path:
            messagebox.showerror("Error", "No hay ningún archivo cargado para ver las estadísticas.")
            return

        stats = view_statistics(self.file_path, self.compressed_file_path, self.decompressed_file_path)
        messagebox.showinfo("Estadísticas", stats)

if __name__ == "__main__":
    root = tk.Tk()
    app = HuffmanApp(root)
    root.mainloop()
